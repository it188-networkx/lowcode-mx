# Module API 接口文档

## 列表模块

### 请求

```
GET /compose/namespace/{namespaceID}/module/
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 否 | `""` | 搜索关键词（模糊匹配模块名称/handle） |
| `limit` | int | 否 | `100` | 每页返回数量 |
| `incTotal` | bool | 否 | `false` | 是否在响应中包含总数 (`filter.total`) |
| `sort` | string | 否 | `"name ASC"` | 排序字段与方向，如 `name ASC`、`createdAt DESC` |
| `pageCursor` | string | 否 | - | 分页游标（来自上一次响应的 `filter.nextPage`） |
| `handle` | string | 否 | `""` | 按 handle 精确过滤 |
| `name` | string | 否 | `""` | 按 name 精确过滤 |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | 操作人邮箱（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 响应

```jsonc
{
  "response": {
    "filter": {
      "moduleID": null,
      "namespaceID": "409824987081211905",
      "query": "",
      "handle": "",
      "name": "",
      "deleted": 0,
      "sort": "name, id",
      "limit": 100,
      "nextPage": "eyJ...",       // 下一页游标（无更多数据时为空）
      "incTotal": true,
      "total": 49                  // 仅在 incTotal=true 时出现
    },
    "set": [
      {
        // ── 模块对象（结构同更新接口的请求体，额外包含以下字段） ──
        "moduleID": "409824987081932801",
        "namespaceID": "409824987081211905",
        "name": "AssignRule",
        "handle": "AssignRule",
        "type": "",
        "isBlockDataTree": false,
        "meta": {},
        "config": { /* ... */ },
        "systemModuleField": [ /* 9 个系统字段 */ ],
        "fields": [
          {
            "fieldID": "409824987070136321",
            "namspaceID": "409824987081211905",   // 注意：API 返回拼写为 namspaceID（缺少 e）
            "moduleID": "409824987081932801",
            "kind": "Bool",
            "name": "enabledFlag",
            "label": "状态",
            "options": { /* ... */ },
            "config": { /* ... */ },
            "isRequired": false,
            "isMulti": false,
            "isName": false,
            "defaultValue": [],
            "expressions": {},
            "serial": 0,
            "serialUpdate": 0,
            "createdAt": "2024-09-28T06:09:30Z",
            "updatedAt": "2026-03-02T19:10:33Z",
            "canReadRecordValue": true,
            "canUpdateRecordValue": true
          }
          // ... 更多字段
        ],
        "createdAt": "2024-09-28T06:09:30Z",
        "updatedAt": "2026-03-02T19:10:33Z",
        "canGrant": true,
        "canUpdateModule": true,
        "canDeleteModule": true,
        "canCreateRecord": true,
        "canCreateOwnedRecord": true
      }
      // ... 更多模块
    ]
  }
}
```

### 分页说明

- 首次请求不传 `pageCursor`，通过 `limit` 控制每页数量。
- 响应中 `filter.nextPage` 为下一页游标；若为空字符串或不存在，则表示已是最后一页。
- 翻页时将 `filter.nextPage` 值作为 `pageCursor` 参数传递即可。
- 如需获取全部数据，循环请求直到 `nextPage` 为空。

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/module/?query=&limit=100&incTotal=true&sort=name+ASC' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 查询模块详情

### 请求

```
GET /compose/namespace/{namespaceID}/module/{moduleID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `moduleID` | string | 模块 ID |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | 操作人邮箱（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 响应

成功返回单个模块对象（**注意**：与列表接口不同，详情接口的 `response` 直接是模块对象，无 `filter`/`set` 包装）。

```jsonc
{
  "response": {
    "moduleID": "409824987082063873",
    "namespaceID": "409824987081211905",
    "name": "事件管理",
    "handle": "Incident",
    "type": "",
    "isBlockDataTree": false,
    "meta": {},
    "config": { /* ... */ },
    "systemModuleField": [ /* 9 个系统字段 */ ],
    "fields": [
      {
        "fieldID": "...",
        "namspaceID": "...",
        "moduleID": "...",
        "kind": "String",
        "name": "...",
        "label": "...",
        "options": { /* ... */ },
        "config": { /* ... */ },
        "isRequired": false,
        "isMulti": false,
        "isName": false,
        "defaultValue": [],
        "expressions": {},
        "serial": 0,
        "serialUpdate": 0,
        "createdAt": "...",
        "updatedAt": "...",
        "canReadRecordValue": true,
        "canUpdateRecordValue": true
      }
      // ... 更多字段
    ],
    "createdAt": "2024-09-28T06:09:30Z",
    "updatedAt": "2026-03-06T10:04:14Z",
    "canGrant": true,
    "canUpdateModule": true,
    "canDeleteModule": true,
    "canCreateRecord": true,
    "canCreateOwnedRecord": true
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/module/{moduleID}' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 新增模块

### 请求

```
POST /compose/namespace/{namespaceID}/module/
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |

### 请求体

```json
{
  "name": "aaaa",
  "handle": "aaaa",
  "type": "",
  "isBlockDataTree": false,
  "systemModuleField": [ ... ],
  "config": {
    "dal": {
      "connectionID": "470129660978593793",
      "ident": "{{namespace}}{{module}}",
      "systemFieldEncoding": { ... }
    },
    "privacy": {
      "sensitivityLevelID": "0",
      "usageDisclosure": ""
    },
    "discovery": { ... },
    "recordRevisions": {
      "enabled": false,
      "ident": ""
    },
    "recordDeDup": {
      "rules": []
    }
  },
  "meta": {},
  "fields": [
    {
      "fieldID": "0",
      "name": "Sample",
      "kind": "String",
      "label": "Sample",
      "width": 130,
      "defaultValue": [],
      "maxLength": 0,
      "isRequired": false,
      "isMulti": false,
      "isName": false,
      "isSystem": false,
      "isSortable": true,
      "isFilterable": true,
      "options": { ... },
      "expressions": {},
      "config": {
        "dal": {
          "encodingStrategy": { "plain": {} }
        },
        "privacy": { ... },
        "recordRevisions": { "enabled": false }
      }
    }
  ],
  "labels": {}
}
```

### 关键字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 模块显示名称 |
| `handle` | string | 是 | 模块唯一标识（namespace 内唯一） |
| `type` | string | 否 | 模块类型 |
| `isBlockDataTree` | bool | 否 | 是否为块数据树 |
| `systemModuleField` | array | 否 | 系统字段列表（recordID、ownedBy、createdBy 等） |
| `config` | object | 否 | 模块配置 |
| `config.dal.connectionID` | string | 否 | DAL 连接 ID |
| `config.dal.ident` | string | 否 | 数据表标识模板（`{{namespace}}{{module}}`） |
| `meta` | object | 否 | 元数据 |
| `fields` | array | 否 | 自定义字段列表 |
| `fields[].fieldID` | string | - | 新增时为 `"0"`，API 会自动分配 |
| `fields[].name` | string | - | 字段名（module 内唯一） |
| `fields[].kind` | string | - | 字段类型（String、Number、DateTime 等） |
| `fields[].label` | string | - | 字段显示标签 |
| `labels` | object | 否 | 标签键值对 |

### 响应

成功时返回 HTTP 200，响应体为创建后的完整模块对象（含分配的 `moduleID` 和 `fieldID`）：

```json
{
  "response": {
    "moduleID": "486400000000000001",
    "namespaceID": "485227732855160833",
    "name": "aaaa",
    "handle": "aaaa",
    "fields": [
      {
        "fieldID": "486400000000000002",
        "name": "Sample",
        "kind": "String",
        ...
      }
    ],
    "config": { ... },
    "meta": {},
    "labels": {},
    "createdAt": "...",
    "createdBy": "..."
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/module/' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --data-raw '{
    "name": "aaaa",
    "handle": "aaaa",
    "type": "",
    "isBlockDataTree": false,
    "systemModuleField": [ ... ],
    "config": { ... },
    "meta": {},
    "fields": [ ... ],
    "labels": {}
  }' \
  --compressed --insecure
```

---

## 更新模块

### 请求

```
POST /compose/namespace/{namespaceID}/module/{moduleID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `moduleID` | string | 模块 ID |

### 请求头

| Header | 必填 | 来源 | 说明 |
|--------|------|------|------|
| `Authorization` | 是 | 登录获取 | Bearer Token |
| `Content-Type` | 是 | `env.json` → `environments.{env}.tenants.{tenant}.headers` | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | `env.json` → `environments.{env}.tenants.{tenant}.headers` | 操作人邮箱，如 `lyh@it188.com` |
| `X-NAMESPACE-ID` | 是 | 手动指定 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 手动指定 | 语言，如 `en` |

> **headers 读取规则**：调用接口时，必须从 `configuration/env.json` 中读取对应环境和租户的 `headers` 配置，合并到请求头中。
> 路径：`env.json → environments.{环境名}.tenants.{租户名}.headers`
>
> 示例（dev.dms / mx）：
> ```json
> {
>   "X-SS-EMAIL": "lyh@it188.com",
>   "Content-Type": "application/json; charset=utf-8"
> }
> ```

### 请求体（JSON）

```jsonc
{
  // ── 模块基本信息 ──
  "name": "Group",                    // 模块名称
  "handle": "Group",                  // 模块标识（唯一）
  "type": "Group",                    // 模块类型："" | "Tree" | "Group"
  "isBlockDataTree": false,           // 是否为树形数据（仅 Tree 类型为 true）
  "meta": {},                         // 元数据
  "labels": {},                       // 标签

  // ── 系统字段（9 个固定字段） ──
  "systemModuleField": [
    // 每个系统字段结构（fieldID 固定为 "0"）
    {
      "fieldID": "0",
      "name": "recordID",             // 字段名（固定值）
      "kind": "String",               // 字段类型
      "label": "记录ID",              // 显示名
      "width": 130,
      "defaultValue": [],
      "maxLength": 0,
      "isRequired": false,
      "disabled": false,
      "customRequired": false,
      "isMulti": false,
      "isName": false,
      "isSystem": true,               // 系统字段固定 true
      "isSortable": false,
      "isFilterable": true,
      "options": { /* 字段选项，因 kind 不同而异 */ },
      "expressions": {},
      "config": {
        "dal": { "encodingStrategy": null },
        "privacy": { "sensitivityLevelID": "0", "usageDisclosure": "" },
        "recordRevisions": { "enabled": false }
      },
      "canUpdateRecordValue": true,
      "canReadRecordValue": true
    }
    // ... 共 9 个系统字段：
    // recordID (String), ownedBy (User), createdBy (User),
    // createdAt (DateTime), updatedBy (User), updatedAt (DateTime),
    // revision (Number), deletedBy (User), deletedAt (DateTime)
  ],

  // ── 自定义字段列表 ──
  "fields": [
    {
      "fieldID": "485220788736360449",   // 字段 ID（Sonyflake 生成）
      "name": "name",                    // 字段名
      "kind": "String",                  // 字段类型（见下方 Kind 速查）
      "label": "名称",                   // 显示名
      "width": 130,                      // 列宽
      "defaultValue": [],                // 默认值数组，格式: [{"name": "", "value": "xxx"}]
      "maxLength": 0,                    // 最大长度（0 = 不限）
      "isRequired": false,               // 是否必填
      "disabled": false,                 // 是否禁用
      "customRequired": false,           // 页面级自定义必填
      "isMulti": false,                  // 是否多值
      "isName": false,                   // 是否作为记录名称
      "isSystem": false,                 // 自定义字段固定 false
      "isSortable": true,                // 是否可排序
      "isFilterable": true,              // 是否可筛选
      "options": {
        // 通用选项
        "description": { "view": "" },
        "hint": { "view": "", "width": "150", "type": "left" },
        "rule": {
          "digit": "", "start": "", "resetFrequency": "",
          "fixedChar": "", "dateFormat": "", "select": "", "timeZone": ""
        },
        "clearCopy": false,
        "multiDelimiter": "\n",

        // String 特有
        "multiLine": false,
        "useRichTextEditor": false,
        "isPassword": false,
        "maxLength": ""

        // Select 特有
        // "options": [{"value": "xxx", "text": "xxx"}],
        // "selectType": "default",
        // "isUniqueMultiValue": false

        // Record 特有
        // "namespaceID": "0",            // 关联模块所在命名空间（"0" = 当前命名空间）
        // "moduleID": "485220445621059585", // 关联的目标模块 ID
        // "labelField": "name",          // 显示的字段名
        // "queryFields": [],             // 搜索字段
        // "selectType": "default",
        // "prefilter": "",               // 预筛选表达式
        // "presort": "createdAt DESC",   // 预排序
        // "isCheckbox": false,
        // "notLink": false,
        // "multipleAll": false,
        // "multipleMax": 100,

        // Bool 特有
        // "trueLabel": "Active",
        // "falseLabel": "Inactive",
        // "switch": false
      },
      "expressions": { "customValidators": null },
      "config": {
        "dal": {
          "encodingStrategy": { "plain": {} }
          // 多值字段使用: { "json": { "ident": "字段name" } }
        },
        "privacy": { "sensitivityLevelID": "0", "usageDisclosure": "" },
        "recordRevisions": { "enabled": false }
      },
      "canUpdateRecordValue": true,
      "canReadRecordValue": true
    }
    // ... 更多自定义字段
  ],

  // ── 模块配置 ──
  "config": {
    "dal": {
      "connectionID": "470129660978593793",  // 数据库连接 ID（"0" = 默认连接）
      "ident": "{{namespace}}{{module}}",    // 数据表标识模板
      "systemFieldEncoding": {               // 系统字段编码（通常全为 null）
        "id": null, "revision": null, "moduleID": null,
        "namespaceID": null, "ownedBy": null,
        "createdBy": null, "createdAt": null,
        "updatedBy": null, "updatedAt": null,
        "deletedBy": null, "deletedAt": null, "meta": null
      },
      "constraints": null
    },
    "privacy": { "sensitivityLevelID": "0", "usageDisclosure": "" },
    "discovery": {
      "public":    { "result": [{ "lang": "", "fields": [] }] },
      "private":   { "result": [{ "lang": "", "fields": [] }] },
      "protected": { "result": [{ "lang": "", "fields": [] }] }
    },
    "recordRevisions": { "enabled": false, "ident": "" },
    "recordDeDup": { "rules": [] },
    "index": null
  }
}
```

### 响应

成功返回更新后的完整模块 JSON 对象（结构同请求体，额外包含时间戳字段）。

---

## 字段 Kind 速查

| Kind | 说明 | encodingStrategy（单值） | encodingStrategy（多值） |
|------|------|-------------------------|-------------------------|
| `String` | 字符串 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Number` | 数字 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Bool` | 布尔 | `{ "plain": {} }` | — |
| `DateTime` | 日期时间 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Email` | 邮箱 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Select` | 下拉选择 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Record` | 关联记录 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `User` | 系统用户 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `File` | 文件附件 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Url` | URL | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |
| `Geometry` | 地理坐标 | `null` | — |
| `BigInt` | 大整数 | `{ "plain": {} }` | `{ "json": { "ident": "<name>" } }` |

---

## curl 示例

```bash
# baseUrl 来自 env.json → environments.dev.dms.tenants.mx.baseUrl
# headers 来自 env.json → environments.dev.dms.tenants.mx.headers
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/module/{moduleID}' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  --data-raw '{
    "name": "Group",
    "handle": "Group",
    "type": "Group",
    "isBlockDataTree": false,
    "systemModuleField": [ ... ],
    "fields": [ ... ],
    "config": { ... },
    "meta": {},
    "labels": {}
  }' \
  --compressed --insecure
```

---

## 删除模块

### 请求

```
DELETE /compose/namespace/{namespaceID}/module/{moduleID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `moduleID` | string | 模块 ID |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `X-SS-EMAIL` | 是 | 操作人邮箱（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 请求体

无（DELETE 请求不需要请求体）。

### 响应

成功返回 `true`。

```jsonc
{
  "response": true
}
```

### curl 示例

```bash
curl -X DELETE 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/module/{moduleID}' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 注意事项

1. **moduleID 在 URL 路径中传递**，请求体中不包含 `moduleID`。
2. **请求头必须包含 env.json 中的 headers**：`baseUrl` 和 `headers`（含 `X-SS-EMAIL`、`Content-Type`）均从 `env.json → environments.{env}.tenants.{tenant}` 读取。
3. **systemModuleField** 的 9 个系统字段必须完整传递，`fieldID` 固定为 `"0"`。
4. **fields** 中的 `fieldID` 是 Sonyflake 生成的唯一 ID，更新时必须保持不变。
5. **encodingStrategy** 规则：单值用 `{ "plain": {} }`，多值用 `{ "json": { "ident": "<字段name>" } }`，系统字段用 `null`。
6. **Record 类型字段**的 `options.namespaceID` 为 `"0"` 表示当前命名空间，非零值表示跨命名空间引用。
