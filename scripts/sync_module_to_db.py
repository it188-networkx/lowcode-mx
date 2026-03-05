#!/usr/bin/env python3
"""
将模块 JSON 配置文件同步（新增/更新）到 MySQL 数据库的
compose_module 和 compose_module_field 两张表中。

数据库连接参数从 configuration/db_config.json 中读取。

用法:
    python sync_module_to_db.py <json_file>
    python sync_module_to_db.py <json_file> --dry-run

示例:
    python sync_module_to_db.py TestModule.json
    python sync_module_to_db.py TestModule.json --dry-run
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

# 将 configuration/ 目录加入模块搜索路径，以便导入 db_utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from db_utils import load_db_config, load_tenant_config

try:
    import pymysql
except ImportError:
    pymysql = None  # dry-run 模式不需要 pymysql


# ────────────────────────────── 解析 JSON ──────────────────────────────

def load_module_data(filepath: str) -> dict:
    """加载模块 JSON 文件，返回模块对象 dict。"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if isinstance(data, dict) and "moduleID" in data:
        return data

    # 支持 {"type": "module", "list": [{...}]} 包装格式
    if isinstance(data, dict) and "list" in data and isinstance(data["list"], list):
        for item in data["list"]:
            if isinstance(item, dict) and "moduleID" in item:
                return item

    raise ValueError(f"无法识别 JSON 文件格式: {filepath}")


# ────────────────────────── 时间格式转换 ───────────────────────────

def parse_datetime(value) -> str | None:
    """将 ISO 8601 时间字符串转为 MySQL datetime 格式，空值返回 None。"""
    if not value:
        return None
    try:
        # 处理 "2026-02-24T07:47:30.000Z" 格式
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return None


# ────────────────────── 构建 compose_module 行 ──────────────────────

def build_module_row(module: dict) -> dict:
    """从模块 JSON 构建 compose_module 表的一行数据。"""
    return {
        "id": int(module["moduleID"]),
        "rel_namespace": int(module["namespaceID"]),
        "handle": module.get("handle", ""),
        "name": module.get("name", ""),
        "systemModuleField": json.dumps(
            module.get("systemModuleField", []), ensure_ascii=False
        ),
        "meta": json.dumps(module.get("meta", {}), ensure_ascii=False),
        "config": json.dumps(module.get("config", {}), ensure_ascii=False),
        "created_at": parse_datetime(module.get("createdAt"))
        or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": parse_datetime(module.get("updatedAt")),
        "deleted_at": None,  # 禁止通过脚本删除模块（忽略 JSON 中的 deletedAt）
        "type": module.get("type", ""),
        "isBlockDataTree": 1 if module.get("isBlockDataTree") else 0,
    }


# ──────────────── 构建 compose_module_field 行列表 ────────────────

def build_field_rows(module: dict) -> list[dict]:
    """从模块 JSON 的 fields 数组构建 compose_module_field 表的行数据列表。"""
    module_id = int(module["moduleID"])
    fields = module.get("fields", [])
    rows = []

    for idx, field in enumerate(fields):
        field_id = field.get("fieldID")
        if not field_id or str(field_id) == "0":
            print(f"  ⚠ 跳过 fieldID 为 0 或空的字段: {field.get('name', '?')}")
            continue

        rows.append(
            {
                "id": int(field_id),
                "rel_module": module_id,
                "place": idx,
                "kind": field.get("kind", ""),
                "options": json.dumps(
                    field.get("options", {}), ensure_ascii=False
                ),
                "name": field.get("name", ""),
                "label": field.get("label", ""),
                "config": json.dumps(
                    field.get("config", {}), ensure_ascii=False
                ),
                "is_required": 1 if field.get("isRequired") else 0,
                "is_multi": 1 if field.get("isMulti") else 0,
                "default_value": json.dumps(
                    field.get("defaultValue", []), ensure_ascii=False
                ),
                "expressions": json.dumps(
                    field.get("expressions", {}), ensure_ascii=False
                ),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": None,
                "deleted_at": None,
                "serial_update": 0,
                "serial": 0,
                "is_name": 1 if field.get("isName") else 0,
            }
        )

    return rows


# ──────────────────────── UPSERT SQL 生成 ─────────────────────────

UPSERT_MODULE_SQL = """
INSERT INTO compose_module
    (id, rel_namespace, handle, name, systemModuleField, meta, config,
     created_at, updated_at, deleted_at, type, isBlockDataTree)
VALUES
    (%(id)s, %(rel_namespace)s, %(handle)s, %(name)s, %(systemModuleField)s,
     %(meta)s, %(config)s, %(created_at)s, %(updated_at)s, %(deleted_at)s,
     %(type)s, %(isBlockDataTree)s)
ON DUPLICATE KEY UPDATE
    rel_namespace     = VALUES(rel_namespace),
    handle            = VALUES(handle),
    name              = VALUES(name),
    systemModuleField = VALUES(systemModuleField),
    meta              = VALUES(meta),
    config            = VALUES(config),
    updated_at        = NOW(),
    type              = VALUES(type),
    isBlockDataTree   = VALUES(isBlockDataTree);
"""

UPSERT_FIELD_SQL = """
INSERT INTO compose_module_field
    (id, rel_module, place, kind, options, name, label, config,
     is_required, is_multi, default_value, expressions,
     created_at, updated_at, deleted_at, serial_update, serial, is_name)
VALUES
    (%(id)s, %(rel_module)s, %(place)s, %(kind)s, %(options)s, %(name)s,
     %(label)s, %(config)s, %(is_required)s, %(is_multi)s,
     %(default_value)s, %(expressions)s, %(created_at)s, %(updated_at)s,
     %(deleted_at)s, %(serial_update)s, %(serial)s, %(is_name)s)
ON DUPLICATE KEY UPDATE
    rel_module    = VALUES(rel_module),
    place         = VALUES(place),
    kind          = VALUES(kind),
    options       = VALUES(options),
    name          = VALUES(name),
    label         = VALUES(label),
    config        = VALUES(config),
    is_required   = VALUES(is_required),
    is_multi      = VALUES(is_multi),
    default_value = VALUES(default_value),
    expressions   = VALUES(expressions),
    updated_at    = NOW(),
    serial_update = VALUES(serial_update),
    serial        = VALUES(serial),
    is_name       = VALUES(is_name);
"""


# ──────────────────── 数据表 DDL 映射常量 ──────────────────────

# 系统固定列（每张数据记录表都自动包含）
SYSTEM_COLUMNS = OrderedDict([
    ('id',            'bigint unsigned NOT NULL'),
    ('rel_module',    'bigint unsigned NOT NULL'),
    ('deleted_by',    'bigint unsigned DEFAULT NULL'),
    ('rel_namespace', 'bigint unsigned NOT NULL'),
    ('revision',      "decimal(10,0) NOT NULL DEFAULT '0'"),
    ('meta',          'json NOT NULL'),
    ('owned_by',      'bigint unsigned NOT NULL'),
    ('created_at',    'datetime NOT NULL'),
    ('created_by',    'bigint unsigned NOT NULL'),
    ('updated_at',    'datetime DEFAULT NULL'),
    ('updated_by',    'bigint unsigned DEFAULT NULL'),
    ('deleted_at',    'datetime DEFAULT NULL'),
])

SYSTEM_COLUMN_NAMES = set(SYSTEM_COLUMNS.keys())

# 字段 kind → DB 列类型映射（isMulti=false 时使用）
KIND_COLUMN_TYPE = {
    'String':     'text',
    'Select':     'text',
    'Code':       'text',
    'Tree':       'text',
    'Url':        'text',
    'Email':      'text',
    'Color':      'text',
    'Signature':  'text',
    'Count':      'text',
    'Record':     'bigint unsigned DEFAULT NULL',
    'User':       'bigint unsigned DEFAULT NULL',
    'DateTime':   'datetime DEFAULT NULL',
    'ExpiryTime': 'datetime DEFAULT NULL',
    'Bool':       'tinyint(1) DEFAULT NULL',
    'Number':     'decimal(10,0) DEFAULT NULL',
    'LongNumber': 'decimal(10,0) DEFAULT NULL',
    'BigInt':     'decimal(10,0) DEFAULT NULL',
    'File':       'json NOT NULL',
}

# isMulti=true → 统一为 json NOT NULL
MULTI_VALUE_COLUMN_TYPE = 'json NOT NULL'


# ──────────────────── 数据表 DDL 工具函数 ──────────────────────

def get_field_column_def(field: dict) -> tuple | None:
    """
    根据字段定义返回 (column_name, column_type_spec) 元组。

    系统字段或 encodingStrategy 为 None 的字段返回 None。
    """
    if field.get('isSystem'):
        return None

    encoding = field.get('config', {}).get('dal', {}).get('encodingStrategy')
    if encoding is None:
        return None

    name = field.get('name', '')
    if not name:
        return None

    is_multi = field.get('isMulti', False)
    kind = field.get('kind', '')

    if is_multi:
        col_type = MULTI_VALUE_COLUMN_TYPE
    elif kind == 'DateTime' and field.get('options', {}).get('onlyDate'):
        col_type = 'date DEFAULT NULL'
    else:
        col_type = KIND_COLUMN_TYPE.get(kind)
        if col_type is None:
            print(f"  ⚠ 未知字段类型 '{kind}'，使用默认 text: {name}")
            col_type = 'text'

    # 列名：json 编码使用 ident，plain 编码使用字段 name
    if isinstance(encoding, dict) and 'json' in encoding:
        col_name = encoding['json'].get('ident', name)
    else:
        col_name = name

    return (col_name, col_type)


def resolve_table_name_from_template(
    ident_template: str, namespace_slug: str, module_handle: str
) -> str:
    """根据 ident 模板解析实际表名。"""
    return (
        ident_template
        .replace('{{namespace}}', namespace_slug)
        .replace('{{module}}', module_handle)
    )


def _parse_col_spec(spec: str) -> tuple:
    """
    解析列类型规格字符串为 (base_type, is_not_null)。

    示例：
        'text' → ('text', False)
        'bigint unsigned DEFAULT NULL' → ('bigint unsigned', False)
        'json NOT NULL' → ('json', True)
        "decimal(10,0) NOT NULL DEFAULT '0'" → ('decimal(10,0)', True)
    """
    s = spec.strip()
    not_null = bool(re.search(r'\bNOT\s+NULL\b', s, re.I))
    s = re.sub(r'\s*\bNOT\s+NULL\b', '', s, flags=re.I)
    s = re.sub(r"\s*DEFAULT\s+(?:NULL|'[^']*'|\S+)", '', s, flags=re.I)
    return s.strip().lower(), not_null


def _normalize_db_type(column_type: str) -> str:
    """规范化 INFORMATION_SCHEMA 的 COLUMN_TYPE 以便比较。"""
    t = column_type.lower().strip()
    # MySQL 8.0.17 之前可能带显示宽度，如 bigint(20) unsigned
    t = re.sub(r'bigint\(\d+\)', 'bigint', t)
    t = re.sub(r'int\(\d+\)', 'int', t)
    return t


def _column_needs_update(expected_spec: str, db_info: dict) -> bool:
    """判断现有列是否需要 ALTER TABLE MODIFY。"""
    expected_type, expected_not_null = _parse_col_spec(expected_spec)
    db_type = _normalize_db_type(db_info['type'])
    db_not_null = db_info['nullable'] == 'NO'
    return expected_type != db_type or expected_not_null != db_not_null


def _infer_namespace_slug(json_path: str) -> str | None:
    """
    从 JSON 文件路径推断 namespace slug。

    路径格式: .../dev.dms/mx/{namespace}/module/{Handle}.json
    """
    parts = Path(json_path).resolve().parts
    for i, part in enumerate(parts):
        if part == 'module' and i > 0:
            return parts[i - 1]
    return None


def _get_namespace_slug_from_db(cursor, namespace_id: int) -> str:
    """从 compose_namespace 表查询 namespace slug。"""
    cursor.execute(
        "SELECT slug FROM compose_namespace WHERE id = %s AND deleted_at IS NULL",
        (namespace_id,),
    )
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"未找到 namespaceID={namespace_id} 的命名空间")
    return row['slug']


def _build_create_table_sql(
    table_name: str, expected_columns: OrderedDict
) -> str:
    """生成 CREATE TABLE SQL。"""
    col_defs = []

    # 自定义字段列
    for col_name, col_type in expected_columns.items():
        col_defs.append(f"  `{col_name}` {col_type}")

    # 系统固定列
    for col_name, col_type in SYSTEM_COLUMNS.items():
        col_defs.append(f"  `{col_name}` {col_type}")

    # 主键和索引
    col_defs.append("  PRIMARY KEY (`id`)")
    col_defs.append(
        f"  KEY `{table_name}_created_at_IDX` (`created_at`) USING BTREE"
    )

    return (
        f"CREATE TABLE `{table_name}` (\n"
        + ",\n".join(col_defs)
        + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    )


def _build_expected_columns(module: dict) -> OrderedDict:
    """从模块 fields 数组构建期望的自定义列定义。"""
    expected = OrderedDict()
    for field in module.get('fields', []):
        result = get_field_column_def(field)
        if result:
            col_name, col_type = result
            expected[col_name] = col_type
    return expected


# ──────────────── 数据表 DDL 同步主函数 ────────────────────

def sync_data_table(
    module: dict,
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    dry_run: bool = False,
    namespace_slug: str = None,
    json_path: str = None,
):
    """
    同步模块对应的数据记录表结构（CREATE / ALTER TABLE）。

    逻辑:
    1. 从 module fields 推导期望的列定义
    2. 解析表名 ({{namespace}}{{module}})
    3. 如果表不存在 → CREATE TABLE
    4. 如果表已存在 → 比较列差异 → ALTER TABLE (ADD/MODIFY COLUMN)

    注意: 禁止删除表和列，多余列仅发出警告。
    """
    # ── 推导期望列定义 ──
    expected_columns = _build_expected_columns(module)
    if not expected_columns:
        print("\n⚠ 模块没有可映射的自定义字段，跳过数据表同步")
        return

    # ── 解析表名 ──
    ident_template = (
        module.get('config', {}).get('dal', {}).get('ident', '{{namespace}}{{module}}')
    )
    module_handle = module.get('handle', '')
    if not module_handle:
        print("\n⚠ 模块没有 handle，无法确定表名，跳过数据表同步")
        return

    ns_slug = namespace_slug

    # ── dry-run 模式：仅打印预览 ──
    if dry_run:
        if not ns_slug:
            ns_slug = _infer_namespace_slug(json_path) if json_path else None
        if not ns_slug:
            print(
                "\n⚠ 预览模式下无法确定 namespace slug"
                "（请通过 --namespace-slug 指定），跳过数据表预览"
            )
            return

        table_name = resolve_table_name_from_template(
            ident_template, ns_slug, module_handle
        )
        print(f"\n── 数据表预览: `{table_name}` ──")
        print(f"  自定义列 ({len(expected_columns)})：")
        for col_name, col_type in expected_columns.items():
            print(f"    `{col_name}` {col_type}")
        print(f"  系统固定列: {len(SYSTEM_COLUMNS)} 个")

        create_sql = _build_create_table_sql(table_name, expected_columns)
        print(f"\n  [预览] 建表 SQL（若表不存在）:\n{create_sql};")
        return

    # ── 实际同步模式 ──
    if pymysql is None:
        print("❌ 数据表同步需要 pymysql，请先安装: pip install pymysql")
        return

    conn = pymysql.connect(
        host=host, port=port, user=user, password=password,
        database=database, charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cur:
            # 获取 namespace slug
            if not ns_slug:
                ns_id = int(module.get('namespaceID', 0))
                ns_slug = _get_namespace_slug_from_db(cur, ns_id)

            table_name = resolve_table_name_from_template(
                ident_template, ns_slug, module_handle
            )
            print(f"\n── 数据表同步: `{table_name}` (namespace={ns_slug}) ──")

            # 检查表是否存在
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
                (database, table_name),
            )
            exists = cur.fetchone()['cnt'] > 0

            if not exists:
                # ── 新建表 ──
                create_sql = _build_create_table_sql(table_name, expected_columns)
                cur.execute(create_sql)
                print(
                    f"  ✔ 已创建数据表 `{table_name}` "
                    f"({len(expected_columns)} 个自定义列 + {len(SYSTEM_COLUMNS)} 个系统列)"
                )
            else:
                # ── 比较并更新表结构（仅 ADD/MODIFY，不 DROP） ──
                _sync_existing_table(
                    cur, table_name, database, expected_columns
                )

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 数据表同步失败，已回滚: {e}")
        raise
    finally:
        conn.close()


def _sync_existing_table(
    cursor, table_name: str, database: str,
    expected_columns: OrderedDict,
):
    """
    对已存在的数据表执行结构比较与 ALTER TABLE。

    - 新增列：expected 中有、DB 中无
    - 修改列：两边都有但类型不匹配
    - 多余列：仅警告，禁止删除
    """
    # 获取现有列信息
    cursor.execute(
        "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT "
        "FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY ORDINAL_POSITION",
        (database, table_name),
    )
    existing = {}
    for row in cursor.fetchall():
        existing[row['COLUMN_NAME']] = {
            'type': row['COLUMN_TYPE'],
            'nullable': row['IS_NULLABLE'],
            'default': row['COLUMN_DEFAULT'],
        }

    alter_stmts = []

    # 1. 新增列
    for col_name, col_type in expected_columns.items():
        if col_name not in existing:
            alter_stmts.append(f"ADD COLUMN `{col_name}` {col_type}")
            print(f"  ＋ 新增列: `{col_name}` {col_type}")

    # 2. 类型变更
    for col_name, col_type in expected_columns.items():
        if col_name in existing:
            if _column_needs_update(col_type, existing[col_name]):
                alter_stmts.append(f"MODIFY COLUMN `{col_name}` {col_type}")
                print(
                    f"  ⇄ 修改列: `{col_name}` → {col_type} "
                    f"(原: {existing[col_name]['type']}, "
                    f"nullable={existing[col_name]['nullable']})"
                )

    # 3. 删除列（仅非系统列）
    existing_custom = {
        k for k in existing if k not in SYSTEM_COLUMN_NAMES
    }
    for col_name in sorted(existing_custom):
        if col_name not in expected_columns:
            print(
                f"  ⚠ 多余列: `{col_name}` "
                f"(原: {existing[col_name]['type']}，禁止自动删除)"
            )

    if not alter_stmts:
        print(f"  ✔ 数据表 `{table_name}` 结构已是最新，无需修改")
        return

    sql = f"ALTER TABLE `{table_name}` " + ", ".join(alter_stmts)
    cursor.execute(sql)
    print(
        f"  ✔ 已更新数据表 `{table_name}` ({len(alter_stmts)} 处变更)"
    )


# ────────────────────────── 数据库操作 ──────────────────────────────

def sync_to_database(
    module_row: dict,
    field_rows: list[dict],
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    dry_run: bool = False,
):
    """将模块数据 upsert 到数据库。"""
    if dry_run:
        print("\n[预览模式] 以下数据不会实际写入数据库\n")
        print("── compose_module ──")
        for k, v in module_row.items():
            display = v if len(str(v)) < 120 else str(v)[:120] + "..."
            print(f"  {k:20s} = {display}")
        print(f"\n── compose_module_field ({len(field_rows)} 条) ──")
        for row in field_rows:
            print(f"  id={row['id']}  name={row['name']!r:20s}  "
                  f"kind={row['kind']!r:12s}  label={row['label']!r}")
        return

    if pymysql is None:
        print("❌ 实际写入数据库需要 pymysql，请先安装: pip install pymysql")
        sys.exit(1)

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cur:
            # 1. upsert compose_module
            cur.execute(UPSERT_MODULE_SQL, module_row)
            print(f"✔ compose_module  upsert 完成  (id={module_row['id']})")

            # 2. upsert compose_module_field
            for row in field_rows:
                cur.execute(UPSERT_FIELD_SQL, row)
                print(
                    f"  ✔ compose_module_field  upsert  "
                    f"id={row['id']}  name={row['name']!r}"
                )

        conn.commit()
        print(f"\n✅ 同步成功! 模块 1 条, 字段 {len(field_rows)} 条。")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 同步失败，已回滚: {e}")
        raise
    finally:
        conn.close()


# ──────────────────── 调用 Module 更新 API ────────────────────────

# 请求体中需要保留的字段（API 不接受 moduleID / namespaceID 等）
_API_BODY_KEYS = [
    "name", "handle", "type", "isBlockDataTree",
    "systemModuleField", "fields", "config",
    "meta", "labels",
]


def call_module_update_api(
    module: dict,
    *,
    base_url: str,
    headers: dict,
    dry_run: bool = False,
):
    """
    调用 POST /compose/namespace/{namespaceID}/module/{moduleID}
    触发服务端刷新模块缓存。

    Args:
        module:   完整的模块 JSON dict（含 moduleID / namespaceID）。
        base_url: 租户 API 基地址（来自 env.json）。
        headers:  租户公共请求头（来自 env.json，含 X-SS-EMAIL / Content-Type）。
        dry_run:  预览模式，不实际发送请求。
    """
    namespace_id = module["namespaceID"]
    module_id = module["moduleID"]
    url = f"{base_url}/compose/namespace/{namespace_id}/module/{module_id}"

    # 构建请求体：只保留 API 需要的字段
    body = {k: module[k] for k in _API_BODY_KEYS if k in module}
    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

    # 合并请求头
    req_headers = dict(headers)
    req_headers["X-NAMESPACE-ID"] = str(namespace_id)
    # 确保 Content-Type 包含 charset
    if "Content-Type" not in req_headers:
        req_headers["Content-Type"] = "application/json; charset=utf-8"

    if dry_run:
        print(f"\n── API 预览 ──")
        print(f"  POST {url}")
        print(f"  Headers: {json.dumps(req_headers, ensure_ascii=False)}")
        print(f"  Body: {len(body_bytes)} bytes")
        return

    print(f"\n── 调用更新 API ──")
    print(f"  POST {url}")

    req = urllib.request.Request(
        url, data=body_bytes, headers=req_headers, method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            resp_body = resp.read().decode("utf-8", errors="replace")
            if status == 200:
                print(f"  ✔ API 调用成功 (HTTP {status})")
            else:
                print(f"  ⚠ API 返回非 200: HTTP {status}")
                print(f"  响应: {resp_body[:300]}")
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"  ❌ API 调用失败: HTTP {e.code} {e.reason}")
        if body_text:
            print(f"  响应: {body_text[:300]}")
    except urllib.error.URLError as e:
        print(f"  ❌ API 连接失败: {e.reason}")
    except Exception as e:
        print(f"  ❌ API 调用异常: {e}")


# ──────────────────────────── 主入口 ────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="将模块 JSON 配置同步到 MySQL compose_module / compose_module_field 表"
    )
    parser.add_argument(
        "json_file",
        help="模块 JSON 文件路径，如 TestModule.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只打印将要写入的数据，不连接数据库",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="环境名（如 dev），不指定则使用 env.json 的 active 值",
    )
    parser.add_argument(
        "--tenant",
        type=str,
        default=None,
        help="租户名（如 mx），不指定则使用该环境下的第一个租户",
    )
    parser.add_argument(
        "--no-ddl",
        action="store_true",
        help="跳过数据记录表的 DDL 同步（CREATE/ALTER TABLE）",
    )
    parser.add_argument(
        "--namespace-slug",
        type=str,
        default=None,
        help="命名空间 slug（如 itsm），用于解析数据表名；不指定则自动从数据库或文件路径推断",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="跳过调用 Module 更新 API（默认会在同步完成后调用 API 刷新缓存）",
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)

    # 从 env.json 读取租户完整配置（含 db、baseUrl、headers）
    tenant_config = load_tenant_config(env=args.env, tenant=args.tenant)
    db_config = tenant_config["db"]
    print(f"🔗 数据库连接: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    print(f"📄 正在读取: {json_path}")
    module = load_module_data(str(json_path))
    print(f"   模块名称: {module.get('name')}")
    print(f"   moduleID: {module.get('moduleID')}")

    module_row = build_module_row(module)
    field_rows = build_field_rows(module)
    print(f"   自定义字段数: {len(field_rows)}")

    sync_to_database(
        module_row,
        field_rows,
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        dry_run=args.dry_run,
    )

    # ── 数据记录表 DDL 同步 ──
    if not args.no_ddl:
        sync_data_table(
            module,
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            dry_run=args.dry_run,
            namespace_slug=args.namespace_slug,
            json_path=str(json_path),
        )
    else:
        print("\nℹ 已跳过数据表 DDL 同步 (--no-ddl)")

    # ── 调用 Module 更新 API ──
    if not args.no_api:
        base_url = tenant_config["baseUrl"]
        api_headers = tenant_config["headers"]
        if not base_url:
            print("\n⚠ env.json 中未配置 baseUrl，跳过 API 调用")
        else:
            call_module_update_api(
                module,
                base_url=base_url,
                headers=api_headers,
                dry_run=args.dry_run,
            )
    else:
        print("\nℹ 已跳过 API 调用 (--no-api)")


if __name__ == "__main__":
    main()
