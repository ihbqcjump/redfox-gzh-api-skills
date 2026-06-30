---
name: gzh-query-ai-works
description: 搜索公众号 AI 创作作品，支持按关键词和时间范围筛选；当用户需要查找 AI 生成的公众号文章、按时间段筛选 AI 创作内容时使用
dependency:
  python:
    - 无第三方依赖（纯标准库：urllib.request, json, os, sys, argparse, datetime）
---

# 搜索关键词获取公众号 AI 创作作品（优质库）

## 1. 简介

通过 RedFox API 搜索公众号中的 AI 创作作品。支持按关键词搜索，并可指定时间范围（开始/结束时间）进行筛选。采用分页查询，返回 AI 生成文章的标题、作者、阅读量、点赞数等信息。

## 2. 功能特性

- 按关键词搜索 AI 创作作品
- 支持按时间范围筛选（开始/结束时间）
- 分页查询，支持指定页码和每页条数
- 返回阅读/点赞/评论/分享等互动数据
- 自动处理时间格式补全
- 支持 JSON 原始输出和格式化输出

## 3. 环境变量

| 环境变量 | 说明 | 是否必填 |
| -------- | ---- | -------- |
| `REDFOX_API_KEY` | 红狐数据 API Key | 是 |

## 4. 使用指南

```bash
python scripts/query_ai_works.py --keyword <关键词>
python scripts/query_ai_works.py --keyword <关键词> --start-time 2026-01-01 --end-time 2026-06-30
python scripts/query_ai_works.py --keyword <关键词> --page-num 2 --page-size 10
python scripts/query_ai_works.py --keyword <关键词> --json
```

### 参数说明

- `--keyword`（必填）：搜索关键词
- `--page-num`（可选）：页码，从 1 开始，默认 1
- `--page-size`（可选）：每页条数，默认 20
- `--start-time`（可选）：开始时间，格式 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
- `--end-time`（可选）：结束时间，格式 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
- `--max-items`（可选）：最大返回数量，默认 20
- `--json`（可选）：输出原始 JSON 数据

## 5. 输出示例

```
AI 创作作品: 共 200 篇，第 1/10 页
============================================================

[1] AI 时代的教育变革
    作者: 教育观察
    阅读: 3.2w | 点赞: 1800
    评论: 150 | 分享: 320
    创建时间: 2026-03-10 14:30:00
    链接: https://mp.weixin.qq.com/s/ai-example
    话题: 人工智能
```
