#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索关键词获取公众号账号（优质库）
API: POST /story/api/gzhData/searchUser
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post, format_output

BASE_URL = "https://redfox.hk/story/api/gzhData/searchUser"

SORT_TYPES = {
    "default": "_0",   # 相关性排序
    "latest": "_2",    # 最新（按发布时间倒序）
    "hottest": "_4",   # 最热（按阅读数倒序）
}


def search_user(keyword, offset=0, sort_type="default", max_items=20):
    """搜索公众号账号"""
    body = {
        "keyword": keyword,
        "offset": offset,
        "sortType": SORT_TYPES.get(sort_type, "_0"),
    }
    return http_post(BASE_URL, body)


def format_result(result, max_items=20):
    """格式化输出结果"""
    if result.get("code") != 2000:
        print(f"Error: code={result.get('code')}, msg={result.get('msg')}")
        return

    data = result.get("data", {})
    total = data.get("total", 0)
    has_more = data.get("hasMore", False)
    accounts = data.get("list", [])[:max_items]

    print(f"搜索结果: 共 {total} 个账号" + (" (有更多)" if has_more else ""))
    print(f"{'='*60}")

    for i, acc in enumerate(accounts, 1):
        print(f"\n[{i}] {acc.get('accountName', 'N/A')}")
        print(f"    微信号: {acc.get('account', 'N/A')}")
        print(f"    红狐指数: {acc.get('redfoxIndex', 'N/A')}")
        print(f"    分类: {acc.get('accountType', 'N/A')}")
        print(f"    认证: {acc.get('verifyInfo', 'N/A')}")
        print(f"    简介: {acc.get('description', 'N/A')[:60]}")
        print(f"    最近发文: {acc.get('lastArticleTitle', 'N/A')}")
        print(f"    最近发文时间: {acc.get('lastPublishTime', 'N/A')}")
        print(f"    标签: {acc.get('tags', 'N/A')}")
        print(f"    地区: {acc.get('province', '')} {acc.get('city', '')}")


def main():
    parser = argparse.ArgumentParser(description="搜索关键词获取公众号账号")
    parser.add_argument("--keyword", required=True, help="搜索关键词")
    parser.add_argument("--offset", type=int, default=0, help="偏移量（从0开始，每页+20）")
    parser.add_argument("--sort", choices=["default", "latest", "hottest"], default="default", help="排序方式")
    parser.add_argument("--max-items", type=int, default=20, help="最大返回数量")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    result = search_user(args.keyword, args.offset, args.sort, args.max_items)

    if args.json:
        format_output(result, f"搜索公众号账号: {args.keyword}")
    else:
        format_result(result, args.max_items)


if __name__ == "__main__":
    main()
