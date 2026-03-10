#!/usr/bin/env python3
"""
将模块 JSON 配置文件通过 API 同步（新增/更新）到服务端。

用法:
    python sync_module_to_api.py <json_file>
    python sync_module_to_api.py <json_file> --dry-run

示例:
    python sync_module_to_api.py TestModule.json
    python sync_module_to_api.py TestModule.json --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

from api_utils import (
    load_api_config, api_get, api_post, api_list_all,
    resource_exists, APIError,
)


# ────────────────────────────── 解析 JSON ──────────────────────────────

def load_module_data(filepath: str) -> dict:
    """加载模块 JSON 文件，返回模块对象 dict。"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict) and "moduleID" in data:
        return data

    # 支持 {"type": "module", "list": [{...}]} 包装格式
    if isinstance(data, dict) and "list" in data and isinstance(data["list"], list):
        for item in data["list"]:
            if isinstance(item, dict) and "moduleID" in item:
                return item

    raise ValueError(f"无法识别 JSON 文件格式: {filepath}")


# ────────────────────── API 请求体构建 ──────────────────────

# 更新 API 请求体中需要保留的字段
_MODULE_BODY_KEYS = [
    "name", "handle", "type", "isBlockDataTree",
    "systemModuleField", "fields", "config",
    "meta", "labels",
]


def build_api_body(module: dict, *, is_create: bool = False) -> dict:
    """
    从模块 JSON 构建 API 请求体。

    Args:
        module:    完整的模块 JSON dict。
        is_create: 是否为新增模式。新增时 fieldID 设为 "0" 让服务端自动分配。
    """
    body = {k: module[k] for k in _MODULE_BODY_KEYS if k in module}

    if is_create:
        # 新增模式下，将 fieldID 置为 "0"，由服务端分配
        for field in body.get("fields", []):
            field["fieldID"] = "0"

    return body


# ────────────────── 模块存在性检测 ──────────────────

def find_module_by_handle(
    base_url: str, headers: dict, namespace_id: str, handle: str
) -> str | None:
    """通过 handle 查找已存在的模块，返回 moduleID；未找到返回 None。"""
    if not handle:
        return None
    items = api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/module/",
        {"handle": handle, "limit": 1},
    )
    for m in items:
        if m.get("handle") == handle:
            return str(m["moduleID"])
    return None


# ──────────────────── 同步主函数 ────────────────────

def sync_module(
    module: dict,
    *,
    base_url: str,
    headers: dict,
    dry_run: bool = False,
) -> dict | None:
    """
    通过 API 同步模块到服务端（新增或更新）。

    逻辑：
    1. 若 JSON 中有 moduleID 且非 "0" → 检查服务端是否已存在
    2. 已存在 → POST 更新
    3. 不存在 → 按 handle 再查一次；仍不存在 → POST 新增

    Returns:
        dict: API 响应 JSON（成功时）；dry_run 模式返回 None。
    """
    namespace_id = str(module["namespaceID"])
    module_id = str(module.get("moduleID", "0"))
    handle = module.get("handle", "")

    # 合并 X-NAMESPACE-ID 到请求头
    req_headers = dict(headers)
    req_headers["X-NAMESPACE-ID"] = namespace_id

    if dry_run:
        print(f"\n[预览模式] 以下数据不会实际发送到服务端\n")
        body = build_api_body(module)
        print(f"  namespaceID: {namespace_id}")
        print(f"  moduleID:    {module_id}")
        print(f"  name:        {module.get('name')}")
        print(f"  handle:      {handle}")
        print(f"  fields:      {len(module.get('fields', []))} 个")
        print(f"  请求体大小:  {len(json.dumps(body, ensure_ascii=False))} 字符")
        return None

    # ── 判断新增 or 更新 ──
    exists = False
    if module_id and module_id != "0":
        exists = resource_exists(
            base_url, req_headers,
            f"/compose/namespace/{namespace_id}/module/{module_id}",
        )

    # 若 moduleID 不存在，再按 handle 查找
    if not exists and handle:
        found_id = find_module_by_handle(base_url, req_headers, namespace_id, handle)
        if found_id:
            module_id = found_id
            exists = True
            print(f"  ℹ 通过 handle='{handle}' 找到已有模块: moduleID={module_id}")

    if exists:
        # ── 更新 ──
        print(f"  📝 模块已存在 (moduleID={module_id})，执行更新...")
        body = build_api_body(module, is_create=False)
        url = f"/compose/namespace/{namespace_id}/module/{module_id}"
        resp = api_post(base_url, req_headers, url, data=body)
        print(f"  ✔ 更新成功")
        return resp
    else:
        # ── 新增 ──
        print(f"  ➕ 模块不存在，执行新增...")
        body = build_api_body(module, is_create=True)
        url = f"/compose/namespace/{namespace_id}/module/"
        resp = api_post(base_url, req_headers, url, data=body)
        new_id = resp.get("response", {}).get("moduleID", "?")
        print(f"  ✔ 新增成功 (moduleID={new_id})")
        return resp


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将模块 JSON 配置通过 API 同步到服务端（新增/更新）"
    )
    parser.add_argument(
        "json_file",
        help="模块 JSON 文件路径，如 TestModule.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只打印将要发送的数据，不实际调用 API",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="环境名（如 dev.dms），不指定则使用 env.json 的 active 值",
    )
    parser.add_argument(
        "--tenant",
        type=str,
        default=None,
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
    module = load_module_data(str(json_path))
    print(f"   模块名称: {module.get('name')}")
    print(f"   moduleID: {module.get('moduleID')}")
    print(f"   handle:   {module.get('handle')}")
    print(f"   字段数:   {len(module.get('fields', []))}")

    try:
        sync_module(
            module,
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
