## lowcode-mx/src 目录指南

> 本目录是 mx 租户所有命名空间配置 JSON 的存放位置，每个子目录对应一个命名空间。
> 平台级通用知识（Field/Block Kind 参考、SOP）请查阅 `../../lowcode-base/`。
> 通用模板规范请参阅 `../../lowcode-template/src/AGENTS.md`。

---

## 强制规则：操作前必须先读参考文档

对任何配置文件（module / page / layout / workflow）执行增删改前，必须先阅读对应资源类型的参考文档：

| 操作对象 | 必读文档 |
|---------|---------|
| Module（字段、配置） | `../../lowcode-base/corteza/field/AGENTS.md` + `../../lowcode-base/process/module/` |
| Page（Block 配置） | `../../lowcode-base/corteza/block/AGENTS.md` + `../../lowcode-base/process/page/` |
| Layout（坐标、按钮） | `../../lowcode-base/corteza/block/AGENTS.md` + `../../lowcode-base/process/layout/` |
| Field（字段 Kind） | `../../lowcode-base/corteza/field/AGENTS.md` |
| Workflow（触发器、步骤） | `../../lowcode-base/corteza/field/AGENTS.md` + `../../lowcode-base/process/workflow/sop-workflow-add.md` |

> ⚠️ **执行任何 SOP 操作前，必须先读取目标命名空间对应子目录的 `AGENTS.md`**（如 `src/{命名空间}/module/AGENTS.md`），以获取当前文件清单和最大 ID。
> 读取顺序：**① 目标目录 AGENTS.md（当前状态）→ ② SOP 参考文档（操作规范）→ ③ 执行操作**。
> 跳过第 ① 步会导致 ID 冲突或文件命名错误。

---

## 新建命名空间最简原则

在参考已有命名空间（如 itsm/fsm）的配置为新空间创建 module / page / layout 时，**不得照搬全部配置**，必须遵循「先最简、后扩展」原则。

### 每个新建的核心业务模块，只需创建以下内容

| 必须创建 | 说明 |
|---------|------|
| Module 文件（基础字段） | 只保留核心业务字段，去掉所有关联到当前空间尚未实现功能的 Record 字段 |
| 列表页（RecordList Page） | 包含基础列表 Block，不加联动按钮或关联 Block |
| 详情页（Record Page） | 包含基础详情 Block |
| 详情页 Layout × 3 | 分别对应：查看（`isView`）、新增（`isCreate`）、编辑（`isEdit`） |

### 可暂缓创建（待 PRD 补充）

- 依赖其他模块的 Record 字段（引用模块尚未创建时跳过）
- 关联其他模块的 Block（跨模块嵌套列表等）
- 触发工作流的 Action 自定义按钮（工作流尚未创建时不添加）
- Tabs Block 下的子关联 Block
- 特殊 Block（SLA、Calendar、ServiceCatalog 等）

### 字段取舍规则

| 情形 | 处理方式 |
|------|---------|
| 字段 `kind` 不是 `Record` | 保留 |
| 字段 `kind` 为 `Record`，引用模块在新空间中**已存在** | 保留，更新 `options.moduleID` |
| 字段 `kind` 为 `Record`，引用模块**尚未创建** | 跳过不添加 |

### clearCopy 唯一字段规则

复制记录时，部分字段值不应被复制（如唯一编号、流水号），需通过字段的 `options.clearCopy` 控制：

| 场景 | clearCopy 设置 |
|------|---------------|
| Code类型字段（自动编号） | 必须设为 `true` |
| 业务唯一编号（如 EMS number、合同编号） | 必须设为 `true` |
| 普通文本 / 选择 / 引用字段 | 保持默认 `false` |

配置位置：Module JSON → `fields[].options.clearCopy`（boolean，默认 `false`）。
详细说明参考 `../../lowcode-base/corteza/field/AGENTS.md` 中的 clearCopy 章节。

---

## 每个命名空间必须创建 topData module

topData 是记录置顶功能的底层存储模块，**每个新建命名空间都必须先创建**。

| 字段名 | kind | 说明 |
|--------|------|------|
| `useID` | BigInt | 执行置顶操作的用户 ID |
| `modID` | BigInt | 被置顶记录所属的模块 ID |
| `pageID` | BigInt | 被置顶记录所在的页面 ID |
| `recoID` | BigInt | 被置顶的记录 ID |
| `topTime` | DateTime | 置顶时间 |

创建规则：

- 文件命名：`topData_{namespaceID}.json`
- `connectionID` 统一设为 `"0"`
- topData 只有 module，**没有对应的 page 和 layout**

---

## 依赖模块复制规则

新空间的核心模块如果通过 Record 字段关联了其他命名空间的模块，必须将被关联的模块也复制到新命名空间的 `module/` 目录下。

操作步骤：

1. 扫描新命名空间所有模块 JSON，收集 `fields[].options.moduleID` 中的外部 moduleID
2. 找到对应的源模块 JSON 文件（通过顶层 `"moduleID"` 匹配）
3. 复制到新命名空间的 `module/` 目录
4. 将 `namespaceID` 替换为新命名空间 ID
5. 使用 Sonyflake 为每个依赖模块重新生成 `moduleID` 和 `fieldID`
6. 将 `connectionID` 统一改为 `"0"`
7. 清空所有 Record 类型字段的 `defaultValue`（改为 `[]`）
8. 更新所有引用方的 `options.moduleID` 为新 moduleID

> **严禁保留原命名空间的 moduleID/fieldID**：sync 脚本做 UPSERT，相同 ID 会覆盖原命名空间数据！

---

## ID 重新生成规则

| 资源 | ID 字段 | 规则 |
|------|---------|------|
| 新建 module | `moduleID` | 必须重新生成（Sonyflake） |
| 新建 module 的字段 | `fieldID` | 必须重新生成（Sonyflake） |
| 依赖 module | `moduleID`、`fieldID` | 必须重新生成，同步更新所有引用方 |
| 新建 page | `pageID` | 必须重新生成 |
| page 内的 Block | `blockID` | 必须重新生成 |
| 新建 layout | `layoutID` | 必须重新生成 |

Sonyflake 简化生成方式：取同类资源中最大已有 ID + 65536。

完整算法参考：`../../lowcode-base/process/module/sop-module-add.md` 中的 fieldID 生成规则。

---

## 详情页与 Layout 必须同步生成

每次新建命名空间，或在现有命名空间中新增核心模块时，**必须同步生成该模块的详情页（Record Page）及其所有配套 Layout**：

- 查看 Layout（`isView: true`）
- 新增 Layout（`isCreate: true`）
- 编辑 Layout（`isEdit: true`）

---

## 新建命名空间必须生成各子目录 AGENTS.md

每个新建命名空间的 `module/`、`page/`、`layout/` 子目录下，**必须同步生成对应的 `AGENTS.md`**，内容包括：

| 文件 | 必须包含的内容 |
|------|---------------|
| `{空间}/AGENTS.md` | 命名空间基本信息（namespaceID、简介）、菜单结构、模块/页面/布局文件数量、操作前必读文档链接 |
| `{空间}/module/AGENTS.md` | 模块文件清单（moduleID、字段数、说明）、各模块字段表（fieldID、kind、name）、ID 生成规则 |
| `{空间}/page/AGENTS.md` | 页面文件清单（pageID、类型、selfID、moduleID、prefilter）、Block tempID 对应关系 |
| `{空间}/layout/AGENTS.md` | Layout 文件清单（layoutID、handle、对应 pageID）、Block tempID 对应关系、下一个可用 layoutID |

> **目的**：当命名空间配置后续扩展时，AI 可直接读取对应 AGENTS.md 获取当前文件清单和 ID 上下文，无需重新扫描全目录。

参考示例：[`src/fsm/`](fsm/AGENTS.md)、[`src/fsm/module/`](fsm/module/AGENTS.md)、[`src/fsm/page/`](fsm/page/AGENTS.md)、[`src/fsm/layout/`](fsm/layout/AGENTS.md)

---

## 四大资源类型对比

| 特性 | Module | Page | Layout | Workflow |
|------|--------|------|--------|----------|
| 文件路径层级 | 命名空间下 | 命名空间下 | 命名空间下 | **租户下** |
| 文件名格式 | `{handle}.json` | `{handle}_{pageID}.json` | `{handle}_{layoutID}.json` | `{handle}.json` |
| 文件名含 ID | 否 | 是 | 是 | 否 |
| 数据库表 | `compose_module` + `compose_module_field` | `compose_page` | `compose_page_layout` | `automation_workflow` |

---

## 文件命名规则

- 所有 JSON 文件统一按 `handle` 命名（handle 为空则用 `name`）
- page 和 layout 文件名追加 `_{id}`，格式：`{handle}_{pageID}.json` / `{handle}_{layoutID}.json`
- module 和 workflow 不追加 ID

---

## 目录结构

```
src/
├── AGENTS.md               ← 本文件：命名空间创建规范
├── fsm/                    ← FSM 示例命名空间（Event/Group/Team/User 管理）
│   ├── AGENTS.md           ← FSM 总览 + ID 映射表
│   ├── module/             ← FSM 模块 JSON（5 个）
│   │   └── AGENTS.md       ← 模块清单 + 字段表 + ID 规则
│   ├── page/               ← FSM 页面 JSON（12 个）
│   │   └── AGENTS.md       ← 页面清单 + Block tempID 对应
│   ├── layout/             ← FSM 布局 JSON（18 个）
│   │   └── AGENTS.md       ← 布局清单 + tempID 对应 + 下一可用 ID
│   └── block/              ← FSM Block 配置指南
└── workflow/
    └── AGENTS.md           ← 工作流配置指南
```

---

## 快捷指令

指令格式：`#指令@{环境}/{租户}/{命名空间} <名称> <操作>`
（workflow 类：`#指令@{环境}/{租户} <名称>`）

### `#配置` — 修改模块配置

```
#配置@{环境}/{租户}/{命名空间} {handle} 把 {字段name} 的 label 改为 {新label}
```

### `#配置layout` — 修改布局配置

```
#配置layout@{环境}/{租户}/{命名空间} {handle}_{layoutID} 把 {属性} 改为 {值}
```

### `#配置page` — 修改页面配置

```
#配置page@{环境}/{租户}/{命名空间} {handle}_{pageID} 把 {属性} 改为 {值}
```

### `#配置workflow` — 修改工作流配置

```
#配置workflow@{环境}/{租户} {handle} 把 {属性} 改为 {值}
```

### `#导出module` — 从数据库导出模块

```
#导出module@{环境}/{租户}/{命名空间} [{handle}]
```

不指定 handle 则导出全部模块。

### `#导出layout` — 从数据库导出布局

```
#导出layout@{环境}/{租户}/{命名空间} [--page-id {pageID}]
```

### `#导出page` — 从数据库导出页面

```
#导出page@{环境}/{租户}/{命名空间} [{handle}]
```

### `#导出workflow` — 从数据库导出工作流

```
#导出workflow@{环境}/{租户} [{handle}]
```

### `#同步module` — 将本地模块同步到数据库

```
#同步module@{环境}/{租户}/{命名空间} {handle}
```

### `#同步layout` / `#同步page` — 同步到数据库

```
#同步layout@{环境}/{租户}/{命名空间} {handle}_{layoutID}
#同步page@{环境}/{租户}/{命名空间} {handle}_{pageID}
```

### `#同步workflow` — 将本地工作流同步到数据库

```
#同步workflow@{环境}/{租户} {handle}
```

---

## 通用执行规则

- 所有快捷指令执行完毕后只报告最终结果
- 环境名、租户名和命名空间名为必填参数，未提供时必须询问
- workflow 类操作需要环境名和租户名，不需要命名空间
- 导出时目标目录不存在则自动创建，文件已存在则直接覆盖
- workflow 统一存放在租户目录下，严禁放到命名空间子目录

---

## 脚本说明

脚本路径参考 `../../lowcode-base/scripts/` 目录：

| 脚本 | 功能 |
|------|------|
| `export_module_from_api.py` | 从 API 导出模块为 JSON |
| `sync_module_to_api.py` | 将模块 JSON 通过 API 同步到服务端 |
| `export_layout_from_api.py` | 从 API 导出布局为 JSON |
| `sync_layout_to_api.py` | 将布局 JSON 通过 API 同步到服务端 |
| `export_page_from_api.py` | 从 API 导出页面为 JSON |
| `sync_page_to_api.py` | 将页面 JSON 通过 API 同步到服务端 |
| `export_workflow_from_api.py` | 从 API 导出工作流为 JSON |
| `sync_workflow_to_api.py` | 将工作流 JSON 通过 API 同步到服务端 |
| `sync_namespace_to_api.py` | 将命名空间配置通过 API 同步到服务端 |

脚本共用 `api_utils.py`，从 `env.json` 中读取 API 连接参数（baseUrl、Authorization headers）。

---

## 常见错误

- 混淆 module / layout / page / workflow，它们对应不同的数据库表。
- 遗漏租户层级，直接将命名空间放在环境目录下（正确路径为 `{环境}/{租户}/{命名空间}/`）。
- workflow 文件放到了命名空间目录下（应放在 `{环境}/{租户}/workflow/`）。
- 混淆租户和命名空间，它们是不同层级：一个租户下可以有多个命名空间。
- 复制依赖模块时保留了原命名空间的 moduleID / fieldID，导致 sync 脚本 UPSERT 时覆盖原命名空间数据。
- 唯一字段（编号、Code）未设 `clearCopy: true`，导致复制记录后出现重复编号。
