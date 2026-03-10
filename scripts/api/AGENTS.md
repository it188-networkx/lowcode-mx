# `scripts/api` 目录代理指南

## 目录用途

- 本目录存放各资源类型的 REST API 接口文档。
- 每个文件对应一类资源的完整 API 规范（请求方法、路径、参数、响应格式）。

## 文件清单

- `api_module.md` — Module（模块）API，路径前缀 `/compose/namespace/{namespaceID}/module/`。
- `api_page.md` — Page（页面）API，路径前缀 `/compose/namespace/{namespaceID}/page/`。
- `api_layout.md` — Page Layout（布局）API，路径前缀 `/compose/namespace/{namespaceID}/page-layout`。
- `api_namespace.md` — Namespace（命名空间）API，路径前缀 `/compose/namespace/`。
- `api_workflow.md` — Workflow（工作流）API，路径前缀 `/automation/workflows/`；触发器路径为 `/automation/triggers/`。

## 命名规则

- 文件命名格式为 `api_{resource}.md`，resource 使用小写单数形式。
- 新增资源类型文档时须遵循此命名惯例并更新本文件的文件清单。

## 编写约定

- 每份文档以 `# {Resource} API 接口文档` 作为标题。
- 公共请求头（Authorization、Content-Type、X-SS-EMAIL 等）在文档顶部或首个接口处统一说明，后续接口不重复。
- 每个接口包含：请求方法与路径、路径参数表、查询参数表（或请求体）、字段说明表、响应示例。
- Compose 类资源（module、page、layout）的路径包含 `{namespaceID}`；Automation 类资源（workflow、trigger）的路径不包含。

## 注意事项

- API baseUrl 和 headers 从 `src/env.json` 中读取，具体路径为 `environments.{env}.tenants.{tenant}`。
- 写操作（PUT）使用 `putHeaders`，读操作（GET）使用 `headers`。
