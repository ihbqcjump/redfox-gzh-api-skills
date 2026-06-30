---
name: gzh-query-user
description: 获取公众号账号详细信息，支持按微信号或公众号名称查询，返回认证状态、分类、标签、简介等完整信息；当用户需要查询某个公众号的基本信息、认证情况、账号分类时使用
dependency:
  python:
    - 无第三方依赖（纯标准库：urllib.request, json, os, sys, argparse）
---

# 获取公众号账号信息（优质库）

## 1. 简介

通过 RedFox API 查询公众号账号的详细信息，包括认证状态、账号分类、标签、简介、地区等。支持按微信号精确查询，也可提供公众号名称辅助匹配。

## 2. 功能特性

- 按微信号查询公众号完整信息
- 支持公众号名称辅助匹配
- 返回认证状态、分类、标签、地区等维度
- 支持 JSON 原始输出和格式化输出

## 3. 环境变量

| 环境变量 | 说明 | 是否必填 |
| -------- | ---- | -------- |
| `REDFOX_API_KEY` | 红狐数据 API Key | 是 |

## 4. 使用指南

```bash
python scripts/query_user.py --account <微信号>
python scripts/query_user.py --account <微信号> --account-name <公众号名称>
python scripts/query_user.py --account <微信号> --json
```

### 参数说明

- `--account`（必填）：公众号微信号，如 `rmrbwx`
- `--account-name`（可选）：公众号名称，辅助匹配
- `--json`（可选）：输出原始 JSON 数据

## 5. 输出示例

```
公众号名称: 人民日报
微信号: rmrbwx
账号分类: 时事新闻
认证状态: 微信认证：人民日报社
简介: 这是一个示例公众号简介
标签: 科技,互联网
地区: 广东 深圳
```
