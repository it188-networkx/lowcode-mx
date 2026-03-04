## 周冲刺任务 - 20260302（mx 命名空间配置）

- 迭代周期：2026-03-02 — 2026-03-09
- 来源：ops-playbook/sprints/20260302/sprint-plan.md（摘录涉及命名空间配置的条目）
- 状态：计划中

---

## 本周配置相关任务

### 从 Sprint 计划摘录

| 序号 | 原始编号 | 类型 | 项目 | 描述 | 责任人 | 配置影响 |
|------|---------|------|------|------|--------|---------|
| 01 | 2003 | 缺陷 P0 | MX | MX service now 对接异常：排查 MX 环境 ServiceNow 接口连接与认证异常 | 凡锐 | 工作流 `push_itsm_incident_servicenow.json` 可能需调整 |
| 02 | 3001 | 项目开发 | MX | MX 短信平台 1o1oSMS 对接方案测试 | 凡锐 | 确认后可能需新增通知类工作流 |

---

## 子任务清单

本周 mx 命名空间配置待执行子任务：

| 序号 | 任务名 | 关联 SOP | 前置依赖 | 文件 |
|------|--------|---------|---------|------|
| 01 | 排查 ServiceNow 工作流配置 | `../../lowcode-base/process/workflow/sop-workflow-upd.md` | 无 | 01-servicenow-workflow-check.md |
| 02 | 确认 1o1oSMS 短信工作流方案 | `../../lowcode-base/process/workflow/sop-workflow-add.md` | 01 完成后，取决于排查结论 | 02-1o1osms-workflow-plan.md |
| 03 | 新建 fsm 命名空间：团队管理 + 事件管理菜单体系初始化 | `../../lowcode-base/process/module/sop-module-add.md` `../../lowcode-base/process/page/sop-page-add.md` | 无 | 03-fsm-namespace-init.md |

---

## 备注

- 2003、3001 均为 MX 项目，配置变更范围待排查后确认
- 03 为本地测试需求：在 `dev.dms/mx/fsm` 新建命名空间，涉及 5 个 module、12 个 page、18 个 layout
- fsm 命名空间已按最简原则初始化，后续扩展参考 `../../lowcode-base/process/module/sop-module-add.md`
