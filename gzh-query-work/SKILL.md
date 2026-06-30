---
name: gzh-query-work
description: 根据作品UUID获取公众号文章完整详情，包含内容关键词云、正文内容、互动数据等；当用户有文章workUuid需要获取详情或关键词分析时使用
dependency:
  python:
    - 无第三方依赖（纯标准库：urllib.request, json, os, sys, argparse）
---

# 根据作品uuid获取公众号作品（优质库）

## 1. 简介

通过 RedFox API 根据作品 UUID 获取公众号文章的完整详情。与 queryArticleDetail 类似，但通过 UUID 查询，额外返回内容关键词云（contentKeywords）信息，适合对文章进行关键词分析。

## 2. 功能特性

- 根据作品 UUID 获取完整详情
- 返回正文内容（全文）
- 额外返回内容关键词云（contentKeywords）
- 返回阅读/在看/点赞/评论/收藏/分享/打赏等完整互动数据
- 标识原创、显示原创账号和原文链接
- 返回封面图、发文位置、账号分类等元信息
- 支持 JSON 原始输出和格式化输出

## 3. 环境变量

| 环境变量 | 说明 | 是否必填 |
| -------- | ---- | -------- |
| `REDFOX_API_KEY` | 红狐数据 API Key | 是 |

## 4. 使用指南

```bash
python scripts/query_work.py --work-uuid <UUID>
python scripts/query_work.py --work-uuid <UUID> --json
```

### 参数说明

- `--work-uuid`（必填）：作品 UUID，如 `3F4DE056583609162E0816FBE8C183A3`
- `--json`（可选）：输出原始 JSON 数据

## 5. 输出示例

```
标题: 人工智能热门课程 [原创]
作品UUID: 3F4DE056583609162E0816FBE8C183A3
作者: 科研云
分类: 时事新闻
发布时间: 2026-01-15 10:00:00
发文位置: 广东深圳
阅读: 5.0w | 在看: 1200 | 点赞: 3500
评论: 280 | 收藏: 500 | 分享: 150 | 打赏: 30
链接: https://mp.weixin.qq.com/s/example
文章位置: 第1条（0=头条）

关键词: 科技(0.85), 互联网(0.72), AI(0.68)

摘要: 这是文章摘要内容

正文（前500字）: 这是文章正文内容...
```
