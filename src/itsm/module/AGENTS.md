## 目录职责

本目录存放 itsm 命名空间（namespaceID: `409824987081211905`）的 47 个模块 JSON 文件。
每个文件对应一个 Corteza 模块，包含字段定义、DAL 连接等配置。

---

## 文件命名格式

```
{Handle}.json
```

例：`Incident.json`、`topData_409824987081211905.json`（topData 带 namespaceID 后缀）

---

## 操作前必读

新增或修改模块前，必须先阅读：

1. `../../../../../lowcode-base/corteza/field/AGENTS.md` — Field Kind 参考
2. `../../../../../lowcode-base/process/module/` — 模块操作 SOP

关键规则：

- `kind`、`fieldID`、`name` 禁止修改
- `isMulti` 变更须同步 `encodingStrategy`（单值 `plain`，多值 `json`）
- 新增 module 必须通过 Sonyflake 生成 moduleID 和 fieldID

---

## 模块清单（handle → 文件名）

| handle | 文件名 | 说明 |
|--------|--------|------|
| AssignRule | AssignRule.json | 分单规则 |
| Category | Category.json | 分类树（Tree type） |
| CauseCode | CauseCode.json | 原因代码 |
| ceshiAI | ceshiAI.json | AI 测试模块 |
| ChangeRequest | ChangeRequest.json | 变更请求（49 字段） |
| ChangeTask | ChangeTask.json | 变更任务 |
| Comment | Comment.json | 通用评论 |
| Company | Company.json | 公司 |
| FaultyAsset | FaultyAsset.json | 故障设备 |
| Group | Group.json | 组（Group type） |
| Impact | Impact.json | 影响度 |
| Incident | Incident.json | 事件管理（63 字段） |
| IncidentComment | IncidentComment.json | 事件评论 |
| InventoryUsage | InventoryUsage.json | 库存使用记录 |
| KnowledgeBase | KnowledgeBase.json | 知识库 |
| Locations | Locations.json | 地点（18 字段） |
| OnsiteTicket | OnsiteTicket.json | 现场服务工单 |
| OrderRule | OrderRule.json | 工单规则 |
| Priority | Priority.json | 优先级 |
| PriorityMatrix | PriorityMatrix.json | 优先级矩阵 |
| Problem | Problem.json | 问题管理（49 字段） |
| ProblemTask | ProblemTask.json | 问题任务（34 字段） |
| PurchaseRequest | PurchaseRequest.json | 采购申请 |
| receiptHistory | receiptHistory.json | 电子签单 |
| Region | Region.json | 区域 |
| ResolutionCode | ResolutionCode.json | 解决方案代码 |
| ServiceApplication | ServiceApplication.json | 服务申请 |
| ServiceCatalog | ServiceCatalog.json | 服务目录 |
| ServiceItem | ServiceItem.json | 服务项 |
| ServiceSetting | ServiceSetting.json | 服务设置 |
| Sla | Sla.json | SLA 配置 |
| SLABreakdown | SLABreakdown.json | SLA 明细 |
| SlaTask | SlaTask.json | SLA 任务（28 字段） |
| SlaTime | SlaTime.json | SLA 时间 |
| SlaTimeSchedule | SlaTimeSchedule.json | SLA 时间表 |
| Staff | Staff.json | 员工（EmploymentApplication） |
| StatusManagement | StatusManagement.json | 状态管理（9 字段） |
| Survey | Survey.json | 满意度调查（13 字段） |
| team | team.json | 团队 |
| TestManag | TestManag.json | 测试管理 |
| TestModule | TestModule.json | 测试模块 |
| TicketManagement | TicketManagement.json | 工单管理 |
| Todo | Todo.json | 待办（13 字段） |
| TodoCalendar | TodoCalendar.json | 待办日历（24 字段） |
| topData | topData_409824987081211905.json | 置顶功能模块（无 page/layout） |
| Urgency | Urgency.json | 紧急度 |
| User | User.json | 用户（12 字段） |
