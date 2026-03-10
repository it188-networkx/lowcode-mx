# `scripts` 目录代理指南 (AGENTS.md)

本目录包含了用于管理、同步和导出各个低代码核心组件（如 Module、Page、Layout、Workflow 等）的自动化脚本和文档。所有同步/导出脚本均通过 API 与服务端交互。

## 目录结构与功能概览

### 1. API 交互与核心工具
这些工具用于管理 API 连接配置或执行特定的跨功能扫描任务。

*   **`api_utils.py`**
    *   **功能**: 统一的 API 连接配置加载工具。
    *   **说明**: 负责从项目的 `src/env.json` 配置文件中按"环境/租户"读取 API 连接参数（baseUrl、headers）。其他所有同步或导出脚本都依赖该模块。
*   **`scan_function_refs.py`**
    *   **功能**: 工作流函数引用扫描脚本。
    *   **说明**: 用于扫描所有工作流的 JSON 配置文件，批量提取并分析工作流中引用了哪些 Gval 函数以及对应的参数情况。

### 2. 同步脚本 (Sync `*_to_api`)
将本地的 JSON 配置文件通过 API 同步（包括新增与更新）到服务端。

*   **`sync_module_to_api.py`**：将 Module（模块）及它的 Module Field（字段）信息同步到服务端。
*   **`sync_page_to_api.py`**：将 Page（页面）的 JSON 配置文件同步到服务端。
*   **`sync_layout_to_api.py`**：将 Layout（布局）配置信息同步到服务端。
*   **`sync_workflow_to_api.py`**：将 Workflow（工作流）包含的各项信息与触发器同步到服务端。
*   **`sync_namespace_to_api.py`**：将低代码应用 Namespace（命名空间）的配置与信息同步到服务端。

### 3. 导出脚本 (Export `*_from_api`)
从服务端 API 查询各项资源配置并导出为符合标准结构的 JSON 配置文件。

*   **`export_module_from_api.py`**：从 API 查询导出模块及字段数据。
*   **`export_page_from_api.py`**：从 API 查询导出页面数据并生成相应 JSON 文件。
*   **`export_layout_from_api.py`**：从 API 查询导出布局数据到 JSON。
*   **`export_workflow_from_api.py`**：从 API 导出工作流/触发器为自动化流程 JSON 配置文件。

### 4. 辅助生成工具
*   **`gen_fieldid.ps1`**
    *   **功能**: Sonyflake ID 分解与生成工具（PowerShell）。
    *   **说明**: 依据特定的位布局（如 `39 bits time | 8 bits sequence | 16 bits machineID`）来分析或批量生成合法的新 `fieldID`等 Snowflake ID。

### 5. 文档资料 (`*.md`)
记录 API 请求规范。

*   **API 文档**: `api/` 目录下包含 `api_module.md`、`api_page.md`、`api_layout.md`、`api_namespace.md`、`api_workflow.md`，分别记录各资源的 API 路由格式与请求规范。

## 使用说明
所有的 Python 脚本均接受命令行参数传递，典型用法包括：
- `python sync_XXX_to_api.py <json_文件_路径> [--dry-run]` 进行安全测试同步
- `python export_XXX_from_api.py --all` 或使用其他特定参数进行批量导出。
相关的 API 配置必须预先在 `src/env.json` 中准备就绪。
