# 数据库表结构文档

## 数据库连接参数

> 数据库连接参数已统一维护在 [`env.json`](../../env.json) 中，按 环境/租户 区分。
> 脚本通过 `--env` 和 `--tenant` 参数指定要连接的数据库。

---

## automation_workflows 表

| 字段名         | 类型                | 说明                  |
|----------------|---------------------|-----------------------|
| id             | bigint unsigned     | 主键                  |
| handle         | varchar(64)         | 句柄/唯一标识         |
| meta           | json                | 元数据                |
| enabled        | tinyint(1)          | 是否启用（默认1）     |
| trace          | tinyint(1)          | 是否追踪（默认0）     |
| keep_sessions  | decimal(10,0)       | 保留会话数（默认0）   |
| scope          | json                | 作用域                |
| steps          | json                | 步骤                  |
| paths          | json                | 路径                  |
| issues         | json                | 问题                  |
| run_as         | bigint unsigned     | 执行身份ID（默认0）   |
| owned_by       | bigint unsigned     | 拥有者ID（默认0）     |
| created_at     | datetime            | 创建时间              |
| updated_at     | datetime            | 更新时间              |
| deleted_at     | datetime            | 删除时间              |
| created_by     | bigint unsigned     | 创建者ID（默认0）     |
| updated_by     | bigint unsigned     | 更新者ID（默认0）     |
| deleted_by     | bigint unsigned     | 删除者ID（默认0）     |
| rel_namespace  | bigint unsigned     | 关联命名空间ID（默认0）|

**说明：**
- 主键为 `id`。
- 采用 InnoDB 引擎，utf8mb4_unicode_ci 字符集。

---

## automation_triggers 表

| 字段名         | 类型                | 说明                    |
|----------------|---------------------|-------------------------|
| id             | bigint unsigned     | 主键                    |
| rel_workflow   | bigint unsigned     | 关联工作流ID            |
| rel_step       | bigint unsigned     | 关联步骤ID              |
| enabled        | tinyint(1)          | 是否启用（默认1）       |
| transaction    | tinyint(1)          | 是否事务（默认1）       |
| meta           | json                | 元数据                  |
| resource_type  | varchar(64)         | 资源类型                |
| event_type     | text                | 事件类型                |
| constraints    | json                | 约束条件                |
| input          | json                | 输入参数                |
| owned_by       | bigint unsigned     | 拥有者ID（默认0）       |
| created_at     | datetime            | 创建时间                |
| updated_at     | datetime            | 更新时间                |
| deleted_at     | datetime            | 删除时间                |
| created_by     | bigint unsigned     | 创建者ID（默认0）       |
| updated_by     | bigint unsigned     | 更新者ID（默认0）       |
| deleted_by     | bigint unsigned     | 删除者ID（默认0）       |
| weight         | decimal(10,0)       | 排序权重（默认0）       |
| type           | decimal(10,0)       | 类型（默认2）           |
| async          | tinyint(1)          | 是否异步（默认0）       |

**说明：**
- 主键为 `id`。
- 采用 InnoDB 引擎，utf8mb4_unicode_ci 字符集。
