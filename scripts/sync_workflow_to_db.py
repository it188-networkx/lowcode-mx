#!/usr/bin/env python3
"""
将工作流 JSON 配置文件同步（新增/更新）到 MySQL 数据库的
automation_workflows 和 automation_triggers 两张表中。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    python sync_workflow_to_db.py <json_file>
    python sync_workflow_to_db.py <json_file> --dry-run

示例:
    python sync_workflow_to_db.py ITSM-Incident-Resolved.json
    python sync_workflow_to_db.py data/ITSM-Incident-Resolved.json --dry-run
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

def load_workflow_data(filepath: str) -> dict:
    """加载工作流 JSON 文件，返回 workflow 对象 dict。"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # {"workflows": [{...}]} 包装格式
    if isinstance(data, dict) and "workflows" in data:
        wf_list = data["workflows"]
        if isinstance(wf_list, list) and len(wf_list) > 0:
            return wf_list[0]

    # 直接的 workflow 对象
    if isinstance(data, dict) and "handle" in data and "steps" in data:
        return data

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


# ────────────────────── 构建 automation_workflows 行 ──────────────

def build_workflow_row(wf: dict, workflow_id: int = None) -> dict:
    """构建 automation_workflows 表的行数据。
    如果 JSON 中没有 workflowID，需要从数据库查询或由调用方提供。
    """
    wf_id = workflow_id or int(wf.get("workflowID", 0))

    return {
        "id": wf_id,
        "handle": wf.get("handle", ""),
        "meta": json.dumps(wf.get("meta", {}), ensure_ascii=False),
        "enabled": 1 if wf.get("enabled", True) else 0,
        "trace": 1 if wf.get("trace", False) else 0,
        "keep_sessions": int(wf.get("keepSessions", 0)),
        "scope": json.dumps(wf.get("scope", {}), ensure_ascii=False),
        "steps": json.dumps(wf.get("steps", []), ensure_ascii=False),
        "paths": json.dumps(wf.get("paths", []), ensure_ascii=False),
        "issues": json.dumps(wf.get("issues", []), ensure_ascii=False),
        "run_as": int(wf.get("runAs", 0)),
        "owned_by": int(wf.get("ownedBy", 0)),
        "created_at": parse_datetime(wf.get("createdAt"))
        or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": parse_datetime(wf.get("updatedAt")),
        "deleted_at": parse_datetime(wf.get("deletedAt")),
        "created_by": int(wf.get("createdBy", 0)),
        "updated_by": int(wf.get("updatedBy", 0)),
        "deleted_by": int(wf.get("deletedBy", 0)),
        "rel_namespace": int(wf.get("namespaceID", 0)),
    }


# ────────────────── 构建 automation_triggers 行列表 ────────────────

def build_trigger_rows(wf: dict, workflow_id: int, existing_trigger_ids: list[int] = None) -> list[dict]:
    """构建 automation_triggers 表的行数据列表。"""
    triggers = wf.get("triggers", [])
    rows = []

    for idx, trigger in enumerate(triggers):
        # 优先复用数据库中已存在的 trigger ID，其次使用 JSON 中的 triggerID
        trigger_id = 0
        if existing_trigger_ids and idx < len(existing_trigger_ids):
            trigger_id = existing_trigger_ids[idx]
        elif trigger.get("triggerID"):
            trigger_id = int(trigger["triggerID"])

        rows.append({
            "id": trigger_id,
            "rel_workflow": workflow_id,
            "rel_step": int(trigger.get("stepID", 0)),
            "enabled": 1 if trigger.get("enabled", True) else 0,
            "transaction": 1,
            "meta": json.dumps(trigger.get("meta", {}), ensure_ascii=False),
            "resource_type": trigger.get("resourceType", ""),
            "event_type": trigger.get("eventType", ""),
            "constraints": json.dumps(trigger.get("constraints", []), ensure_ascii=False),
            "input": json.dumps(trigger.get("input", {}), ensure_ascii=False),
            "owned_by": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": None,
            "deleted_at": None,
            "created_by": 0,
            "updated_by": 0,
            "deleted_by": 0,
            "weight": idx,
            "type": 2,
            "async": 0,
        })

    return rows


# ──────────────────────── UPSERT SQL ─────────────────────────

UPSERT_WORKFLOW_SQL = """
INSERT INTO automation_workflows
    (id, handle, meta, enabled, trace, keep_sessions, scope, steps, paths, issues,
     run_as, owned_by, created_at, updated_at, deleted_at,
     created_by, updated_by, deleted_by, rel_namespace)
VALUES
    (%(id)s, %(handle)s, %(meta)s, %(enabled)s, %(trace)s, %(keep_sessions)s,
     %(scope)s, %(steps)s, %(paths)s, %(issues)s,
     %(run_as)s, %(owned_by)s, %(created_at)s, %(updated_at)s, %(deleted_at)s,
     %(created_by)s, %(updated_by)s, %(deleted_by)s, %(rel_namespace)s)
ON DUPLICATE KEY UPDATE
    handle        = VALUES(handle),
    meta          = VALUES(meta),
    enabled       = VALUES(enabled),
    trace         = VALUES(trace),
    keep_sessions = VALUES(keep_sessions),
    scope         = VALUES(scope),
    steps         = VALUES(steps),
    paths         = VALUES(paths),
    issues        = VALUES(issues),
    run_as        = VALUES(run_as),
    owned_by      = VALUES(owned_by),
    updated_at    = NOW(),
    deleted_at    = VALUES(deleted_at),
    updated_by    = VALUES(updated_by),
    deleted_by    = VALUES(deleted_by),
    rel_namespace = VALUES(rel_namespace);
"""

UPSERT_TRIGGER_SQL = """
INSERT INTO automation_triggers
    (id, rel_workflow, rel_step, enabled, `transaction`, meta,
     resource_type, event_type, `constraints`, input,
     owned_by, created_at, updated_at, deleted_at,
     created_by, updated_by, deleted_by, weight, type, `async`)
VALUES
    (%(id)s, %(rel_workflow)s, %(rel_step)s, %(enabled)s, %(transaction)s, %(meta)s,
     %(resource_type)s, %(event_type)s, %(constraints)s, %(input)s,
     %(owned_by)s, %(created_at)s, %(updated_at)s, %(deleted_at)s,
     %(created_by)s, %(updated_by)s, %(deleted_by)s, %(weight)s, %(type)s, %(async)s)
ON DUPLICATE KEY UPDATE
    rel_workflow  = VALUES(rel_workflow),
    rel_step      = VALUES(rel_step),
    enabled       = VALUES(enabled),
    `transaction` = VALUES(`transaction`),
    meta          = VALUES(meta),
    resource_type = VALUES(resource_type),
    event_type    = VALUES(event_type),
    `constraints` = VALUES(`constraints`),
    input         = VALUES(input),
    owned_by      = VALUES(owned_by),
    updated_at    = NOW(),
    deleted_at    = VALUES(deleted_at),
    updated_by    = VALUES(updated_by),
    deleted_by    = VALUES(deleted_by),
    weight        = VALUES(weight),
    type          = VALUES(type),
    `async`       = VALUES(`async`);
"""


# ────────────────────────── 数据库操作 ──────────────────────────────

def resolve_workflow_id(cur, handle: str) -> int | None:
    """根据 handle 查询已存在的 workflow ID。"""
    cur.execute(
        "SELECT id FROM automation_workflows WHERE handle = %s AND deleted_at IS NULL",
        (handle,),
    )
    row = cur.fetchone()
    return row["id"] if row else None


def get_existing_trigger_ids(cur, workflow_id: int) -> list[int]:
    """获取某工作流已存在的 trigger ID 列表。"""
    cur.execute(
        "SELECT id FROM automation_triggers "
        "WHERE rel_workflow = %s AND deleted_at IS NULL "
        "ORDER BY weight, id",
        (workflow_id,),
    )
    return [r["id"] for r in cur.fetchall()]


def sync_to_database(
    wf: dict,
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
        wf_row = build_workflow_row(wf, workflow_id=0)
        print("── automation_workflows ──")
        for k, v in wf_row.items():
            display = v if len(str(v)) < 120 else str(v)[:120] + "..."
            print(f"  {k:20s} = {display}")
        triggers = wf.get("triggers", [])
        print(f"\n── automation_triggers ({len(triggers)} 条) ──")
        for i, t in enumerate(triggers):
            print(
                f"  #{i}  resourceType={t.get('resourceType')!r}  "
                f"eventType={t.get('eventType')!r}  stepID={t.get('stepID')!r}"
            )
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
            handle = wf.get("handle", "")

            # 查询已存在的 workflow ID
            existing_id = resolve_workflow_id(cur, handle) if handle else None

            if existing_id:
                workflow_id = existing_id
                print(f"   发现已有工作流 ID: {workflow_id}，执行更新")
            else:
                # 没有已存在的，需要 JSON 中有 workflowID 或者生成新的
                workflow_id = int(wf.get("workflowID", 0))
                if not workflow_id:
                    print("❌ JSON 中没有 workflowID，且数据库中未找到同 handle 的工作流")
                    sys.exit(1)
                print(f"   新增工作流 ID: {workflow_id}")

            # 1. upsert automation_workflows
            wf_row = build_workflow_row(wf, workflow_id=workflow_id)
            cur.execute(UPSERT_WORKFLOW_SQL, wf_row)
            print(f"✔ automation_workflows  upsert 完成  (id={workflow_id})")

            # 2. upsert automation_triggers
            existing_trigger_ids = get_existing_trigger_ids(cur, workflow_id)
            trigger_rows = build_trigger_rows(wf, workflow_id, existing_trigger_ids)

            for row in trigger_rows:
                if row["id"] == 0:
                    # 无法 upsert，需要用 INSERT 并获取自增 ID
                    # 但 automation_triggers 的 id 是 bigint unsigned NOT NULL 非自增
                    # 跳过没有 ID 的 trigger
                    print(
                        f"  ⚠ 跳过无ID的trigger: resourceType={row['resource_type']!r} "
                        f"eventType={row['event_type']!r}  (数据库中无对应记录)"
                    )
                    continue
                cur.execute(UPSERT_TRIGGER_SQL, row)
                print(
                    f"  ✔ automation_triggers  upsert  "
                    f"id={row['id']}  resourceType={row['resource_type']!r}"
                )

        conn.commit()
        print(f"\n✅ 同步成功! 工作流 1 条, triggers {len(trigger_rows)} 条。")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 同步失败，已回滚: {e}")
        raise
    finally:
        conn.close()


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将工作流 JSON 配置同步到 MySQL automation_workflows / automation_triggers 表"
    )
    parser.add_argument(
        "json_file",
        help="工作流 JSON 文件路径，如 ITSM-Incident-Resolved.json",
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
    wf = load_workflow_data(str(json_path))
    meta = wf.get("meta", {})
    print(f"   名称:       {meta.get('name', '')}")
    print(f"   handle:     {wf.get('handle')}")
    print(f"   steps 数:   {len(wf.get('steps', []))}")
    print(f"   paths 数:   {len(wf.get('paths', []))}")
    print(f"   triggers 数: {len(wf.get('triggers', []))}")

    sync_to_database(
        wf,
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
