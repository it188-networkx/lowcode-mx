# Page Layout API 接口文档

## 列表布局

### 请求

```
GET /compose/namespace/{namespaceID}/page-layout
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
| `sort` | string | 否 | `"weight ASC"` | 排序字段与方向，如 `weight ASC` |
| `pageCursor` | string | 否 | - | 分页游标（来自上一次响应的 `filter.nextPage`） |
| `handle` | string | 否 | `""` | 按 handle 精确过滤 |
| `name` | string | 否 | `""` | 按 name 精确过滤 |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `Authorization` | 是 | Bearer Token（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

> **headers 读取规则**：同 Module API，从 `env.json → environments.{env}.tenants.{tenant}` 读取 `baseUrl` 和 `headers`。

### 响应

```jsonc
{
  "response": {
    "filter": {
      "pageLayoutID": null,
      "namespaceID": "409824987081211905",
      "handle": "",
      "name": "",
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
        "pageLayoutID": "410114147129425921",
        "namespaceID": "409824987081211905",
        "moduleID": "409824987081736193",    // 关联的模块 ID
        "pageID": "410114147113107457",      // 所属页面 ID
        "parentID": "0",                     // 父布局 ID（"0" 表示顶级）
        "handle": "primary",
        "primary": false,                    // 是否为主布局
        "weight": 0,                         // 排序权重
        "meta": { /* 元数据，含 title 等 */ },
        "config": { /* 布局配置 */ },
        "blocks": [ /* 布局块列表 */ ],
        "ownedBy": "0",
        "createdAt": "2024-09-30T06:47:24Z",
        "updatedAt": "2026-03-02T19:12:17Z"
      }
      // ... 更多布局
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
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page-layout?sort=weight+ASC' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 按页面列表布局

### 请求

```
GET /compose/namespace/{namespaceID}/page/{pageID}/layout/
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 页面 ID |

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `sort` | string | 否 | `"weight ASC"` | 排序字段与方向 |
| `limit` | int | 否 | `100` | 每页返回数量 |
| `pageCursor` | string | 否 | - | 分页游标 |

### 请求头

同列表布局接口。

### 响应

```jsonc
{
  "response": {
    "filter": {
      "pageLayoutID": null,
      "namespaceID": "409824987081211905",
      "pageID": "485611457202225153",    // 注意：filter 中包含 pageID
      "handle": "",
      "name": "",
      "query": "",
      "deleted": 0,
      "sort": "weight, id",
      "limit": 100
    },
    "set": [
      {
        "pageLayoutID": "485611457202618369",
        "namespaceID": "409824987081211905",
        "moduleID": "0",
        "pageID": "485611457202225153",
        "parentID": "0",
        "handle": "primary",
        "primary": false,
        "weight": 0,
        "meta": { /* 元数据，含 title 等 */ },
        "config": { /* 布局配置 */ },
        "blocks": [ /* 布局块列表 */ ],
        "ownedBy": "0",
        "createdAt": "2026-03-05T02:03:47Z",
        "updatedAt": "2026-03-09T08:48:22Z"
      }
      // ... 该页面下的更多布局
    ]
  }
}
```

> **说明**：此接口与"列表布局"的区别在于路径中包含 `pageID`，返回的 `filter` 也包含 `pageID` 字段，仅返回该页面下的布局。

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}/layout/?sort=weight+ASC' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 新增布局

### 请求

```
POST /compose/namespace/{namespaceID}/page/{pageID}/layout/
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 所属页面 ID |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json` |
| `Authorization` | 是 | Bearer Token（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 请求体（JSON）

```jsonc
{
  "weight": 0,                           // 排序权重
  "moduleID": "0",                       // 关联的模块 ID（"0" 表示无关联）
  "handle": "aaaa",                      // 布局标识
  "ownedBy": "0",                        // 所有者 ID

  "meta": {
    "title": "aaaa",                     // 布局标题
    "description": "",                   // 布局描述
    "updated": true
  },

  "config": {
    "visibility": {
      "expression": "",
      "roles": []
    },
    "buttons": {
      "back":   { "enabled": true, "loading": true, "refresh": true, "actionID": "1", "params": {} },
      "delete": { "enabled": true, "loading": true, "refresh": true, "actionID": "2", "params": {} },
      "clone":  { "enabled": true, "loading": true, "refresh": true, "actionID": "3", "params": {} },
      "new":    { "enabled": true, "loading": true, "refresh": true, "actionID": "4", "params": {} },
      "edit":   { "enabled": true, "loading": true, "refresh": true, "actionID": "5", "params": {} },
      "submit": { "enabled": true, "loading": true, "refresh": true, "actionID": "6", "params": {} }
    },
    "actions": [],
    "useTitle": false
  },

  "blocks": []                           // 新增时通常为空数组
}
```

### 响应

成功返回新创建的布局对象（含服务端生成的 `pageLayoutID`、`createdAt` 等字段）。

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}/layout/' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --data-raw '{
    "weight": 0,
    "moduleID": "0",
    "handle": "aaaa",
    "meta": { "title": "aaaa", "description": "" },
    "config": { ... },
    "blocks": [],
    "ownedBy": "0"
  }' \
  --compressed --insecure
```

---

## 更新布局

### 请求

```
POST /compose/namespace/{namespaceID}/page/{pageID}/layout/{pageLayoutID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 所属页面 ID |
| `pageLayoutID` | string | 布局 ID |

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token |
| `Content-Type` | 是 | `application/json` |
| `Authorization` | 是 | Bearer Token（来自 `env.json → headers`） |
| `X-NAMESPACE-ID` | 是 | 命名空间 ID（与路径中一致） |
| `Content-Language` | 否 | 语言，如 `en` |

### 请求体（JSON）

```jsonc
{
  // ── 布局基本信息 ──
  "weight": 0,                           // 排序权重
  "moduleID": "0",                       // 关联的模块 ID（"0" 表示无关联）
  "handle": "primary",                   // 布局标识
  "ownedBy": "0",                        // 所有者 ID

  // ── 元数据 ──
  "meta": {
    "title": "SLA Task List",            // 布局标题
    "description": "",                   // 布局描述
    "script": "",                        // 自定义脚本
    "scriptEnabled": false               // 是否启用脚本
  },

  // ── 布局配置 ──
  "config": {
    "visibility": {
      "expression": "",                  // 可见性表达式
      "roles": []                        // 可见角色列表
    },
    "buttons": {                         // 操作按钮配置
      "back":   { "enabled": true, "loading": true, "refresh": true, "actionID": "1", "params": {}, "label": "" },
      "delete": { "enabled": true, "loading": true, "refresh": true, "actionID": "2", "params": {}, "label": "" },
      "clone":  { "enabled": true, "loading": true, "refresh": true, "actionID": "3", "params": {}, "label": "" },
      "new":    { "enabled": true, "loading": true, "refresh": true, "actionID": "4", "params": {}, "label": "" },
      "edit":   { "enabled": true, "loading": true, "refresh": true, "actionID": "5", "params": {}, "label": "" },
      "submit": { "enabled": true, "loading": true, "refresh": true, "actionID": "6", "params": {}, "label": "" }
    },
    "actions": [],                       // 自定义动作列表
    "useTitle": false                    // 是否使用标题
  },

  // ── 布局块列表 ──
  // 注意：布局中的 blocks 仅包含位置信息和元数据，
  //       不包含完整的块选项（完整块定义在 page 的 blocks 中）
  "blocks": [
    {
      "blockID": "1",                    // 块 ID（对应 page.blocks 中的 blockID）
      "xywh": [0, 0, 48, 81],           // 位置和大小 [x, y, width, height]
      "meta": {
        "hidden": false,
        "tempID": "tempID-xxx"
      }
    }
    // ... 更多块
  ],

  // ── 更新时间戳（可选） ──
  "updatedAt": "2026-03-06T07:41:55.000Z"
}
```

### 响应

成功返回更新后的完整布局 JSON 对象（结构同列表接口 `set[]` 中的元素）。

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}/layout/{pageLayoutID}' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --data-raw '{
    "weight": 0,
    "moduleID": "0",
    "handle": "primary",
    "meta": { ... },
    "config": { ... },
    "blocks": [ ... ],
    "ownedBy": "0",
    "updatedAt": "2026-03-06T07:41:55.000Z"
  }' \
  --compressed --insecure
```

---

## 删除布局

### 请求

```
DELETE /compose/namespace/{namespaceID}/page/{pageID}/layout/{pageLayoutID}
```

| 路径参数 | 类型 | 说明 |
|---------|------|------|
| `namespaceID` | string | 命名空间 ID |
| `pageID` | string | 页面 ID |
| `pageLayoutID` | string | 要删除的布局 ID |

### 响应

成功时返回 HTTP 200，响应体为：

```json
{
  "response": true
}
```

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/{namespaceID}/page/{pageID}/layout/{pageLayoutID}' \
  -X 'DELETE' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-NAMESPACE-ID: {namespaceID}' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 注意事项

1. **布局使用 `pageLayoutID`** 而非 `layoutID`（与本地 JSON 配置中的 `layoutID` 字段名不同）。
2. **`pageID`** 表示该布局所属的页面。
3. **`parentID`** 为 `"0"` 表示顶级布局，非零值表示嵌套在其他布局下。
4. **`primary`** 标识是否为页面的主布局。
5. **列表 API 路径为 `page-layout`**（带连字符），更新/新增/删除 API 路径为 `page/{pageID}/layout/{pageLayoutID}`。
6. **更新接口的 `blocks` 仅含位置信息**（`blockID` + `xywh` + `meta`），完整的块定义（`kind`、`options` 等）在 Page 的 `blocks` 中。
7. **删除接口** 使用 `DELETE` 方法，成功返回 `{"response": true}`。
