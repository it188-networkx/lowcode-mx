#!/usr/bin/env python3
"""
从 MySQL 数据库的 automation_workflows 和 automation_triggers 表中查询工作流数据，
构造成与 ITSM-Incident-Resolved.json 相同结构的 JSON 并生成文件。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    # 导出所有工作流
    python export_workflow_from_db.py --all

    # 按 workflowID 导出
    python export_workflow_from_db.py --id 123456

    # 按 handle 导出
    python export_workflow_from_db.py --handle ITSM-Incident-Resolved

    # 列出所有工作流
    python export_workflow_from_db.py --list
"""

import argparse
import json
import re
import sys
from collections import Counter
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


# ────────────────── 从 DB 行构建 trigger JSON ──────────────────

def build_trigger_json(row: dict) -> dict:
    meta = safe_json_loads(row.get("meta"), {})
    constraints = safe_json_loads(row.get("constraints"), [])
    input_data = safe_json_loads(row.get("input"), {})

    trigger = {
        "triggerID": str(row.get("id", 0)),
        "resourceType": row.get("resource_type", ""),
        "eventType": row.get("event_type", ""),
        "constraints": constraints,
        "enabled": bool(row.get("enabled", 1)),
        "stepID": str(row.get("rel_step", 0)),
        "meta": meta,
    }

    if input_data:
        trigger["input"] = input_data

    return trigger


# ────────────────── 从 DB 行构建 workflow JSON ──────────────────

def build_workflow_json(wf_row: dict, trigger_rows: list[dict]) -> dict:
    meta = safe_json_loads(wf_row.get("meta"), {})
    steps = safe_json_loads(wf_row.get("steps"), [])
    paths = safe_json_loads(wf_row.get("paths"), [])
    scope = safe_json_loads(wf_row.get("scope"), {})
    issues = safe_json_loads(wf_row.get("issues"), [])

    workflow = {
        "workflowID": str(wf_row.get("id", 0)),
        "handle": wf_row.get("handle", ""),
        "enabled": bool(wf_row.get("enabled", 1)),
        "meta": meta,
        "keepSessions": int(wf_row.get("keep_sessions", 0)),
        "steps": steps,
        "paths": paths,
        "triggers": [build_trigger_json(t) for t in trigger_rows],
    }

    # 仅在有值时添加额外字段
    if scope:
        workflow["scope"] = scope
    if issues:
        workflow["issues"] = issues
    if wf_row.get("run_as"):
        workflow["runAs"] = str(wf_row["run_as"])
    if wf_row.get("owned_by"):
        workflow["ownedBy"] = str(wf_row["owned_by"])
    if wf_row.get("trace"):
        workflow["trace"] = bool(wf_row["trace"])

    created = to_iso8601(wf_row.get("created_at"))
    if created:
        workflow["createdAt"] = created
    updated = to_iso8601(wf_row.get("updated_at"))
    if updated:
        workflow["updatedAt"] = updated

    return workflow


def build_export_json(wf_row: dict, trigger_rows: list[dict]) -> dict:
    """构建最终导出的 JSON，使用 {"workflows": [...]} 包装格式。"""
    return {
        "workflows": [build_workflow_json(wf_row, trigger_rows)]
    }


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


def list_workflows(db_config: dict, namespace_id: int = None) -> list[dict]:
    """列出数据库中所有工作流，可按 namespace 过滤。自动排除已删除 namespace 下的工作流。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT id, handle, meta, enabled, rel_namespace, created_at "
                   "FROM automation_workflows "
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


def query_triggers_for_workflow(cur, workflow_id: int) -> list[dict]:
    """查询某个工作流关联的所有 triggers。"""
    cur.execute(
        "SELECT * FROM automation_triggers "
        "WHERE rel_workflow = %s AND deleted_at IS NULL "
        "ORDER BY weight, id",
        (workflow_id,),
    )
    return cur.fetchall()


def query_workflow(db_config: dict, workflow_id: int = None, handle: str = None):
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            if workflow_id:
                cur.execute(
                    "SELECT * FROM automation_workflows WHERE id = %s AND deleted_at IS NULL",
                    (workflow_id,),
                )
            elif handle:
                cur.execute(
                    "SELECT * FROM automation_workflows WHERE handle = %s AND deleted_at IS NULL",
                    (handle,),
                )
            else:
                raise ValueError("必须提供 --id 或 --handle")

            wf_row = cur.fetchone()
            if not wf_row:
                return None, None

            trigger_rows = query_triggers_for_workflow(cur, wf_row["id"])
            return wf_row, trigger_rows
    finally:
        conn.close()


def query_all_workflows(db_config: dict, namespace_id: int = None) -> list[tuple[dict, list[dict]]]:
    """查询所有工作流及其触发器，可按 namespace 过滤。自动排除已删除 namespace 下的工作流。"""
    conn = get_connection(db_config)
    try:
        with conn.cursor() as cur:
            sql = ("SELECT * FROM automation_workflows WHERE deleted_at IS NULL"
                   " AND (rel_namespace = 0 OR rel_namespace IN "
                   "(SELECT id FROM compose_namespace WHERE deleted_at IS NULL))")
            params = []
            if namespace_id is not None:
                sql += " AND rel_namespace = %s"
                params.append(namespace_id)
            sql += " ORDER BY id"
            cur.execute(sql, params)
            wf_rows = cur.fetchall()

            results = []
            for wf_row in wf_rows:
                trigger_rows = query_triggers_for_workflow(cur, wf_row["id"])
                results.append((wf_row, trigger_rows))

            return results
    finally:
        conn.close()


# ────────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


def make_filename(wf_row: dict) -> str:
    """用 handle 生成文件名，为空时用 meta.name，再为空用 ID。"""
    name = (wf_row.get("handle") or "").strip()
    if not name:
        meta = safe_json_loads(wf_row.get("meta"), {})
        name = (meta.get("name") or "").strip()
    if not name:
        name = str(wf_row["id"])
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从数据库导出工作流数据为 JSON 文件（格式与 ITSM-Incident-Resolved.json 一致）"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=int, dest="workflow_id",
        help="按 workflowID 导出",
    )
    group.add_argument(
        "--handle", type=str,
        help="按 handle 导出",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有工作流到 data 目录",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出数据库中所有工作流",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="输出文件路径（默认为 data/{handle}.json）",
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

    db_config = load_db_config(env=args.env, tenant=args.tenant)
    print(f"🔗 数据库连接: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    # 计算输出根目录: configuration/{env_dir}/{tenant}/workflow/
    env_dir, tenant_name = resolve_env_and_tenant(env=args.env, tenant=args.tenant)
    workflow_out_dir = CONF_ROOT / env_dir / tenant_name / "workflow"
    print(f"📂 输出目录: {workflow_out_dir}")

    # --list
    if args.list:
        rows = list_workflows(db_config)
        if not rows:
            print("⚠ 数据库中没有找到任何工作流")
            return
        print(f"\n📋 共 {len(rows)} 个工作流:\n")
        print(f"  {'ID':<25s} {'Handle':<40s} {'Enabled':<10s} {'Created'}")
        print(f"  {'─'*25} {'─'*40} {'─'*10} {'─'*20}")
        for r in rows:
            meta = safe_json_loads(r.get("meta"), {})
            name = meta.get("name", "")
            display = r.get("handle") or name or str(r["id"])
            print(
                f"  {str(r['id']):<25s} {display:<40s} "
                f"{'✔' if r.get('enabled') else '✘':<10s} {r.get('created_at', '')}"
            )
        return

    # --all
    if args.all:
        print("📄 正在查询所有工作流...")
        results = query_all_workflows(db_config)
        if not results:
            print("⚠ 数据库中没有找到任何工作流")
            return
        print(f"   共找到 {len(results)} 个工作流\n")

        # 检测文件名重复
        filenames = [make_filename(wf) for wf, _ in results]
        name_count = Counter(filenames)
        dup_names = {n for n, c in name_count.items() if c > 1}
        if dup_names:
            print(f"   ⚠ 检测到重复名称: {', '.join(dup_names)}，将在文件名中附加 workflowID\n")

        success, fail = 0, 0
        for wf_row, trigger_rows in results:
            fname = make_filename(wf_row)
            export_json = build_export_json(wf_row, trigger_rows)

            # workflow 不区分命名空间，统一输出到 {env}/{tenant}/workflow/
            if fname in dup_names:
                output_path = workflow_out_dir / f"{fname}_{wf_row['id']}.json"
            else:
                output_path = workflow_out_dir / f"{fname}.json"

            try:
                write_json_file(export_json, output_path)
                suffix = f" (id: {wf_row['id']})" if fname in dup_names else ""
                print(f"   {fname:<40s} triggers: {len(trigger_rows)}{suffix}")
                success += 1
            except Exception as e:
                print(f"   ❌ {fname}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 单工作流查询
    print("📄 正在查询工作流...")
    wf_row, trigger_rows = query_workflow(
        db_config, workflow_id=args.workflow_id, handle=args.handle
    )

    if not wf_row:
        identifier = args.workflow_id or args.handle
        print(f"❌ 未找到工作流: {identifier}")
        sys.exit(1)

    meta = safe_json_loads(wf_row.get("meta"), {})
    print(f"   名称:       {meta.get('name', '')}")
    print(f"   workflowID: {wf_row['id']}")
    print(f"   handle:     {wf_row.get('handle')}")
    print(f"   steps 数:   {len(safe_json_loads(wf_row.get('steps'), []))}")
    print(f"   triggers 数: {len(trigger_rows)}")

    export_json = build_export_json(wf_row, trigger_rows)

    if args.output:
        output_path = Path(args.output)
    else:
        fname = make_filename(wf_row)
        output_path = workflow_out_dir / f"{fname}.json"

    write_json_file(export_json, output_path)


if __name__ == "__main__":
    main()
