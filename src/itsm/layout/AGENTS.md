## 目录职责

本目录存放 itsm 命名空间的 279 个布局 JSON 文件。
Layout 文件只存储 blockID 引用和 xywh 坐标，Block 完整定义在 Page JSON 中。

---

## 文件命名格式

```
{LayoutTitle}_{layoutID}.json
```

例：`View_409824987082981377.json`、`Edit_409824987083112449.json`

---

## 三种 Layout 类型

| 类型标识 | handle 值 | 用途 | 按钮特征 |
|---------|-----------|------|---------|
| 查看 | `isView` 或 `primary` | 列表页 / 详情查看 | `back`、自定义 Action |
| 新增 | `isCreate` | 详情页新增 | `new`（列表页）或 `save`（详情页） |
| 编辑 | `isEdit` | 详情页编辑 | `edit`、`save`、`back` |

**规则**：
- 列表页对应 1 个 Layout（`handle: "primary"`）
- 详情页对应 3 个 Layout（isView + isCreate + isEdit）

---

## 操作规则

- **改 Block 位置**：修改 Layout JSON 中对应 blockID 的 `xywh` 数组
- **添加/删除 Block**：必须同步修改对应的 Page JSON
- **修改按钮**：修改 Layout JSON 的 `config.actions` 数组
- **新建 Layout**：必须通过 Sonyflake 生成 layoutID；创建 Page 时必须同时创建 Layout

操作前必读：`../../../../../lowcode-base/process/layout/`

---

## 按钮 action kind 参考

| kind | 用途 |
|------|------|
| `new` | 新建记录（列表页） |
| `back` | 返回上一页 |
| `edit` | 进入编辑模式 |
| `save` | 保存记录 |
| `delete` | 删除记录 |
| `workflow` | 触发工作流 |

---

## layoutID 映射说明

layoutID 存于各 JSON 文件的 `"layoutID"` 字段。
关联 pageID 存于各 JSON 文件的 `"pageID"` 字段。
`handle` 字段标识布局类型（如 `"primary"`, `"isCreate"`, `"isEdit"`, `"isView"`）。
