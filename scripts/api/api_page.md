# Page API 接口文档

## 列表页面

### 请求

```
GET /compose/namespace/{namespaceID}/page/
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 否 | `""` | 搜索关键词 |
| `limit` | int | 否 | `100` | 每页返回数量 |
| `incTotal` | bool | 否 | `false` | 是否在响应中包含总数 (`filter.total`) |
| `sort` | string | 否 | `"weight ASC"` | 排序字段与方向，如 `weight ASC`、`title ASC` |
| `pageCursor` | string | 否 | - | 分页游标（来自上一次响应的 `filter.nextPage`） |
| `handle` | string | 否 | `""` | 按 handle 精确过滤 |
| `title` | string | 否 | `""` | 按 title 精确过滤 |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | 操作人邮箱（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

> **headers 读取规则**：同 Module API，从 `env.json → environments.{env}.tenants.{tenant}` 读取 `baseUrl` 和 `headers`。

### 响应

```jsonc
{
  "response": {
    "filter": {
      "namespaceID": 409824987081211905,
      "pageID": null,
      "handle": "",
      "title": "",
      "query": "",
      "deleted": 0,
      "sort": "weight, id",
      "limit": 100,
      "nextPage": "eyJ...",       // 下一页游标（无更多数据时为空）
      "incTotal": true,
      "total": 50                  // 仅在 incTotal=true 时出现
    },
    "set": [
      {
        "pageID": "484224679515652097",
        "selfID": "484225182798512129",      // 父页面 ID（"0" 表示顶级页面）
        "namespaceID": "409824987081211905",
        "moduleID": "484224679364657153",    // 关联的模块 ID（"0" 表示无关联）
        "handle": "",
        "config": { /* 页面配置 */ },
        "blocks": [ /* 页面块列表 */ ],
        "meta": { /* 元数据 */ },
        "visible": false,                    // 是否在导航中可见
        "weight": 0,                         // 排序权重
        "createdAt": "2026-02-24T03:20:28Z",
        "updatedAt": "2026-03-02T19:10:53Z",
        "title": "模块记录页面 \"ceshiAI\"",
        "description": "",
        "canGrant": true,
        "canUpdatePage": true,
        "canDeletePage": true
      }
      // ... 更多页面
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
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/?sort=weight+ASC' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 查询页面详情

### 请求

```
GET /compose/namespace/{namespaceID}/page/{pageID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 页面 ID |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | 操作人邮箱（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 响应

成功返回单个页面对象（`response` 直接是页面对象，无 `filter`/`set` 包装）。

```jsonc
{
  "response": {
    "pageID": "485611457202225153",
    "selfID": "0",                           // 父页面 ID（"0" 表示顶级页面）
    "namespaceID": "409824987081211905",
    "moduleID": "0",                         // 关联的模块 ID（"0" 表示无关联）
    "handle": "",
    "config": { /* 页面配置 */ },
    "blocks": [ /* 页面块列表 */ ],
    "meta": { /* 元数据 */ },
    "visible": true,
    "weight": 40,
    "createdAt": "2026-03-05T02:03:47Z",
    "updatedAt": "2026-03-06T07:41:55Z",
    "title": "SLA Task List",
    "description": "",
    "canGrant": true,
    "canUpdatePage": true,
    "canDeletePage": true
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 新增页面

### 请求

```
POST /compose/namespace/{namespaceID}/page/
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |

### 请求体

```json
{
  "selfID": "0",
  "moduleID": "0",
  "title": "aaaa",
  "handle": "",
  "description": "",
  "weight": 6,
  "labels": {},
  "visible": true,
  "blocks": [],
  "config": {
    "navItem": {
      "icon": { "type": "", "src": "" },
      "expanded": false
    }
  },
  "meta": {}
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `selfID` | string | 否 | 父页面 ID，`"0"` 表示顶级页面 |
| `moduleID` | string | 否 | 关联的模块 ID，`"0"` 表示不关联 |
| `title` | string | 是 | 页面标题 |
| `handle` | string | 否 | 页面唯一标识 |
| `description` | string | 否 | 页面描述 |
| `weight` | int | 否 | 排序权重 |
| `labels` | object | 否 | 标签键值对 |
| `visible` | bool | 否 | 是否在导航中可见 |
| `blocks` | array | 否 | 块列表（新增时可为空，后续通过更新填充） |
| `config` | object | 否 | 页面配置（导航图标、展开状态等） |
| `meta` | object | 否 | 元数据 |

### 响应

成功时返回 HTTP 200，响应体为创建后的完整页面对象（含分配的 `pageID`）：

```json
{
  "response": {
    "pageID": "486400000000000001",
    "namespaceID": "485227732855160833",
    "selfID": "0",
    "moduleID": "0",
    "title": "aaaa",
    "handle": "",
    "description": "",
    "weight": 6,
    "labels": {},
    "visible": true,
    "blocks": [],
    "config": { ... },
    "meta": {},
    "createdAt": "...",
    "createdBy": "..."
  }
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --data-raw '{
    "selfID": "0",
    "moduleID": "0",
    "title": "aaaa",
    "handle": "",
    "description": "",
    "weight": 6,
    "labels": {},
    "visible": true,
    "blocks": [],
    "config": { ... },
    "meta": {}
  }' \
  --compressed --insecure
```

---

## 更新页面

### 请求

```
POST /compose/namespace/{namespaceID}/page/{pageID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 页面 ID |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json` |
| `X-SS-EMAIL` | 是 | 操作人邮箱（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 请求体（JSON）

```jsonc
{
  // ── 页面基本信息 ──
  "selfID": "0",                         // 父页面 ID（"0" 表示顶级页面）
  "moduleID": "0",                       // 关联的模块 ID（"0" 表示无关联）
  "title": "SLA Task List",              // 页面标题
  "handle": "",                          // 页面标识（唯一，可为空）
  "description": "",                     // 页面描述
  "weight": 40,                          // 排序权重
  "labels": {},                          // 标签
  "visible": true,                       // 是否在导航中可见

  // ── 页面块列表 ──
  "blocks": [
    {
      "blockID": "1",                    // 块 ID（页面内唯一）
      "kind": "RecordSlaList",           // 块类型
      "title": "",                       // 块标题
      "description": "",                 // 块描述
      "xywh": [0, 0, 48, 81],           // 位置和大小 [x, y, width, height]
      "options": {
        "moduleID": "...",               // 关联模块 ID
        "prefilter": "...",              // 预筛选表达式
        "presort": "createdAt DESC",     // 预排序
        "fields": [ /* 字段配置列表 */ ],
        // ... 更多块选项（因 kind 不同而异）
      },
      "meta": {
        "hidden": false,
        "tempID": "tempID-xxx"
      },
      "visible": {
        "visibleBlock": true,
        "editableBlock": true,
        "recordVisible": "",
        "visibleParams": { "actionID": "1", "params": {} },
        "editableParams": { "actionID": "2", "params": {} }
      },
      "style": {
        "variants": { "headerText": "dark" },
        "wrap": { "kind": "card" },
        "border": { "enabled": false }
      }
    }
    // ... 更多块
  ],

  // ── 页面配置 ──
  "config": {
    "navItem": {
      "icon": { "type": "", "src": "" },
      "expanded": false
    }
  },

  // ── 元数据 ──
  "meta": {
    "allowPersonalLayouts": false,
    "newTab": false,
    "newTabLink": "",
    "btnVisibleKey": "",
    "isToEdit": false,
    "localPageID": "",
    "localTab": false,
    "isClick": true
  },

  // ── 更新时间戳（可选） ──
  "updatedAt": "2026-03-06T07:41:55.000Z"
}
```

### 响应

成功返回更新后的完整页面 JSON 对象（结构同详情接口响应）。

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --data-raw '{
    "selfID": "0",
    "moduleID": "0",
    "title": "SLA Task List",
    "handle": "",
    "description": "",
    "weight": 40,
    "labels": {},
    "visible": true,
    "blocks": [ ... ],
    "config": { ... },
    "meta": { ... },
    "updatedAt": "2026-03-06T07:41:55.000Z"
  }' \
  --compressed --insecure
```

---

## 删除页面

### 请求

```
DELETE /compose/namespace/{namespaceID}/page/{pageID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 要删除的页面 ID |

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `strategy` | string | 否 | - | 删除策略，如 `rebase`（将子页面提升到被删页面的父级） |

### 响应

成功时返回 HTTP 200，响应体为：

```json
{
  "response": true
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}?strategy=rebase' \
  -X 'DELETE' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 注意事项

1. **pageID 在 URL 路径中传递**，请求体中不包含 `pageID`。
2. **请求头必须包含 env.json 中的 headers**：`baseUrl` 和 `headers`（含 `X-SS-EMAIL`、`Content-Type`）均从 `env.json → environments.{env}.tenants.{tenant}` 读取。
3. **blocks** 中的 `blockID` 是页面内唯一标识，更新时必须保持不变。
4. **blocks[].xywh** 为 `[x, y, width, height]` 格式的位置/大小数组。
5. **blocks[].options** 因块的 `kind` 不同而差异较大，详见 block 文档。
6. **updatedAt** 可选，用于乐观并发控制。
7. **删除接口** 使用 `DELETE` 方法，`strategy=rebase` 会将子页面提升到被删页面的父级，成功返回 `{"response": true}`。
