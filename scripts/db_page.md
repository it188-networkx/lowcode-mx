# 数据库表结构文档

## 数据库连接参数

> 数据库连接参数已统一维护在 [`env.json`](../../env.json) 中，按 环境/租户 区分。
> 脚本通过 `--env` 和 `--tenant` 参数指定要连接的数据库。

---

## compose_page 表

| 字段名         | 类型                | 说明                |
|----------------|---------------------|---------------------|
| id             | bigint unsigned     | 主键                |
| title          | text                | 页面标题            |
| handle         | varchar(64)         | 句柄/唯一标识       |
| self_id        | bigint unsigned     | 自身ID（父级关联）  |
| rel_module     | bigint unsigned     | 关联模块ID          |
| rel_namespace  | bigint unsigned     | 关联命名空间ID      |
| meta           | json                | 元数据              |
| config         | json                | 配置                |
| blocks         | json                | 页面区块            |
| visible        | tinyint(1)          | 是否可见（默认1）   |
| weight         | decimal(10,0)       | 排序权重（默认0）   |
| description    | text                | 描述                |
| created_at     | datetime            | 创建时间            |
| updated_at     | datetime            | 更新时间            |
| deleted_at     | datetime            | 删除时间            |

**说明：**
- 主键为 `id`。
- 采用 InnoDB 引擎，utf8mb4_unicode_ci 字符集。