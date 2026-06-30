#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取公众号账号信息（优质库）
API: POST /story/api/gzhData/queryUser
"""

import argparse
import json
import os
import sys

# 添加同目录到 path 以导入公共模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post, format_output

BASE_URL = "https://redfox.hk/story/api/gzhData/queryUser"


def query_user(account, account_name=None):
    """查询公众号账号信息"""
    body = {"account": account}
    if account_name:
        body["accountName"] = account_name
    return http_post(BASE_URL, body)


def format_result(result):
    """格式化输出结果"""
    if result.get("code") != 2000:
        print(f"Error: code={result.get('code')}, msg={result.get('msg')}")
        return

    data = result.get("data", {})
    print(f"公众号名称: {data.get('accountName', 'N/A')}")
    print(f"微信号: {data.get('account', 'N/A')}")
    print(f"账号分类: {data.get('accountType', 'N/A')}")
    print(f"认证状态: {data.get('verifyInfo', 'N/A')}")
    print(f"简介: {data.get('description', 'N/A')}")
    print(f"标签: {data.get('tags', 'N/A')}")
    print(f"地区: {data.get('province', '')} {data.get('city', '')}")
    print(f"头像: {data.get('avatarUrl', 'N/A')}")
    print(f"二维码: {data.get('qrcodeUrl', 'N/A')}")
    print(f"更新时间: {data.get('updateTime', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="获取公众号账号信息")
    parser.add_argument("--account", required=True, help="公众号微信号（必填）")
    parser.add_argument("--account-name", help="公众号名称（可选，辅助匹配）")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    result = query_user(args.account, args.account_name)

    if args.json:
        format_output(result, "获取公众号账号信息")
    else:
        format_result(result)


if __name__ == "__main__":
    main()
