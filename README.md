## 仓库定位

本仓库（`lowcode-mx`）是面向 `mx` 租户的命名空间配置运营层，基于 `lowcode-template` 初始化，此后与模板仓库独立演进。

- 源头数据：`itsm-build/configuration/dev.dms/mx/`（只读，部署用）
- 模板参考：`lowcode-template/src/itsm/`（通用模板，可参考但不同步）
- 本仓库：`lowcode-mx/src/itsm/`（mx 环境命名空间配置，每周 Sprint 驱动变更）

---

## 命名空间清单

| slug | namespaceID | 创建 Sprint | 说明 |
|------|-------------|------------|------|
| itsm | 409824987081211905 | 2026-S01 | ITSM 服务台（事件/变更/问题/服务目录） |

---

## 目录结构

```text
lowcode-mx/
├── README.md              # 本文件：仓库定位、命名空间清单
├── env.json.template      # 环境配置模板（不含密码/地址等敏感信息）
├── design/                # mx 独有的产品设计文档
│   └── AGENTS.md
├── sprints/               # 每周 Sprint 任务（周一从 ops-playbook 摘录）
│   ├── AGENTS.md
│   └── <YYYYMMDD>/        # 周目录，以周一日期命名
├── scripts/               # 工具脚本（复用自 lowcode-base）
└── src/                   # 命名空间配置 JSON（核心内容）
    ├── AGENTS.md
    └── itsm/              # ITSM 命名空间（namespaceID: 409824987081211905）
        ├── AGENTS.md
        ├── module/        # 47 个模块 JSON
        ├── page/          # 123 个页面 JSON
        ├── layout/        # 279 个布局 JSON
        └── workflow/      # 95 个工作流 JSON
```

---

## 与相关仓库的关系

| 仓库 | 关系说明 |
|------|---------|
| `itsm-build` | 只读源，提供部署环境实际数据；本仓库不修改它 |
| `lowcode-template` | 初始化蓝本；本仓库已独立，不要求保持同步 |
| `lowcode-base` | 平台公共知识（SOP、Field/Block 参考）；始终引用，不复制内容 |
| `ops-playbook` | 只读，每周从 `sprints/` 摘录配置相关任务到本仓库 `sprints/` |

---

## 快速开始

1. 查看本周 Sprint 任务：`sprints/<YYYYMMDD>/`
2. 修改模块：参考 `../../lowcode-base/process/module/` SOP
3. 修改页面/布局：参考 `../../lowcode-base/process/page/` + `process/layout/` SOP
4. 同步到数据库：使用 `../../lowcode-base/scripts/` 下的脚本
