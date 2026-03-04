## 目录职责

本目录存放 fsm 命名空间（namespaceID: `485325475439181825`）的 5 个模块 JSON 文件。
每个文件对应一个 Corteza 模块，包含字段定义、DAL 连接等配置。

---

## 文件命名格式

```
{Handle}.json
```

特例：`topData_{namespaceID}.json`（topData 带 namespaceID 后缀）

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

## 模块清单

| handle | 文件名 | moduleID | 说明 |
|--------|--------|----------|------|
| topData | topData_485325475439181825.json | 485325475441475585 | 置顶功能存储，无 page/layout |
| User | User.json | 485325475439247361 | 用户（9 字段） |
| Group | Group.json | 485325475439312897 | 组（3 字段） |
| Team | Team.json | 485325475439378433 | 团队（7 字段） |
| Event | Event.json | 485325475439443969 | 事件（5 字段） |

---

## 当前最大 ID

| 类型 | 最大已用 ID |
|------|-----------|
| moduleID | 485325475441475585 |
| fieldID | 485325475443376129 |

新增 module：moduleID = 485325475441475585 + 65536 *n
新增字段：fieldID = 485325475443376129 + 65536* n
