# Namespace API 接口文档

## 公共请求头

> 以下请求头适用于本文档中的**所有接口**。

| Header | 必填 | 说明 |
|--------|------|------|
| `Content-Type` | 是 | `application/json; charset=utf-8` |
| `X-SS-EMAIL` | 是 | 操作人邮箱，从 `env.json → environments.{env}.tenants.{tenant}.headers` 读取 |
| `Content-Language` | 否 | 语言，如 `en` |

---

## 列表命名空间

### 请求

```
GET /compose/namespace/
```

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 否 | `""` | 搜索关键词 |
| `slug` | string | 否 | `""` | 按 slug 过滤 |
| `name` | string | 否 | `""` | 按名称过滤 |
| `sort` | string | 否 | `id` | 排序字段 |

### 响应

```json
{
  "response": {
    "filter": {
      "namespaceID": null,
      "query": "",
      "slug": "",
      "name": "",
      "deleted": 0,
      "sort": "id"
    },
    "set": [
      {
        "namespaceID": "409824987081211905",
        "slug": "itsm",
        "enabled": true,
        "meta": {
          "iconID": "0",
          "logoID": "0",
          "hideSidebar": false
        },
        "createdAt": "2024-09-28T06:09:30Z",
        "updatedAt": "2025-12-30T08:38:07Z",
        "name": "ITSM",
        "canGrant": true,
        "canUpdateNamespace": true,
        "canDeleteNamespace": true,
        "canManageNamespace": true,
        "canCreateModule": true,
        "canCreateChart": true,
        "canCreatePage": true
      }
    ]
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `namespaceID` | string | 命名空间唯一 ID |
| `slug` | string | 命名空间短标识（如 `itsm`、`fsm`） |
| `name` | string | 命名空间显示名称 |
| `enabled` | bool | 是否启用 |
| `meta` | object | 元数据（图标、Logo 等） |
| `createdAt` | string | 创建时间 (ISO 8601) |
| `updatedAt` | string | 最后更新时间 (ISO 8601) |

### curl 示例

```bash
curl 'http://dev.dms/mx/pionapaas/api/compose/namespace/' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-SS-EMAIL: lyh@it188.com' \
  -H 'Content-Language: en' \
  --compressed --insecure
```

---

## 注意事项

1. **slug** 是脚本中用来通过 `--namespace-slug` 参数查找 `namespaceID` 的关键字段。
2. **无需分页**：命名空间数量通常较少，单次请求可获取全部。
3. **`can*` 权限字段** 可忽略，仅用于前端 UI 权限控制。
4. **请求头必须包含 env.json 中的 headers**：`baseUrl` 和 `headers`（含 `X-SS-EMAIL`、`Content-Type`）均从 `env.json → environments.{env}.tenants.{tenant}` 读取。
