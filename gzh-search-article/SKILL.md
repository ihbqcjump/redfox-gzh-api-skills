---
name: gzh-search-article
description: 通过关键词搜索公众号文章列表，支持相关性/最新/最热排序，返回阅读量、点赞、原创标识等；当用户想搜索某主题的文章、找热门/最新公众号文章时使用
dependency:
  python:
    - 无第三方依赖（纯标准库：urllib.request, json, os, sys, argparse）
---

# 搜索关键词获取公众号作品（优质库）

## 1. 简介

通过 RedFox API 按关键词搜索公众号文章，返回匹配的文章列表。支持按相关性、最新发布时间、最热阅读量排序，返回阅读量、在看数、点赞数、原创标识、文章链接等完整信息。

## 2. 功能特性

- 按关键词搜索公众号文章
- 支持三种排序：相关性（默认）、最新、最热
- 分页查询，每页 20 条
- 返回阅读/在看/点赞/评论/收藏/分享等互动数据
- 标识原创文章
- 支持 JSON 原始输出和格式化输出

## 3. 环境变量

| 环境变量 | 说明 | 是否必填 |
| -------- | ---- | -------- |
| `REDFOX_API_KEY` | 红狐数据 API Key | 是 |

## 4. 使用指南

```bash
python scripts/search_article.py --keyword <关键词>
python scripts/search_article.py --keyword <关键词> --sort latest
python scripts/search_article.py --keyword <关键词> --sort hottest --offset 40
python scripts/search_article.py --keyword <关键词> --json
```

### 参数说明

- `--keyword`（必填）：搜索关键词，如 `人工智能`
- `--offset`（可选）：偏移量，从 0 开始，每页 +20，默认 0
- `--sort`（可选）：排序方式，可选 `default`（相关性）、`latest`（最新）、`hottest`（最热），默认 `default`
- `--max-items`（可选）：最大返回数量，默认 20
- `--json`（可选）：输出原始 JSON 数据

## 5. 输出示例

```
搜索结果: 共 500 篇文章 (有更多)
============================================================

[1] 人工智能热门课程 [原创]
    作者: 科研云
    分类: 时事新闻
    发布时间: 2026-01-15 10:00:00
    阅读: 5.0w | 在看: 1200 | 点赞: 3500
    评论: 280 | 收藏: 500 | 分享: 150
    链接: https://mp.weixin.qq.com/s/example
    摘要: 这是文章摘要内容
```
