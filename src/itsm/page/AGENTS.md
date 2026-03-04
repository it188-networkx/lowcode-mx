## 目录职责

本目录存放 itsm 命名空间的 123 个页面 JSON 文件。
Page 文件存储 Block 的**完整定义**（kind、options、字段等），Layout 文件只存储 blockID 引用和 xywh 坐标。

---

## 文件命名格式

```
{PageTitle}_{pageID}.json
```

例：`事件管理_409824987078983681.json`、`Home_409824987078328321.json`

---

## 列表页与详情页区分规则

| 类型 | 特征 | 对应 Layout 数量 |
|------|------|----------------|
| 列表页（RecordList） | 顶层 Block 为 RecordList kind | 1 个（handle: "primary"） |
| 详情页（Record） | 顶层 Block 为 Record kind | 3 个（isView / isCreate / isEdit） |

---

## 操作规则

- **改 Block 内容（字段、options）**：修改 Page JSON
- **改 Block 位置（xywh）或按钮**：修改 Layout JSON
- **新增 Block**：必须同时更新 Page JSON（添加 Block 定义）和 Layout JSON（添加 blockID + xywh）
- **删除 Block**：必须同时清理 Page JSON 和 Layout JSON
- **创建新 Page**：必须同时创建对应的 Layout（详见 Layout AGENTS.md）

操作前必读：`../../../../../lowcode-base/process/page/`

---

## pageID 映射（部分核心页面）

| 页面名称 | 文件名（前缀） | 说明 |
|---------|-------------|------|
| Home | Home_409824987078328321 | 首页 |
| 事件管理 | 事件管理_409824987078983681 | 事件管理列表页 |
| 问题管理 | 问题管理_420624705702068225 | 问题管理列表页 |
| 变更管理 | 变更管理_421394677741256705 | 变更管理列表页 |
| 服务目录 | 服务目录_410137265131487233 | 服务目录列表页 |
| 服务门户 | 服务门户_416930265647677441 | 服务门户页 |
| User | User_409824987077935105 | 用户列表页 |
| 团队管理 | 团队管理_409824987078197249 | 团队管理列表页 |

> 完整 pageID 映射请从各 JSON 文件的 `"pageID"` 字段读取。

---

## 特殊 Block 实例（RecordSlaList）

以下两个页面使用 `RecordSlaList` 特殊 Block，通过自定义后端 API 渲染数据，**不能套用普通 RecordList 操作流程**：

| 页面名称 | pageID | moduleID | customApi | 模式 |
|---------|--------|----------|-----------|------|
| SLA配置 | `409824987080097793` | `409824987082784769`（Sla） | `/components/sla` | `slaEnable: true` |
| 待办日历 | `470138789221498881` | `470138789204393985`（TodoCalendar） | `/components/schedule/task/list` | `schedule: true` |

- 修改这两个页面的 `fields[]` 前，必须确认后端 API 是否返回该字段。
- `customApi` 路径不可随意修改，修改会导致页面无法渲染数据。
- `prefilter` CQL 过滤对 `RecordSlaList` 无效，过滤逻辑由后端 API 内部实现。
