# topitms.com 目录说明

本目录主要用于存放 `topitms.com` 租户或域名相关的低代码配置资产。根据不同的业务模块或子系统划分，包含具体的数据模型、页面、布局以及工作流配置。

## 目录结构
- **mx/**: 可能代表特定的区域、租户或环境（如 Mexico 环境）的配置。
  - **itsm/**: IT 服务管理 (ITSM) 系统相关的低代码资产。
    - `layout/`: 布局配置
    - `module/`: 数据模型配置
    - `page/`: 页面配置
  - **wms/**: 仓储管理系统 (WMS) 相关的低代码资产。
    - `layout/`: 布局配置
    - `module/`: 数据模型配置
    - `page/`: 页面配置
  - **workflow/**: 存放特定于该业务环境的工作流 JSON 配置文件（如 Incident、Service Application、ITOM alerts 等自动化流程）。

此目录结构支持低代码平台的元数据导出与同步。