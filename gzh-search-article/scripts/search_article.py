#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索关键词获取公众号作品（优质库）
API: POST /story/api/gzhData/searchArticle
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post, format_output

BASE_URL = "https://redfox.hk/story/api/gzhData/searchArticle"

SORT_TYPES = {
    "default": "_0",   # 相关性排序
    "latest": "_2",    # 最新（按发布时间倒序）
    "hottest": "_4",   # 最热（按阅读数倒序）
}


def search_article(keyword, offset=0, sort_type="default", max_items=20):
    """搜索公众号作品"""
    body = {
        "keyword": keyword,
        "offset": offset,
        "sortType": SORT_TYPES.get(sort_type, "_0"),
    }
    return http_post(BASE_URL, body)


def format_num(n):
    """格式化数字"""
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
    has_more = data.get("hasMore", False)
    articles = data.get("list", [])[:max_items]

    print(f"搜索结果: 共 {total} 篇文章" + (" (有更多)" if has_more else ""))
    print(f"{'='*60}")

    for i, art in enumerate(articles, 1):
        original = " [原创]" if art.get("isOriginal") == 1 else ""
        print(f"\n[{i}] {art.get('title', 'N/A')}{original}")
        print(f"    作者: {art.get('author', 'N/A')}")
        print(f"    分类: {art.get('accountType', 'N/A')}")
        print(f"    发布时间: {art.get('publishTime', 'N/A')}")
        print(f"    阅读: {format_num(art.get('readCount'))} | 在看: {format_num(art.get('watchCount'))} | 点赞: {format_num(art.get('likeCount'))}")
        print(f"    评论: {format_num(art.get('commentCount'))} | 收藏: {format_num(art.get('collectCount'))} | 分享: {format_num(art.get('shareCount'))}")
        print(f"    链接: {art.get('workUrl', 'N/A')}")
        if art.get("summary"):
            print(f"    摘要: {art.get('summary', '')[:80]}")


def main():
    parser = argparse.ArgumentParser(description="搜索关键词获取公众号作品")
    parser.add_argument("--keyword", required=True, help="搜索关键词")
    parser.add_argument("--offset", type=int, default=0, help="偏移量（从0开始，每页+20）")
    parser.add_argument("--sort", choices=["default", "latest", "hottest"], default="default", help="排序方式")
    parser.add_argument("--max-items", type=int, default=20, help="最大返回数量")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    result = search_article(args.keyword, args.offset, args.sort, args.max_items)

    if args.json:
        format_output(result, f"搜索公众号作品: {args.keyword}")
    else:
        format_result(result, args.max_items)


if __name__ == "__main__":
    main()
