## 目录定位

本目录（`design/`）存放 mx 租户各命名空间的**业务设计文档**，与 `src/` 下的 JSON 配置文件互为补充：

- `src/`  机器可读的配置（module / page / layout / workflow JSON）
- `design/`  人类可读的设计（数据模型、业务流程、决策记录）

每个命名空间对应一个子目录，文件在动手修改 JSON 之前编写，作为变更的上游输入。

---

## 目录结构

```text
design/
 AGENTS.md              # 本文件：设计文档操作规范
 {namespace}/           # 命名空间设计目录（与 src/{namespace}/ 一一对应）
     data-model.md      # 数据模型：模块分层、实体关系图、ID 速查表
     process-design.md  # 业务流程：状态机、时序图、跨模块关联汇总
```

当前已有：

| 命名空间 | 设计文档 |
|---------|---------|
| `itsm/` | `itsm/data-model.md`、`itsm/process-design.md` |

---

## 操作前强制规则

**对 `src/` 下任意 JSON 执行增删改前，必须先阅读对应资源类型的参考文档：**

| 操作对象 | 必读文档 |
|---------|---------|
| Module / Field | `../../lowcode-base/process/module/AGENTS.md` + `../../lowcode-base/corteza/field/AGENTS.md` |
| Page / Block | `../../lowcode-base/process/page/AGENTS.md` + `../../lowcode-base/corteza/block/AGENTS.md` |
| Layout / 按钮 | `../../lowcode-base/process/layout/AGENTS.md` + `../../lowcode-base/process/button/AGENTS.md` |
| Workflow | `../../lowcode-base/process/workflow/sop-workflow-add.md` |

---

## 场景一：新增命名空间

### 前提

需先确认：目标租户、命名空间 slug、初始模块范围（通常参考 ITSM 模板裁剪）。

### 完整步骤

```mermaid
flowchart TD
    A[确认租户 & slug] --> B[生成 namespaceID\nSonyflake 算法]
    B --> C[在 src/ 下新建命名空间目录]
    C --> D[创建 topData module\n必须最先创建]
    D --> E[按最简原则裁剪并复制\n核心业务模块 JSON]
    E --> F[为所有 moduleID / fieldID\n重新生成 ID]
    F --> G[创建每个模块的\n列表页 + 详情页 Page JSON]
    G --> H[创建配套 Layout JSON\n列表页1 / 详情页3]
    H --> I[按需复制相关 Workflow JSON\n并更新 namespace 约束]
    I --> J[编写 design/{namespace}/data-model.md]
    J --> K[同步到数据库验证]
```

### 关键约束

| 约束 | 说明 |
|------|------|
| topData 必须最先创建 | 置顶功能依赖；只有 module，无 page / layout |
| 最简原则 | 只创建核心业务字段，Record 字段引用的模块尚未创建时跳过 |
| ID 严禁保留 | 所有 moduleID / fieldID / pageID / layoutID / blockID 必须重新生成 |
| Page + Layout 必须同步 | 列表页  1 个 Layout；详情页  3 个 Layout（isView / isCreate / isEdit） |
| workflow 存租户层 | `src/workflow/` 下，不放命名空间子目录 |
| connectionID 统一 `"0"` | 新命名空间所有模块 `connectionID` 改为 `"0"` |

### ID 生成规则

Sonyflake 简化方式：取同类资源最大已有 ID + 65536。

完整规则：`../../lowcode-base/process/module/sop-module-add.md`

---

## 场景二：修改内容

### 2a 修改 Module（字段）

**禁止修改**：`kind`、`fieldID`、`name`（这三项变更会导致数据损坏）。

**可以修改**：`label`、`required`、`disabled`、`options` 中的展示配置。

**特别注意**：
- `isMulti` 变更时须同步修改 `encodingStrategy`（单值  `plain`，多值  `json`）
- 新增字段必须生成新 `fieldID`（Sonyflake），不得复用已有 ID
- 新增 `kind: "Record"` 字段前，确认引用的目标模块在当前命名空间已存在

操作参考：`../../lowcode-base/process/module/`

### 2b 修改 Page（Block 内容）

Page 存储 Block 的**完整定义**（kind、options、字段映射等）。

- 修改 Block 显示字段  编辑对应 Page JSON
- 新增 Block  同时修改 Page JSON（加 block 定义）**和** Layout JSON（加 blockID + xywh）
- 删除 Block  同时从 Page 和 Layout 中移除

> **改内容改 Page，改位置改 Layout**，两者不要混淆。

操作参考：`../../lowcode-base/process/page/` + `../../lowcode-base/corteza/block/AGENTS.md`

### 2c 修改 Layout（Block 位置 / 按钮）

Layout 只存 `blockID` 引用和 `xywh` 坐标，不含 Block 内容。

- 调整 Block 位置大小  只改 Layout JSON 中的 `x`/`y`/`w`/`h`
- 新增/修改按钮  编辑 Layout `config.actions[]`
  - 按钮 kind：`new`、`back`、`edit`、`save`、`delete`、`workflow`
  - `workflow` 类按钮需填写 `workflowID`，必须与 `src/workflow/` 中的实际 ID 对应
- 控制列表页新增  `new` 按钮的 `enabled: true/false`

操作参考：`../../lowcode-base/process/layout/` + `../../lowcode-base/process/button/AGENTS.md`

### 2d 修改 Workflow（工作流）

**禁止修改**：`workflowID`、`triggerID`（已被 Layout 按钮或其他 Workflow 引用）。

**可以修改**：步骤逻辑（`steps`/`paths`）、触发条件（`constraints`）、`enabled` 状态。

- 修改命名空间约束时，检查 `triggers[].constraints` 中的 `namespace` 值
- 修改 `Record` 类型字段比较逻辑时，不能直接比较业务值，须先 `composeRecordsLookup`
- 工作流统一存放在 `src/workflow/`，不按命名空间分目录

操作参考：`../../lowcode-base/process/workflow/sop-workflow-add.md`

---

## 场景三：删除内容

### 删除字段（Module Field）

1. 确认无 Page Block 或 Workflow 步骤引用该字段
2. 从 Module JSON 的 `fields[]` 中移除
3. 同步到数据库（**不可逆**，线上数据将丢失该列）

### 删除 Block

1. 从 Page JSON 中删除 block 定义
2. 从对应所有 Layout JSON 中删除该 `blockID` 的引用（`blocks[]` 数组）
3. 如果该 block 绑定了 workflow 按钮，检查 `config.actions[]`

### 删除 Page

1. 确认无 Layout 引用该 pageID
2. 确认无 Module 的 `topData` 或 ServiceItem 的 `page_id` 引用该 pageID
3. 删除 Page JSON 文件
4. 删除所有配套 Layout JSON 文件（命名中含该 pageID 的）

### 删除 Module

>  **高风险操作**，谨慎执行。

1. 确认无其他模块的 `kind: "Record"` 字段通过 `options.moduleID` 引用此模块
2. 确认无 Page Block 使用此模块
3. 确认无 Workflow 触发器或步骤引用此模块
4. 删除 Module JSON
5. 删除所有引用此模块的 Page JSON 和对应 Layout JSON

### 删除 Workflow

1. 检查所有 Layout JSON 的 `config.actions[]`，找出 `kind: "workflow"` 且 `workflowID` 匹配的按钮
2. 先从 Layout 中移除该按钮（或改为 `enabled: false`），再删除 Workflow JSON
3. 检查其他 Workflow 是否通过 `workflowID` 调用此工作流

---

## 设计文档制品

每个命名空间的 `design/{namespace}/` 下应维护：

| 文件 | 内容 | 何时创建 |
|------|------|---------|
| `data-model.md` | 模块分层、ERD 关系图、ID 速查表 | 新建命名空间时 |
| `process-design.md` | 状态机、核心时序图、跨流程关联汇总 | 新建命名空间时，或新增核心流程时更新 |

已有参考：[itsm/data-model.md](itsm/data-model.md)、[itsm/process-design.md](itsm/process-design.md)

---

## 快速参考：资源类型对比

| 特性 | Module | Page | Layout | Workflow |
|------|--------|------|--------|----------|
| 存放位置 | `src/{ns}/module/` | `src/{ns}/page/` | `src/{ns}/layout/` | `src/workflow/` |
| 文件名格式 | `{handle}.json` | `{handle}_{pageID}.json` | `{handle}_{layoutID}.json` | `{handle}.json` |
| 存储内容 | 字段定义 | Block 完整定义 | Block 位置 + 按钮 | 触发器 + 步骤逻辑 |
| 新增时配套 |  | 必须同步创建 Layout | 必须与 Page 同步 | 可选绑定 Layout 按钮 |
| 禁改字段 | `kind`/`fieldID`/`name` | `pageID`/`blockID` | `layoutID` | `workflowID`/`triggerID` |