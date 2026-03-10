#!/usr/bin/env python3
"""
从服务端 API 查询页面布局数据，构造成标准 JSON 并生成文件。

用法:
    # 导出所有布局
    python export_layout_from_api.py --all

    # 按 layoutID 导出
    python export_layout_from_api.py --id 123456

    # 按 page-id 导出该页面的所有布局
    python export_layout_from_api.py --page-id 484225182798512129

    # 列出所有布局
    python export_layout_from_api.py --list

    # 导出指定命名空间的所有布局
    python export_layout_from_api.py --all --namespace itsm
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

def safe_json_loads(value, default=None):
    """安全地将 JSON 字符串/已解析对象加载为 Python 对象。"""
    if default is None:
        default = {}
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def make_filename(layout: dict) -> str:
    """用 meta.title 生成文件名，为空时用 handle，再为空用 ID。"""
    meta = layout.get("meta", {})
    if isinstance(meta, str):
        meta = safe_json_loads(meta, {})
    name = (meta.get("title") or "").strip()
    if not name:
        name = (layout.get("handle") or "").strip()
    if not name:
        # API 返回 pageLayoutID，本地 JSON 使用 layoutID
        name = str(layout.get("pageLayoutID", layout.get("layoutID", "unknown")))
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name


def normalize_layout(layout: dict) -> dict:
    """
    将 API 返回的布局数据标准化为本地 JSON 格式。
    主要是将 API 的 pageLayoutID 映射为本地的 layoutID。
    """
    result = dict(layout)
    if "pageLayoutID" in result and "layoutID" not in result:
        result["layoutID"] = result["pageLayoutID"]
    return result


# ────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


# ────────────────────── API 查询封装 ──────────────────────────

def list_all_layouts_api(
    base_url: str, headers: dict, namespace_id: str
) -> list[dict]:
    """通过全局 page-layout API 列出某命名空间下的所有布局。"""
    return api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/page-layout",
        {"limit": 100},
    )


def list_layouts_by_page(
    base_url: str, headers: dict, namespace_id: str, page_id: str
) -> list[dict]:
    """获取某页面下的所有布局。"""
    return api_list_all(
        base_url, headers,
        f"/compose/namespace/{namespace_id}/page/{page_id}/layout/",
    )


def get_layout_by_id(
    base_url: str, headers: dict, namespace_id: str, page_id: str, layout_id: str
) -> dict | None:
    """按 layoutID 获取布局详情。"""
    try:
        resp = api_get(
            base_url, headers,
            f"/compose/namespace/{namespace_id}/page/{page_id}/layout/{layout_id}",
        )
        return resp.get("response")
    except APIError as e:
        if e.status in (404, 422):
            return None
        raise


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从 API 导出页面布局数据为 JSON 文件"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=str, dest="layout_id",
        help="按 layoutID 导出",
    )
    group.add_argument(
        "--page-id", type=str, dest="page_id",
        help="按 page_id 导出该页面的所有布局",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有布局到配置目录",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出所有布局",
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
        print(f"\n{'ID':<25s} {'Handle':<15s} {'PageID':<25s} {'Title':<25s} {'Namespace'}")
        print(f"{'─'*25} {'─'*15} {'─'*25} {'─'*25} {'─'*15}")
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            layouts = list_all_layouts_api(base_url, api_headers, ns_id)
            for l in layouts:
                lid = l.get("pageLayoutID", l.get("layoutID", ""))
                handle = l.get("handle", "")
                page_id = l.get("pageID", "")
                meta = l.get("meta", {})
                if isinstance(meta, str):
                    meta = safe_json_loads(meta, {})
                title = meta.get("title", "")
                print(f"{lid:<25s} {handle:<15s} {page_id:<25s} {title:<25s} {ns_slug}")
                total += 1
        if total == 0:
            print("⚠ 未找到任何布局")
        else:
            print(f"\n📋 共 {total} 个布局")
        return

    # --all
    if args.all:
        print("📄 正在查询所有布局...")
        all_layouts = []
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            layouts = list_all_layouts_api(base_url, api_headers, ns_id)
            for l in layouts:
                all_layouts.append((l, ns_slug))
        if not all_layouts:
            print("⚠ 未找到任何布局")
            return
        print(f"   共找到 {len(all_layouts)} 个布局\n")

        success, fail = 0, 0
        for layout_data, ns_slug in all_layouts:
            layout_data = normalize_layout(layout_data)
            layout_id = layout_data.get("pageLayoutID", layout_data.get("layoutID", ""))
            fname = make_filename(layout_data)
            output_path = tenant_root / ns_slug / "layout" / f"{fname}_{layout_id}.json"

            try:
                write_json_file(layout_data, output_path)
                meta = layout_data.get("meta", {})
                if isinstance(meta, str):
                    meta = safe_json_loads(meta, {})
                title = meta.get("title", "")
                print(f"   {(title or fname)}_{layout_id}  layoutID: {layout_id}  pageID: {layout_data.get('pageID', '')}")
                success += 1
            except Exception as e:
                print(f"   ❌ {fname}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # --page-id: 导出某页面的所有布局
    if args.page_id:
        print(f"📄 正在查询页面 {args.page_id} 的布局...")
        found = False
        for ns_id in target_ns_ids:
            ns_slug = ns_map.get(ns_id, ns_id)
            layouts = list_layouts_by_page(base_url, api_headers, ns_id, args.page_id)
            if layouts:
                found = True
                print(f"   找到 {len(layouts)} 个布局\n")
                for l in layouts:
                    l = normalize_layout(l)
                    layout_id = l.get("pageLayoutID", l.get("layoutID", ""))
                    fname = make_filename(l)
                    output_path = tenant_root / ns_slug / "layout" / f"{fname}_{layout_id}.json"
                    write_json_file(l, output_path)
                    meta = l.get("meta", {})
                    if isinstance(meta, str):
                        meta = safe_json_loads(meta, {})
                    print(f"   {meta.get('title', fname):<30s} layoutID: {layout_id}")
                break
        if not found:
            print(f"❌ 未找到页面 {args.page_id} 的布局")
            sys.exit(1)
        return

    # --id: 按 layoutID 导出
    if args.layout_id:
        print(f"📄 正在按 ID 查询布局: {args.layout_id}")
        layout_data = None
        # 需要在全局列表中查找该布局以获取 pageID
        for ns_id in target_ns_ids:
            all_layouts = list_all_layouts_api(base_url, api_headers, ns_id)
            for l in all_layouts:
                lid = str(l.get("pageLayoutID", l.get("layoutID", "")))
                if lid == args.layout_id:
                    layout_data = normalize_layout(l)
                    break
            if layout_data:
                break

        if not layout_data:
            print(f"❌ 未找到布局: {args.layout_id}")
            sys.exit(1)

        meta = layout_data.get("meta", {})
        if isinstance(meta, str):
            meta = safe_json_loads(meta, {})
        print(f"   标题:     {meta.get('title', '')}")
        print(f"   layoutID: {layout_data.get('layoutID', layout_data.get('pageLayoutID', ''))}")
        print(f"   pageID:   {layout_data.get('pageID', '')}")
        print(f"   handle:   {layout_data.get('handle', '')}")

        if args.output:
            output_path = Path(args.output)
        else:
            fname = make_filename(layout_data)
            layout_id = layout_data.get("pageLayoutID", layout_data.get("layoutID", ""))
            ns_id = layout_data.get("namespaceID", "0")
            ns_slug = ns_map.get(str(ns_id), str(ns_id))
            output_path = tenant_root / ns_slug / "layout" / f"{fname}_{layout_id}.json"

        write_json_file(layout_data, output_path)


if __name__ == "__main__":
    main()
