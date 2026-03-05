#!/usr/bin/env python3
"""
将页面布局 JSON 配置文件同步（新增/更新）到 MySQL 数据库的
compose_page_layout 表中。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    python sync_layout_to_db.py <json_file>
    python sync_layout_to_db.py <json_file> --dry-run

示例:
    python sync_layout_to_db.py ceshiAI.json
    python sync_layout_to_db.py data/ceshiAI.json --dry-run
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


# ────────────────────────── 时间格式转换 ───────────────────────────

def parse_datetime(value) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return None


# ────────────────────── 构建 compose_page_layout 行 ──────────────────

def build_layout_row(layout: dict) -> dict:
    return {
        "id": int(layout["layoutID"]),
        "handle": layout.get("handle", ""),
        "page_id": int(layout.get("pageID", 0)),
        "parent_id": int(layout.get("parentID", 0)),
        "rel_namespace": int(layout.get("namespaceID", 0)),
        "weight": int(layout.get("weight", 0)),
        "meta": json.dumps(layout.get("meta", {}), ensure_ascii=False),
        "config": json.dumps(layout.get("config", {}), ensure_ascii=False),
        "blocks": json.dumps(layout.get("blocks", []), ensure_ascii=False),
        "owned_by": int(layout.get("ownedBy", 0)),
        "created_at": parse_datetime(layout.get("createdAt"))
        or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": parse_datetime(layout.get("updatedAt")),
        "deleted_at": parse_datetime(layout.get("deletedAt")),
    }


# ──────────────────────── UPSERT SQL ─────────────────────────

UPSERT_LAYOUT_SQL = """
INSERT INTO compose_page_layout
    (id, handle, page_id, parent_id, rel_namespace, weight,
     meta, config, blocks, owned_by,
     created_at, updated_at, deleted_at)
VALUES
    (%(id)s, %(handle)s, %(page_id)s, %(parent_id)s, %(rel_namespace)s, %(weight)s,
     %(meta)s, %(config)s, %(blocks)s, %(owned_by)s,
     %(created_at)s, %(updated_at)s, %(deleted_at)s)
ON DUPLICATE KEY UPDATE
    handle        = VALUES(handle),
    page_id       = VALUES(page_id),
    parent_id     = VALUES(parent_id),
    rel_namespace = VALUES(rel_namespace),
    weight        = VALUES(weight),
    meta          = VALUES(meta),
    config        = VALUES(config),
    blocks        = VALUES(blocks),
    owned_by      = VALUES(owned_by),
    updated_at    = NOW(),
    deleted_at    = VALUES(deleted_at);
"""


# ────────────────────────── 数据库操作 ──────────────────────────────

def sync_to_database(
    layout_row: dict,
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    dry_run: bool = False,
):
    if dry_run:
        print("\n[预览模式] 以下数据不会实际写入数据库\n")
        print("── compose_page_layout ──")
        for k, v in layout_row.items():
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
            cur.execute(UPSERT_LAYOUT_SQL, layout_row)
            print(f"✔ compose_page_layout  upsert 完成  (id={layout_row['id']})")

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
        description="将页面布局 JSON 配置同步到 MySQL compose_page_layout 表"
    )
    parser.add_argument(
        "json_file",
        help="布局 JSON 文件路径，如 ceshiAI.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只打印将要写入的数据，不连接数据库",
    )
    parser.add_argument(
        "--env", type=str, default=None,
        help="环境名（如 dev），不指定则使用 env.json 的 active 值",
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

    db_config = load_db_config(env=args.env, tenant=args.tenant)
    print(f"🔗 数据库连接: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    print(f"📄 正在读取: {json_path}")
    layout = load_layout_data(str(json_path))
    meta = layout.get("meta", {})
    print(f"   标题:     {meta.get('title', '')}")
    print(f"   layoutID: {layout.get('layoutID')}")
    print(f"   pageID:   {layout.get('pageID')}")
    print(f"   handle:   {layout.get('handle')}")
    print(f"   blocks 数: {len(layout.get('blocks') or [])}")

    layout_row = build_layout_row(layout)

    sync_to_database(
        layout_row,
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
