#!/usr/bin/env python3
"""
从 MySQL 数据库的 compose_page 表中查询所有页面数据，
构造成与 ceshiAi.json 相同结构的 JSON 并生成文件。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    # 导出所有页面
    python export_page_from_db.py --all

    # 按 pageID 导出
    python export_page_from_db.py --id 484225182798512129

    # 按 handle 导出
    python export_page_from_db.py --handle ceshiAI

    # 导出到指定文件
    python export_page_from_db.py --id 484225182798512129 -o output/page.json

    # 列出所有页面
    python export_page_from_db.py --list
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 将 configuration/ 目录加入模块搜索路径，以便导入 db_utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from db_utils import load_db_config, resolve_namespace_id, build_namespace_map, resolve_env_and_tenant

# configuration/ 目录路径
CONF_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import pymysql
except ImportError:
    print("❌ 需要 pymysql，请先安装: pip install pymysql")
    sys.exit(1)


# ────────────────────── 工具函数 ──────────────────────────────

def to_iso8601(value) -> str:
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, AttributeError):
        return ""


def safe_json_loads(value, default=None):
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


# ────────────────── 从 DB 行构建 page JSON ──────────────────

def build_page_json(row: dict) -> dict:
    meta = safe_json_loads(row.get("meta"), {})
    config = safe_json_loads(row.get("config"), {})
    blocks = safe_json_loads(row.get("blocks"), [])

    page = {
        "pageID": str(row["id"]),
        "selfID": str(row.get("self_id", 0)),
        "namespaceID": str(row.get("rel_namespace", 0)),
        "moduleID": str(row.get("rel_module", 0)),
        "handle": row.get("handle", ""),
        "config": config,
        "blocks": blocks,
        "meta": meta,
        "visible": bool(row.get("visible", 1)),
        "weight": int(row.get("weight", 0)),
        "createdAt": to_iso8601(row.get("created_at")),
        "title": row.get("title", ""),
        "description": row.get("description", ""),
        "canGrant": True,
        "canUpdatePage": True,
        "canDeletePage": True,
    }

    updated = to_iso8601(row.get("updated_at"))
    if updated:
        page["updatedAt"] = updated
    deleted = to_iso8601(row.get("deleted_at"))
    if deleted:
        page["deletedAt"] = deleted

    return page


# ────────────────────────── 数据库操作 ──────────────────────────────

def get_connection(db_config: dict):
    return pymysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def list_pages(db_config: dict, namespace_id: int = None) -> list[dict]:
    """列出数据库中所有页面，可按 namespace 过滤。自动排除已删除 namespace 下的页面。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT id, title, handle, rel_namespace, self_id, rel_module, created_at "
                   "FROM compose_page "
                   "WHERE deleted_at IS NULL"
                   " AND (rel_namespace = 0 OR rel_namespace IN "
                   "(SELECT id FROM compose_namespace WHERE deleted_at IS NULL))")
            params = []
            if namespace_id is not None:
                sql += " AND rel_namespace = %s"
                params.append(namespace_id)
            sql += " ORDER BY id"
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def query_page(db_config: dict, page_id: int = None, handle: str = None) -> dict | None:
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            if page_id:
                cur.execute(
                    "SELECT * FROM compose_page WHERE id = %s AND deleted_at IS NULL",
                    (page_id,),
                )
            elif handle:
                cur.execute(
                    "SELECT * FROM compose_page WHERE handle = %s AND deleted_at IS NULL",
                    (handle,),
                )
            else:
                raise ValueError("必须提供 --id 或 --handle")
            return cur.fetchone()
    finally:
        conn.close()


def query_all_pages(db_config: dict, namespace_id: int = None) -> list[dict]:
    """查询所有页面，可按 namespace 过滤。自动排除已删除 namespace 下的页面。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT * FROM compose_page WHERE deleted_at IS NULL"
                   " AND (rel_namespace = 0 OR rel_namespace IN "
                   "(SELECT id FROM compose_namespace WHERE deleted_at IS NULL))")
            params = []
            if namespace_id is not None:
                sql += " AND rel_namespace = %s"
                params.append(namespace_id)
            sql += " ORDER BY id"
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


# ────────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


def make_filename(title: str, page_id) -> str:
    """用 title 生成文件名，title 为空时用 pageID。"""
    name = (title or "").strip()
    if not name:
        name = str(page_id)
    # 替换文件名中不安全的字符
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从数据库导出页面数据为 JSON 文件（格式与 ceshiAi.json 一致）"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=int, dest="page_id",
        help="按 pageID 导出",
    )
    group.add_argument(
        "--handle", type=str,
        help="按 handle 导出",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有页面到 data 目录",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出数据库中所有页面",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="输出文件路径（默认为 data/{title}.json）",
    )
    parser.add_argument(
        "--env", type=str, default=None,
        help="环境名（如 dev），不指定则使用 env.json 的 active 值",
    )
    parser.add_argument(
        "--tenant", type=str, default=None,
        help="租户名（如 mx），不指定则使用该环境下的第一个租户",
    )
    parser.add_argument(
        "--namespace", type=str, default=None,
        help="命名空间 slug（如 itsm），指定则只导出该命名空间的数据；不指定则导出全部并按命名空间分目录",
    )

    args = parser.parse_args()

    db_config = load_db_config(env=args.env, tenant=args.tenant)
    print(f"🔗 数据库连接: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    # 计算输出根目录: configuration/{env_dir}/{tenant}/
    env_dir, tenant_name = resolve_env_and_tenant(env=args.env, tenant=args.tenant)
    tenant_root = CONF_ROOT / env_dir / tenant_name
    print(f"📂 输出根目录: {tenant_root}")

    # 解析 namespace
    namespace_id = None
    if args.namespace:
        namespace_id = resolve_namespace_id(db_config, args.namespace)
        print(f"📁 命名空间: {args.namespace} (ID: {namespace_id})")

    # --list
    if args.list:
        pages = list_pages(db_config, namespace_id=namespace_id)
        if not pages:
            print("⚠ 数据库中没有找到任何页面")
            return
        print(f"\n📋 共 {len(pages)} 个页面:\n")
        print(f"  {'ID':<25s} {'Title':<25s} {'Handle':<20s} {'Namespace':<25s} {'Created'}")
        print(f"  {'─'*25} {'─'*25} {'─'*20} {'─'*25} {'─'*20}")
        for p in pages:
            print(
                f"  {str(p['id']):<25s} {(p['title'] or ''):<25s} "
                f"{(p['handle'] or ''):<20s} {str(p['rel_namespace']):<25s} "
                f"{p.get('created_at', '')}"
            )
        return

    # --all
    if args.all:
        print("📄 正在查询所有页面...")
        rows = query_all_pages(db_config, namespace_id=namespace_id)
        if not rows:
            print("⚠ 数据库中没有找到任何页面")
            return
        print(f"   共找到 {len(rows)} 个页面\n")

        # 构建 namespace 映射
        ns_map = {}
        if not args.namespace:
            ns_map = build_namespace_map(db_config)

        success, fail = 0, 0
        for row in rows:
            fname = make_filename(row.get("title", ""), row["id"])
            ns_id = int(row.get("rel_namespace", 0))
            page_id = row["id"]
            page_json = build_page_json(row)

            # 确定输出路径: {env}/{tenant}/{ns}/page/{fname}_{pageID}.json
            if args.namespace:
                ns_slug = args.namespace
            else:
                ns_slug = ns_map.get(ns_id, str(ns_id))
            output_path = tenant_root / ns_slug / "page" / f"{fname}_{page_id}.json"

            try:
                write_json_file(page_json, output_path)
                print(f"   {fname}_{page_id}  pageID: {row['id']}")
                success += 1
            except Exception as e:
                print(f"   ❌ {fname}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 单页面查询
    print("📄 正在查询页面...")
    row = query_page(db_config, page_id=args.page_id, handle=args.handle)

    if not row:
        identifier = args.page_id or args.handle
        print(f"❌ 未找到页面: {identifier}")
        sys.exit(1)

    print(f"   标题:     {row.get('title')}")
    print(f"   pageID:   {row['id']}")
    print(f"   handle:   {row.get('handle')}")

    page_json = build_page_json(row)

    if args.output:
        output_path = Path(args.output)
    else:
        fname = make_filename(row.get("title", ""), row["id"])
        ns_id = int(row.get("rel_namespace", 0))
        ns_map = build_namespace_map(db_config)
        ns_slug = ns_map.get(ns_id, str(ns_id))
        output_path = tenant_root / ns_slug / "page" / f"{fname}_{row['id']}.json"

    write_json_file(page_json, output_path)


if __name__ == "__main__":
    main()
