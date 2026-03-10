#!/usr/bin/env python3
"""
将命名空间配置通过 API 同步（新增/更新）到服务端。

用法:
    python sync_namespace_to_api.py --slug <slug> --name <name>
    python sync_namespace_to_api.py --slug <slug> --name <name> --dry-run

示例:
    python sync_namespace_to_api.py --slug change --name "变更管理"
    python sync_namespace_to_api.py --slug change --name "变更管理" --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

from api_utils import (
    load_api_config, api_post, api_list_all,
    resource_exists, APIError,
)


# ────────────────────── API 请求体构建 ──────────────────────

_NAMESPACE_BODY_KEYS = [
    "name", "slug", "enabled", "meta",
]


def build_api_body(
    slug: str,
    name: str,
    enabled: bool = True,
    meta: dict | None = None,
) -> dict:
    """构建命名空间 API 请求体。"""
    return {
        "slug": slug,
        "name": name,
        "enabled": enabled,
        "meta": meta or {},
    }


# ────────────────── 命名空间查找 ──────────────────

def find_namespace_by_slug(
    base_url: str, headers: dict, slug: str
) -> str | None:
    """通过 slug 查找已存在的命名空间，返回 namespaceID；未找到返回 None。"""
    if not slug:
        return None
    items = api_list_all(
        base_url, headers,
        "/compose/namespace/",
        {"slug": slug},
    )
    for ns in items:
        if ns.get("slug") == slug:
            return str(ns["namespaceID"])
    return None


# ──────────────────── 同步主函数 ────────────────────

def sync_namespace(
    *,
    base_url: str,
    headers: dict,
    slug: str,
    name: str,
    enabled: bool = True,
    meta: dict | None = None,
    dry_run: bool = False,
) -> dict | None:
    """
    通过 API 同步命名空间到服务端（新增或更新）。

    逻辑：
    1. 按 slug 查找已存在的命名空间
    2. 存在 → POST 更新
    3. 不存在 → POST 新增
    """
    body = build_api_body(slug=slug, name=name, enabled=enabled, meta=meta)

    if dry_run:
        print(f"\n[预览模式] 以下数据不会实际发送到服务端\n")
        print(f"  slug:    {slug}")
        print(f"  name:    {name}")
        print(f"  enabled: {enabled}")
        print(f"  meta:    {json.dumps(meta or {}, ensure_ascii=False)}")
        return None

    # ── 查找已存在的命名空间 ──
    existing_id = find_namespace_by_slug(base_url, headers, slug)

    if existing_id:
        print(f"  📝 命名空间已存在 (namespaceID={existing_id})，执行更新...")
        url = f"/compose/namespace/{existing_id}"
        resp = api_post(base_url, headers, url, data=body)
        print(f"  ✔ 更新成功")
        return resp
    else:
        print(f"  ➕ 命名空间不存在，执行新增...")
        url = "/compose/namespace/"
        resp = api_post(base_url, headers, url, data=body)
        new_id = resp.get("response", {}).get("namespaceID", "?")
        print(f"  ✔ 新增成功 (namespaceID={new_id})")
        return resp


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将命名空间配置通过 API 同步到服务端（新增/更新）"
    )
    parser.add_argument(
        "--slug",
        type=str,
        required=True,
        help="命名空间 slug，如 change",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="命名空间名称，如 '变更管理'",
    )
    parser.add_argument(
        "--enabled",
        type=int,
        default=1,
        choices=[0, 1],
        help="是否启用（默认 1）",
    )
    parser.add_argument(
        "--meta",
        type=str,
        default="{}",
        help="元数据 JSON 字符串（默认 {}）",
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

    cfg = load_api_config(env=args.env, tenant=args.tenant)
    base_url = cfg["baseUrl"]
    api_headers = cfg["headers"]

    if not base_url:
        print("❌ env.json 中未配置 baseUrl")
        sys.exit(1)

    print(f"🔗 API: {base_url}")

    try:
        meta = json.loads(args.meta)
    except json.JSONDecodeError:
        print(f"❌ --meta 参数不是合法的 JSON: {args.meta}")
        sys.exit(1)

    print(f"📄 命名空间信息:")
    print(f"   slug:    {args.slug}")
    print(f"   name:    {args.name}")
    print(f"   enabled: {args.enabled}")

    try:
        sync_namespace(
            base_url=base_url,
            headers=api_headers,
            slug=args.slug,
            name=args.name,
            enabled=bool(args.enabled),
            meta=meta,
            dry_run=args.dry_run,
        )
    except APIError as e:
        print(f"\n❌ API 调用失败: {e}")
        if e.body:
            print(f"   响应: {e.body[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
