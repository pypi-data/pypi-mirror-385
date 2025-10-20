# -*- coding: UTF-8 -*-
'''
@File    ：server
@Date    ：2025/10/20 14:36 
@Author  ：Fbx
'''
import os
import json
import requests
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ThreatBook IP‑Lookup")

def load_config() -> Dict[str, Any]:
    config_path = os.getenv("THREATBOOK_CONFIG_PATH", "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"配置文件 {config_path} 不是合法的 JSON: {e}"
        raise ValueError(msg)
    except OSError as e:
        msg = f"读取配置文件 {config_path} 失败: {e}"
        raise ValueError(msg)
    return cfg


def _call_threatbook_api(resource: str, timeout: float = 10.0) -> Dict[str, Any]:
    cfg = load_config()
    api_url = cfg.get("api_url")
    apikey = cfg.get("apikey")
    if not api_url or not apikey:
        raise RuntimeError("配置中 api_url或apikey缺失")
    lang = cfg.get("lang")
    if lang:
        params = {"apikey": apikey, "resource": resource, "lang":lang}
    else:
        params = {"apikey": apikey, "resource": resource,"lang":"zh"}
    try:
        resp = requests.get(api_url, params=params, timeout=timeout)
    except requests.exceptions.RequestException as e:
        msg = f"网络请求失败: {e}"
        logger.exception(msg)
        return {"error": {"code": "REQUEST_ERROR", "message": msg}}
    resp.raise_for_status()

    try:
        data = resp.json()
    except (ValueError, json.JSONDecodeError) as e:
        msg = f"响应不是合法 JSON: {e}; HTTP {resp.status_code}; 前1000字: {resp.text[:1000]!r}"
        return {"ok": False, "error": {"code": "INVALID_JSON", "message": msg, "status_code": resp.status_code}}
    # 成功：返回结构化结果
    return {"ok": True, "data": data}


# @mcp.tool()
def ip_lookup(resource: str) -> Dict[str, Any]:
    """
        查询 IP 的威胁情报。
        返回统一结构：
          成功 -> {"ok": True, "data": ...}
          失败 -> {"ok": False, "error": {"code": "...", "message": "..."}}
        """
    if not resource:
        msg = "参数 resource 非法或为空"
        return {"ok": False, "error": {"code": "INVALID_PARAM", "message": msg}}
    try:
        return _call_threatbook_api(resource)
    except Exception as e:
        raise RuntimeError(f"ThreatBook API 调用失败: {e}")

if __name__ == "__main__":
    mcp.run()
