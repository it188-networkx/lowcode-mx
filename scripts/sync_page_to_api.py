#!/usr/bin/env python3
"""
将页面 JSON 配置文件通过 API 同步（新增/更新）到服务端。

用法:
    python sync_page_to_api.py <json_file>
    python sync_page_to_api.py <json_file> --dry-run

示例:
    python sync_page_to_api.py ceshiAi.json
    python sync_page_to_api.py data/ceshiAI.json --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

from api_utils import (
    load_api_config, api_post, api_list_all,
    resource_exists, APIError,
)


# ────────────────────────────── 解析 JSON ──────────────────────────────

def load_page_data(filepath: str) -> dict:
    """加载页面 JSON 文件，返回页面对象 dict。"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict) and "pageID" in data:
        return data

    # 支持 {"type": "page", "list": [{...}]} 包装格式
    if isinstance(data, dict) and "list" in data and isinstance(data["list"], list):
        for item in data["list"]:
            if isinstance(item, dict) and "pageID" in item:
                return item

    raise ValueError(f"无法识别 JSON 文件格式: {filepath}")


# ────────────────────── API 请求体构建 ──────────────────────

_PAGE_BODY_KEYS = [
    "selfID", "moduleID", "title", "handle", "description",
    "weight", "labels", "visible", "blocks", "config", "meta",
    "updatedAt",
]


def build_api_body(page: dict) -> dict:
    """从页面 JSON 构建 API 请求体。"""
    return {k: page[k] for k in _PAGE_BODY_KEYS if k in page}


# ────────────────── 页面存在性检测 ──────────────────

def find_page_by_handle(
    base_url: str, headers: dict, namespace_id: str, handle: str
) -> str | None:
    """通过 handle 查找已存在的页面，返回 pageID；未找到返回 None。"""
    if not handle:
        return None
    items = api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/page/",
        {"handle": handle, "limit": 1},
    )
    for p in items:
        if p.get("handle") == handle:
            return str(p["pageID"])
    return None


# ──────────────────── 同步主函数 ────────────────────

def sync_page(
    page: dict,
    *,
    base_url: str,
    headers: dict,
    dry_run: bool = False,
) -> dict | None:
    """
    通过 API 同步页面到服务端（新增或更新）。

    逻辑：
    1. 若 JSON 中有 pageID 且非 "0" → 检查服务端是否已存在
    2. 已存在 → POST 更新
    3. 不存在 → 按 handle 再查一次；仍不存在 → POST 新增
    """
    namespace_id = str(page["namespaceID"])
    page_id = str(page.get("pageID", "0"))
    handle = page.get("handle", "")

    req_headers = dict(headers)
    req_headers["X-NAMESPACE-ID"] = namespace_id

    if dry_run:
        print(f"\n[预览模式] 以下数据不会实际发送到服务端\n")
        body = build_api_body(page)
        print(f"  namespaceID: {namespace_id}")
        print(f"  pageID:      {page_id}")
        print(f"  title:       {page.get('title')}")
        print(f"  handle:      {handle}")
        print(f"  blocks:      {len(page.get('blocks') or [])} 个")
        print(f"  请求体大小:  {len(json.dumps(body, ensure_ascii=False))} 字符")
        return None

    # ── 判断新增 or 更新 ──
    exists = False
    if page_id and page_id != "0":
        exists = resource_exists(
            base_url, req_headers,
            f"/compose/namespace/{namespace_id}/page/{page_id}",
        )

    if not exists and handle:
        found_id = find_page_by_handle(base_url, req_headers, namespace_id, handle)
        if found_id:
            page_id = found_id
            exists = True
            print(f"  ℹ 通过 handle='{handle}' 找到已有页面: pageID={page_id}")

    if exists:
        print(f"  📝 页面已存在 (pageID={page_id})，执行更新...")
        body = build_api_body(page)
        url = f"/compose/namespace/{namespace_id}/page/{page_id}"
        resp = api_post(base_url, req_headers, url, data=body)
        print(f"  ✔ 更新成功")
        return resp
    else:
        print(f"  ➕ 页面不存在，执行新增...")
        body = build_api_body(page)
        url = f"/compose/namespace/{namespace_id}/page/"
        resp = api_post(base_url, req_headers, url, data=body)
        new_id = resp.get("response", {}).get("pageID", "?")
        print(f"  ✔ 新增成功 (pageID={new_id})")
        return resp


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将页面 JSON 配置通过 API 同步到服务端（新增/更新）"
    )
    parser.add_argument(
        "json_file",
        help="页面 JSON 文件路径，如 ceshiAi.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只打印将要发送的数据，不实际调用 API",
    )
    parser.add_argument(
        "--env", type=str, default=None,
        help="环境名（如 dev.dms），不指定则使用 env.json 的 active 值",
    )
    parser.add_argument(
        "--tenant", type=str, default=None,
        help="租户名（如 mx），不指定则使用该环境下的第一个租户",
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)

    cfg = load_api_config(env=args.env, tenant=args.tenant)
    base_url = cfg["baseUrl"]
    api_headers = cfg["headers"]

    if not base_url:
        print("❌ env.json 中未配置 baseUrl")
        sys.exit(1)

    print(f"🔗 API: {base_url}")

    print(f"📄 正在读取: {json_path}")
    page = load_page_data(str(json_path))
    print(f"   页面标题: {page.get('title')}")
    print(f"   pageID:   {page.get('pageID')}")
    print(f"   handle:   {page.get('handle')}")
    print(f"   blocks 数: {len(page.get('blocks') or [])}")

    try:
        sync_page(
            page,
            base_url=base_url,
            headers=api_headers,
            dry_run=args.dry_run,
        )
    except APIError as e:
        print(f"\n❌ API 调用失败: {e}")
        if e.body:
            print(f"   响应: {e.body[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
