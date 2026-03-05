#!/usr/bin/env python3
"""
从 MySQL 数据库的 compose_page_layout 表中查询所有页面布局数据，
构造成与 ceshiAI.json 相同结构的 JSON 并生成文件。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    # 导出所有布局
    python export_layout_from_db.py --all

    # 按 layoutID 导出
    python export_layout_from_db.py --id 123456

    # 按 page_id 导出该页面的所有布局
    python export_layout_from_db.py --page-id 484225182798512129

    # 列出所有布局
    python export_layout_from_db.py --list
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
        return value.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    try:
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
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


# ────────────────── 从 DB 行构建 layout JSON ──────────────────

def build_layout_json(row: dict) -> dict:
    meta = safe_json_loads(row.get("meta"), {})
    config = safe_json_loads(row.get("config"), {})
    blocks = safe_json_loads(row.get("blocks"), [])

    layout = {
        "layoutID": str(row["id"]),
        "pageID": str(row.get("page_id", 0)),
        "parentID": str(row.get("parent_id", 0)),
        "namespaceID": str(row.get("rel_namespace", 0)),
        "weight": int(row.get("weight", 0)),
        "handle": row.get("handle", ""),
        "meta": meta,
        "config": config,
        "blocks": blocks,
        "ownedBy": str(row.get("owned_by", 0)),
        "createdAt": to_iso8601(row.get("created_at")),
    }

    updated = to_iso8601(row.get("updated_at"))
    if updated:
        layout["updatedAt"] = updated
    deleted = to_iso8601(row.get("deleted_at"))
    if deleted:
        layout["deletedAt"] = deleted

    return layout


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


def list_layouts(db_config: dict, namespace_id: int = None) -> list[dict]:
    """列出数据库中所有布局，可按 namespace 过滤。自动排除已删除 namespace 下的布局。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT id, handle, page_id, parent_id, rel_namespace, weight, meta, created_at "
                   "FROM compose_page_layout "
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


def query_layout(db_config: dict, layout_id: int = None, page_id: int = None) -> list[dict]:
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            if layout_id:
                cur.execute(
                    "SELECT * FROM compose_page_layout WHERE id = %s AND deleted_at IS NULL",
                    (layout_id,),
                )
            elif page_id:
                cur.execute(
                    "SELECT * FROM compose_page_layout WHERE page_id = %s AND deleted_at IS NULL ORDER BY id",
                    (page_id,),
                )
            else:
                raise ValueError("必须提供 --id 或 --page-id")
            return cur.fetchall()
    finally:
        conn.close()


def query_all_layouts(db_config: dict, namespace_id: int = None) -> list[dict]:
    """查询所有布局，可按 namespace 过滤。自动排除已删除 namespace 下的布局。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT * FROM compose_page_layout WHERE deleted_at IS NULL"
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

def write_json_file(data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


def make_filename(row: dict) -> str:
    """用 meta.title 生成文件名，为空时用 handle，再为空用 ID。"""
    meta = safe_json_loads(row.get("meta"), {})
    name = (meta.get("title") or "").strip()
    if not name:
        name = (row.get("handle") or "").strip()
    if not name:
        name = str(row["id"])
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从数据库导出页面布局数据为 JSON 文件（格式与 ceshiAI.json 一致）"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=int, dest="layout_id",
        help="按 layoutID 导出",
    )
    group.add_argument(
        "--page-id", type=int, dest="page_id",
        help="按 page_id 导出该页面的所有布局",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有布局到 data 目录",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出数据库中所有布局",
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
        rows = list_layouts(db_config, namespace_id=namespace_id)
        if not rows:
            print("⚠ 数据库中没有找到任何布局")
            return
        print(f"\n📋 共 {len(rows)} 个布局:\n")
        print(f"  {'ID':<25s} {'Handle':<15s} {'PageID':<25s} {'Title':<25s} {'Created'}")
        print(f"  {'─'*25} {'─'*15} {'─'*25} {'─'*25} {'─'*20}")
        for r in rows:
            meta = safe_json_loads(r.get("meta"), {})
            title = meta.get("title", "")
            print(
                f"  {str(r['id']):<25s} {(r['handle'] or ''):<15s} "
                f"{str(r['page_id']):<25s} {title:<25s} {r.get('created_at', '')}"
            )
        return

    # --all
    if args.all:
        print("📄 正在查询所有布局...")
        rows = query_all_layouts(db_config, namespace_id=namespace_id)
        if not rows:
            print("⚠ 数据库中没有找到任何布局")
            return
        print(f"   共找到 {len(rows)} 个布局\n")

        # 构建 namespace 映射
        ns_map = {}
        if not args.namespace:
            ns_map = build_namespace_map(db_config)

        success, fail = 0, 0
        for row in rows:
            fname = make_filename(row)
            ns_id = int(row.get("rel_namespace", 0))
            layout_id = row["id"]
            layout_json = build_layout_json(row)

            # 确定输出路径: {env}/{tenant}/{ns}/layout/{fname}_{layoutID}.json
            if args.namespace:
                ns_slug = args.namespace
            else:
                ns_slug = ns_map.get(ns_id, str(ns_id))
            output_path = tenant_root / ns_slug / "layout" / f"{fname}_{layout_id}.json"

            try:
                write_json_file(layout_json, output_path)
                meta = safe_json_loads(row.get("meta"), {})
                title = meta.get("title", "")
                print(f"   {(title or fname)}_{layout_id}  layoutID: {row['id']}  pageID: {row['page_id']}")
                success += 1
            except Exception as e:
                print(f"   ❌ {fname}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 单布局 / 按页面查询
    print("📄 正在查询布局...")
    rows = query_layout(db_config, layout_id=args.layout_id, page_id=args.page_id)

    if not rows:
        identifier = args.layout_id or args.page_id
        print(f"❌ 未找到布局: {identifier}")
        sys.exit(1)

    if len(rows) == 1:
        row = rows[0]
        meta = safe_json_loads(row.get("meta"), {})
        print(f"   标题:     {meta.get('title', '')}")
        print(f"   layoutID: {row['id']}")
        print(f"   pageID:   {row['page_id']}")
        print(f"   handle:   {row.get('handle')}")

        layout_json = build_layout_json(row)

        if args.output:
            output_path = Path(args.output)
        else:
            fname = make_filename(row)
            ns_id = int(row.get("rel_namespace", 0))
            ns_map = build_namespace_map(db_config)
            ns_slug = ns_map.get(ns_id, str(ns_id))
            output_path = tenant_root / ns_slug / "layout" / f"{fname}_{row['id']}.json"

        write_json_file(layout_json, output_path)
    else:
        print(f"   找到 {len(rows)} 个布局\n")
        ns_map = build_namespace_map(db_config)
        for row in rows:
            meta = safe_json_loads(row.get("meta"), {})
            fname = make_filename(row)
            ns_id = int(row.get("rel_namespace", 0))
            ns_slug = ns_map.get(ns_id, str(ns_id))
            layout_json = build_layout_json(row)
            output_path = tenant_root / ns_slug / "layout" / f"{fname}_{row['id']}.json"
            write_json_file(layout_json, output_path)
            print(f"   {meta.get('title', fname):<30s} layoutID: {row['id']}")


if __name__ == "__main__":
    main()
