#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据作品uuid获取公众号作品（优质库）
API: POST /story/api/gzhData/queryWork
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post, format_output

BASE_URL = "https://redfox.hk/story/api/gzhData/queryWork"


def query_work(work_uuid):
    """根据作品 UUID 获取公众号作品详情"""
    body = {"workUuid": work_uuid}
    return http_post(BASE_URL, body)


def format_num(n):
    if n is None:
        return "N/A"
    if n >= 10000:
        return f"{n/10000:.1f}w"
    return str(n)


def format_result(result):
    """格式化输出结果"""
    if result.get("code") != 2000:
        print(f"Error: code={result.get('code')}, msg={result.get('msg')}")
        return

    data = result.get("data", {})
    original = " [原创]" if data.get("isOriginal") == 1 else ""

    print(f"标题: {data.get('title', 'N/A')}{original}")
    print(f"作品UUID: {data.get('workUuid', 'N/A')}")
    print(f"作者: {data.get('author', 'N/A')}")
    print(f"分类: {data.get('accountType', 'N/A')}")
    print(f"发布时间: {data.get('publishTime', 'N/A')}")
    print(f"发文位置: {data.get('publishLocation', 'N/A')}")
    print(f"阅读: {format_num(data.get('readCount'))} | 在看: {format_num(data.get('watchCount'))} | 点赞: {format_num(data.get('likeCount'))}")
    print(f"评论: {format_num(data.get('commentCount'))} | 收藏: {format_num(data.get('collectCount'))} | 分享: {format_num(data.get('shareCount'))} | 打赏: {format_num(data.get('rewardCount'))}")
    print(f"链接: {data.get('workUrl', 'N/A')}")
    if data.get("sourceUrl"):
        print(f"原文链接: {data.get('sourceUrl', 'N/A')}")
    if data.get("originalAuthor"):
        print(f"原创账号: {data.get('originalAuthor', 'N/A')}")
    print(f"文章位置: 第{data.get('orderNum', 0)+1}条（0=头条）")

    # 关键词云
    keywords = data.get("contentKeywords")
    if keywords:
        if isinstance(keywords, dict):
            kw_list = [f"{k.get('keyword', '')}({k.get('weight', 0)})" for k in [keywords] if k.get("keyword")]
        elif isinstance(keywords, list):
            kw_list = [f"{k.get('keyword', '')}({k.get('weight', 0)})" for k in keywords[:10]]
        else:
            kw_list = [str(keywords)]
        if kw_list:
            print(f"\n关键词: {', '.join(kw_list)}")

    if data.get("summary"):
        print(f"\n摘要: {data.get('summary', '')[:200]}")
    if data.get("content"):
        content = data.get("content", "")
        print(f"\n正文（前500字）: {content[:500]}{'...' if len(content) > 500 else ''}")


def main():
    parser = argparse.ArgumentParser(description="根据作品uuid获取公众号作品详情")
    parser.add_argument("--work-uuid", required=True, help="作品 UUID")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    result = query_work(args.work_uuid)

    if args.json:
        format_output(result, "获取公众号作品详情 (by UUID)")
    else:
        format_result(result)


if __name__ == "__main__":
    main()
