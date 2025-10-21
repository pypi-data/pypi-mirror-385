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
    """从环境变量中读取配置参数"""
    api_url = os.getenv("TIP_API_URL")
    apikey = os.getenv("TIP_APIKEY")
    
    if not api_url or not apikey:
        raise RuntimeError("环境变量 API_URL 或 APIKEY 未设置")
    
    return {
        "api_url": api_url,
        "apikey": apikey
    }


def _call_threatbook_api(resource: str, api_type: str, timeout: float = 10.0) -> Dict[str, Any]:
    cfg = load_config()
    base_url = cfg.get("api_url")
    apikey = cfg.get("apikey")
    
    # 根据查询类型构建完整的API URL
    if api_type == "ip":
        api_url = base_url.rstrip('/') + "/tip_api/v4/ip"
    elif api_type == "dns":
        api_url = base_url.rstrip('/') + "/tip_api/v4/dns"
    elif api_type == "location":
        api_url = base_url.rstrip('/') + "/tip_api/v4/location"
    elif api_type == "hash":
        api_url = base_url.rstrip('/') + "/tip_api/v4/hash"
    elif api_type == "vuln":
        api_url = base_url.rstrip('/') + "/tip_api/v4/vuln"
    else:
        return {"ok": False, "error": {"code": "INVALID_TYPE", "message": f"不支持的查询类型: {api_type}"}}
    
    # 根据API类型使用不同的参数名
    if api_type == "vuln":
        params = {"apikey": apikey, "vuln_id": resource}
    else:
        params = {"apikey": apikey, "resource": resource}
    
    try:
        resp = requests.get(api_url, params=params, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        msg = f"网络请求失败: {e}"
        return {"ok": False, "error": {"code": "REQUEST_ERROR", "message": msg}}

    try:
        data = resp.json()
    except (ValueError, json.JSONDecodeError) as e:
        msg = f"响应不是合法 JSON: {e}; HTTP {resp.status_code}; 前1000字: {resp.text[:1000]!r}"
        return {"ok": False, "error": {"code": "INVALID_JSON", "message": msg, "status_code": resp.status_code}}
    # 成功：返回结构化结果
    return {"ok": True, "data": data}


@mcp.tool()
def search_ip(resource: str) -> Dict[str, Any]:
    """
        查询 IP 地址的威胁情报。
        调用 /tip_api/v4/ip 接口
        返回统一结构：
          成功 -> {"ok": True, "data": ...}
          失败 -> {"ok": False, "error": {"code": "...", "message": "..."}}
        """
    if not resource:
        msg = "参数 resource 非法或为空"
        return {"ok": False, "error": {"code": "INVALID_PARAM", "message": msg}}
    try:
        return _call_threatbook_api(resource, "ip")
    except Exception as e:
        raise RuntimeError(f"TTP IP API 调用失败: {e}")


@mcp.tool()
def search_domain(resource: str) -> Dict[str, Any]:
    """
        查询域名的威胁情报。
        调用 /tip_api/v4/domain 接口
        返回统一结构：
          成功 -> {"ok": True, "data": ...}
          失败 -> {"ok": False, "error": {"code": "...", "message": "..."}}
        """
    if not resource:
        msg = "参数 resource 非法或为空"
        return {"ok": False, "error": {"code": "INVALID_PARAM", "message": msg}}
    try:
        return _call_threatbook_api(resource, "dns")
    except Exception as e:
        raise RuntimeError(f"TIP DNS API 调用失败: {e}")


@mcp.tool()
def search_location(resource: str) -> Dict[str, Any]:
    """
        获取IP地理位置信息。
        调用 /tip_api/v4/location 接口
        返回统一结构：
          成功 -> {"ok": True, "data": ...}
          失败 -> {"ok": False, "error": {"code": "...", "message": "..."}}
        """
    if not resource:
        msg = "参数 resource 非法或为空"
        return {"ok": False, "error": {"code": "INVALID_PARAM", "message": msg}}
    try:
        return _call_threatbook_api(resource, "location")
    except Exception as e:
        raise RuntimeError(f"TIP Location API 调用失败: {e}")


@mcp.tool()
def search_hash(resource: str) -> Dict[str, Any]:
    """
        文件信誉检测
        调用 /tip_api/v4/hash 接口
        参数：
        - resource: 文件sha1、sha256、md5
        返回统一结构：
          成功 -> {"ok": True, "data": ...}
          失败 -> {"ok": False, "error": {"code": "...", "message": "..."}}
        """
    if not resource:
        msg = "参数 resource 非法或为空"
        return {"ok": False, "error": {"code": "INVALID_PARAM", "message": msg}}
    try:
        return _call_threatbook_api(resource, "hash")
    except Exception as e:
        raise RuntimeError(f"TIP Hash API 调用失败: {e}")


@mcp.tool()
def search_vuln(vuln_id: str) -> Dict[str, Any]:
    """
        获取漏洞情报信息接口。
        调用 /tip_api/v4/vuln 接口
        参数：
        - vuln_id: 支持通过XVE编号、CVE编号、CNVD编号、CNNVD编号、NVDB编号、CITIVD编号、统信UTSA/UT编号或麒麟KVE/KYSA编号进行精确查询，XVE编号为微步漏洞唯一标识。
        返回统一结构：
          成功 -> {"ok": True, "data": ...}
          失败 -> {"ok": False, "error": {"code": "...", "message": "..."}}
        """
    if not vuln_id:
        msg = "参数 vuln_id 非法或为空"
        return {"ok": False, "error": {"code": "INVALID_PARAM", "message": msg}}
    try:
        return _call_threatbook_api(vuln_id, "vuln")
    except Exception as e:
        raise RuntimeError(f"TIP Vuln API 调用失败: {e}")


def main():
    mcp.run()

if __name__ == "__main__":
    main()

app = mcp