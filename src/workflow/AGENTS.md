## lowcode-template/src/workflow 目录指南

本目录包含工作流配置的通用指南，适用于所有基于此模板创建的命名空间。

> 完整工作流 SOP 请参阅：[../../../lowcode-base/process/workflow/sop-workflow-add.md](../../../lowcode-base/process/workflow/sop-workflow-add.md)

---

## 核心规则

### 工作流存放位置

每个仓库对应一个租户，工作流文件统一存放在仓库的 `src/workflow/` 目录下，不区分命名空间：

```
src/workflow/{handle}.json
```

**严禁**放到命名空间子目录下（如 `src/{命名空间}/workflow/`）。

---

## Workflow JSON 基础结构

```json
{
  "workflows": [{
    "workflowID": "唯一ID（Sonyflake生成）",
    "handle": "{Namespace}-{Module}-{Action}",
    "enabled": true,
    "meta": {
      "name": "显示名称",
      "type": "",
      "description": ""
    },
    "steps": [],
    "paths": [],
    "triggers": [{
      "triggerID": "唯一ID（Sonyflake生成）",
      "resourceType": "compose:record",
      "eventType": "afterCreate",
      "constraints": [
        { "name": "namespace", "op": "eq", "value": ["{命名空间handle}"] },
        { "name": "module", "op": "eq", "value": ["{模块handle}"] }
      ]
    }]
  }]
}
```

---

## handle 命名约定

格式：`{Namespace}-{Module}-{Action}`

示例：
- `FSM-Event-AfterCreate`
- `FSM-Team-Assigned`
- `Itsm-Incident-Resolved`

---

## 触发器类型速查

| resourceType | eventType | 触发时机 |
|-------------|-----------|---------|
| `compose:record` | `afterCreate` | 记录创建后 |
| `compose:record` | `afterUpdate` | 记录更新后 |
| `compose:record` | `beforeCreate` | 记录创建前 |
| `compose:record` | `beforeUpdate` | 记录更新前 |
| `compose:record` | `onManual` | 手动触发（按钮） |

---

## 步骤类型速查

| Kind | 说明 |
|------|------|
| `function` | 调用系统函数（记录操作/发邮件等） |
| `expressions` | 变量赋值 |
| `gateway` | 条件分支 |
| `iterator` | 循环 |
| `termination` | 终止 |
| `error-handler` | 错误处理 |

---

## 常用系统函数

| 函数名 | 说明 |
|--------|------|
| `composeRecordsLookup` | 按 ID 查找单条记录 |
| `composeRecordsSearch` | 按条件搜索记录 |
| `composeRecordsNew` | 创建空记录对象 |
| `composeRecordsCreate` | 持久化记录到数据库 |
| `composeRecordsUpdate` | 更新已有记录 |
| `composeRecordsDelete` | 删除记录 |
| `emailSend` | 发送邮件 |

---

## ID 生成规则

首次创建工作流时，必须提供有效的 `workflowID` 和 `triggerID`（Sonyflake 格式，非 0）。

简化方式：取租户中最大已有 workflowID + 65536。

完整规则参见：`../../../lowcode-base/process/workflow/sop-workflow-add.md`

---

## 注意事项

- Layout 的 `config.actions[]` 中的 `workflowID` 引用工作流，修改 handle 或删除时需同步检查
- `Record` 类型字段存储关联记录 ID，不可直接比较业务值，需先通过 `composeRecordsLookup` 查出关联记录后再比较字段值
- `Basic` 工作流 vs `Advanced` 工作流结构不同，不要混用特有步骤类型

---

## 工作流清单（共 96 条）

### Incident（事件管理）

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `Incident-Create-SendEmail.json` | `Incident-Create-SendEmail` | — |
| `Incident_assigned_to_me.json` | `Incident_assigned_to_me` | Incident assigned to me |
| `Incident_assigned_to_my_group.json` | `Incident_assigned_to_my_group` | Incident assigned to my group |
| `itsm-Incident-BeforeCreate-CheckCaller.json` | `itsm-Incident-BeforeCreate-CheckCaller` | itsm-Incident-BeforeCreate-CheckCaller |
| `ITSM-Incident-Comment.json` | `ITSM-Incident-Comment` | ITSM-Incident-Comment |
| `ITSM-incident-createAndUpdate.json` | `ITSM-incident-createAndUpdate` | ITSM-incident-createAndUpdate |
| `itsm-incident-faultyAsset-remove.json` | `itsm-incident-faultyAsset-remove` | itsm-incident-faultyAsset-remove |
| `itsm-Incident-Onsite-Arrive.json` | `itsm-Incident-Onsite-Arrive` | itsm-Incident-Onsite-Arrive |
| `itsm-Incident-Onsite-Cancel.json` | `itsm-Incident-Onsite-Cancel` | itsm-Incident-Onsite-Cancel |
| `itsm-Incident-Onsite-Resolve.json` | `itsm-Incident-Onsite-Resolve` | itsm-Incident-Onsite-Resolve |
| `ITSM-Incident-Participant-Create.json` | `ITSM-Incident-Participant-Create` | ITSM-Participant-Create |
| `ITSM-Incident-Participant-Update.json` | `ITSM-Incident-Participant-Update` | ITSM-Participant-Update |
| `ITSM-Incident-Resolved.json` | `ITSM-Incident-Resolved` | ITSM-Incident-Resolved |
| `ITSM-Incident-ResolvedStatus-CreateSurvey-Create.json` | `ITSM-Incident-ResolvedStatus-CreateSurvey-Create` | ITSM-Incident-ResolvedStatus-CreateSurvey-Create |
| `ITSM-Incident-ResolvedStatus-CreateSurvey-Update.json` | `ITSM-Incident-ResolvedStatus-CreateSurvey-Update` | ITSM-Incident-ResolvedStatus-CreateSurvey-Update |
| `ITSM-Incident-StatsVip.json` | `ITSM-Incident-StatsVip` | ITSM-Incident-StatsVip |
| `itsm-Incident-Update-SendEmail.json` | — | itsm-Incident-Update-SendEmail |
| `itsm-auto-ralated.json` | `itsm-auto-ralated` | itsm-auto-ralated |
| `itsm-faultyAsset-create.json` | `itsm-faultyAsset-create` | itsm-faultyAsset-createAndUpdate |

### Change（变更管理）

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `ITSM-Change-Comment.json` | `ITSM-Change-Comment` | ITSM-Change-Comment |
| `itsm-Change-ChangeTask-remove.json` | `itsm-Change-ChangeTask-remove` | itsm-Change-ChangeTask-remove |
| `itsm-Change-RelatedIncident-add.json` | `itsm-Change-RelatedIncident-add` | itsm-Change-RelatedIncident-add |
| `itsm-Change-RelatedIncident-remove.json` | `itsm-Change-RelatedIncident-remove` | itsm-Change-RelatedIncident-remove |
| `itsm-ChangeRequest-Insert.json` | `itsm-ChangeRequest-Insert` | itsm-ChangeRequest-Insert |
| `itsm-ChangeRequest-Refresh.json` | `itsm-ChangeRequest-Refresh` | itsm-ChangeRequest-Refresh |
| `itsm-ChangeTask-Cancel.json` | `itsm-ChangeTask-Cancel` | itsm-ChangeTask-Cancel |
| `itsm-ChangeTask-Comment.json` | `itsm-ChangeTask-Comment` | itsm-ChangeTask-Comment |
| `itsm-ChangeTask-Complete.json` | `itsm-ChangeTask-Complete` | itsm-ChangeTask-Complete |
| `itsm-ChangeTask-Insert.json` | `itsm-ChangeTask-Insert` | itsm-ChangeTask-Insert |
| `itsm-ChangeTask-ReOpen.json` | `itsm-ChangeTask-ReOpen` | itsm-ChangeTask-ReOpen |
| `itsm-ChangeTask-StartWork.json` | `itsm-ChangeTask-StartWork` | itsm-ChangeTask-StartWork |

### Problem（问题管理）

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `ITSM-Problem-Comment.json` | `ITSM-Problem-Comment` | ITSM-Problem-Comment |
| `ITSM-Problem-ReAnalyze.json` | `ITSM-Problem-ReAnalyze` | ITSM-Problem-ReAnalyze |
| `itsm-Problem-accept-risk.json` | `itsm-Problem-accept-risk` | itsm-Problem-accept-risk |
| `itsm-Problem-communicate-resolution.json` | `itsm-Problem-communicate-resolution` | itsm-Problem-communicate-resolution |
| `itsm-Problem-communicate-workaround.json` | `itsm-Problem-communicate-workaround` | itsm-Problem-communicate-workaround |
| `itsm-Problem-duplicate.json` | `itsm-Problem-duplicate` | itsm-Problem-duplicate |
| `itsm-Problem-mark-duplicate.json` | `itsm-Problem-mark-duplicate` | itsm-Problem-mark-duplicate |
| `itsm-Problem-RelatedProblemTask-remove.json` | `itsm-Problem-RelatedProblemTask-remove` | itsm-Problem-RelatedProblemTask-remove |
| `itsm-Problem-resolve.json` | `itsm-Problem-resolve` | itsm-Problem-resolve |
| `itsm-problemTask-count.json` | `itsm-problemTask-count` | itsm-problemTask-count |
| `itsm-ProblemTask-Insert.json` | `itsm-ProblemTask-Insert` | itsm-ProblemTask-Insert |
| `ProblemTask.json` | `ProblemTask` | ITSM-ProblemTask-Complete-adv |

### OnsiteTicket（现场工单）

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `itsm-base-tranferOnsite.json` | `itsm-base-tranferOnsite` | itsm-base-tranferOnsite |
| `itsm-onsiteTicket-add.json` | — | itsm-onsiteTicket-add |
| `itsm-onsiteTicket-arrived.json` | — | itsm-onsiteTicket-arrived |
| `itsm-onsiteTicket-cancel.json` | — | itsm-onsiteTicket-cancel |
| `itsm-onsiteTicket-resolve.json` | — | itsm-onsiteTicket-resolve |

### SLA

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `sla_warning_parm.json` | `sla_warning_parm` | SLA warning parm |
| `sla_workflow_7_24.json` | — | sla_workflow_7*24 |
| `sla_workflow_aaadasda.json` | — | sla_workflow_aaadasda |
| `sla_workflow_db.json` | — | sla_workflow_db |
| `sla_workflow_db-test-sla.json` | — | sla_workflow_db-test-sla |
| `sla_workflow_db-zz.json` | — | sla_workflow_db-zz |
| `sla_workflow_dongb.json` | — | sla_workflow_dongb |
| `sla_workflow_sla.json` | — | sla_workflow_sla |
| `sla_workflow_测试sla.json` | — | sla_workflow_测试sla |

### Group / User

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `ITSM-Group-AddUserToGroup.json` | `ITSM-Group-AddUserToGroup` | ITSM-Group-增加用户到组 |
| `ITSM-Group-RemoveUserFromGroup.json` | `ITSM-Group-RemoveUserFromGroup` | ITSM-Group-组内人员删除 |
| `ITSM-User-SystemUser.json` | `ITSM-User-SystemUser` | ITSM-User-平台层用户 |
| `itsm-outline-role-sync.json` | `itsm-outline-role-sync` | itsm-outline-role-sync |
| `Staff_apprival.json` | `Staff_apprival` | staff apprival |
| `approval-会签99999.json` | `approval-会签99999` | — |

### Location（位置与资产）

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `itsm-Location-User.json` | `itsm-Location-User` | itsm-Location-User |
| `itsm-locations-delete-record.json` | `itsm-locations-delete-record` | itsm-locations-delete-record |
| `itsm-locations-sync-to-shop.json` | `itsm-locations-sync-to-shop` | itsm-locations-sync-to-shop |
| `itsm-requestedAssets-return.json` | — | itsm-requestedAssets-return |
| `itsm-设备- return.json` | `itsm-设备- return` | — |

### ITOM / ServiceNow 集成

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `itom_alert_event_recovery.json` | `itom_alert_event_recovery` | itom_alert_event_recovery |
| `itom_alert_event_sync.json` | `itom_alert_event_sync` | itom_alert_event_sync |
| `itsm-MTR-insert-INC.json` | `itsm-MTR-insert-INC` | itsm-MTR-insert-INC |
| `push_itsm_incident_servicenow.json` | `push_itsm_incident_servicenow` | push_itsm_incident_servicenow |
| `servicenow_incident_attachment_sync.json` | `servicenow_incident_attachment_sync` | servicenow_incident_attachment_sync |
| `test-sync-file-to-serviceNow.json` | `test-sync-file-to-serviceNow` | test-sync-file-to-serviceNow |
| `test-sync-note-to-serviceNow.json` | `test-sync-note-to-serviceNow` | test-sync-note-to-serviceNow |

### Survey / Service

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `ITSM-Survey-Expired.json` | `ITSM-Survey-Expired` | ITSM-Survey-Expired |
| `itsm-ServiceApplication-sync.json` | `itsm-ServiceApplication-sync` | itsm-ServiceApplication-sync |

### Todo / 定时任务

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `CloseTodo.json` | `CloseTodo` | CloseTodo |
| `itsm-cron-task.json` | `itsm-cron-task` | itsm-cron-task |
| `push-to-do.json` | `push-to-do` | — |
| `push-todo.json` | `push-todo` | PushTodo |

### 工具 / Demo

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `BASIC.json` | `BASIC` | — |
| `cancel.json` | — | — |
| `demo_email_comment.json` | `demo_email_comment` | demo_email_comment |
| `Insert-Record.json` | `Insert-Record` | Insert Record |
| `Query-Record.json` | `Query-Record` | Query Record |
| `Remove-Element-From-Array.json` | `Remove-Element-From-Array` | Remove Element From Array |
| `Send-Email.json` | `Send-Email` | Send Email |
| `Update-Record.json` | `Update-Record` | Update Record |

### 测试 / 临时

| 文件名 | handle | meta.name |
|-------|--------|-----------|
| `test.json` | — | test |
| `test_update.json` | — | test_update |
| `test-20250313.json` | — | test-20250313 |
| `test-empty.json` | `test-empty` | — |
| `test-insert.json` | `test-insert` | test-insert |
| `test-record-update-to-bridge.json` | `test-record-update-to-bridge` | test-record-update-to-bridge |
| `test-stacktrace.json` | — | test-stacktrace |
