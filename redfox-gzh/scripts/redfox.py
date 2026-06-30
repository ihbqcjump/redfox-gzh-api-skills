#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedFox 公众号全自动分析

输入一个关键词 → 自动串联 6 个 API → 输出完整分析报告

自动化流程:
  ① searchUser    → 搜索相关公众号账号
  ② searchArticle → 搜索相关文章
  ③ queryUser     → 获取 Top1 账号完整详情
  ④ queryWork     → 获取 Top1 文章正文 + 关键词云
  ⑤ queryArticleDetail → 获取 Top1 文章 URL 详情（若与④不同源）
  ⑥ queryAiMsgs   → 搜索 AI 创作相关内容

用法:
  python redfox.py "关键词"
  python redfox.py "关键词" --sort hottest
  python redfox.py "关键词" --sort latest --top 5
  python redfox.py "关键词" --json
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post

# ─── API Endpoints ───────────────────────────────────────────────
API = {
    "search_user":    "https://redfox.hk/story/api/gzhData/searchUser",
    "query_user":     "https://redfox.hk/story/api/gzhData/queryUser",
    "search_article": "https://redfox.hk/story/api/gzhData/searchArticle",
    "article_detail": "https://redfox.hk/story/api/gzhData/queryArticleDetail",
    "query_work":     "https://redfox.hk/story/api/gzhData/queryWork",
    "ai_works":       "https://redfox.hk/story/api/parseWork/queryAiMsgs",
}

SORT_MAP = {"default": "_0", "latest": "_2", "hottest": "_4"}


# ─── 工具函数 ────────────────────────────────────────────────────
def fmt_num(n):
    if n is None:
        return "N/A"
    if isinstance(n, (int, float)) and n >= 10000:
        return f"{n/10000:.1f}w"
    return str(n)


def safe_call(name, body):
    """安全调用 API，返回 result dict"""
    r = http_post(API[name], body)
    if r.get("code") != 2000:
        return None
    return r.get("data")


def extract_keywords(kw_data):
    """从 contentKeywords 提取关键词字符串"""
    if not kw_data:
        return ""
    if isinstance(kw_data, dict) and kw_data.get("keyword"):
        return f"{kw_data['keyword']}({kw_data.get('weight', 0):.2f})"
    if isinstance(kw_data, list):
        return ", ".join(
            f"{k.get('keyword','')}({k.get('weight',0):.2f})"
            for k in kw_data[:8] if k.get("keyword")
        )
    return str(kw_data)


def parse_tags(tags):
    if isinstance(tags, list):
        return ", ".join(tags[:10])
    return str(tags) if tags else ""


# ─── 全自动流水线 ────────────────────────────────────────────────
def run_pipeline(keyword, sort="default", top_n=3, as_json=False):
    sort_type = SORT_MAP.get(sort, "_0")
    report = {"keyword": keyword, "sort": sort}

    # ── ① 搜索账号 ──────────────────────────────────────────────
    acc_data = safe_call("search_user", {
        "keyword": keyword, "offset": 0, "sortType": sort_type
    })
    accounts = []
    acc_total = 0
    if acc_data:
        acc_total = acc_data.get("total", 0)
        accounts = acc_data.get("list", [])[:top_n]

    # ── ② 搜索文章 ──────────────────────────────────────────────
    art_data = safe_call("search_article", {
        "keyword": keyword, "offset": 0, "sortType": sort_type
    })
    articles = []
    art_total = 0
    if art_data:
        art_total = art_data.get("total", 0)
        articles = art_data.get("list", [])[:top_n]

    # ── ③ 获取 Top1 账号详情 ─────────────────────────────────────
    top_account_detail = None
    if accounts:
        acc_id = accounts[0].get("account", "")
        if acc_id:
            top_account_detail = safe_call("query_user", {"account": acc_id})

    # ── ④ 获取 Top1 文章正文（用 UUID → 带关键词云）─────────────
    top_article_detail = None
    if articles:
        uuid = articles[0].get("workUuid", "")
        if uuid:
            top_article_detail = safe_call("query_work", {"workUuid": uuid})

    # ── ⑤ 获取 Top1 文章 URL 详情（补充数据）────────────────────
    top_article_url_detail = None
    if articles:
        url = articles[0].get("workUrl", "")
        if url:
            top_article_url_detail = safe_call("article_detail", {"url": url})

    # ── ⑥ 搜索 AI 创作内容 ──────────────────────────────────────
    ai_data = safe_call("ai_works", {
        "keyword": keyword, "pageNum": 1, "pageSize": top_n
    })
    ai_works = []
    ai_total = 0
    if ai_data:
        ai_total = ai_data.get("total", 0)
        ai_works = ai_data.get("list", [])[:top_n]

    # ── 组装报告 ────────────────────────────────────────────────
    report["accounts"] = {"total": acc_total, "top": accounts}
    report["articles"] = {"total": art_total, "top": articles}
    report["top_account_detail"] = top_account_detail
    report["top_article_detail"] = top_article_detail
    report["top_article_url_detail"] = top_article_url_detail
    report["ai_works"] = {"total": ai_total, "top": ai_works}

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    _print_report(report)
    return report


# ─── 报告输出 ────────────────────────────────────────────────────
def _print_report(r):
    kw = r["keyword"]
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  RedFox 公众号分析报告: \"{kw}\"")
    print(f"  排序: {r['sort']}")
    print(f"{sep}\n")

    # ── 1. 账号概览 ─────────────────────────────────────────────
    acc = r["accounts"]
    print(f"[1] 相关公众号: 共 {acc['total']} 个")
    print("-" * 40)
    for i, a in enumerate(acc["top"], 1):
        print(f"  {i}. {a.get('accountName', 'N/A')}")
        print(f"     微信号: {a.get('account', 'N/A')} | 红狐指数: {fmt_num(a.get('redfoxIndex'))}")
        print(f"     分类: {a.get('accountType', 'N/A')} | 认证: {a.get('verifyInfo', 'N/A')}")
        if a.get("description"):
            print(f"     简介: {a['description'][:80]}")
    print()

    # ── 2. Top 账号深度画像 ─────────────────────────────────────
    detail = r.get("top_account_detail")
    if detail:
        print(f"[2] 头部账号画像: {detail.get('accountName', 'N/A')}")
        print("-" * 40)
        print(f"  微信号: {detail.get('account', 'N/A')}")
        print(f"  分类: {detail.get('accountType', 'N/A')}")
        print(f"  认证: {detail.get('verifyInfo', 'N/A')}")
        if detail.get("description"):
            print(f"  简介: {detail['description']}")
        tags = parse_tags(detail.get("tags"))
        if tags:
            print(f"  标签: {tags}")
        print(f"  地区: {detail.get('province', '')} {detail.get('city', '')}")
        if detail.get("lastPublishTime"):
            print(f"  最近发文: {detail.get('lastArticleTitle', 'N/A')}")
            print(f"  发文时间: {detail['lastPublishTime']}")
        if detail.get("syncTime"):
            print(f"  数据更新: {detail['syncTime']}")
    else:
        print("[2] 头部账号画像: 无数据")
    print()

    # ── 3. 文章概览 ─────────────────────────────────────────────
    art = r["articles"]
    print(f"[3] 相关文章: 共 {art['total']} 篇")
    print("-" * 40)
    for i, a in enumerate(art["top"], 1):
        orig = " [原创]" if a.get("isOriginal") == 1 else ""
        print(f"  {i}. {a.get('title', 'N/A')}{orig}")
        print(f"     作者: {a.get('author', 'N/A')} | {a.get('publishTime', 'N/A')}")
        print(f"     阅读:{fmt_num(a.get('readCount'))} 点赞:{fmt_num(a.get('likeCount'))} 在看:{fmt_num(a.get('watchCount'))} 分享:{fmt_num(a.get('shareCount'))}")
    print()

    # ── 4. 头部文章深度解析 ─────────────────────────────────────
    ad = r.get("top_article_detail")
    au = r.get("top_article_url_detail")
    # 优先用 queryWork 的数据（有关键词云），URL 详情做补充
    merged = ad or au or {}
    if merged:
        title = merged.get("title", art["top"][0].get("title", "N/A") if art["top"] else "N/A")
        orig = " [原创]" if merged.get("isOriginal") == 1 else ""
        print(f"[4] 头部文章解析: {title}{orig}")
        print("-" * 40)
        print(f"  作者: {merged.get('author', 'N/A')} | 分类: {merged.get('accountType', 'N/A')}")
        print(f"  发布: {merged.get('publishTime', 'N/A')} | 位置: {merged.get('publishLocation', 'N/A')}")
        print(f"  阅读:{fmt_num(merged.get('readCount'))} 在看:{fmt_num(merged.get('watchCount'))} 点赞:{fmt_num(merged.get('likeCount'))} 评论:{fmt_num(merged.get('commentCount'))} 收藏:{fmt_num(merged.get('collectCount'))} 分享:{fmt_num(merged.get('shareCount'))} 打赏:{fmt_num(merged.get('rewardCount'))}")
        if merged.get("workUrl"):
            print(f"  链接: {merged['workUrl']}")

        # 关键词云（仅 queryWork 有）
        kw_str = extract_keywords(merged.get("contentKeywords"))
        if kw_str:
            print(f"  关键词云: {kw_str}")

        # 正文摘要
        if merged.get("summary"):
            print(f"\n  摘要: {merged['summary'][:300]}")
        if merged.get("content"):
            content = merged["content"]
            print(f"\n  正文节选（前500字）:")
            print(f"  {content[:500]}{'...' if len(content) > 500 else ''}")
    else:
        print("[4] 头部文章解析: 无数据")
    print()

    # ── 5. AI 创作内容 ──────────────────────────────────────────
    ai = r["ai_works"]
    print(f"[5] AI 创作内容: 共 {ai['total']} 篇")
    print("-" * 40)
    if ai["top"]:
        for i, w in enumerate(ai["top"], 1):
            print(f"  {i}. {w.get('title', 'N/A')}")
            print(f"     作者: {w.get('userName', 'N/A')} | {w.get('gmtCreate', 'N/A')}")
            print(f"     阅读:{fmt_num(w.get('readCount'))} 点赞:{fmt_num(w.get('likeCount'))}")
            if w.get("topic"):
                print(f"     话题: {w['topic']}")
    else:
        print("  暂无 AI 创作内容")
    print()

    # ── 总结 ────────────────────────────────────────────────────
    print(f"{sep}")
    print(f"  数据概览")
    print(f"  相关账号: {acc['total']} 个 | 相关文章: {art['total']} 篇 | AI 创作: {ai['total']} 篇")
    if detail:
        print(f"  头部账号: {detail.get('accountName', 'N/A')} ({detail.get('accountType', 'N/A')})")
    if merged:
        print(f"  头部文章: 阅读 {fmt_num(merged.get('readCount'))} | 点赞 {fmt_num(merged.get('likeCount'))} | 分享 {fmt_num(merged.get('shareCount'))}")
    print(f"{sep}\n")


# ─── 入口 ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="RedFox 公众号全自动分析 — 输入关键词，自动串联 6 个 API，输出完整报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python redfox.py "人工智能"
  python redfox.py "量子计算" --sort hottest
  python redfox.py "ChatGPT" --sort latest --top 5
  python redfox.py "新能源" --json
        """)
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--sort", choices=["default", "latest", "hottest"],
                        default="default", help="排序方式（默认/最新/最热）")
    parser.add_argument("--top", type=int, default=3, help="Top N 数量（默认3）")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON 报告")
    args = parser.parse_args()

    run_pipeline(args.keyword, args.sort, args.top, args.json)


if __name__ == "__main__":
    main()
