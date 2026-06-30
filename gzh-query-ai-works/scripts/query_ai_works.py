#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索关键词获取公众号 AI 创作作品（优质库）
API: POST /story/api/parseWork/queryAiMsgs
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post, format_output

BASE_URL = "https://redfox.hk/story/api/parseWork/queryAiMsgs"


def query_ai_works(keyword, page_num=1, page_size=20, start_time=None, end_time=None):
    """搜索公众号 AI 创作作品"""
    body = {
        "keyword": keyword,
        "pageNum": page_num,
        "pageSize": page_size,
    }
    if start_time:
        body["startTime"] = start_time
    if end_time:
        body["endTime"] = end_time
    return http_post(BASE_URL, body)


def format_num(n):
    if n is None:
        return "N/A"
    if n >= 10000:
        return f"{n/10000:.1f}w"
    return str(n)


def format_result(result, max_items=20):
    """格式化输出结果"""
    if result.get("code") != 2000:
        print(f"Error: code={result.get('code')}, msg={result.get('msg')}")
        return

    data = result.get("data", {})
    total = data.get("total", 0)
    pages = data.get("pages", 0)
    page_num = data.get("pageNum", 1)
    works = data.get("list", [])[:max_items]

    print(f"AI 创作作品: 共 {total} 篇，第 {page_num}/{pages} 页")
    print(f"{'='*60}")

    for i, work in enumerate(works, 1):
        print(f"\n[{i}] {work.get('title', 'N/A')}")
        print(f"    作者: {work.get('userName', 'N/A')}")
        print(f"    阅读: {format_num(work.get('readCount'))} | 点赞: {format_num(work.get('likeCount'))}")
        print(f"    评论: {format_num(work.get('commentCount'))} | 分享: {format_num(work.get('shareCount'))}")
        print(f"    创建时间: {work.get('gmtCreate', 'N/A')}")
        print(f"    链接: {work.get('url', 'N/A')}")
        if work.get("topic"):
            print(f"    话题: {work.get('topic', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="搜索关键词获取公众号 AI 创作作品")
    parser.add_argument("--keyword", required=True, help="搜索关键词")
    parser.add_argument("--page-num", type=int, default=1, help="页码（从1开始）")
    parser.add_argument("--page-size", type=int, default=20, help="每页条数")
    parser.add_argument("--start-time", help="开始时间 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end-time", help="结束时间 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--max-items", type=int, default=20, help="最大返回数量")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    # 处理时间格式
    start_time = args.start_time
    end_time = args.end_time
    if start_time and len(start_time) == 10:
        start_time += " 00:00:00"
    if end_time and len(end_time) == 10:
        end_time += " 23:59:59"

    result = query_ai_works(args.keyword, args.page_num, args.page_size, start_time, end_time)

    if args.json:
        format_output(result, f"搜索 AI 创作作品: {args.keyword}")
    else:
        format_result(result, args.max_items)


if __name__ == "__main__":
    main()
