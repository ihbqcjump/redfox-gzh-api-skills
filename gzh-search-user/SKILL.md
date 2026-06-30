---
name: gzh-search-user
description: 通过关键词搜索公众号账号列表，支持相关性/最新/最热排序，返回红狐指数、认证信息、最近发文等；当用户想搜索某类公众号、找热门账号、按关键词发现公众号时使用
dependency:
  python:
    - 无第三方依赖（纯标准库：urllib.request, json, os, sys, argparse）
---

# 搜索关键词获取公众号账号（优质库）

## 1. 简介

通过 RedFox API 按关键词搜索公众号账号，返回匹配的账号列表。支持按相关性、最新发文时间、最热阅读数排序，返回红狐指数、认证信息、账号分类、最近发文等完整信息。

## 2. 功能特性

- 按关键词搜索公众号账号
- 支持三种排序：相关性（默认）、最新、最热
- 分页查询，每页 20 条
- 返回红狐指数、认证状态、分类、标签、地区等维度
- 支持 JSON 原始输出和格式化输出

## 3. 环境变量

| 环境变量 | 说明 | 是否必填 |
| -------- | ---- | -------- |
| `REDFOX_API_KEY` | 红狐数据 API Key | 是 |

## 4. 使用指南

```bash
python scripts/search_user.py --keyword <关键词>
python scripts/search_user.py --keyword <关键词> --sort latest
python scripts/search_user.py --keyword <关键词> --sort hottest --offset 20
python scripts/search_user.py --keyword <关键词> --json
```

### 参数说明

- `--keyword`（必填）：搜索关键词，如 `人工智能`
- `--offset`（可选）：偏移量，从 0 开始，每页 +20，默认 0
- `--sort`（可选）：排序方式，可选 `default`（相关性）、`latest`（最新）、`hottest`（最热），默认 `default`
- `--max-items`（可选）：最大返回数量，默认 20
- `--json`（可选）：输出原始 JSON 数据

## 5. 输出示例

```
搜索结果: 共 100 个账号 (有更多)
============================================================

[1] 人民日报
    微信号: rmrbwx
    红狐指数: 85.5
    分类: 时事新闻
    认证: 微信认证：人民日报社
    简介: 这是一个示例公众号简介
    最近发文: 人工智能热门课程
    最近发文时间: 2026-01-13 18:00:00
    标签: 科技,互联网
    地区: 广东 深圳
```
