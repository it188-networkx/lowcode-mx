#!/usr/bin/env python3
"""
从服务端 API 查询工作流数据（含触发器），
构造成 {"workflows": [...]} 格式的 JSON 并生成文件。

用法:
    # 导出所有工作流
    python export_workflow_from_api.py --all

    # 按 workflowID 导出
    python export_workflow_from_api.py --id 123456

    # 按 handle 导出
    python export_workflow_from_api.py --handle ITSM-Incident-Resolved

    # 列出所有工作流
    python export_workflow_from_api.py --list
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from api_utils import (
    load_api_config,
    api_get, api_list_all, APIError,
)

# src/ 目录路径（输出根目录）
SRC_ROOT = Path(__file__).resolve().parent.parent / "src"


# ────────────────────── 工具函数 ──────────────────────────────

def make_filename(wf: dict) -> str:
    """用 handle 生成文件名，为空时用 meta.name，再为空用 ID。"""
    name = (wf.get("handle") or "").strip()
    if not name:
        meta = wf.get("meta", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except (json.JSONDecodeError, TypeError):
                meta = {}
        name = (meta.get("name") or "").strip()
    if not name:
        name = str(wf.get("workflowID", "unknown"))
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name


# ────────────────────── 写入 JSON 文件 ──────────────────────────

def write_json_file(data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {output_path}")


# ────────────────────── API 查询封装 ──────────────────────────

def list_workflows_api(base_url: str, headers: dict) -> list[dict]:
    """列出所有工作流（含子工作流和已禁用的）。"""
    return api_list_all(
        base_url, headers,
        "/automation/workflows/",
        {"limit": 100, "disabled": 1, "subWorkflow": 1},
    )


def get_workflow_by_id(base_url: str, headers: dict, wf_id: str) -> dict | None:
    """按 workflowID 获取工作流详情。"""
    try:
        resp = api_get(base_url, headers, f"/automation/workflows/{wf_id}")
        return resp.get("response")
    except APIError as e:
        if e.status in (404, 422):
            return None
        raise


def find_workflow_by_handle(base_url: str, headers: dict, handle: str) -> dict | None:
    """按 handle 查找工作流。"""
    items = api_list_all(
        base_url, headers,
        "/automation/workflows/",
        {"query": handle, "limit": 100, "disabled": 2},
    )
    for wf in items:
        if wf.get("handle") == handle:
            return wf
    return None


def get_triggers_for_workflow(base_url: str, headers: dict, wf_id: str) -> list[dict]:
    """获取某工作流的所有触发器。"""
    return api_list_all(
        base_url, headers,
        "/automation/triggers/",
        {"workflowID": wf_id, "disabled": 1},
    )


def build_trigger_export(trigger: dict) -> dict:
    """
    将 API 返回的触发器数据转换为导出格式。
    API 返回 stepID (在某些版本中为 workflowStepID)，统一为 stepID。
    """
    result = dict(trigger)
    # 确保有 stepID
    if "workflowStepID" in result and "stepID" not in result:
        result["stepID"] = result["workflowStepID"]
    return result


def build_export_json(wf_data: dict, triggers: list[dict]) -> dict:
    """构建最终导出的 JSON，扁平 workflow 对象格式（含内嵌 triggers）。"""
    wf = dict(wf_data)
    wf["triggers"] = [build_trigger_export(t) for t in triggers]
    return wf


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="从 API 导出工作流数据为 JSON 文件（含触发器）"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id", type=str, dest="workflow_id",
        help="按 workflowID 导出",
    )
    group.add_argument(
        "--handle", type=str,
        help="按 handle 导出",
    )
    group.add_argument(
        "--all", action="store_true",
        help="导出所有工作流",
    )
    group.add_argument(
        "--list", action="store_true",
        help="列出所有工作流",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="输出文件路径（默认为 {handle}.json）",
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

    cfg = load_api_config(env=args.env, tenant=args.tenant)
    base_url = cfg["baseUrl"]
    api_headers = cfg["headers"]

    if not base_url:
        print("❌ env.json 中未配置 baseUrl")
        sys.exit(1)

    print(f"🔗 API: {base_url}")

    # 工作流输出目录: lowcode-mx/src/workflow/
    workflow_out_dir = SRC_ROOT / "workflow"
    print(f"📂 输出目录: {workflow_out_dir}")

    # --list
    if args.list:
        workflows = list_workflows_api(base_url, api_headers)
        if not workflows:
            print("⚠ 未找到任何工作流")
            return
        print(f"\n📋 共 {len(workflows)} 个工作流:\n")
        print(f"{'ID':<25s} {'Handle':<40s} {'Enabled':<10s}")
        print(f"{'─'*25} {'─'*40} {'─'*10}")
        for wf in workflows:
            wf_id = wf.get("workflowID", "")
            display = wf.get("handle") or ""
            if not display:
                meta = wf.get("meta", {})
                if isinstance(meta, dict):
                    display = meta.get("name", str(wf_id))
            enabled = "✔" if wf.get("enabled") else "✘"
            print(f"{wf_id:<25s} {display:<40s} {enabled:<10s}")
        return

    # --all
    if args.all:
        print("📄 正在查询所有工作流...")
        workflows = list_workflows_api(base_url, api_headers)
        if not workflows:
            print("⚠ 未找到任何工作流")
            return
        print(f"   共找到 {len(workflows)} 个工作流\n")

        # 检测文件名重复
        filenames = [make_filename(wf) for wf in workflows]
        name_count = Counter(filenames)
        dup_names = {n for n, c in name_count.items() if c > 1}
        if dup_names:
            print(f"   ⚠ 检测到重复名称: {', '.join(dup_names)}，将在文件名中附加 workflowID\n")

        success, fail = 0, 0
        for wf in workflows:
            wf_id = wf.get("workflowID", "")
            fname = make_filename(wf)

            try:
                # 获取触发器
                triggers = get_triggers_for_workflow(base_url, api_headers, wf_id)
                export_json = build_export_json(wf, triggers)

                if fname in dup_names:
                    output_path = workflow_out_dir / f"{fname}_{wf_id}.json"
                else:
                    output_path = workflow_out_dir / f"{fname}.json"

                write_json_file(export_json, output_path)
                suffix = f" (id: {wf_id})" if fname in dup_names else ""
                print(f"   {fname:<40s} triggers: {len(triggers)}{suffix}")
                success += 1
            except Exception as e:
                print(f"   ❌ {fname}: {e}")
                fail += 1
        print(f"\n✅ 导出完成! 成功 {success} 个, 失败 {fail} 个。")
        return

    # 单工作流查询
    wf_data = None

    if args.workflow_id:
        print(f"📄 正在按 ID 查询工作流: {args.workflow_id}")
        wf_data = get_workflow_by_id(base_url, api_headers, args.workflow_id)
    elif args.handle:
        print(f"📄 正在按 handle 查询工作流: {args.handle}")
        wf_data = find_workflow_by_handle(base_url, api_headers, args.handle)

    if not wf_data:
        identifier = args.workflow_id or args.handle
        print(f"❌ 未找到工作流: {identifier}")
        sys.exit(1)

    wf_id = wf_data.get("workflowID", "")
    meta = wf_data.get("meta", {})
    if isinstance(meta, dict):
        print(f"   名称:       {meta.get('name', '')}")
    print(f"   workflowID: {wf_id}")
    print(f"   handle:     {wf_data.get('handle', '')}")
    print(f"   steps 数:   {len(wf_data.get('steps', []))}")

    # 获取触发器
    triggers = get_triggers_for_workflow(base_url, api_headers, wf_id)
    print(f"   triggers 数: {len(triggers)}")

    export_json = build_export_json(wf_data, triggers)

    if args.output:
        output_path = Path(args.output)
    else:
        fname = make_filename(wf_data)
        output_path = workflow_out_dir / f"{fname}.json"

    write_json_file(export_json, output_path)


if __name__ == "__main__":
    main()
