## ITSM 命名空间总览

| 属性 | 值 |
|------|-----|
| slug | itsm |
| namespaceID | 409824987081211905 |
| 环境 | mx（dev.dms 租户） |
| 模块数 | 47 |
| 页面数 | 123 |
| 布局数 | 279 |
| 工作流数 | 95 |
| 初始化 Sprint | 2026-S01 |
| 对应 lowcode-template 版本 | 初始版本（2026-03-04 复制） |

---

## 目录结构与职责

```text
src/itsm/
├── AGENTS.md      # 本文件：命名空间总览
├── module/        # 47 个模块 JSON（字段定义、DAL 连接）
│   └── AGENTS.md
├── page/          # 123 个页面 JSON（Block 完整定义）
│   └── AGENTS.md
└── layout/        # 279 个布局 JSON（Block 位置、按钮）
    └── AGENTS.md
```

---

## 操作前必读规则

对任何 JSON 文件执行增删改前，必须先阅读对应资源类型的参考文档：

| 操作对象 | 必读文档 |
|---------|---------|
| Module（字段） | `../../../../lowcode-base/corteza/field/AGENTS.md` + `../../../../lowcode-base/process/module/` |
| Page（Block 配置） | `../../../../lowcode-base/corteza/block/AGENTS.md` + `../../../../lowcode-base/process/page/` |
| Layout（坐标、按钮） | `../../../../lowcode-base/process/layout/` |

---

## 模块清单（handle → moduleID）

| # | handle | name | moduleID |
|---|--------|------|----------|
| 1 | AssignRule | AssignRule | — |
| 2 | Category | Category | — |
| 3 | CauseCode | CauseCode | — |
| 4 | ceshiAI | ceshiAI | — |
| 5 | ChangeRequest | ChangeRequest | — |
| 6 | ChangeTask | ChangeTask | — |
| 7 | Comment | Comment | — |
| 8 | Company | Company | — |
| 9 | FaultyAsset | FaultyAsset | — |
| 10 | Group | Group | — |
| 11 | Impact | Impact | — |
| 12 | Incident | 事件管理 | — |
| 13 | IncidentComment | IncidentComment | — |
| 14 | InventoryUsage | InventoryUsageCopy | — |
| 15 | KnowledgeBase | KnowledgeBase | — |
| 16 | Locations | Locations | — |
| 17 | OnsiteTicket | OnsiteTicket | — |
| 18 | OrderRule | OrderRule | — |
| 19 | Priority | Priority | — |
| 20 | PriorityMatrix | PriorityMatrix | — |
| 21 | Problem | Problem | — |
| 22 | ProblemTask | ProblemTask | — |
| 23 | PurchaseRequest | Purchase Request | — |
| 24 | receiptHistory | 电子签单 | — |
| 25 | Region | Region | — |
| 26 | ResolutionCode | ResolutionCode | — |
| 27 | ServiceApplication | ServiceApplication | — |
| 28 | ServiceCatalog | ServiceCatalog | — |
| 29 | ServiceItem | ServiceItem | — |
| 30 | ServiceSetting | ServiceSetting | — |
| 31 | Sla | Sla | — |
| 32 | SLABreakdown | SLABreakdown | — |
| 33 | SlaTask | SlaTask | — |
| 34 | SlaTime | SlaTime | — |
| 35 | SlaTimeSchedule | SlaTimeSchedule | — |
| 36 | Staff | EmploymentApplication | — |
| 37 | StatusManagement | StatusManagement | — |
| 38 | Survey | Survey | — |
| 39 | team | team | — |
| 40 | TestManag | TestManag | — |
| 41 | TestModule | TestModule | — |
| 42 | TicketManagement | TicketManagement | — |
| 43 | Todo | Todo | — |
| 44 | TodoCalendar | 待办日历 | — |
| 45 | topData | topData | 470129866610507777 |
| 46 | Urgency | Urgency | — |
| 47 | User | User | — |

> moduleID 请从对应 JSON 文件的顶层 `"moduleID"` 字段读取，此处仅作索引用途。

---

## Incident 模块常用 Record 类型字段

> Incident 模块中以下字段的 `kind` 为 `Record`，存储的是关联记录的 ID，**不可在工作流中直接与显示值比较**，必须先通过 `composeRecordsLookup` 查出关联记录再比较具体字段。

| 字段名 | 关联模块 | moduleID | 常见比较字段 |
|--------|---------|------------|-------------|
| `caller` | User | `409824987082522625` | `email`, `name` |
| `assignee` | User | `409824987082522625` | `email`, `name` |
| `assignmentGroup` | Group | `409824987082653697` | `name` |
| `category` | Category | `409824987082457089` | `name`, `code` |
| `impact` | Impact | `409824987081670657` | `name`, `code` |
| `urgency` | Urgency | `409824987082194945` | `name`, `code` |
| `priority` | Priority | `409824987082326017` | `name`, `code` |
| `statusCode` | StatusManagement | `409824987081605121` | `name`, `code` |

工作流中正确用法：

```
# 错误：直接比较 caller 字段
# record.values.caller == "dongb@it188.com"  ← caller 存储的是记录 ID

# 正确：先查出 User 记录，再比较 email
Step 1: composeRecordsLookup(module="User", record=record.values.caller) → callerUser
Step 2: gateway → callerUser.values.email == "dongb@it188.com"
```
