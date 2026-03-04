## 子任务 02：1o1oSMS 短信工作流方案规划

- 序号：02
- 关联 Sprint 原始编号：3001
- 优先级：P2 (待排查 01 结论后确认)
- 责任人：凡锐
- 关联 SOP：`../../../lowcode-base/process/workflow/sop-workflow-add.md`
- 前置依赖：01（ServiceNow 工作流排查完成，确认当前工作流框架可扩展通知类集成）

---

## 目标

在 01 的结论基础上，规划 MX 环境接入 1o1oSMS 短信平台的工作流方案。

---

## 当前状态

- 对接方案测试阶段，需等待 1o1oSMS 提供测试沙箱凭证（预期本周五前确认）
- 本子任务为**规划任务**，暂不创建实际工作流 JSON

---

## 规划内容

待 1o1oSMS 沙箱凭证确认后，需创建的工作流：

| 申请工作流 handle | 触发方式 | 说明 |
|-----------------|---------|------|
| `itsm-incident-sms-notify` | `onRecord`（Incident update） | 事件更新时发送短信通知 |

---

## 操作步骤（规划阶段）

1. 确认 1o1oSMS 接口文档（URL 格式、请求参数、签名算法）
2. 参考 `../../../lowcode-base/process/workflow/sop-workflow-add.md` 规划步骤
3. 使用 Sonyflake 生成新 `workflowID` 和 `triggerID`
4. 在下一个 Sprint 执行创建

---

## 验收标准（规划阶段）

- 本文档完成 1o1oSMS 接口对接方案的基本规划
- 下一个 Sprint 中可直接基于此规划创建工作流 JSON
