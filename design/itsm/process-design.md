## 概述

本文描述 `lowcode-mx` ITSM 命名空间的四条核心业务流程：事件管理、问题管理、变更管理、服务请求。所有流程均通过 Corteza lowcode 平台的 Module（数据层）+ Workflow（自动化层）+ Page/Layout（展示层）协同实现。

---

## 事件管理流程

### 状态机

```mermaid
stateDiagram-v2
    [*] --> Open : 创建事件
    Open --> InProgress : 接单 / 分配处理人
    InProgress --> Pending : 等待用户确认 / 第三方
    Pending --> InProgress : 恢复处理
    InProgress --> Resolved : 填写解决方案
    Resolved --> Closed : 用户确认关闭 / 自动关闭
    Resolved --> Open : 用户拒绝 / 重开
    InProgress --> Cancelled : 取消工单
    Open --> Cancelled : 取消工单
```

### 核心时序

```mermaid
sequenceDiagram
    participant User as 用户 / 系统
    participant Portal as 服务门户
    participant Incident as Incident 模块
    participant AssignRule as 分单规则
    participant Group as 处理组
    participant SLA as SLA 引擎
    participant Notification as 通知

    User->>Portal: 提交事件
    Portal->>Incident: 创建记录（status=Open）
    Incident->>AssignRule: 触发自动分单规则
    AssignRule-->>Incident: 写入 assignmentGroup / assignee
    Incident->>SLA: 启动 SLA 计时（创建 SlaTask）
    SLA-->>Notification: 到期前发送提醒
    Group->>Incident: 处理人接单（status=InProgress）
    Group->>Incident: 填写 resolution（status=Resolved）
    Incident->>SLA: 停止 SLA 计时
    User->>Incident: 确认关闭（status=Closed）
```

### 关键业务规则

- `priority` 由 `urgency` × `impact` 经 PriorityMatrix 自动计算写入。
- `onSite=true` 时自动创建 OnsiteTicket 子工单并派遣现场工程师。
- `parentIncident` 支持父子工单层级，子工单状态不影响父工单独立流转。
- 事件关闭后 `hasBreached` 标记由 SLA 引擎写回；已违约的事件在报表中单独统计。
- 重开次数通过 workflow 计数，写入 `reopenCount`（若有）或日志模块。

---

## 问题管理流程

### 状态机

```mermaid
stateDiagram-v2
    [*] --> Open : 创建问题单（手动/从事件提升）
    Open --> Analysis : 开始根因分析
    Analysis --> ResolutionProposed : 根因识别，提出解决方案
    ResolutionProposed --> Resolved : 解决方案实施完毕
    Resolved --> Closed : 确认关闭
    Resolved --> Open : 复发再开
    Analysis --> RiskAccepted : 已知错误，接受风险
    RiskAccepted --> Closed : 关闭已知错误
    Open --> Cancelled : 取消
```

### 核心时序

```mermaid
sequenceDiagram
    participant Analyst as 问题分析师
    participant Incident as Incident 模块
    participant Problem as Problem 模块
    participant ProblemTask as ProblemTask 模块
    participant Change as ChangeRequest 模块

    Incident->>Problem: 升级为问题单（relatedProblem 写入）
    Problem->>ProblemTask: 创建子任务（调查、分析）
    Analyst->>Problem: 填写 rootCause / workaround
    Problem->>Change: 若需变更修复，关联 relatedChange
    Analyst->>Problem: 填写 resolution（status=Resolved）
    Analyst->>Problem: 确认关闭（status=Closed）
```

### 关键业务规则

- `duplicateOf` 字段指向另一个 Problem，用于标记重复问题单合并处理。
- `workaroundApplied=true` 时可跳过解决方案直接进入 Resolved 状态。
- 已知错误（Known Error）通过 `status=RiskAccepted` 持久化存档，不强制关闭。
- Problem 与 Incident 为多对多双向关联（`relatedIncident` / `relatedProblem`）。

---

## 变更管理流程

### 变更类型与状态机

变更类型（`type` 字段，Select）：

| 值 | 说明 | 审批要求 |
|----|------|--------|
| Standard | 标准变更（预审批） | 自动审批 |
| Normal | 普通变更 | CAB 审批 |
| Emergency | 紧急变更 | 授权人紧急审批 |

```mermaid
stateDiagram-v2
    [*] --> New : 提交变更请求
    New --> Assess : 分配评审
    Assess --> Scheduled : 审批通过，排期
    Scheduled --> Implement : 开始实施
    Implement --> Review : 实施完成，进入回顾
    Review --> Closed : 回顾通过
    Review --> Implement : 回顾不通过，重新实施
    Assess --> Rejected : 审批拒绝
    New --> Cancelled : 取消
    Scheduled --> Cancelled : 取消
```

### 核心时序

```mermaid
sequenceDiagram
    participant Requestor as 变更申请人
    participant CR as ChangeRequest 模块
    participant CT as ChangeTask 模块
    participant Approver as 审批人 / CAB
    participant Incident as Incident 模块

    Requestor->>CR: 提交变更申请（status=New）
    CR->>Approver: 触发审批通知
    Approver->>CR: 审批通过（status=Scheduled）
    CR->>CT: 创建实施子任务（changeTask）
    CT->>CR: 子任务全部完成
    CR->>CR: 状态推进至 Review
    Approver->>CR: 回顾通过（status=Closed，reviewStatus 填写）
    CR-->>Incident: 关联 relatedIncident 更新（若变更来源于事件）
```

### 关键业务规则

- `changePlan`、`backoutPlan`、`riskAndImpactAnalysis`、`testPlan`、`implementationPlan` 均为必填文档字段，审批前需填写。
- 紧急变更（Emergency）跳过标准 CAB 审批，由授权角色直接审批。
- `reviewDate` 在关闭前必须填写；`reviewStatus` 用于记录回顾结论。
- ChangeTask 的完成情况不自动推进 ChangeRequest 状态，需由处理人手动更新。
- `reassignmentCount` 由 workflow 自动累加，用于追踪转派次数。

---

## 服务请求流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Portal as 服务门户
    participant Catalog as ServiceCatalog 模块
    participant Item as ServiceItem 模块
    participant SA as ServiceApplication 模块
    participant Group as 处理组

    User->>Portal: 浏览服务门户
    Portal->>Catalog: 展示服务目录树（parent_id 层级）
    Portal->>Item: 展示服务项列表（catelog_id 关联）
    User->>SA: 提交服务申请（选择 ServiceItem）
    SA->>Group: 按 ServiceItem.groups 路由处理组
    Group->>SA: 处理并关闭申请
```

### 服务目录层级

ServiceCatalog 通过 `parent_id`（LongNumber 自引用）构建多级目录树，ServiceItem 通过 `catelog_id`（多值 String）挂载到一个或多个目录节点。

`ServiceItem` 的可见性由以下字段联合控制：

| 字段 | 类型 | 说明 |
|------|------|------|
| is_all | Bool | 所有人可见 |
| roles | String (multi) | 按角色控制 |
| groups | String (multi) | 按组控制 |
| users | String (multi) | 按用户控制 |
| published | Select | 发布状态控制 |

---

## SLA 执行机制

```mermaid
sequenceDiagram
    participant Incident as Incident 模块
    participant SlaEngine as SLA 引擎（Workflow）
    participant SlaTask as SlaTask 模块
    participant SLABreakdown as SLABreakdown 模块
    participant Notification as 通知系统

    Incident->>SlaEngine: 事件创建 / 状态变更触发
    SlaEngine->>SlaTask: 创建 SlaTask（taskType: response / resolution）
    SlaEngine->>SlaTask: 计算 dueTime（基于 Sla.timeTable 工作时间表）
    SlaTask->>Notification: dueTime 到期前 N 分钟提醒
    alt 超时
        SlaTask->>Incident: 写入 hasBreached=true
        SlaTask->>SLABreakdown: 创建违约记录
    else 按时完成
        SlaTask->>SlaTask: 标记 resolved
    end
```

---

## 跨流程关联汇总

| 关联方向 | 字段 | 关联类型 |
|---------|------|---------|
| Incident → Problem | `relatedProblem` | M:N 双向 |
| Incident → ChangeRequest | `relatedChange` | M:N 双向 |
| Problem → ChangeRequest | `relatedChange` | M:N 双向 |
| Incident → Incident | `parentIncident` | 1:N 父子 |
| Problem → Problem | `duplicateOf` | 合并引用 |
| ChangeRequest → ChangeTask | `changeTask` | 1:N |
| Problem → ProblemTask | `problemTask` | 1:N |
| Incident → OnsiteTicket | `onsiteTicket` | 1:N |
| Incident → SlaTask | 工作流创建 | 1:N |
| Incident → SLABreakdown | 工作流创建 | 1:N |
