---
name: redfox-auto-publish
description: >
  RedFox 公众号热点一条龙：自动抓取全网热门话题，AI 生成原创文章，发布到微信公众号草稿。
  输入一个关键词（或留空自动抓热点），一条龙完成「热点发现 → 内容生成 → 草稿发布」全流程。
  触发词：热点文章、公众号内容、自动写文章、公众号草稿、一条龙、自动发布、RedFox 发布、热点创作
version: 1.0.0
---

# RedFox 热点一条龙 → 公众号草稿自动发布

## 链路概览

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Phase 1     │     │  Phase 2     │     │  Phase 3     │
│  热点发现    │ ──▶ │  内容生成    │ ──▶ │  草稿发布    │
│  RedFox API  │     │  LLM API     │     │  微信 MP API │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 用法

```bash
# 全自动：抓热点 → 生成文章 → 发布草稿
python scripts/pipeline.py

# 指定关键词
python scripts/pipeline.py "人工智能"

# 只生成不发布（预览）
python scripts/pipeline.py --dry-run

# JSON 输出
python scripts/pipeline.py --json
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `REDFOX_API_KEY` | 是 | RedFox API 密钥 |
| `WECHAT_APPID` | 发布时 | 公众号 AppID |
| `WECHAT_SECRET` | 发布时 | 公众号 AppSecret |
| `LLM_API_URL` | 否 | LLM 接口（默认 `https://api.openai.com/v1`） |
| `LLM_API_KEY` | 生成时 | LLM API Key |
| `LLM_MODEL` | 否 | 模型名（默认 `gpt-4o`） |
| `WECHAT_THUMB_ID` | 否 | 预置封面图 media_id |

## 工作流程

### Phase 1 — 热点发现
- 使用 15+ 个跨类别关键词（科技/财经/社会/国际）扫描 RedFox 最热文章
- 按互动量（阅读/点赞/分享/在看）综合打分排序
- 自动去重，提取 Top 10 热点

### Phase 2 — 内容生成
- 将热点数据 + 参考文章摘要喂给 LLM
- LLM 生成原创文章：标题 + HTML 正文 + 摘要
- 自动适配公众号排版风格

### Phase 3 — 草稿发布
- 获取微信 access_token（带缓存）
- 自动生成封面图并上传（或使用预置封面）
- 创建公众号草稿

## 注意事项
- 缩略图使用纯 Python 标准库生成蓝色渐变 PNG，无需 Pillow
- access_token 缓存在 `/tmp/_wechat_access_token.json`
- LLM 返回 JSON 格式，自动兼容 markdown 代码块包裹
