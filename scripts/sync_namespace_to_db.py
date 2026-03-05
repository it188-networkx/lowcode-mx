#!/usr/bin/env python3
"""
将命名空间配置同步（新增/更新）到 MySQL 数据库的
compose_namespace 表中。

数据库连接参数从 configuration/env.json 中读取。

用法:
    python sync_namespace_to_db.py --id <namespaceID> --slug <slug> --name <name>
    python sync_namespace_to_db.py --id <namespaceID> --slug <slug> --name <name> --dry-run

示例:
    python sync_namespace_to_db.py --id 490001000000000001 --slug change --name "变更管理"
    python sync_namespace_to_db.py --id 490001000000000001 --slug change --name "变更管理" --dry-run
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# 将 configuration/ 目录加入模块搜索路径，以便导入 db_utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from db_utils import load_db_config

try:
    import pymysql
except ImportError:
    pymysql = None  # dry-run 模式不需要 pymysql


# ────────────────────── 构建 compose_namespace 行 ──────────────────

def build_namespace_row(
    namespace_id: int,
    slug: str,
    name: str,
    enabled: bool = True,
    meta: dict | None = None,
) -> dict:
    """构建 compose_namespace 表的一行数据。"""
    return {
        "id": namespace_id,
        "slug": slug,
        "enabled": 1 if enabled else 0,
        "meta": json.dumps(meta or {}, ensure_ascii=False),
        "name": name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": None,
        "deleted_at": None,
    }


# ──────────────────────── UPSERT SQL ─────────────────────────

UPSERT_NAMESPACE_SQL = """
INSERT INTO compose_namespace
    (id, slug, enabled, meta, name,
     created_at, updated_at, deleted_at)
VALUES
    (%(id)s, %(slug)s, %(enabled)s, %(meta)s, %(name)s,
     %(created_at)s, %(updated_at)s, %(deleted_at)s)
ON DUPLICATE KEY UPDATE
    slug       = VALUES(slug),
    enabled    = VALUES(enabled),
    meta       = VALUES(meta),
    name       = VALUES(name),
    updated_at = NOW(),
    deleted_at = VALUES(deleted_at);
"""


# ────────────────────────── 数据库操作 ──────────────────────────────

def sync_to_database(
    namespace_row: dict,
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    dry_run: bool = False,
):
    """将命名空间数据 upsert 到数据库。"""
    if dry_run:
        print("\n[预览模式] 以下数据不会实际写入数据库\n")
        print("── compose_namespace ──")
        for k, v in namespace_row.items():
            display = v if len(str(v)) < 120 else str(v)[:120] + "..."
            print(f"  {k:20s} = {display}")
        return

    if pymysql is None:
        print("❌ 实际写入数据库需要 pymysql，请先安装: pip install pymysql")
        sys.exit(1)

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(UPSERT_NAMESPACE_SQL, namespace_row)
            print(f"✔ compose_namespace  upsert 完成  (id={namespace_row['id']})")

        conn.commit()
        print(f"\n✅ 同步成功!")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 同步失败，已回滚: {e}")
        raise
    finally:
        conn.close()


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将命名空间配置同步到 MySQL compose_namespace 表"
    )
    parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="命名空间 ID，如 490001000000000001",
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
        help="预览模式：只打印将要写入的数据，不连接数据库",
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

    # 从 env.json 读取数据库连接参数
    db_config = load_db_config(env=args.env, tenant=args.tenant)
    print(f"🔗 数据库连接: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    try:
        meta = json.loads(args.meta)
    except json.JSONDecodeError:
        print(f"❌ --meta 参数不是合法的 JSON: {args.meta}")
        sys.exit(1)

    print(f"📄 命名空间信息:")
    print(f"   ID:      {args.id}")
    print(f"   slug:    {args.slug}")
    print(f"   name:    {args.name}")
    print(f"   enabled: {args.enabled}")

    namespace_row = build_namespace_row(
        namespace_id=args.id,
        slug=args.slug,
        name=args.name,
        enabled=bool(args.enabled),
        meta=meta,
    )

    sync_to_database(
        namespace_row,
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
