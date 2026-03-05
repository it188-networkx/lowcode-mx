#!/usr/bin/env python3
"""
从 MySQL 数据库的 compose_module 和 compose_module_field 表中查询模块数据，
构造成与 TestModule.json 相同结构的 JSON 并生成文件。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    # 按 moduleID 导出
    python export_module_from_db.py --id 484341972136493057

    # 按 handle 导出
    python export_module_from_db.py --handle TestModule

    # 导出到指定文件
    python export_module_from_db.py --handle TestModule -o output/TestModule.json

    # 列出所有模块
    python export_module_from_db.py --list
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


# ────────────────────── 时间格式转换 ──────────────────────────────

def to_iso8601(value) -> str:
    """将 MySQL datetime 转为 ISO 8601 格式字符串，空值返回空字符串。"""
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


# ────────────────── 构建 systemModuleField 中单个字段 ──────────────

def build_system_field_json(field: dict) -> dict:
    """从 systemModuleField JSON 数组中的元素构建标准字段对象。"""
    # systemModuleField 已经是完整的 JSON 结构，直接返回
    return field


# ────────────────── 从 DB 行构建 field JSON ──────────────────────

def build_field_json(row: dict) -> dict:
    """从 compose_module_field 表的一行数据构建 fields[] 中的字段对象。"""
    options = safe_json_loads(row.get("options"), {})
    config = safe_json_loads(row.get("config"), {})
    expressions = safe_json_loads(row.get("expressions"), {})
    default_value = safe_json_loads(row.get("default_value"), [])

    return {
        "fieldID": str(row["id"]),
        "name": row.get("name", ""),
        "kind": row.get("kind", ""),
        "label": row.get("label", ""),
        "width": 130,
        "defaultValue": default_value if isinstance(default_value, list) else [],
        "maxLength": 0,
        "isRequired": bool(row.get("is_required", 0)),
        "disabled": False,
        "customRequired": False,
        "isMulti": bool(row.get("is_multi", 0)),
        "isName": bool(row.get("is_name", 0)),
        "isSystem": False,
        "isSortable": True,
        "isFilterable": True,
        "options": options,
        "expressions": expressions,
        "config": config,
        "canUpdateRecordValue": True,
        "canReadRecordValue": True,
    }


# ────────────────── 从 DB 行构建完整 module JSON ──────────────────

def build_module_json(module_row: dict, field_rows: list[dict]) -> dict:
    """从 compose_module 和 compose_module_field 查询结果构建完整的模块 JSON。"""
    system_fields = safe_json_loads(module_row.get("systemModuleField"), [])
    meta = safe_json_loads(module_row.get("meta"), {})
    config = safe_json_loads(module_row.get("config"), {})

    # 按 place 排序自定义字段
    sorted_fields = sorted(field_rows, key=lambda r: r.get("place", 0))

    module = {
        "moduleID": str(module_row["id"]),
        "namespaceID": str(module_row["rel_namespace"]),
        "name": module_row.get("name", ""),
        "handle": module_row.get("handle", ""),
        "type": module_row.get("type", ""),
        "isBlockDataTree": bool(module_row.get("isBlockDataTree", 0)),
        "systemModuleField": system_fields,
        "fields": [build_field_json(r) for r in sorted_fields],
        "issues": [],
        "config": config,
        "meta": meta,
        "labels": {},
        "createdAt": to_iso8601(module_row.get("created_at")),
        "canUpdateModule": True,
        "canDeleteModule": True,
        "canCreateRecord": True,
        "canCreateOwnedRecord": True,
        "canGrant": True,
    }

    # 仅在有值时添加 updatedAt / deletedAt
    updated = to_iso8601(module_row.get("updated_at"))
    if updated:
        module["updatedAt"] = updated
    deleted = to_iso8601(module_row.get("deleted_at"))
    if deleted:
        module["deletedAt"] = deleted

    return module


# ────────────────────────── 数据库查询 ──────────────────────────────

def get_connection(db_config: dict):
    """创建数据库连接。"""
    return pymysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def list_modules(db_config: dict, namespace_id: int = None):
    """列出数据库中所有模块，可按 namespace 过滤。自动排除已删除 namespace 下的模块。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT id, handle, name, rel_namespace, created_at "
                   "FROM compose_module "
                   "WHERE deleted_at IS NULL"
                   " AND (rel_namespace = 0 OR rel_namespace IN "
                   "(SELECT id FROM compose_namespace WHERE deleted_at IS NULL))")
            params = []
            if namespace_id is not None:
                sql += " AND rel_namespace = %s"
                params.append(namespace_id)
            sql += " ORDER BY id"
            cur.execute(sql, params)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def query_module(db_config: dict, module_id: int = None, handle: str = None) -> dict:
    """按 moduleID 或 handle 查询单个模块及其字段。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            # 查询 compose_module
            if module_id:
                cur.execute(
                    "SELECT * FROM compose_module WHERE id = %s AND deleted_at IS NULL",
                    (module_id,),
                )
            elif handle:
                cur.execute(
                    "SELECT * FROM compose_module WHERE handle = %s AND deleted_at IS NULL",
                    (handle,),
                )
            else:
                raise ValueError("必须提供 --id 或 --handle")

            module_row = cur.fetchone()
            if not module_row:
                return None, None

            # 查询 compose_module_field
            cur.execute(
                "SELECT * FROM compose_module_field "
                "WHERE rel_module = %s AND deleted_at IS NULL "
                "ORDER BY place",
                (module_row["id"],),
            )
            field_rows = cur.fetchall()

        return module_row, field_rows
    finally:
        conn.close()


def query_all_modules(db_config: dict, namespace_id: int = None) -> list[tuple[dict, list[dict]]]:
    """查询所有模块及其字段，可按 namespace 过滤。自动排除已删除 namespace 下的模块。返回 [(module_row, field_rows), ...] 列表。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT * FROM compose_module WHERE deleted_at IS NULL"
                   " AND (rel_namespace = 0 OR rel_namespace IN "
                   "(SELECT id FROM compose_namespace WHERE deleted_at IS NULL))")
            params = []
            if namespace_id is not None:
                sql += " AND rel_namespace = %s"
                params.append(namespace_id)
            sql += " ORDER BY id"
            cur.execute(sql, params)
            module_rows = cur.fetchall()

            results = []
            for module_row in module_rows:
                cur.execute(
                    "SELECT * FROM compose_module_field "
                    "WHERE rel_module = %s AND deleted_at IS NULL "
                    "ORDER BY place",
                    (module_row["id"],),
                )
                field_rows = cur.fetchall()
                results.append((module_row, field_rows))

        return results
    finally:
        conn.close()


# ────────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data: dict, output_path: Path):
    """将模块数据写入 JSON 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从数据库导出模块数据为 JSON 文件（格式与 TestModule.json 一致）"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id",
        type=int,
        dest="module_id",
        help="按 moduleID 导出，如 --id 484341972136493057",
    )
    group.add_argument(
        "--handle",
        type=str,
        help="按 handle 导出，如 --handle TestModule",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="导出所有模块到 data 目录",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="列出数据库中所有模块",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出文件路径（默认为 {handle}.json）",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="环境名（如 dev），不指定则使用 env.json 的 active 值",
    )
    parser.add_argument(
        "--tenant",
        type=str,
        default=None,
        help="租户名（如 mx），不指定则使用该环境下的第一个租户",
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default=None,
        help="命名空间 slug（如 itsm），指定则只导出该命名空间的数据；不指定则导出全部并按命名空间分目录",
    )

    args = parser.parse_args()

    # 读取数据库配置
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

    # --list: 列出所有模块
    if args.list:
        modules = list_modules(db_config, namespace_id=namespace_id)
        if not modules:
            print("⚠ 数据库中没有找到任何模块")
            return
        print(f"\n📋 共 {len(modules)} 个模块:\n")
        print(f"  {'ID':<25s} {'Handle':<25s} {'Name':<25s} {'Created'}")
        print(f"  {'─'*25} {'─'*25} {'─'*25} {'─'*20}")
        for m in modules:
            print(
                f"  {str(m['id']):<25s} {m['handle'] or '':<25s} "
                f"{m['name'] or '':<25s} {m.get('created_at', '')}"
            )
        return

    # --all: 导出所有模块
    if args.all:
        print("📄 正在查询所有模块...")
        results = query_all_modules(db_config, namespace_id=namespace_id)
        if not results:
            print("⚠ 数据库中没有找到任何模块")
            return
        print(f"   共找到 {len(results)} 个模块\n")

        # 构建 namespace 映射（未指定 namespace 时需要按 slug 分目录）
        ns_map = {}  # namespace_id -> slug
        if not args.namespace:
            ns_map = build_namespace_map(db_config)

        # 检测 handle 重复，重复的用 namespaceID 子目录区分
        from collections import Counter
        handle_count = Counter(
            (m.get("handle") or str(m["id"])) for m, _ in results
        )
        dup_handles = {h for h, c in handle_count.items() if c > 1}
        if dup_handles:
            print(f"   ⚠ 检测到重复 handle: {', '.join(dup_handles)}，将按 namespaceID 分目录\n")

        success, fail = 0, 0
        for module_row, field_rows in results:
            handle = module_row.get("handle") or str(module_row["id"])
            ns_id = int(module_row.get("rel_namespace", 0))
            module_json = build_module_json(module_row, field_rows)

            # 确定输出路径: {env}/{tenant}/{ns}/module/{handle}.json
            if args.namespace:
                ns_slug = args.namespace
            else:
                ns_slug = ns_map.get(ns_id, str(ns_id))
            if handle in dup_handles:
                output_path = tenant_root / ns_slug / "module" / f"{handle}_{ns_id}.json"
            else:
                output_path = tenant_root / ns_slug / "module" / f"{handle}.json"

            try:
                write_json_file(module_json, output_path)
                suffix = f" (ns: {ns_id})" if handle in dup_handles else ""
                print(f"   {handle:<25s} 字段数: {len(field_rows)}{suffix}")
                success += 1
            except Exception as e:
                print(f"   ❌ {handle}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 查询模块
    print(f"📄 正在查询模块...")
    module_row, field_rows = query_module(
        db_config,
        module_id=args.module_id,
        handle=args.handle,
    )

    if not module_row:
        identifier = args.module_id or args.handle
        print(f"❌ 未找到模块: {identifier}")
        sys.exit(1)

    print(f"   模块名称: {module_row.get('name')}")
    print(f"   moduleID: {module_row['id']}")
    print(f"   handle:   {module_row.get('handle')}")
    print(f"   自定义字段数: {len(field_rows)}")

    # 构建 JSON
    module_json = build_module_json(module_row, field_rows)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        handle = module_row.get("handle") or str(module_row["id"])
        ns_id = int(module_row.get("rel_namespace", 0))
        ns_map = build_namespace_map(db_config)
        ns_slug = ns_map.get(ns_id, str(ns_id))
        output_path = tenant_root / ns_slug / "module" / f"{handle}.json"

    write_json_file(module_json, output_path)

    # 打印字段摘要
    print(f"\n📊 字段列表:")
    for f in module_json["fields"]:
        print(f"   {f['fieldID']:<25s} {f['name']:<20s} {f['kind']:<12s} label={f['label']!r}")


if __name__ == "__main__":
    main()
