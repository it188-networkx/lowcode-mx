#!/usr/bin/env python3
"""
将工作流 JSON 配置文件通过 API 同步（新增/更新）到服务端。
包含工作流本体和关联的触发器。

用法:
    python sync_workflow_to_api.py <json_file>
    python sync_workflow_to_api.py <json_file> --dry-run

示例:
    python sync_workflow_to_api.py ITSM-Incident-Resolved.json
    python sync_workflow_to_api.py data/ITSM-Incident-Resolved.json --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

from api_utils import (
    load_api_config, api_get, api_post, api_put, api_delete, api_list_all,
    resource_exists, APIError,
)


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

    # 扁平 workflow 对象（含 workflowID 或 steps）
    if isinstance(data, dict) and ("workflowID" in data or "steps" in data):
        return data

    raise ValueError(f"无法识别 JSON 文件格式: {filepath}")


# ────────────────────── API 请求体构建 ──────────────────────

_WORKFLOW_BODY_KEYS = [
    "handle", "meta", "enabled", "trace", "keepSessions",
    "scope", "steps", "paths", "runAs", "namespaceID",
    "ownedBy", "labels", "type",
]

_TRIGGER_BODY_KEYS = [
    "type", "eventType", "resourceType", "enabled",
    "workflowID", "workflowStepID", "meta", "constraints",
    "input", "ownedBy", "transaction", "async", "weight",
]


def build_workflow_body(wf: dict) -> dict:
    """从工作流 JSON 构建 Workflow API 请求体。"""
    return {k: wf[k] for k in _WORKFLOW_BODY_KEYS if k in wf}


def build_trigger_body(trigger: dict, workflow_id: str) -> dict:
    """
    从触发器 JSON 构建 Trigger API 请求体。

    注意字段名映射：
    - JSON 中的 stepID → API 请求体中的 workflowStepID
    - JSON 中的 type 可能是 int → API 请求体中需要是 string
    """
    body = {}
    for k in _TRIGGER_BODY_KEYS:
        if k == "workflowStepID":
            # 从 JSON 的 stepID 或 workflowStepID 映射
            body[k] = str(trigger.get("stepID", trigger.get("workflowStepID", "0")))
        elif k == "workflowID":
            body[k] = workflow_id
        elif k == "type":
            # 确保 type 为 string
            body[k] = str(trigger.get("type", "2"))
        elif k in trigger:
            body[k] = trigger[k]
    return body


# ────────────── 工作流查找 ──────────────

def find_workflow_by_handle(base_url: str, headers: dict, handle: str) -> str | None:
    """通过 handle 查找已存在的工作流，返回 workflowID；未找到返回 None。"""
    if not handle:
        return None
    items = api_list_all(
        base_url, headers,
        "/automation/workflows/",
        {"query": handle, "limit": 100, "disabled": 2},
    )
    for wf in items:
        if wf.get("handle") == handle:
            return str(wf["workflowID"])
    return None


def get_existing_triggers(base_url: str, headers: dict, workflow_id: str) -> list[dict]:
    """获取某工作流已存在的所有触发器。"""
    return api_list_all(
        base_url, headers,
        "/automation/triggers/",
        {"workflowID": workflow_id, "disabled": 1},
    )


# ──────────────────── 同步主函数 ────────────────────

def sync_workflow(
    wf: dict,
    *,
    base_url: str,
    headers: dict,
    dry_run: bool = False,
) -> dict | None:
    """
    通过 API 同步工作流到服务端（新增或更新）。

    逻辑：
    1. 按 handle 查找已存在的工作流
    2. 存在 → PUT 更新；不存在 → POST 新增
    3. 同步触发器：对比现有触发器，新增/更新/删除多余的
    """
    handle = wf.get("handle", "")
    workflow_id = str(wf.get("workflowID", "0"))

    if dry_run:
        triggers = wf.get("triggers", [])
        print(f"\n[预览模式] 以下数据不会实际发送到服务端\n")
        print(f"  handle:     {handle}")
        print(f"  workflowID: {workflow_id}")
        print(f"  steps 数:   {len(wf.get('steps', []))}")
        print(f"  paths 数:   {len(wf.get('paths', []))}")
        print(f"  triggers 数: {len(triggers)}")
        for i, t in enumerate(triggers):
            print(
                f"    #{i}  resourceType={t.get('resourceType')!r}  "
                f"eventType={t.get('eventType')!r}  stepID={t.get('stepID')!r}"
            )
        return None

    # ── 查找已存在的工作流 ──
    existing_id = find_workflow_by_handle(base_url, headers, handle)

    if existing_id:
        workflow_id = existing_id
        print(f"  📝 工作流已存在 (workflowID={workflow_id})，执行更新...")
        body = build_workflow_body(wf)
        resp = api_put(
            base_url, headers,
            f"/automation/workflows/{workflow_id}",
            data=body,
        )
        print(f"  ✔ 工作流更新成功")
    elif workflow_id and workflow_id != "0":
        # 有 workflowID 但服务端找不到 handle → 检查直接 ID
        exists = resource_exists(
            base_url, headers,
            f"/automation/workflows/{workflow_id}",
        )
        if exists:
            print(f"  📝 工作流已存在 (workflowID={workflow_id})，执行更新...")
            body = build_workflow_body(wf)
            resp = api_put(
                base_url, headers,
                f"/automation/workflows/{workflow_id}",
                data=body,
            )
            print(f"  ✔ 工作流更新成功")
        else:
            print(f"  ➕ 工作流不存在，执行新增...")
            body = build_workflow_body(wf)
            resp = api_post(base_url, headers, "/automation/workflows/", data=body)
            workflow_id = str(resp.get("response", {}).get("workflowID", workflow_id))
            print(f"  ✔ 工作流新增成功 (workflowID={workflow_id})")
    else:
        print(f"  ➕ 工作流不存在，执行新增...")
        body = build_workflow_body(wf)
        resp = api_post(base_url, headers, "/automation/workflows/", data=body)
        workflow_id = str(resp.get("response", {}).get("workflowID", "?"))
        print(f"  ✔ 工作流新增成功 (workflowID={workflow_id})")

    # ── 同步触发器 ──
    json_triggers = wf.get("triggers", [])
    if not json_triggers:
        print(f"  ℹ JSON 中没有触发器，跳过触发器同步")
        return resp

    print(f"\n── 同步触发器 ({len(json_triggers)} 个) ──")

    existing_triggers = get_existing_triggers(base_url, headers, workflow_id)
    existing_map = {str(t["triggerID"]): t for t in existing_triggers}
    print(f"  服务端已有 {len(existing_triggers)} 个触发器")

    synced_ids = set()

    for idx, trigger in enumerate(json_triggers):
        trigger_id = str(trigger.get("triggerID", "0"))

        if trigger_id and trigger_id != "0" and trigger_id in existing_map:
            # ── 更新已有触发器 ──
            body = build_trigger_body(trigger, workflow_id)
            resp_t = api_put(
                base_url, headers,
                f"/automation/triggers/{trigger_id}",
                data=body,
            )
            print(f"  ✔ 更新触发器 #{idx}  triggerID={trigger_id}")
            synced_ids.add(trigger_id)
        else:
            # 尝试按 idx 从现有列表中匹配
            matched = False
            if idx < len(existing_triggers):
                et = existing_triggers[idx]
                et_id = str(et["triggerID"])
                if et_id not in synced_ids:
                    body = build_trigger_body(trigger, workflow_id)
                    resp_t = api_put(
                        base_url, headers,
                        f"/automation/triggers/{et_id}",
                        data=body,
                    )
                    print(f"  ✔ 更新触发器 #{idx}  triggerID={et_id} (按位置匹配)")
                    synced_ids.add(et_id)
                    matched = True

            if not matched:
                # ── 新增触发器 ──
                body = build_trigger_body(trigger, workflow_id)
                resp_t = api_post(
                    base_url, headers,
                    "/automation/triggers/",
                    data=body,
                )
                new_tid = resp_t.get("response", {}).get("triggerID", "?")
                print(f"  ✔ 新增触发器 #{idx}  triggerID={new_tid}")
                synced_ids.add(str(new_tid))

    # ── 删除多余的触发器 ──
    for et_id, et in existing_map.items():
        if et_id not in synced_ids:
            try:
                api_delete(base_url, headers, f"/automation/triggers/{et_id}")
                print(f"  🗑 删除多余触发器  triggerID={et_id}")
            except APIError as e:
                print(f"  ⚠ 删除触发器失败 triggerID={et_id}: {e}")

    print(f"\n✅ 工作流同步完成!")
    return resp


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将工作流 JSON 配置通过 API 同步到服务端（新增/更新）"
    )
    parser.add_argument(
        "json_file",
        help="工作流 JSON 文件路径，如 ITSM-Incident-Resolved.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只打印将要发送的数据，不实际调用 API",
    )
    parser.add_argument(
        "--env", type=str, default=None,
        help="环境名（如 dev.dms），不指定则使用 env.json 的 active 值",
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

    cfg = load_api_config(env=args.env, tenant=args.tenant)
    base_url = cfg["baseUrl"]
    api_headers = cfg["headers"]

    if not base_url:
        print("❌ env.json 中未配置 baseUrl")
        sys.exit(1)

    print(f"🔗 API: {base_url}")

    print(f"📄 正在读取: {json_path}")
    wf = load_workflow_data(str(json_path))
    meta = wf.get("meta", {})
    print(f"   名称:       {meta.get('name', '')}")
    print(f"   handle:     {wf.get('handle')}")
    print(f"   steps 数:   {len(wf.get('steps', []))}")
    print(f"   paths 数:   {len(wf.get('paths', []))}")
    print(f"   triggers 数: {len(wf.get('triggers', []))}")

    try:
        sync_workflow(
            wf,
            base_url=base_url,
            headers=api_headers,
            dry_run=args.dry_run,
        )
    except APIError as e:
        print(f"\n❌ API 调用失败: {e}")
        if e.body:
            print(f"   响应: {e.body[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
