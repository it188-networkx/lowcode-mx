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

---

## 快捷指令

以下命令格式适用于 `itsm` 命名空间的常见 module 修改操作：

```
# 修改字段 label
#配置@itsm {Handle} 把 {字段name} 的 label 改为 {新label}

# 修改字段必填
#配置@itsm {Handle} 把 {字段name} 设为必填

# 添加新字段
#配置@itsm {Handle} 添加字段 {name} 类型 {kind} label {label}

# 删除字段
#配置@itsm {Handle} 删除字段 {name}

# 修改模块配置
#配置@itsm {Handle} 设置 config.recordRevisions.enabled 为 true
```

示例：

- `#配置@itsm Incident 把 shortDescription 的 label 改为 事件简述`
- `#配置@itsm Incident 添加字段 newField 类型 String label 新字段`

---

## 高频公共字段模式

### 几乎所有模块共有的字段

| 字段名 | Kind | 出现模块数 | 说明 |
|--------|------|-----------|------|
| status | Record/Select/String | 24+ | 记录状态，不同模块 kind 不同 |
| name | String | 18+ | 记录名称 |
| description | String | 17+ | 描述信息 |

### ITIL 工单模块共享字段

适用于 Incident / Problem / ChangeRequest / ChangeTask / ProblemTask：

| 字段名 | Kind | 说明 |
|--------|------|------|
| number | Code | 工单编号（自动编号） |
| shortDescription | String | 工单简述 |
| description | String | 工单详情 |
| status | Record | 工单状态（关联 StatusManagement） |
| category | Record | 分类（关联 Category） |
| subCategory | Tree | 子分类 |
| assignmentGroup | Record | 处理组（关联 Group） |
| assignee | Record | 处理人 |
| priority | Record | 优先级（关联 Priority） |
| urgency | Record | 紧急度（关联 Urgency） |
| impact | Record | 影响度（关联 Impact） |
| company | Record | 客户/公司 |
| location | Record | 地点/网点 |
| participantGroup | Record (multi) | 参与组 |
| participant | Record (multi) | 参与人 |

### 参考数据模块标准字段

适用于 Impact / Urgency / Priority / StatusManagement / TicketManagement 等参考数据模块：

| 字段名 | Kind | 说明 |
|--------|------|------|
| name | String | 名称（通常 isRequired=true） |
| code | String | 编码（通常 isRequired=true） |
| enabledFlag | Bool | 是否启用（通常 isRequired=true） |
| description | String | 描述 |

---

## 模块关系图

### ITIL 核心工单关系

```
Incident (事件) ──── IncidentComment (评论)
  ├── relatedProblem ──→ Problem (问题)
  ├── relatedChange  ──→ ChangeRequest (变更)
  ├── onsiteTicket   ──→ OnsiteTicket (现场工单)
  ├── faultyAssetIDs ──→ FaultyAsset (故障设备)
  └── causeCode      ──→ CauseCode (原因分类)

Problem (问题)
  ├── problemTask    ──→ ProblemTask (问题任务)
  ├── relatedIncident──→ Incident
  └── relatedChange  ──→ ChangeRequest

ChangeRequest (变更)
  ├── changeTask     ──→ ChangeTask (变更任务)
  ├── relatedIncident──→ Incident
  └── relatedProblem ──→ Problem
```

### 参考数据关系

```
PriorityMatrix
  ├── urgency  ──→ Urgency
  ├── impact   ──→ Impact
  └── priority ──→ Priority

Category (树形) ──→ pid (自引用父分类)
  └── relModule ──→ 关联的业务模块

StatusManagement
  └── relModule ──→ 关联的业务模块
```

### SLA 体系

```
Sla (SLA 定义)
  └── SlaTask (SLA 执行实例)
       └── SlaTime (工作时间表)
            └── SlaTimeSchedule (排程)

SLABreakdown (SLA 分解记录)
```

### 组织架构

```
User (用户)
  ├── group    ──→ Group (组)
  ├── team     ──→ team (团队)
  └── company  ──→ Company (公司)

Group (组)
  ├── users    ──→ User
  ├── team     ──→ team
  └── categorys──→ Category
```

---

## 业务模块分类

### 核心工单模块

- Incident — 事件管理（63 字段，最大模块）
- Problem — 问题管理（49 字段）
- ChangeRequest — 变更管理（49 字段）
- ProblemTask — 问题任务（34 字段）
- ChangeTask — 变更任务（14 字段）
- OnsiteTicket — 现场工单（12 字段）

### 参考数据模块

- Category — 分类（树形）
- CauseCode — 原因分类
- Impact — 影响度
- Urgency — 紧急度
- Priority — 优先级
- PriorityMatrix — 优先级矩阵
- StatusManagement — 状态管理
- ResolutionCode — 解决方案分类
- Region — 区域
- TicketManagement — 工单管理

### SLA 模块

- Sla — SLA 定义
- SlaTask — SLA 任务实例
- SlaTime — SLA 工作时间
- SlaTimeSchedule — SLA 排程
- SLABreakdown — SLA 分解

### 服务目录

- ServiceCatalog — 服务目录
- ServiceItem — 服务项
- ServiceApplication — 服务申请
- ServiceSetting — 服务设置

### 组织架构

- User — 用户
- Group — 组
- team — 团队
- Company — 公司
- Locations — 网点/地点
- Staff — 员工

### 辅助模块

- Comment / IncidentComment — 评论
- KnowledgeBase — 知识库
- Todo / TodoCalendar — 待办/待办日历
- Survey — 满意度调查
- AssignRule / OrderRule — 分配/排队规则
- FaultyAsset — 故障设备
- InventoryUsage — 库存使用
- PurchaseRequest — 采购申请
- receiptHistory — 电子签单
- topData — 置顶数据

### 测试模块

- ceshiAI — AI 测试模块
- TestModule — 测试模块
- TestManag — 测试管理
