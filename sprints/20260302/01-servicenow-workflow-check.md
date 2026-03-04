## 子任务 01：排查 ServiceNow 工作流配置

- 序号：01
- 关联 Sprint 原始编号：2003
- 优先级：P0
- 责任人：凡锐
- 关联 SOP：`../../../lowcode-base/process/workflow/sop-workflow-upd.md`
- 前置依赖：无

---

## 目标

排查 MX 环境 ServiceNow 对接工作流配置是否存在连接参数或步骤逻辑异常。

---

## 涉及文件

| 文件 | 路径 |
|------|------|
| 主工作流 | `../../src/itsm/workflow/push_itsm_incident_servicenow.json` |
| 附件同步工作流 | `../../src/itsm/workflow/servicenow_incident_attachment_sync.json` |
| 测试工作流 | `../../src/itsm/workflow/test-sync-file-to-serviceNow.json` |
| 测试工作流 | `../../src/itsm/workflow/test-sync-note-to-serviceNow.json` |

---

## 操作步骤

1. 阅读 `../../../lowcode-base/process/workflow/sop-workflow-upd.md`
2. 打开 `push_itsm_incident_servicenow.json`，检查 `steps[]` 中的 HTTP 请求参数
3. 确认 ServiceNow 连接地址、认证 Header 参数是否与当前 MX 环境凭证一致
4. 若参数错误，按 SOP 修改并提交变更
5. 若需要新增重试逻辑，记录到 `02-1o1osms-workflow-plan.md` 一并规划

---

## 验收标准

- JSON 格式合法，`workflowID` 和 `handle` 未被修改
- HTTP 请求步骤的 URL 和认证参数与 MX 环境配置一致
