# 数据库表结构文档

## 数据库连接参数

> 数据库连接参数已统一维护在 [`env.json`](../../env.json) 中，按 环境/租户 区分。
> 脚本通过 `--env` 和 `--tenant` 参数指定要连接的数据库。

---

## compose_page_layout 表

| 字段名         | 类型                | 说明                |
|----------------|---------------------|---------------------|
| id             | bigint unsigned     | 主键                |
| handle         | varchar(64)         | 句柄/唯一标识       |
| page_id        | bigint unsigned     | 关联页面ID          |
| parent_id      | bigint unsigned     | 父级布局ID          |
| rel_namespace  | bigint unsigned     | 关联命名空间ID      |
| weight         | decimal(10,0)       | 排序权重（默认0）   |
| meta           | json                | 元数据              |
| config         | json                | 配置                |
| blocks         | json                | 布局区块            |
| owned_by       | bigint unsigned     | 拥有者ID（默认0）   |
| created_at     | datetime            | 创建时间            |
| updated_at     | datetime            | 更新时间            |
| deleted_at     | datetime            | 删除时间            |

**说明：**
- 主键为 `id`。
- 采用 InnoDB 引擎，utf8mb4_unicode_ci 字符集。
