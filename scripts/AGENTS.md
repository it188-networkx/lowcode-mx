# `scripts` 目录代理指南 (AGENTS.md)

本目录包含了用于管理、同步和导出各个低代码核心组件（如 Module、Page、Layout、Workflow 等）以及处理数据库操作的自动化脚本和文档。

## 目录结构与功能概览

### 1. 数据库交互与核心工具
这些工具用于管理数据库连接或执行特定的跨功能扫描任务。

*   **`db_utils.py`**
    *   **功能**: 统一的数据库连接配置加载工具。
    *   **说明**: 负责从项目的 `configuration/env.json` 配置文件中按“环境/租户”读取数据库连接参数。其他所有涉及到数据库的同步或导出脚本都依赖该模块，从而避免了重复维护数据库连接信息。
*   **`scan_function_refs.py`**
    *   **功能**: 工作流函数引用扫描脚本。
    *   **说明**: 用于扫描所有工作流的 JSON 配置文件，批量提取并分析工作流中引用了哪些 Gval 函数以及对应的参数情况。

### 2. 同步脚本 (Sync `*_to_db`)
将本地的 JSON 配置文件同步（包括新增与更新）到目标 MySQL 数据库内的对应相关表中。

*   **`sync_module_to_db.py`**：将 Module（模块）及它的 Module Field（字段）信息同步到 `compose_module` 与 `compose_module_field` 表中。
*   **`sync_page_to_db.py`**：将 Page（页面）的 JSON 配置文件同步到 `compose_page` 表中。
*   **`sync_layout_to_db.py`**：将 Layout（布局）配置信息同步到 `compose_page_layout` 表中。
*   **`sync_workflow_to_db.py`**：将 Workflow（工作流）包含的各项信息与触发器同步到 `automation_workflows` 和 `automation_triggers` 表中。
*   **`sync_namespace_to_db.py`**：将低代码应用 Namespace（命名空间）的配置与信息同步至 `compose_namespace` 表中。

### 3. 取出脚本 (Export `*_from_db`)
从目标 MySQL 数据库将存在的各项资源配置查询并导出为符合标准结构（类似本地开发结构）的 JSON 配置文件。

*   **`export_module_from_db.py`**：从数据库查询导出 `compose_module` 和字段表数据。
*   **`export_page_from_db.py`**：从数据库查询导出 `compose_page` 内的数据并生成相应页面 JSON 文件。
*   **`export_layout_from_db.py`**：从数据库查询导出 `compose_page_layout` 布局数据到 JSON。
*   **`export_workflow_from_db.py`**：从数据库读取并导出工作流/触发器为对应的自动化流程 JSON 配置文件。

### 4. 辅助生成工具
*   **`gen_fieldid.ps1`**
    *   **功能**: Sonyflake ID 分解与生成工具（PowerShell）。
    *   **说明**: 依据特定的位布局（如 `39 bits time | 8 bits sequence | 16 bits machineID`）来分析或批量生成合法的新 `fieldID`等 Snowflake ID。

### 5. 文档资料 (`*.md`)
记录数据库表结构设计及相关的 API 请求规范。

*   **数据库表结构说明**: 包含 `db_module.md`、`db_page.md`、`db_layout.md`、`db_workflow.md`、`db_namespace.md`，分别详尽记录了相对应的底层 MySQL 存储表结构的设计、字段说明和约束。
*   **API 文档**: `api_module.md`，用于记录和阐明 Module 相关的操作 API（如用于更新或获取模块的 API 路由格式）。 

## 使用说明
所有的 Python 数据库相关脚本均接受命令行参数传递，典型用法包括：
- `python sync_XXX_to_db.py <json_文件_路径> [--dry-run]` 进行安全测试同步 
- `python export_XXX_from_db.py --all` 或使用其他特定参数进行批量导出。
相关的数据库凭证与配置必须预先在 `env.json` 等环境中准备就绪。
