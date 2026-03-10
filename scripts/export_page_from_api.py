#!/usr/bin/env python3
"""
从服务端 API 查询页面数据，构造成标准 JSON 并生成文件。

用法:
    # 导出所有页面
    python export_page_from_api.py --all

    # 按 pageID 导出
    python export_page_from_api.py --id 484225182798512129

    # 按 handle 导出
    python export_page_from_api.py --handle ceshiAI

    # 导出到指定文件
    python export_page_from_api.py --id 484225182798512129 -o output/page.json

    # 列出所有页面
    python export_page_from_api.py --list

    # 导出指定命名空间的所有页面
    python export_page_from_api.py --all --namespace itsm
"""

import argparse
import json
import re
import sys
from pathlib import Path

from api_utils import (
    load_api_config,
    api_get, api_list_all, resolve_namespace_id, build_namespace_map, APIError,
)

# src/ 目录路径（输出根目录）
SRC_ROOT = Path(__file__).resolve().parent.parent / "src"


# ────────────────────── 工具函数 ──────────────────────────────

def make_filename(title: str, page_id) -> str:
    """用 title 生成文件名，title 为空时用 pageID。"""
    name = (title or "").strip()
    if not name:
        name = str(page_id)
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name


# ────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


# ────────────────────── API 查询封装 ──────────────────────────

def list_pages_api(
    base_url: str, headers: dict, namespace_id: str
) -> list[dict]:
    """通过 API 列出某命名空间下的所有页面。"""
    return api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/page/",
        {"limit": 100},
    )


def get_page_by_id(
    base_url: str, headers: dict, namespace_id: str, page_id: str
) -> dict | None:
    """按 pageID 获取页面详情。"""
    try:
        resp = api_get(
            base_url, headers,
            f"/compose/namespace/{namespace_id}/page/{page_id}",
        )
        return resp.get("response")
    except APIError as e:
        if e.status in (404, 422):
            return None
        raise


def find_page_by_handle(
    base_url: str, headers: dict, namespace_id: str, handle: str
) -> dict | None:
    """按 handle 查找页面。"""
    items = api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/page/",
        {"handle": handle, "limit": 10},
    )
    for p in items:
        if p.get("handle") == handle:
            return p
    return None


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从 API 导出页面数据为 JSON 文件"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=str, dest="page_id",
        help="按 pageID 导出",
    )
    group.add_argument(
        "--handle", type=str,
        help="按 handle 导出",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有页面到配置目录",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出所有页面",
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
        help="命名空间 slug（如 itsm），指定则只导出该命名空间的数据；不指定则遍历所有命名空间",
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
    ns_map = build_namespace_map(base_url, api_headers)
    ns_id_map = {v: k for k, v in ns_map.items()}

    if args.namespace:
        if args.namespace in ns_id_map:
            target_ns_ids = [ns_id_map[args.namespace]]
        else:
            target_ns_ids = [resolve_namespace_id(base_url, api_headers, args.namespace)]
        print(f"📁 命名空间: {args.namespace} (ID: {target_ns_ids[0]})")
    else:
        target_ns_ids = list(ns_map.keys())

    # --list
    if args.list:
        total = 0
        print(f"\n{'ID':<25s} {'Title':<25s} {'Handle':<20s} {'Namespace'}")
        print(f"{'─'*25} {'─'*25} {'─'*20} {'─'*15}")
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            pages = list_pages_api(base_url, api_headers, ns_id)
            for p in pages:
                pid = p.get("pageID", "")
                title = p.get("title", "")
                handle = p.get("handle", "")
                print(f"{pid:<25s} {title:<25s} {handle:<20s} {ns_slug}")
                total += 1
        if total == 0:
            print("⚠ 未找到任何页面")
        else:
            print(f"\n📋 共 {total} 个页面")
        return

    # --all
    if args.all:
        print("📄 正在查询所有页面...")
        all_pages = []
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            pages = list_pages_api(base_url, api_headers, ns_id)
            for p in pages:
                all_pages.append((p, ns_slug))
        if not all_pages:
            print("⚠ 未找到任何页面")
            return
        print(f"   共找到 {len(all_pages)} 个页面\n")

        success, fail = 0, 0
        for page_data, ns_slug in all_pages:
            page_id = page_data.get("pageID", "")
            title = page_data.get("title", "")
            fname = make_filename(title, page_id)
            output_path = tenant_root / ns_slug / "page" / f"{fname}_{page_id}.json"

            try:
                write_json_file(page_data, output_path)
                print(f"   {fname}_{page_id}  pageID: {page_id}")
                success += 1
            except Exception as e:
                print(f"   ❌ {fname}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 单页面查询
    if not args.namespace and len(target_ns_ids) > 1:
        print("⚠ 未指定 --namespace，将在所有命名空间中搜索...")

    page_data = None

    if args.page_id:
        print(f"📄 正在按 ID 查询页面: {args.page_id}")
        for ns_id in target_ns_ids:
            page_data = get_page_by_id(base_url, api_headers, ns_id, args.page_id)
            if page_data:
                break
    elif args.handle:
        print(f"📄 正在按 handle 查询页面: {args.handle}")
        for ns_id in target_ns_ids:
            page_data = find_page_by_handle(base_url, api_headers, ns_id, args.handle)
            if page_data:
                break

    if not page_data:
        identifier = args.page_id or args.handle
        print(f"❌ 未找到页面: {identifier}")
        sys.exit(1)

    print(f"   标题:     {page_data.get('title')}")
    print(f"   pageID:   {page_data.get('pageID')}")
    print(f"   handle:   {page_data.get('handle')}")

    if args.output:
        output_path = Path(args.output)
    else:
        page_id = page_data.get("pageID", "")
        title = page_data.get("title", "")
        fname = make_filename(title, page_id)
        ns_id = page_data.get("namespaceID", "0")
        ns_slug = ns_map.get(ns_id, str(ns_id))
        output_path = tenant_root / ns_slug / "page" / f"{fname}_{page_id}.json"

    write_json_file(page_data, output_path)


if __name__ == "__main__":
    main()
