# Workflow API 接口文档

## 公共请求头

> 以下请求头适用于本文档中的**所有接口**。

| Header | 必填 | 说明 |
|--------|------|------|
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | 操作人邮箱，从 `env.json → environments.{env}.tenants.{tenant}.headers` 读取 |
| `Content-Language` | 否 | 语言，如 `en` |

---

## 新增工作流

### 请求

```
POST /automation/workflows/
```

> **注意**：Workflow API 路径为 `/automation/workflows/`，不在 `/compose/namespace/` 下。

### 请求体

```json
{
  "handle": "aaa",
  "labels": {},
  "meta": {
    "name": "aaa",
    "type": "Advanced",
    "description": "aaa"
  },
  "enabled": true,
  "steps": [],
  "paths": [],
  "runAs": "0",
  "namespaceID": "409824987081211905",
  "type": "",
  "ownedBy": "472156272836608001"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `handle` | string | 是 | 工作流唯一标识 |
| `meta` | object | 是 | 元数据 |
| `meta.name` | string | 是 | 工作流显示名称 |
| `meta.type` | string | 否 | 类型，如 `"Advanced"` |
| `meta.description` | string | 否 | 描述 |
| `labels` | object | 否 | 标签键值对 |
| `enabled` | bool | 否 | 是否启用 |
| `steps` | array | 否 | 步骤列表 |
| `paths` | array | 否 | 路径（步骤间连接）列表 |
| `runAs` | string | 否 | 以指定用户身份执行，`"0"` 为默认 |
| `namespaceID` | string | 否 | 关联的命名空间 ID（`"0"` 或空表示不限命名空间） |
| `type` | string | 否 | 工作流类型 |
| `ownedBy` | string | 否 | 所有者用户 ID |

### 响应

成功时返回 HTTP 200，响应体为创建后的完整工作流对象：

```json
{
  "response": {
    "workflowID": "486300000000000001",
    "handle": "aaa",
    "meta": { ... },
    "enabled": true,
    "steps": [],
    "paths": [],
    "runAs": "0",
    "namespaceID": "409824987081211905",
    "type": "",
    "ownedBy": "472156272836608001",
    "createdAt": "2026-03-09T09:00:00Z",
    "createdBy": "472156272836608001"
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/workflows/' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --data-raw '{
    "handle": "aaa",
    "labels": {},
    "meta": {
      "name": "aaa",
      "type": "Advanced",
      "description": "aaa"
    },
    "enabled": true,
    "steps": [],
    "paths": [],
    "runAs": "0",
    "namespaceID": "409824987081211905",
    "type": "",
    "ownedBy": "0"
  }' \
  --compressed --insecure
```

---

## 查询工作流详情

### 请求

```
GET /automation/workflows/{workflowID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `workflowID` | string | 工作流 ID |

### 响应

成功时返回 HTTP 200，响应体为完整的工作流对象（与列表中的单个元素结构一致）：

```json
{
  "response": {
    "workflowID": "486201022694424577",
    "handle": "aaa",
    "meta": {
      "name": "aaa",
      "description": "aaa",
      "visual": null,
      "type": "Advanced",
      "formList": null,
      "businessType": "",
      "businessLabel": "",
      "results": "",
      "icon": ""
    },
    "enabled": true,
    "trace": false,
    "keepSessions": 0,
    "scope": {},
    "steps": [ ... ],
    "paths": [ ... ],
    "runAs": "0",
    "ownedBy": "472156272836608001",
    "createdAt": "2026-03-09T09:11:51Z",
    "createdBy": "472156272836608001",
    "updatedAt": "2026-03-09T09:25:23Z",
    "namespaceID": "409824987081211905",
    "canGrant": true,
    "canUpdateWorkflow": true,
    "canDeleteWorkflow": true,
    "canUndeleteWorkflow": true,
    "canExecuteWorkflow": true,
    "canManageWorkflowTriggers": true,
    "canManageWorkflowSessions": true
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/workflows/{workflowID}' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 列表工作流

### 请求

```
GET /automation/workflows/
```

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 否 | `""` | 搜索关键词 |
| `deleted` | int | 否 | `0` | 是否包含已删除（`0`=不包含, `1`=仅已删除, `2`=全部） |
| `disabled` | int | 否 | `0` | 过滤禁用状态（`0`=仅启用, `1`=全部, `2`=仅禁用） |
| `subWorkflow` | int | 否 | `1` | 过滤子工作流（`0`=仅主工作流, `1`=全部, `2`=仅子工作流） |
| `limit` | int | 否 | `100` | 每页返回数量 |
| `incTotal` | bool | 否 | `false` | 是否返回总数 |
| `pageCursor` | string | 否 | - | 分页游标（来自上一页 `nextPage`） |
| `sort` | string | 否 | - | 排序表达式，如 `coalesce(deletedAt,+updatedAt,+createdAt)+DESC` |

### 响应

```json
{
  "response": {
    "filter": {
      "workflowID": null,
      "namespaceID": "0",
      "handle": "",
      "query": "",
      "deleted": 0,
      "disabled": 0,
      "subWorkflow": 1,
      "sort": "coalesce(deletedAt,updatedAt,createdAt) DESC, id DESC",
      "limit": 100,
      "nextPage": "<cursor>",
      "incTotal": true,
      "total": 93
    },
    "set": [
      {
        "workflowID": "486201022694424577",
        "handle": "aaa",
        "meta": {
          "name": "aaa",
          "description": "aaa",
          "visual": null,
          "type": "Advanced",
          "formList": null,
          "businessType": null,
          "businessLabel": null,
          "results": null,
          "icon": null
        },
        "enabled": true,
        "trace": false,
        "keepSessions": 0,
        "scope": {},
        "steps": [],
        "paths": [],
        "runAs": "0",
        "ownedBy": "472156272836608001",
        "createdAt": "2026-03-09T09:11:51Z",
        "createdBy": "472156272836608001",
        "namespaceID": "409824987081211905",
        "canGrant": true,
        "canUpdateWorkflow": true,
        "canDeleteWorkflow": true,
        "canUndeleteWorkflow": true,
        "canExecuteWorkflow": true,
        "canManageWorkflowTriggers": true,
        "canManageWorkflowSessions": true
      }
    ]
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `workflowID` | string | 工作流唯一 ID |
| `handle` | string | 工作流唯一标识 |
| `meta` | object | 元数据（名称、描述、类型、图标等） |
| `enabled` | bool | 是否启用 |
| `trace` | bool | 是否开启追踪 |
| `keepSessions` | int | 保留会话数 |
| `scope` | object | 作用域变量 |
| `steps` | array | 步骤列表 |
| `paths` | array | 路径（步骤间连接）列表 |
| `runAs` | string | 运行身份用户 ID |
| `ownedBy` | string | 所有者用户 ID |
| `namespaceID` | string | 关联命名空间 ID |
| `createdAt` | string | 创建时间 (ISO 8601) |
| `createdBy` | string | 创建者用户 ID |

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/workflows/?query=&deleted=0&disabled=0&subWorkflow=1&limit=100&incTotal=true&sort=coalesce(deletedAt,+updatedAt,+createdAt)+DESC' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 更新工作流

### 请求

```
PUT /automation/workflows/{workflowID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `workflowID` | string | 工作流 ID |

### 请求体

```json
{
  "handle": "aaa",
  "meta": {
    "name": "aaa",
    "description": "aaa",
    "visual": null,
    "type": "Advanced",
    "formList": null,
    "businessType": "",
    "businessLabel": "",
    "results": "",
    "icon": ""
  },
  "enabled": true,
  "trace": false,
  "keepSessions": 0,
  "scope": {},
  "steps": [
    {
      "stepID": "4",
      "kind": "expressions",
      "ref": "",
      "customName": "",
      "defaultName": true,
      "results": [],
      "arguments": [
        {
          "target": "a",
          "expr": "100",
          "type": "Any"
        }
      ],
      "meta": {
        "label": "Define and mutate scope variables",
        "description": "",
        "visual": {
          "id": "4",
          "value": "Define and mutate scope variables",
          "defaultName": true,
          "xywh": [2664, 1976, 200, 80],
          "parent": "1"
        }
      }
    }
  ],
  "paths": [],
  "runAs": "0",
  "namespaceID": "409824987081211905",
  "ownedBy": "472156272836608001"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `handle` | string | 工作流唯一标识 |
| `meta` | object | 元数据（名称、描述、类型、可视化布局等） |
| `enabled` | bool | 是否启用 |
| `trace` | bool | 是否开启追踪 |
| `keepSessions` | int | 保留会话数 |
| `scope` | object | 作用域变量 |
| `steps` | array | 步骤列表 |
| `steps[].stepID` | string | 步骤 ID（工作流内唯一） |
| `steps[].kind` | string | 步骤类型（如 `expressions`、`function`、`gateway` 等） |
| `steps[].arguments` | array | 步骤参数列表 |
| `steps[].meta.visual` | object | 可视化位置信息（`xywh` 等） |
| `paths` | array | 路径（步骤间连接）列表 |
| `runAs` | string | 运行身份用户 ID |
| `namespaceID` | string | 关联命名空间 ID |
| `ownedBy` | string | 所有者用户 ID |

### 响应

成功时返回 HTTP 200，响应体为更新后的完整工作流对象：

```json
{
  "response": {
    "workflowID": "486201022694424577",
    "handle": "aaa",
    "meta": { ... },
    "enabled": true,
    "trace": false,
    "keepSessions": 0,
    "scope": {},
    "steps": [ ... ],
    "paths": [],
    "runAs": "0",
    "ownedBy": "472156272836608001",
    "createdAt": "...",
    "updatedAt": "...",
    "namespaceID": "409824987081211905"
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/workflows/{workflowID}' \
  -X 'PUT' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --data-raw '{
    "handle": "aaa",
    "meta": { ... },
    "enabled": true,
    "trace": false,
    "keepSessions": 0,
    "scope": {},
    "steps": [ ... ],
    "paths": [ ... ],
    "runAs": "0",
    "namespaceID": "409824987081211905",
    "ownedBy": "0"
  }' \
  --compressed --insecure
```

---

## 新增触发器 (Trigger)

> Trigger API 路径为 `/automation/triggers/`，与 Workflow 同属 `/automation/` 下。

### 请求

```
POST /automation/triggers/
```

### 请求体

```json
{
  "type": "2",
  "eventType": "afterUpdate",
  "resourceType": "compose:record",
  "enabled": true,
  "workflowID": "486201022694424577",
  "workflowStepID": "4",
  "meta": {
    "name": "Compose record - afterUpdate",
    "description": "",
    "visual": {
      "id": "3",
      "value": "Compose record - afterUpdate",
      "defaultName": true,
      "xywh": [2336, 1976, 200, 80],
      "parent": "1",
      "edges": [
        {
          "parentID": "3",
          "childID": "4",
          "meta": {
            "label": "",
            "description": "",
            "visual": {
              "id": "5",
              "value": null,
              "parent": "1",
              "points": null,
              "style": "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
            }
          }
        }
      ]
    }
  },
  "constraints": [
    {
      "name": "namespace.handle",
      "op": "=",
      "values": ["itsm"]
    },
    {
      "name": "module.handle",
      "op": "=",
      "values": ["Incident"]
    }
  ],
  "ownedBy": "472156272836608001"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 触发器类型编号（如 `"2"` 表示事件触发） |
| `eventType` | string | 是 | 事件类型，如 `afterUpdate`、`beforeCreate`、`afterCreate`、`beforeUpdate` 等 |
| `resourceType` | string | 是 | 资源类型，如 `compose:record`、`compose:module` 等 |
| `enabled` | bool | 否 | 是否启用 |
| `workflowID` | string | 是 | 关联的工作流 ID |
| `workflowStepID` | string | 是 | 触发后执行的起始步骤 ID |
| `meta` | object | 否 | 元数据（名称、描述、可视化信息） |
| `meta.visual` | object | 否 | 可视化布局信息（`xywh`、`edges` 等） |
| `constraints` | array | 否 | 约束条件列表 |
| `constraints[].name` | string | - | 约束字段名（如 `namespace.handle`、`module.handle`） |
| `constraints[].op` | string | - | 操作符（如 `=`） |
| `constraints[].values` | array | - | 匹配值列表 |
| `ownedBy` | string | 否 | 所有者用户 ID |

### 响应

成功时返回 HTTP 200，响应体为创建后的完整触发器对象：

```json
{
  "response": {
    "triggerID": "486300000000000001",
    "type": "2",
    "eventType": "afterUpdate",
    "resourceType": "compose:record",
    "enabled": true,
    "workflowID": "486201022694424577",
    "workflowStepID": "4",
    "meta": { ... },
    "constraints": [ ... ],
    "ownedBy": "472156272836608001",
    "createdAt": "2026-03-09T09:30:00Z",
    "createdBy": "472156272836608001"
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/triggers/' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --data-raw '{
    "type": "2",
    "eventType": "afterUpdate",
    "resourceType": "compose:record",
    "enabled": true,
    "workflowID": "{workflowID}",
    "workflowStepID": "4",
    "meta": { ... },
    "constraints": [ ... ],
    "ownedBy": "0"
  }' \
  --compressed --insecure
```

---

## 列表触发器

### 请求

```
GET /automation/triggers/
```

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `workflowID` | string | 否 | - | 按工作流 ID 过滤 |
| `eventType` | string | 否 | `""` | 按事件类型过滤 |
| `resourceType` | string | 否 | `""` | 按资源类型过滤 |
| `deleted` | int | 否 | `0` | 是否包含已删除 |
| `disabled` | int | 否 | `1` | 是否包含已禁用（`1`=包含） |

### 响应

```json
{
  "response": {
    "filter": {
      "triggerID": null,
      "workflowID": ["486201022694424577"],
      "eventType": "",
      "resourceType": "",
      "deleted": 0,
      "disabled": 1
    },
    "set": [
      {
        "triggerID": "486201022713757697",
        "enabled": true,
        "transaction": false,
        "async": false,
        "workflowID": "486201022694424577",
        "stepID": "4",
        "resourceType": "compose:record",
        "eventType": "afterUpdate",
        "constraints": [
          {
            "name": "namespace.handle",
            "op": "=",
            "values": ["itsm"],
            "condition": null
          },
          {
            "name": "module.handle",
            "op": "=",
            "values": ["Incident"],
            "condition": null
          }
        ],
        "input": {},
        "type": 0,
        "meta": {
          "description": "",
          "visual": { ... },
          "namespace": "",
          "moduleID": "",
          "namespaceID": "",
          "endTimeCondition": { ... },
          "startTimeCondition": { ... },
          "startTime": "0001-01-01T00:00:00Z",
          "endTime": "0001-01-01T00:00:00Z",
          "timeNode": "",
          "timeRepeat": "",
          "days": "",
          "hours": "",
          "minutes": "",
          "condition": null
        },
        "weight": 0,
        "ownedBy": "472156272836608001",
        "createdAt": "2026-03-09T09:17:54Z",
        "createdBy": "472156272836608001"
      }
    ]
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `triggerID` | string | 触发器唯一 ID |
| `enabled` | bool | 是否启用 |
| `transaction` | bool | 是否在事务中执行 |
| `async` | bool | 是否异步执行 |
| `workflowID` | string | 关联的工作流 ID |
| `stepID` | string | 触发后执行的起始步骤 ID（对应新增时的 `workflowStepID`） |
| `resourceType` | string | 资源类型（如 `compose:record`） |
| `eventType` | string | 事件类型（如 `afterUpdate`） |
| `constraints` | array | 约束条件列表 |
| `input` | object | 输入参数映射 |
| `type` | int | 触发器类型编号（列表返回为 int，新增时传 string） |
| `meta` | object | 元数据（描述、可视化、时间配置等） |
| `weight` | int | 排序权重 |
| `ownedBy` | string | 所有者用户 ID |

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/triggers/?workflowID={workflowID}&disabled=1' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 更新触发器

### 请求

```
PUT /automation/triggers/{triggerID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `triggerID` | string | 触发器 ID |

### 请求体

```json
{
  "type": "2",
  "eventType": "afterUpdate",
  "resourceType": "compose:record",
  "enabled": false,
  "transaction": false,
  "async": false,
  "weight": 0,
  "workflowID": "486201022694424577",
  "workflowStepID": "4",
  "input": {},
  "meta": {
    "description": "",
    "visual": {
      "id": "3",
      "value": "Compose record - afterUpdate",
      "defaultName": true,
      "xywh": [2336, 1976, 200, 80],
      "parent": "1",
      "edges": [
        {
          "childID": "4",
          "parentID": "3",
          "meta": {
            "label": "",
            "description": "",
            "visual": {
              "id": "5",
              "value": null,
              "parent": "1",
              "points": [],
              "style": "exitX=1;exitY=0.5;..."
            }
          }
        }
      ]
    },
    "namespace": "",
    "moduleID": "",
    "namespaceID": "",
    "endTimeCondition": { ... },
    "startTimeCondition": { ... },
    "startTime": "0001-01-01T00:00:00Z",
    "endTime": "0001-01-01T00:00:00Z",
    "timeNode": "",
    "timeRepeat": "",
    "days": "",
    "hours": "",
    "minutes": "",
    "condition": null,
    "name": "Compose record - afterUpdate"
  },
  "constraints": [
    {
      "name": "namespace.handle",
      "op": "=",
      "values": ["itsm"],
      "condition": null
    },
    {
      "name": "module.handle",
      "op": "=",
      "values": ["Incident"],
      "condition": null
    }
  ],
  "ownedBy": "472156272836608001"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 触发器类型编号 |
| `eventType` | string | 事件类型 |
| `resourceType` | string | 资源类型 |
| `enabled` | bool | 是否启用 |
| `transaction` | bool | 是否在事务中执行 |
| `async` | bool | 是否异步执行 |
| `weight` | int | 排序权重 |
| `workflowID` | string | 关联的工作流 ID |
| `workflowStepID` | string | 触发后执行的起始步骤 ID |
| `input` | object | 输入参数映射 |
| `meta` | object | 元数据（描述、可视化、时间配置等） |
| `meta.name` | string | 触发器显示名称（更新时在 `meta` 内） |
| `constraints` | array | 约束条件列表 |
| `ownedBy` | string | 所有者用户 ID |

### 响应

成功时返回 HTTP 200，响应体为更新后的完整触发器对象：

```json
{
  "response": {
    "triggerID": "486201022713757697",
    "enabled": false,
    "transaction": false,
    "async": false,
    "workflowID": "486201022694424577",
    "stepID": "4",
    "resourceType": "compose:record",
    "eventType": "afterUpdate",
    "constraints": [ ... ],
    "input": {},
    "type": 0,
    "meta": { ... },
    "weight": 0,
    "ownedBy": "472156272836608001",
    "updatedAt": "...",
    "updatedBy": "..."
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/triggers/{triggerID}' \
  -X 'PUT' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --data-raw '{
    "type": "2",
    "eventType": "afterUpdate",
    "resourceType": "compose:record",
    "enabled": false,
    "transaction": false,
    "async": false,
    "weight": 0,
    "workflowID": "{workflowID}",
    "workflowStepID": "4",
    "input": {},
    "meta": { ... },
    "constraints": [ ... ],
    "ownedBy": "0"
  }' \
  --compressed --insecure
```

---

## 删除触发器

### 请求

```
DELETE /automation/triggers/{triggerID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `triggerID` | string | 要删除的触发器 ID |

### 响应

成功时返回 HTTP 200，响应体为：

```json
{
  "response": true
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/triggers/{triggerID}' \
  -X 'DELETE' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 删除工作流

### 请求

```
DELETE /automation/workflows/{workflowID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `workflowID` | string | 要删除的工作流 ID |

### 响应

成功时返回 HTTP 200，响应体为：

```json
{
  "response": true
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/automation/workflows/{workflowID}' \
  -X 'DELETE' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 注意事项

1. **Workflow API 基础路径为 `/automation/workflows/`**，不像 Module/Page/Layout 那样在 `/compose/namespace/{namespaceID}/` 下。
2. **`namespaceID`** 在请求体中传递（不在 URL 路径中），`"0"` 表示全局工作流。
3. **`steps` 和 `paths`** 定义工作流的逻辑图，新增时可为空数组，后续通过更新接口填充。
4. **`handle`** 必须全局唯一。
5. **列表接口** 返回的每个工作流对象包含完整的 `steps` 和 `paths`，用于脚本中按 `handle` 查找 `workflowID`。
6. **`meta` 字段** 包含 `name`、`description`、`type`、`visual`（可视化布局）、`formList`、`businessType`、`businessLabel`、`results`、`icon` 等子字段。
7. **Trigger API 基础路径为 `/automation/triggers/`**，与 Workflow 平行，`workflowID` 在请求体/查询参数中关联。
8. **`constraints`** 用于限定触发条件的作用范围（如特定命名空间、特定模块），`_showDetails` 字段为前端 UI 用，API 提交时可忽略。
9. **Trigger `stepID`** 在列表响应中叫 `stepID`，新增时请求体中叫 `workflowStepID`，注意区别。
10. **Trigger `type`** 在列表响应中为 `int`（如 `0`），新增时请求体中为 `string`（如 `"2"`），注意类型差异。
11. **删除接口** Workflow 和 Trigger 均使用 `DELETE` 方法，成功返回 `{"response": true}`。
12. **请求头必须包含 env.json 中的 headers**：`baseUrl` 和 `headers`（含 `X-SS-EMAIL`、`Content-Type`）均从 `env.json → environments.{env}.tenants.{tenant}` 读取。
