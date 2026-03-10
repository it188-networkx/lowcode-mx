#!/usr/bin/env python3
"""
从服务端 API 查询模块数据，构造成标准 JSON 并生成文件。

用法:
    # 按 moduleID 导出
    python export_module_from_api.py --id 484341972136493057

    # 按 handle 导出
    python export_module_from_api.py --handle TestModule

    # 导出到指定文件
    python export_module_from_api.py --handle TestModule -o output/TestModule.json

    # 列出所有模块
    python export_module_from_api.py --list

    # 导出指定命名空间的所有模块
    python export_module_from_api.py --all --namespace itsm
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from api_utils import (
    load_api_config,
    api_get, api_list_all, resolve_namespace_id, build_namespace_map, APIError,
)

# src/ 目录路径（输出根目录）
SRC_ROOT = Path(__file__).resolve().parent.parent / "src"


# ────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data: dict, output_path: Path):
    """将模块数据写入 JSON 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


# ────────────────────── API 查询封装 ──────────────────────────

def list_modules_api(
    base_url: str, headers: dict, namespace_id: str
) -> list[dict]:
    """通过 API 列出某命名空间下的所有模块（含字段）。"""
    return api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/module/",
        {"limit": 100},
    )


def get_module_by_id(
    base_url: str, headers: dict, namespace_id: str, module_id: str
) -> dict | None:
    """按 moduleID 获取模块详情。"""
    try:
        resp = api_get(
            base_url, headers,
            f"/compose/namespace/{namespace_id}/module/{module_id}",
        )
        return resp.get("response")
    except APIError as e:
        if e.status in (404, 422):
            return None
        raise


def find_module_by_handle(
    base_url: str, headers: dict, namespace_id: str, handle: str
) -> dict | None:
    """按 handle 查找模块，返回模块数据或 None。"""
    items = api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/module/",
        {"handle": handle, "limit": 10},
    )
    for m in items:
        if m.get("handle") == handle:
            return m
    return None


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从 API 导出模块数据为 JSON 文件"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=str, dest="module_id",
        help="按 moduleID 导出，如 --id 484341972136493057",
    )
    group.add_argument(
        "--handle", type=str,
        help="按 handle 导出，如 --handle TestModule",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有模块到配置目录",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出所有模块",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="输出文件路径（默认按命名空间自动计算）",
    )
    parser.add_argument(
        "--env", type=str, default=None,
        help="环境名（如 dev.dms），不指定则使用 env.json 的 active 值",
    )
    parser.add_argument(
        "--tenant", type=str, default=None,
        help="租户名（如 mx），不指定则使用该环境下的第一个租户",
    )
    parser.add_argument(
        "--namespace", type=str, default=None,
        help="命名空间 slug（如 itsm），指定则只导出该命名空间的数据；--all 模式下必须指定或者会遍历所有命名空间",
    )

    args = parser.parse_args()

    cfg = load_api_config(env=args.env, tenant=args.tenant)
    base_url = cfg["baseUrl"]
    api_headers = cfg["headers"]

    if not base_url:
        print("❌ env.json 中未配置 baseUrl")
        sys.exit(1)

    print(f"🔗 API: {base_url}")

    # 输出根目录: lowcode-mx/src/
    tenant_root = SRC_ROOT
    print(f"📂 输出根目录: {tenant_root}")

    # 解析命名空间
    ns_map = build_namespace_map(base_url, api_headers)  # {nsID: slug}
    ns_id_map = {v: k for k, v in ns_map.items()}  # {slug: nsID}

    if args.namespace:
        if args.namespace in ns_id_map:
            target_ns_ids = [ns_id_map[args.namespace]]
        else:
            target_ns_ids = [resolve_namespace_id(base_url, api_headers, args.namespace)]
        print(f"📁 命名空间: {args.namespace} (ID: {target_ns_ids[0]})")
    else:
        target_ns_ids = list(ns_map.keys())

    # --list: 列出所有模块
    if args.list:
        total = 0
        print(f"\n{'ID':<25s} {'Handle':<25s} {'Name':<25s} {'Namespace'}")
        print(f"{'─'*25} {'─'*25} {'─'*25} {'─'*15}")
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            modules = list_modules_api(base_url, api_headers, ns_id)
            for m in modules:
                mid = m.get("moduleID", "")
                handle = m.get("handle", "")
                name = m.get("name", "")
                print(f"{mid:<25s} {handle:<25s} {name:<25s} {ns_slug}")
                total += 1
        if total == 0:
            print("⚠ 未找到任何模块")
        else:
            print(f"\n📋 共 {total} 个模块")
        return

    # --all: 导出所有模块
    if args.all:
        print("📄 正在查询所有模块...")
        all_modules = []  # [(module_data, ns_slug), ...]
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            modules = list_modules_api(base_url, api_headers, ns_id)
            for m in modules:
                all_modules.append((m, ns_slug))
        if not all_modules:
            print("⚠ 未找到任何模块")
            return
        print(f"   共找到 {len(all_modules)} 个模块\n")

        # 检测 handle 重复
        handle_count = Counter(
            m.get("handle") or m.get("moduleID", "") for m, _ in all_modules
        )
        dup_handles = {h for h, c in handle_count.items() if c > 1}
        if dup_handles:
            print(f"   ⚠ 检测到重复 handle: {', '.join(dup_handles)}，将在文件名中附加 moduleID\n")

        success, fail = 0, 0
        for module_data, ns_slug in all_modules:
            handle = module_data.get("handle") or module_data.get("moduleID", "unknown")
            module_id = module_data.get("moduleID", "")
            fields = module_data.get("fields", [])

            if handle in dup_handles:
                output_path = tenant_root / ns_slug / "module" / f"{handle}_{module_id}.json"
            else:
                output_path = tenant_root / ns_slug / "module" / f"{handle}.json"

            try:
                write_json_file(module_data, output_path)
                print(f"   {handle:<25s} 字段数: {len(fields)}")
                success += 1
            except Exception as e:
                print(f"   ❌ {handle}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 单模块查询
    if not args.namespace and len(target_ns_ids) > 1:
        print("⚠ 未指定 --namespace，将在所有命名空间中搜索...")

    module_data = None

    if args.module_id:
        print(f"📄 正在按 ID 查询模块: {args.module_id}")
        for ns_id in target_ns_ids:
            module_data = get_module_by_id(base_url, api_headers, ns_id, args.module_id)
            if module_data:
                break
    elif args.handle:
        print(f"📄 正在按 handle 查询模块: {args.handle}")
        for ns_id in target_ns_ids:
            module_data = find_module_by_handle(base_url, api_headers, ns_id, args.handle)
            if module_data:
                break

    if not module_data:
        identifier = args.module_id or args.handle
        print(f"❌ 未找到模块: {identifier}")
        sys.exit(1)

    print(f"   模块名称: {module_data.get('name')}")
    print(f"   moduleID: {module_data.get('moduleID')}")
    print(f"   handle:   {module_data.get('handle')}")
    print(f"   字段数:   {len(module_data.get('fields', []))}")

    if args.output:
        output_path = Path(args.output)
    else:
        handle = module_data.get("handle") or module_data.get("moduleID", "unknown")
        ns_id = module_data.get("namespaceID", "0")
        ns_slug = ns_map.get(ns_id, str(ns_id))
        output_path = tenant_root / ns_slug / "module" / f"{handle}.json"

    write_json_file(module_data, output_path)

    # 打印字段摘要
    print(f"\n📊 字段列表:")
    for f in module_data.get("fields", []):
        print(
            f"   {f.get('fieldID', ''):<25s} {f.get('name', ''):<20s} "
            f"{f.get('kind', ''):<12s} label={f.get('label', '')!r}"
        )


if __name__ == "__main__":
    main()
