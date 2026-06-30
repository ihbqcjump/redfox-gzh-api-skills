#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RedFox 热点一条龙 → 公众号草稿自动发布

全自动链路:
  Phase 1  热点发现  — RedFox API 多类别扫描，按互动量打分排序
  Phase 2  内容生成  — LLM 基于热点数据生成原创文章
  Phase 3  草稿发布  — 微信公众号 API 上传封面 + 创建草稿

用法:
  python pipeline.py                     # 全自动：抓热点 → 生成 → 发布
  python pipeline.py --dry-run           # 只抓热点 + 生成，不发布
  python pipeline.py "新能源"            # 指定关键词
  python pipeline.py --json              # 输出 JSON 结果
  python pipeline.py --no-publish        # 抓热点 + 生成但不发布（同 dry-run）

环境变量:
  REDFOX_API_KEY      — RedFox API 密钥（必填）
  WECHAT_APPID        — 公众号 AppID（发布时必填）
  WECHAT_SECRET       — 公众号 AppSecret（发布时必填）
  LLM_API_URL         — LLM 接口地址（默认 https://api.openai.com/v1）
  LLM_API_KEY         — LLM API Key（生成时必填）
  LLM_MODEL           — 模型名称（默认 gpt-4o）
  WECHAT_THUMB_ID     — 预置封面图 media_id（可选，没有则自动生成）
"""

import argparse
import json
import os
import random
import re
import struct
import sys
import time
import urllib.error
import urllib.request
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redfox_api import get_api_key, http_post

try:
    import wechat_mp
except ImportError:
    wechat_mp = None


# ═══════════════════════════════════════════════════════════════════
#  配  置
# ═══════════════════════════════════════════════════════════════════

API = {
    "search_article": "https://redfox.hk/story/api/gzhData/searchArticle",
    "query_work":     "https://redfox.hk/story/api/gzhData/queryWork",
    "ai_works":       "https://redfox.hk/story/api/parseWork/queryAiMsgs",
}

# 热点扫描关键词类别 — 覆盖科技/财经/社会/生活/国际 等
HOT_KEYWORDS = [
    # 通用热点
    "热点", "最新", "重磅", "关注", "突破",
    # 科技
    "人工智能", "芯片", "新能源", "5G",
    # 财经
    "股市", "经济", "房价",
    # 社会
    "教育", "医疗", "就业",
    # 国际
    "全球", "中美",
]


# ═══════════════════════════════════════════════════════════════════
#  Phase 1 — 热点发现
# ═══════════════════════════════════════════════════════════════════

def discover_trends(top_n=10):
    """
    用 HOT_KEYWORDS 扫描 RedFox 最热文章，按互动量打分排序。
    返回 (ranked_articles, raw_stats)
    """
    print("\n[Phase 1] 热点发现", flush=True)
    print(f"  扫描 {len(HOT_KEYWORDS)} 个关键词类别...", flush=True)

    seen_uuids = set()
    articles = []

    for kw in HOT_KEYWORDS:
        result = http_post(API["search_article"], {
            "keyword": kw,
            "offset": 0,
            "sortType": "_4",       # hottest
        })
        if result.get("code") != 2000:
            continue
        for art in result.get("data", {}).get("list", [])[:5]:
            uuid = art.get("workUuid", "")
            if uuid and uuid not in seen_uuids:
                seen_uuids.add(uuid)
                art["_kw"] = kw
                articles.append(art)

    print(f"  去重后共 {len(articles)} 篇候选", flush=True)

    # 打分排序
    for a in articles:
        a["_score"] = _score_article(a)
    articles.sort(key=lambda x: x["_score"], reverse=True)

    top = articles[:top_n]
    print(f"  Top {len(top)} 热点:", flush=True)
    for i, a in enumerate(top, 1):
        print(
            f"    {i:2d}. [{a.get('_kw', '')}] {a.get('title', 'N/A')[:36]}"
            f"  (score={a['_score']:.0f}"
            f" 阅读={a.get('readCount', 0)}"
            f" 点赞={a.get('likeCount', 0)})"
        )

    stats = {
        "total_scanned": len(articles),
        "categories": len(HOT_KEYWORDS),
    }
    return top, stats


def _score_article(a):
    """互动量综合打分"""
    score = 0.0
    score += (a.get("readCount") or 0) / 10000       # 阅读 / 万
    score += (a.get("likeCount") or 0) * 3 / 1000    # 点赞 ×3 / 千
    score += (a.get("shareCount") or 0) * 5 / 1000   # 分享 ×5 / 千
    score += (a.get("watchCount") or 0) * 2 / 1000   # 在看 ×2 / 千
    # 时效加分：7 天内发布 +20%
    pt = a.get("publishTime", "")
    if pt and _is_recent(pt, days=7):
        score *= 1.2
    return score


def _is_recent(time_str, days=7):
    """粗略判断时间字符串是否在 days 天内"""
    try:
        # 尝试解析 "2026-06-25 10:00:00" 格式
        from datetime import datetime, timedelta
        dt = datetime.strptime(time_str[:10], "%Y-%m-%d")
        return (datetime.now() - dt).days <= days
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════
#  Phase 2 — 内容生成
# ═══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
你是一位资深微信公众号内容创作者，擅长打造 10W+ 爆文。

你的任务：基于提供的热点话题和参考数据，创作一篇高质量的原创公众号文章。

要求：
1. 标题抓眼球但不标题党，让人有点击欲望
2. 开头 3 句话内必须勾住读者，制造悬念或共鸣
3. 内容要有独特视角和深度分析，不是简单复述新闻
4. 段落短小（2-4 句），适合手机阅读
5. 适当用数据、案例、对比增强说服力
6. 结尾引导读者思考和互动

输出严格 JSON（不要 markdown 代码块包裹）：
{
  "title": "文章标题（20字以内）",
  "content": "<p>HTML正文</p>（1500-2500字，段落用<p>包裹，可加<strong>强调</strong>）",
  "digest": "文章摘要（60字以内，显示在推送消息中）"
}"""


def _build_prompt(topic, refs):
    """构建 LLM 创作 prompt"""
    ref_text = ""
    for i, r in enumerate(refs, 1):
        ref_text += (
            f"\n--- 参考文章 {i} ---\n"
            f"标题: {r.get('title', 'N/A')}\n"
            f"数据: 阅读{r.get('readCount', 0)} "
            f"点赞{r.get('likeCount', 0)} "
            f"分享{r.get('shareCount', 0)}\n"
        )
        summary = r.get("summary") or r.get("description") or ""
        if summary:
            ref_text += f"摘要: {summary[:300]}\n"
        content = r.get("content", "")
        if content:
            ref_text += f"正文节选: {content[:500]}\n"

    return (
        f"当前热点话题: {topic}\n\n"
        f"以下是相关热门文章数据，请分析热点角度并创作原创文章:\n"
        f"{ref_text}"
    )


def generate_article(topic, refs):
    """调用 LLM 生成原创文章"""
    print(f"\n[Phase 2] 内容生成", flush=True)
    print(f"  话题: {topic}", flush=True)

    api_url = os.environ.get("LLM_API_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("LLM_API_KEY", "")
    model   = os.environ.get("LLM_MODEL", "gpt-4o")

    if not api_key:
        raise RuntimeError("LLM_API_KEY 环境变量未设置")

    url = f"{api_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_prompt(topic, refs)},
        ],
        "temperature": 0.85,
        "max_tokens": 4096,
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Authorization", f"Bearer {api_key}")

    print(f"  调用 LLM ({model})...", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"LLM 请求失败 HTTP {e.code}: {body[:300]}")
    except Exception as e:
        raise RuntimeError(f"LLM 请求失败: {e}")

    content = data["choices"][0]["message"]["content"]
    article = _parse_llm_json(content)

    print(f"  标题: {article['title']}", flush=True)
    print(f"  摘要: {article['digest']}", flush=True)
    print(f"  正文: {len(article['content'])} 字符", flush=True)
    return article


def _parse_llm_json(text):
    """从 LLM 响应中解析 JSON（兼容 markdown 代码块包裹）"""
    # 去掉可能的 ```json ... ``` 包裹
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # 尝试提取第一个 { ... } 块
        m2 = re.search(r"\{[\s\S]*\}", text)
        if m2:
            obj = json.loads(m2.group())
        else:
            raise
    for key in ("title", "content", "digest"):
        if key not in obj:
            raise ValueError(f"LLM 返回缺少字段: {key}")
    return obj


# ═══════════════════════════════════════════════════════════════════
#  缩略图生成（纯标准库，无需 Pillow）
# ═══════════════════════════════════════════════════════════════════

def _make_png_chunk(chunk_type, data):
    chunk = chunk_type + data
    return (
        struct.pack(">I", len(data))
        + chunk
        + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
    )


def generate_thumbnail(width=900, height=383):
    """
    生成蓝色渐变 PNG 缩略图（纯标准库实现）。
    返回 PNG 字节。
    """
    raw_rows = []
    for y in range(height):
        row = b"\x00"           # filter=None
        for x in range(width):
            r = int(25 + 50 * y / height)
            g = int(80 + 100 * y / height)
            b = int(200 + 55 * (1 - y / height))
            row += bytes([r, g, b])
        raw_rows.append(row)
    raw = b"".join(raw_rows)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = _make_png_chunk(b"IHDR", ihdr_data)
    idat = _make_png_chunk(b"IDAT", zlib.compress(raw, 6))
    iend = _make_png_chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


# ═══════════════════════════════════════════════════════════════════
#  Phase 3 — 发布到公众号草稿
# ═══════════════════════════════════════════════════════════════════

def publish_to_draft(article, thumb_png):
    """上传封面 + 创建草稿，返回 draft_media_id"""
    print(f"\n[Phase 3] 发布到公众号草稿", flush=True)

    if wechat_mp is None:
        raise RuntimeError("wechat_mp 模块未找到，请检查 scripts/ 目录")

    appid  = os.environ.get("WECHAT_APPID", "")
    secret = os.environ.get("WECHAT_SECRET", "")
    if not appid or not secret:
        raise RuntimeError("WECHAT_APPID / WECHAT_SECRET 环境变量未设置")

    token = wechat_mp.get_access_token(appid, secret)

    # 封面图：优先使用预置 media_id
    thumb_id = os.environ.get("WECHAT_THUMB_ID", "")
    if not thumb_id:
        print("  生成封面图...", flush=True)
        thumb_id = wechat_mp.upload_image(token, thumb_png, "cover.png")

    # 包装正文样式
    styled = _wrap_html(article["content"])

    draft_articles = [{
        "title":            article["title"],
        "author":           "",
        "digest":           article["digest"],
        "content":          styled,
        "content_source_url": "",
        "thumb_media_id":   thumb_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }]
    draft_id = wechat_mp.create_draft(token, draft_articles)
    return draft_id


def _wrap_html(body_html):
    """给正文加上适配公众号的 CSS 样式"""
    return (
        "<section style=\"margin:0;padding:0;\">"
        "<section style=\"font-size:16px;color:#333;"
        "line-height:1.8;letter-spacing:1px;"
        "word-break:break-all;\">"
        f"{body_html}"
        "</section></section>"
    )


# ═══════════════════════════════════════════════════════════════════
#  主编排
# ═══════════════════════════════════════════════════════════════════

def run_pipeline(keyword=None, dry_run=False, as_json=False):
    """
    主入口：串联 Phase 1→2→3。
    keyword=None 表示全自动热点扫描。
    """
    start = time.time()
    result = {"status": "ok"}

    # ── Phase 1 ───────────────────────────────────────────────────
    if keyword:
        print(f"\n[Phase 1] 关键词模式: \"{keyword}\"", flush=True)
        r = http_post(API["search_article"], {
            "keyword": keyword, "offset": 0, "sortType": "_4",
        })
        if r.get("code") == 2000:
            arts = r.get("data", {}).get("list", [])[:10]
            for a in arts:
                a["_kw"] = keyword
                a["_score"] = _score_article(a)
            arts.sort(key=lambda x: x["_score"], reverse=True)
            top_articles = arts
        else:
            top_articles = []
        topic = keyword
    else:
        top_articles, scan_stats = discover_trends()
        result["scan"] = scan_stats
        if not top_articles:
            print("\n  未发现热点数据，请检查 REDFOX_API_KEY", flush=True)
            result["status"] = "no_data"
            if as_json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return result
        topic = top_articles[0].get("_kw", "热点")

    result["topic"] = topic
    result["top_articles"] = [
        {
            "title": a.get("title"),
            "score": a.get("_score"),
            "readCount": a.get("readCount"),
            "likeCount": a.get("likeCount"),
            "shareCount": a.get("shareCount"),
        }
        for a in top_articles[:5]
    ]

    # ── Phase 2 ───────────────────────────────────────────────────
    refs = top_articles[:5]
    try:
        article = generate_article(topic, refs)
    except Exception as e:
        print(f"\n  内容生成失败: {e}", flush=True)
        result["status"] = "generate_failed"
        result["error"] = str(e)
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    result["article"] = article

    # ── Phase 3 ───────────────────────────────────────────────────
    if dry_run:
        print("\n[Phase 3] --dry-run 模式，跳过发布", flush=True)
        print(f"  标题: {article['title']}", flush=True)
        print(f"  摘要: {article['digest']}", flush=True)
        print(f"  正文长度: {len(article['content'])} 字符", flush=True)
    else:
        try:
            thumb_png = generate_thumbnail()
            draft_id = publish_to_draft(article, thumb_png)
            result["draft_media_id"] = draft_id
            print(f"\n  草稿 ID: {draft_id}", flush=True)
        except Exception as e:
            print(f"\n  发布失败: {e}", flush=True)
            result["status"] = "publish_failed"
            result["error"] = str(e)

    elapsed = time.time() - start
    result["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n{'='*50}", flush=True)
    print(f"  流水线完成  耗时 {elapsed:.1f}s", flush=True)
    print(f"{'='*50}\n", flush=True)

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


# ═══════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="RedFox 热点一条龙 → 公众号草稿自动发布",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  python pipeline.py                  # 全自动：抓热点 → 生成 → 发布
  python pipeline.py --dry-run        # 只生成不发布
  python pipeline.py "人工智能"       # 指定关键词
  python pipeline.py --json           # JSON 输出
""")
    parser.add_argument(
        "keyword", nargs="?", default=None,
        help="搜索关键词（留空则全自动扫描全网热点）",
    )
    parser.add_argument(
        "--dry-run", "--no-publish", dest="dry_run", action="store_true",
        help="只生成内容，不发布到公众号草稿",
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true",
        help="输出 JSON 格式结果",
    )
    args = parser.parse_args()
    run_pipeline(keyword=args.keyword, dry_run=args.dry_run, as_json=args.as_json)


if __name__ == "__main__":
    main()
