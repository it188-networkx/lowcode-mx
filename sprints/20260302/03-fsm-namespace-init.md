## 子任务 03：新建 fsm 命名空间 — 团队管理 + 事件管理菜单体系初始化

- 序号：03
- 关联 Sprint 原始编号：—（本地测试需求）
- 优先级：P1
- 责任人：AI Agent
- 关联 SOP：
  - `../../lowcode-base/process/module/sop-module-add.md`
  - `../../lowcode-base/process/page/sop-page-add.md`
  - `../../lowcode-base/process/layout/sop-layout-add.md`
- 前置依赖：无

---

## 目标

在 `lowcode-mx\src` 下新建命名空间 **fsm**，遵循「最简原则」完成以下菜单体系的 Module / Page / Layout 初始配置：

1. **一级菜单：团队管理** — 子菜单：用户 / 组 / 团队（每个子菜单对应独立 module）
2. **一级菜单：事件管理** — 子菜单：已提交 / 待申请 / 所有工单（三个视图共用同一 `Event` module）

---

## 命名空间信息

| 项目 | 值 |
|------|----|
| namespaceID | `485325475439181825` |
| 路径前缀 | `lowcode-mx/src/fsm/` |

---

## 涉及文件

### Module（`module/`）

| 文件 | moduleID | 说明 |
|------|----------|------|
| `topData_485325475439181825.json` | `485325475441475585` | 置顶功能存储，无需 page/layout |
| `User.json` | `485325475439247361` | 用户模块（姓名/账号/邮箱/手机/状态等 9 字段） |
| `Group.json` | `485325475439312897` | 组模块（组名/描述/状态 3 字段） |
| `Team.json` | `485325475439378433` | 团队模块（团队名/描述/负责人/状态等 7 字段） |
| `Event.json` | `485325475439443969` | 事件模块（标题/描述/状态/优先级/创建时间 5 字段），三个视图共用 |

### Page（`page/`）

| 文件 | 类型 | 说明 |
|------|------|------|
| `团队管理_485325475439509505.json` | 一级菜单页（父页） | 团队管理一级菜单容器 |
| `用户_485325475439640577.json` | RecordList | 用户列表页 |
| `组_485325475439706113.json` | RecordList | 组列表页 |
| `团队_485325475439771649.json` | RecordList | 团队列表页 |
| `模块记录页面_User_485325475440033793.json` | Record | 用户详情页 |
| `模块记录页面_Group_485325475440099329.json` | Record | 组详情页 |
| `模块记录页面_Team_485325475440164865.json` | Record | 团队详情页 |
| `事件管理_485325475439575041.json` | 一级菜单页（父页） | 事件管理一级菜单容器 |
| `已提交_485325475439837185.json` | RecordList | 事件列表（filter: `status = 'submitted'`） |
| `待申请_485325475439902721.json` | RecordList | 事件列表（filter: `status = 'pending'`） |
| `所有工单_485325475439968257.json` | RecordList | 事件列表（无 filter） |
| `模块记录页面_Event_485325475440230401.json` | Record | 事件详情页（三视图共用） |

### Layout（`layout/`）

| 文件 | 对应 Page | 类型 |
|------|-----------|------|
| `模块记录列表_User_485325475441082369.json` | 用户列表页 | primary |
| `用户-查看_485325475440295937.json` | 用户详情页 | isView |
| `用户-新建_485325475440361473.json` | 用户详情页 | isCreate |
| `用户-编辑_485325475440427009.json` | 用户详情页 | isEdit |
| `模块记录列表_Group_485325475441147905.json` | 组列表页 | primary |
| `组-查看_485325475440492545.json` | 组详情页 | isView |
| `组-新建_485325475440558081.json` | 组详情页 | isCreate |
| `组-编辑_485325475440623617.json` | 组详情页 | isEdit |
| `模块记录列表_Team_485325475441213441.json` | 团队列表页 | primary |
| `团队-查看_485325475440689153.json` | 团队详情页 | isView |
| `团队-新建_485325475440754689.json` | 团队详情页 | isCreate |
| `团队-编辑_485325475440820225.json` | 团队详情页 | isEdit |
| `模块记录列表_已提交_485325475441278977.json` | 已提交列表页 | primary |
| `模块记录列表_待申请_485325475441344513.json` | 待申请列表页 | primary |
| `模块记录列表_所有工单_485325475441410049.json` | 所有工单列表页 | primary |
| `事件-查看_485325475440885761.json` | 事件详情页 | isView |
| `事件-新建_485325475440951297.json` | 事件详情页 | isCreate |
| `事件-编辑_485325475441016833.json` | 事件详情页 | isEdit |

---

## 约束说明

| 约束 | 细节 |
|------|------|
| 最简原则 | 所有 module 只含基础非关联字段，暂不添加跨模块 `kind: "Record"` 字段 |
| 共用 module | `Event` module 只创建一份，三个视图页通过 `prefilter` 区分 |
| Layout 按钮 | `config.actions` 均为空数组 `[]`，只使用平台内置标准按钮 |
| topData 无 page/layout | `topData` 只需 module 文件，不创建对应页面和布局 |
| ID 规则 | 所有 ID 由 Sonyflake 生成（machineID=1），不复用任何 itsm 原始 ID |

---

## 操作步骤

1. 读取 `../../lowcode-base/process/module/sop-module-add.md`（Module 新增 SOP，含 ID 生成规则）
2. 读取 `../../lowcode-base/process/page/sop-page-add.md`（Page 新增 SOP）
3. 读取 `../../lowcode-base/process/layout/sop-layout-add.md`（Layout 新增 SOP，含按钮配置规范）
4. 生成 `topData_485325475439181825.json`（module only，`connectionID: "0"`），存入 `src/fsm/module/`
5. 依次生成团队管理三个 module：`User.json` → `Group.json` → `Team.json`
6. 生成事件管理 module：`Event.json`（`status` 字段为 Select，选项：submitted / pending / closed）
7. 生成对应 page 文件（列表页 + 详情页），存入 `src/fsm/page/`
   - 事件管理三个列表视图设置不同 `prefilter`
8. 生成对应 layout 文件（列表页×primary，详情页×isView/isCreate/isEdit），存入 `src/fsm/layout/`
9. 检查所有 layout 的 `pageID` 指向正确，`blockID` 与 page 保持一致

---

## 验收标准

- [ ] `topData_485325475439181825.json` 存在，`connectionID: "0"`
- [ ] 团队管理：User / Group / Team 三个 module + 各自 page(2) + layout(4) = 21 个文件
- [ ] 事件管理：Event module × 1 + 列表视图 page(3) + layout(3) + 详情 page(1) + layout(3) = 11 个文件
- [ ] `Event.json` 的 `status` 字段为 Select 类型，含 submitted / pending / closed 选项
- [ ] 三个事件列表页 `prefilter` 分别为 `status = 'submitted'`、`status = 'pending'`、`""`
- [ ] 所有 JSON 无格式错误，文件存放于 `src/fsm/`
- [ ] 无任何其他命名空间的 moduleID / fieldID / pageID / layoutID 被复用
