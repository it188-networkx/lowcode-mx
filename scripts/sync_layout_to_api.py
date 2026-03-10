#!/usr/bin/env python3
"""
将页面布局 JSON 配置文件通过 API 同步（新增/更新）到服务端。

用法:
    python sync_layout_to_api.py <json_file>
    python sync_layout_to_api.py <json_file> --dry-run

示例:
    python sync_layout_to_api.py ceshiAI.json
    python sync_layout_to_api.py data/ceshiAI.json --dry-run
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

def load_layout_data(filepath: str) -> dict:
    """加载布局 JSON 文件，返回布局对象 dict。"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict) and "layoutID" in data:
        return data

    # 支持 {"type": "layout", "list": [{...}]} 包装格式
    if isinstance(data, dict) and "list" in data and isinstance(data["list"], list):
        for item in data["list"]:
            if isinstance(item, dict) and "layoutID" in item:
                return item

    raise ValueError(f"无法识别 JSON 文件格式: {filepath}")


# ────────────────────── API 请求体构建 ──────────────────────

_LAYOUT_BODY_KEYS = [
    "weight", "moduleID", "handle", "ownedBy",
    "meta", "config", "blocks", "updatedAt",
]


def build_api_body(layout: dict) -> dict:
    """从布局 JSON 构建 API 请求体。"""
    return {k: layout[k] for k in _LAYOUT_BODY_KEYS if k in layout}


# ────────────────── 布局存在性检测 ──────────────────

def find_layout_by_handle(
    base_url: str, headers: dict, namespace_id: str, page_id: str, handle: str
) -> str | None:
    """通过 handle 在指定页面下查找已存在的布局，返回 pageLayoutID；未找到返回 None。"""
    if not handle:
        return None
    items = api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/page/{page_id}/layout/",
    )
    for l in items:
        if l.get("handle") == handle:
            return str(l["pageLayoutID"])
    return None


# ──────────────────── 同步主函数 ────────────────────

def sync_layout(
    layout: dict,
    *,
    base_url: str,
    headers: dict,
    dry_run: bool = False,
) -> dict | None:
    """
    通过 API 同步布局到服务端（新增或更新）。

    注意：
    - 本地 JSON 使用 `layoutID` 字段，API 使用 `pageLayoutID`。
    - 布局 API 路径含 pageID：/compose/namespace/{nsID}/page/{pageID}/layout/
    """
    namespace_id = str(layout["namespaceID"])
    page_id = str(layout["pageID"])
    # 本地 JSON 字段名为 layoutID，API 中为 pageLayoutID
    layout_id = str(layout.get("layoutID", "0"))
    handle = layout.get("handle", "")

    req_headers = dict(headers)
    req_headers["X-NAMESPACE-ID"] = namespace_id

    if dry_run:
        meta = layout.get("meta", {})
        print(f"\n[预览模式] 以下数据不会实际发送到服务端\n")
        body = build_api_body(layout)
        print(f"  namespaceID: {namespace_id}")
        print(f"  pageID:      {page_id}")
        print(f"  layoutID:    {layout_id}")
        print(f"  title:       {meta.get('title', '')}")
        print(f"  handle:      {handle}")
        print(f"  blocks:      {len(layout.get('blocks') or [])} 个")
        print(f"  请求体大小:  {len(json.dumps(body, ensure_ascii=False))} 字符")
        return None

    # ── 判断新增 or 更新 ──
    exists = False
    if layout_id and layout_id != "0":
        # 使用全局 page-layout 列表检测
        exists = resource_exists(
            base_url, req_headers,
            f"/compose/namespace/{namespace_id}/page/{page_id}/layout/{layout_id}",
        )
        # 如果直接 GET 不可用，回退到列表查找
        if not exists:
            items = api_list_all(
                base_url, req_headers,
                f"/compose/namespace/{namespace_id}/page/{page_id}/layout/",
            )
            for item in items:
                if str(item.get("pageLayoutID")) == layout_id:
                    exists = True
                    break

    if not exists and handle:
        found_id = find_layout_by_handle(
            base_url, req_headers, namespace_id, page_id, handle
        )
        if found_id:
            layout_id = found_id
            exists = True
            print(f"  ℹ 通过 handle='{handle}' 找到已有布局: pageLayoutID={layout_id}")

    if exists:
        print(f"  📝 布局已存在 (pageLayoutID={layout_id})，执行更新...")
        body = build_api_body(layout)
        url = f"/compose/namespace/{namespace_id}/page/{page_id}/layout/{layout_id}"
        resp = api_post(base_url, req_headers, url, data=body)
        print(f"  ✔ 更新成功")
        return resp
    else:
        print(f"  ➕ 布局不存在，执行新增...")
        body = build_api_body(layout)
        url = f"/compose/namespace/{namespace_id}/page/{page_id}/layout/"
        resp = api_post(base_url, req_headers, url, data=body)
        new_id = resp.get("response", {}).get("pageLayoutID", "?")
        print(f"  ✔ 新增成功 (pageLayoutID={new_id})")
        return resp


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将页面布局 JSON 配置通过 API 同步到服务端（新增/更新）"
    )
    parser.add_argument(
        "json_file",
        help="布局 JSON 文件路径，如 ceshiAI.json",
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
    layout = load_layout_data(str(json_path))
    meta = layout.get("meta", {})
    print(f"   标题:     {meta.get('title', '')}")
    print(f"   layoutID: {layout.get('layoutID')}")
    print(f"   pageID:   {layout.get('pageID')}")
    print(f"   handle:   {layout.get('handle')}")
    print(f"   blocks 数: {len(layout.get('blocks') or [])}")

    try:
        sync_layout(
            layout,
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
