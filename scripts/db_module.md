# 数据库表结构文档

## 数据库连接参数

> 数据库连接参数已统一维护在 [`env.json`](../../env.json) 中，按 环境/租户 区分。
> 脚本通过 `--env` 和 `--tenant` 参数指定要连接的数据库。

---

## 1. compose_module 表

| 字段名            | 类型                | 说明                |
|-------------------|---------------------|---------------------|
| id                | bigint unsigned     | 主键，自增ID        |
| rel_namespace     | bigint unsigned     | 关联命名空间ID      |
| handle            | varchar(64)         | 句柄/唯一标识       |
| name              | text                | 名称                |
| systemModuleField | json                | 系统模块字段        |
| meta              | json                | 元数据              |
| config            | json                | 配置                |
| created_at        | datetime            | 创建时间            |
| updated_at        | datetime            | 更新时间            |
| deleted_at        | datetime            | 删除时间            |
| type              | varchar(64)         | 类型                |
| isBlockDataTree   | tinyint(1)          | 是否为区块数据树    |

**说明：**
- 主键为 `id`。
- 采用 InnoDB 引擎，utf8mb4_unicode_ci 字符集。

---

## 3. 数据记录表 DDL 同步

> `sync_module_to_db.py` 在同步模块元数据后，会自动同步模块对应的**数据记录表**结构。

### 3.1 表名规则

表名由 `module.config.dal.ident` 模板决定，默认为 `{{namespace}}{{module}}`：
- `{{namespace}}` → namespace slug（如 `itsm`）
- `{{module}}` → module handle（如 `Incident`）
- 示例：`itsmIncident`

### 3.2 DDL 同步行为

| 场景 | 行为 |
|------|------|
| 表不存在 | `CREATE TABLE`，包含自定义字段列 + 系统固定列 |
| 表存在，新增字段 | `ALTER TABLE ADD COLUMN` |
| 表存在，字段类型变更 | `ALTER TABLE MODIFY COLUMN` |
| 表存在，字段被删除 | **仅警告，禁止自动删除列** |

### 3.3 字段 kind → 列类型映射

| kind | isMulti=false | isMulti=true |
|------|--------------|--------------|
| String, Select, Code, Tree, Url, Email, Color, Signature, Count | `text` | `json NOT NULL` |
| Record, User | `bigint unsigned DEFAULT NULL` | `json NOT NULL` |
| DateTime | `datetime DEFAULT NULL`（`onlyDate=true` 时为 `date DEFAULT NULL`） | `json NOT NULL` |
| Bool | `tinyint(1) DEFAULT NULL` | `json NOT NULL` |
| Number, LongNumber, BigInt | `decimal(10,0) DEFAULT NULL` | `json NOT NULL` |
| File | `json NOT NULL` | `json NOT NULL` |
| ExpiryTime | `datetime DEFAULT NULL` | `json NOT NULL` |

> `encodingStrategy: null` 的字段存储在 `values` JSON 列中，不生成独立列。

### 3.4 新增 CLI 参数

| 参数 | 说明 |
|------|------|
| `--no-ddl` | 跳过数据记录表的 DDL 同步 |
| `--namespace-slug` | 手动指定 namespace slug（不指定则自动推断） |

> **安全策略**：脚本禁止删除模块（`deleted_at` 始终为 NULL）、禁止删除数据表、禁止删除数据表中的列。多余列仅输出警告信息。

### 3.5 使用示例

```bash
# 完整同步（元数据 + DDL）
python sync_module_to_db.py Incident.json --env dev.dms --tenant mx

# 仅同步元数据，不修改数据表
python sync_module_to_db.py Incident.json --env dev.dms --tenant mx --no-ddl

# 预览模式
python sync_module_to_db.py Incident.json --env dev.dms --tenant mx --dry-run
```

---

## 2. compose_module_field 表

| 字段名         | 类型                | 说明                |
|----------------|---------------------|---------------------|
| id             | bigint unsigned     | 主键，自增ID        |
| rel_module     | bigint unsigned     | 关联模块ID          |
| place          | decimal(10,0)       | 排序位置            |
| kind           | text                | 字段类型            |
| options        | json                | 字段选项            |
| name           | text                | 字段名称            |
| label          | text                | 字段标签            |
| config         | json                | 字段配置            |
| is_required    | tinyint(1)          | 是否必填            |
| is_multi       | tinyint(1)          | 是否多值            |
| default_value  | json                | 默认值              |
| expressions    | json                | 表达式              |
| created_at     | datetime            | 创建时间            |
| updated_at     | datetime            | 更新时间            |
| deleted_at     | datetime            | 删除时间            |
| serial_update  | bigint unsigned     | 序列更新标识        |
| serial         | decimal(10,0)       | 序列号              |
| is_name        | tinyint(1)          | 是否为名称字段      |

**说明：**
- 主键为 `id`。
- 采用 InnoDB 引擎，utf8mb4_unicode_ci 字符集。
