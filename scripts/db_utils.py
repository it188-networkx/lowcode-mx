#!/usr/bin/env python3
"""
统一的数据库连接配置加载工具。

所有子目录（page / module / layout / workflow）中的 Python 脚本
均通过此模块从 configuration/env.json 中按 环境/租户 读取数据库连接参数，
避免在每个脚本中重复维护连接信息。

用法（在子目录脚本中）:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from db_utils import load_db_config

    # 按环境和租户加载
    config = load_db_config(env="dev", tenant="mx")
"""

import json
from pathlib import Path

# env.json 位于 src/ 目录下（scripts/ 的兄弟目录）
_ENV_JSON_PATH = Path(__file__).resolve().parent.parent / "src" / "env.json"

_DEFAULTS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "itsm",
}


def _load_env_json(env_json_path: Path = _ENV_JSON_PATH) -> dict:
    """加载 env.json 并返回完整内容。"""
    if not env_json_path.exists():
        raise FileNotFoundError(f"未找到配置文件 {env_json_path}")
    with open(env_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_db_config(env: str = None, tenant: str = None, env_json_path: Path = _ENV_JSON_PATH) -> dict:
    """
    从 env.json 中按 环境/租户 加载数据库连接参数。

    Args:
        env:    环境名（如 "dev"）。为 None 时使用 env.json 的 active 字段。
        tenant: 租户名（如 "mx"）。为 None 时使用该环境下的第一个租户。
        env_json_path: env.json 文件路径。

    Returns:
        dict: 包含 host, port, user, password, database 的字典。
    """
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    # 确定环境
    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}")

    env_config = environments[env]
    tenants = env_config.get("tenants", {})

    if not tenants:
        raise ValueError(f"环境 '{env}' 下未配置任何租户 (tenants)")

    # 确定租户
    if tenant is None:
        tenant = next(iter(tenants))
        print(f"⚠ 未指定租户，使用环境 '{env}' 下的第一个租户: '{tenant}'")
    if tenant not in tenants:
        raise ValueError(f"租户 '{tenant}' 不存在于环境 '{env}' 中。可用租户: {list(tenants.keys())}")

    tenant_config = tenants[tenant]
    db_raw = tenant_config.get("db", {})

    # 合并默认值
    config = dict(_DEFAULTS)
    for key in _DEFAULTS:
        if key in db_raw and db_raw[key] not in (None, ""):
            config[key] = int(db_raw[key]) if key == "port" else db_raw[key]

    return config


def get_env_dir_name(env: str = None, env_json_path: Path = _ENV_JSON_PATH) -> str:
    """
    获取环境对应的目录名。

    若环境配置了 dirName 则返回 dirName，否则返回环境键名本身。
    """
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}")

    return environments[env].get("dirName", env)


def resolve_env_and_tenant(env: str = None, tenant: str = None, env_json_path: Path = _ENV_JSON_PATH) -> tuple:
    """
    解析环境目录名和租户名。

    Args:
        env:    环境名。为 None 时使用 env.json 的 active 字段。
        tenant: 租户名。为 None 时使用该环境下的第一个租户。

    Returns:
        tuple: (env_dir_name, tenant_name)
    """
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}")

    env_config = environments[env]
    env_dir = env_config.get("dirName", env)

    tenants = env_config.get("tenants", {})
    if tenant is None:
        tenant = next(iter(tenants))

    return env_dir, tenant


def list_tenants(env: str = None, env_json_path: Path = _ENV_JSON_PATH) -> list:
    """列出指定环境下的所有租户名。"""
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}")

    return list(environments[env].get("tenants", {}).keys())


def load_tenant_config(env: str = None, tenant: str = None, env_json_path: Path = _ENV_JSON_PATH) -> dict:
    """
    从 env.json 中加载租户的完整配置（baseUrl、headers、db）。

    Args:
        env:    环境名（如 "dev.dms"）。为 None 时使用 env.json 的 active 字段。
        tenant: 租户名（如 "mx"）。为 None 时使用该环境下的第一个租户。

    Returns:
        dict: 包含 baseUrl, headers, db 的字典。
              {
                  "baseUrl": "http://dev.dms/mx/pionapaas/api",
                  "headers": {"X-SS-EMAIL": "...", "Content-Type": "..."},
                  "db": {"host": ..., "port": ..., "user": ..., "password": ..., "database": ...}
              }
    """
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}")

    env_config = environments[env]
    tenants = env_config.get("tenants", {})

    if not tenants:
        raise ValueError(f"环境 '{env}' 下未配置任何租户 (tenants)")

    if tenant is None:
        tenant = next(iter(tenants))

    if tenant not in tenants:
        raise ValueError(f"租户 '{tenant}' 不存在于环境 '{env}' 中。可用租户: {list(tenants.keys())}")

    tenant_config = tenants[tenant]

    # 构建 db 配置（合并默认值）
    db_raw = tenant_config.get("db", {})
    db_config = dict(_DEFAULTS)
    for key in _DEFAULTS:
        if key in db_raw and db_raw[key] not in (None, ""):
            db_config[key] = int(db_raw[key]) if key == "port" else db_raw[key]

    return {
        "baseUrl": tenant_config.get("baseUrl", ""),
        "headers": dict(tenant_config.get("headers", {})),
        "db": db_config,
    }


# ──────────────── Namespace 解析工具（需要 pymysql） ────────────────

def resolve_namespace_id(db_config: dict, slug: str) -> int:
    """
    通过 namespace slug 查询对应的 id。

    Args:
        db_config: 数据库连接参数字典。
        slug:      命名空间 slug（如 "itsm"）。

    Returns:
        int: 命名空间 ID。

    Raises:
        ValueError: 如果未找到对应的命名空间。
    """
    import pymysql
    conn = pymysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM compose_namespace WHERE slug = %s AND deleted_at IS NULL",
                (slug,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"未找到 slug='{slug}' 的命名空间")
            return int(row["id"])
    finally:
        conn.close()


def build_namespace_map(db_config: dict) -> dict:
    """
    构建 namespaceID → slug 的映射字典。

    Returns:
        dict: {namespace_id(int): slug(str), ...}
    """
    import pymysql
    conn = pymysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, slug FROM compose_namespace WHERE deleted_at IS NULL"
            )
            rows = cur.fetchall()
        return {int(r["id"]): r["slug"] for r in rows}
    finally:
        conn.close()
