#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedFox API 公共工具模块
"""

import json
import os
import sys
import urllib.request
import urllib.error


def get_api_key():
    """从环境变量获取 REDFOX_API_KEY"""
    api_key = os.environ.get("REDFOX_API_KEY")
    if not api_key:
        print("ERROR: REDFOX_API_KEY environment variable not set. Please configure it first.", file=sys.stderr)
        sys.exit(1)
    return api_key


def http_post(url, body_dict, api_key=None):
    """发送 POST JSON 请求到 RedFox API，返回解析后的 dict"""
    if api_key is None:
        api_key = get_api_key()
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    data = json.dumps(body_dict, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return {"code": e.code, "msg": f"HTTP {e.code}", "data": None, "_raw": body}
    except Exception as e:
        return {"code": -1, "msg": str(e), "data": None}


def format_output(result, title=""):
    """格式化输出 API 结果"""
    if title:
        print(f"=== {title} ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
