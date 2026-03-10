#!/usr/bin/env python3
"""
统一的 API 请求工具模块。

所有 sync / export 脚本均通过此模块与服务端 API 交互，
替代之前的直接数据库操作。

配置从 src/env.json 中读取 baseUrl 和 headers。

用法（在同目录脚本中）:
    from api_utils import load_api_config, api_get, api_post, api_list_all

    cfg = load_api_config(env="dev.dms", tenant="mx")
    base_url, headers = cfg["baseUrl"], cfg["headers"]
    modules = api_list_all(base_url, headers, "/compose/namespace/{nsID}/module/")
"""

import json
import sys
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path

# env.json 位于 src/ 目录下（scripts/ 的兄弟目录）
_ENV_JSON_PATH = Path(__file__).resolve().parent.parent / "src" / "env.json"

# ──────────────── 配置加载 ────────────────


def _load_env_json(env_json_path: Path = _ENV_JSON_PATH) -> dict:
    """加载 env.json 并返回完整内容。"""
    if not env_json_path.exists():
        raise FileNotFoundError(f"未找到配置文件 {env_json_path}")
    with open(env_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_api_config(
    env: str = None, tenant: str = None, env_json_path: Path = _ENV_JSON_PATH
) -> dict:
    """
    从 env.json 加载租户的 API 配置。

    Args:
        env:    环境名（如 "dev.dms"）。为 None 时使用 env.json 的 active 字段。
        tenant: 租户名（如 "mx"）。为 None 时使用该环境下的第一个租户。

    Returns:
        dict: {
            "baseUrl": "http://dev.dms/mx/pionapaas/api",
            "headers": {"Authorization": "Bearer ..."},
            "env": "dev.dms",
            "env_dir": "dev.dms",
            "tenant": "mx"
        }
    """
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(
            f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}"
        )

    env_config = environments[env]
    tenants = env_config.get("tenants", {})

    if not tenants:
        raise ValueError(f"环境 '{env}' 下未配置任何租户 (tenants)")

    if tenant is None:
        tenant = next(iter(tenants))
        print(f"⚠ 未指定租户，使用环境 '{env}' 下的第一个租户: '{tenant}'")

    if tenant not in tenants:
        raise ValueError(
            f"租户 '{tenant}' 不存在于环境 '{env}' 中。可用租户: {list(tenants.keys())}"
        )

    tenant_config = tenants[tenant]
    env_dir = env_config.get("dirName", env)

    return {
        "baseUrl": tenant_config.get("baseUrl", ""),
        "headers": dict(tenant_config.get("headers", {})),
        "env": env,
        "env_dir": env_dir,
        "tenant": tenant,
    }


def get_env_dir_name(
    env: str = None, env_json_path: Path = _ENV_JSON_PATH
) -> str:
    """获取环境对应的目录名（dirName 或环境键名本身）。"""
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})
    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(
            f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}"
        )
    return environments[env].get("dirName", env)


def resolve_env_and_tenant(
    env: str = None, tenant: str = None, env_json_path: Path = _ENV_JSON_PATH
) -> tuple:
    """
    解析环境目录名和租户名。

    Returns:
        tuple: (env_dir_name, tenant_name)
    """
    data = _load_env_json(env_json_path)
    environments = data.get("environments", {})

    if env is None:
        env = data.get("active")
    if env not in environments:
        raise ValueError(
            f"环境 '{env}' 不存在于 env.json 中。可用环境: {list(environments.keys())}"
        )

    env_config = environments[env]
    env_dir = env_config.get("dirName", env)

    tenants = env_config.get("tenants", {})
    if tenant is None:
        tenant = next(iter(tenants))

    return env_dir, tenant


# ──────────────── API 错误类 ────────────────


class APIError(Exception):
    """API 请求失败异常。"""

    def __init__(self, status: int, reason: str, body: str):
        self.status = status
        self.reason = reason
        self.body = body
        super().__init__(f"HTTP {status}: {reason}")


# ──────────────── HTTP 请求封装 ────────────────


def api_request(
    base_url: str,
    headers: dict,
    method: str,
    path: str,
    data: dict = None,
    params: dict = None,
) -> dict:
    """
    发送 HTTP 请求并返回解析后的 JSON 响应。

    Args:
        base_url: API 基地址（如 http://dev.dms/mx/pionapaas/api）
        headers:  公共请求头（如 Authorization: Bearer ...）
        method:   HTTP 方法（GET / POST / PUT / DELETE）
        path:     API 路径（如 /compose/namespace/{id}/module/）
        data:     请求体（dict，将被 JSON 序列化）
        params:   查询参数（dict）

    Returns:
        dict: 解析后的 JSON 响应

    Raises:
        APIError: 请求失败时抛出
    """
    url = f"{base_url}{path}"
    if params:
        qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"

    body_bytes = None
    if data is not None:
        body_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")

    req_headers = dict(headers)
    if "Content-Type" not in req_headers:
        req_headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(
        url, data=body_bytes, headers=req_headers, method=method
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(resp_body) if resp_body else {}

            # 服务端有时返回 HTTP 200 但 body 包含 error 字段
            if isinstance(parsed, dict) and "error" in parsed and "response" not in parsed:
                err = parsed["error"]
                err_msg = err.get("message", "") if isinstance(err, dict) else str(err)
                err_type = ""
                if isinstance(err, dict):
                    err_type = err.get("meta", {}).get("type", "")
                # 将 notFound 映射为 404，其他映射为 422
                status = 404 if err_type == "notFound" else 422
                raise APIError(status, err_msg, resp_body)

            return parsed
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise APIError(e.code, e.reason, body) from e
    except urllib.error.URLError as e:
        raise APIError(0, str(e.reason), "") from e


def api_get(base_url: str, headers: dict, path: str, params: dict = None) -> dict:
    """发送 GET 请求。"""
    return api_request(base_url, headers, "GET", path, params=params)


def api_post(base_url: str, headers: dict, path: str, data: dict = None) -> dict:
    """发送 POST 请求。"""
    return api_request(base_url, headers, "POST", path, data=data)


def api_put(base_url: str, headers: dict, path: str, data: dict = None) -> dict:
    """发送 PUT 请求。"""
    return api_request(base_url, headers, "PUT", path, data=data)


def api_delete(base_url: str, headers: dict, path: str) -> dict:
    """发送 DELETE 请求。"""
    return api_request(base_url, headers, "DELETE", path)


def api_list_all(
    base_url: str, headers: dict, path: str, params: dict = None
) -> list:
    """
    获取所有分页数据。

    自动处理 cursor-based 分页，循环请求直到无下一页。

    Returns:
        list: 所有条目的列表
    """
    all_items = []
    page_params = dict(params or {})
    page_params.setdefault("limit", 100)

    while True:
        resp = api_get(base_url, headers, path, params=page_params)
        response = resp.get("response", {})
        items = response.get("set", [])
        all_items.extend(items)

        next_page = response.get("filter", {}).get("nextPage", "")
        if not next_page:
            break
        page_params["pageCursor"] = next_page

    return all_items


# ─────────── Compose 命名空间解析 ───────────


def resolve_namespace_id(base_url: str, headers: dict, slug: str) -> str:
    """
    通过 Namespace list API 查找 slug 对应的 namespaceID。

    Args:
        base_url: API 基地址
        headers:  请求头
        slug:     命名空间 slug（如 "itsm"）

    Returns:
        str: namespaceID

    Raises:
        ValueError: 未找到对应的命名空间
    """
    items = api_list_all(base_url, headers, "/compose/namespace/", {"slug": slug})
    for ns in items:
        if ns.get("slug") == slug:
            return str(ns["namespaceID"])
    raise ValueError(f"未找到 slug='{slug}' 的命名空间")


def build_namespace_map(base_url: str, headers: dict) -> dict:
    """
    构建 namespaceID → slug 的映射字典。

    Returns:
        dict: {namespaceID(str): slug(str), ...}
    """
    items = api_list_all(base_url, headers, "/compose/namespace/")
    return {str(ns["namespaceID"]): ns["slug"] for ns in items}


# ─────────── 通用资源存在性检测 ───────────


def resource_exists(base_url: str, headers: dict, path: str) -> bool:
    """
    检查某个 API 资源是否存在（GET 返回 200 视为存在）。

    Returns:
        bool: 资源是否存在
    """
    try:
        resp = api_get(base_url, headers, path)
        return resp.get("response") is not None
    except APIError as e:
        if e.status in (404, 422):
            return False
        # 检查 body 中是否有 notFound 类型错误
        if e.body:
            try:
                err_data = json.loads(e.body)
                err_type = err_data.get("error", {}).get("meta", {}).get("type", "")
                if err_type == "notFound":
                    return False
            except (json.JSONDecodeError, AttributeError):
                pass
        raise
