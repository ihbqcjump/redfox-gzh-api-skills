#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号 API 模块

提供公众号基础能力：
  - 获取 access_token（带文件缓存）
  - 上传永久素材（图片）
  - 新建草稿
"""

import json
import os
import time
import urllib.request
import urllib.error

BASE = "https://api.weixin.qq.com/cgi-bin"
TOKEN_CACHE = "/tmp/_wechat_access_token.json"


def _log(msg):
    print(f"  [wechat] {msg}", flush=True)


# ─── access_token ─────────────────────────────────────────────────

def get_access_token(appid, secret, force_refresh=False):
    """获取 access_token，带文件缓存（有效期内直接复用）"""
    if not force_refresh and os.path.exists(TOKEN_CACHE):
        try:
            with open(TOKEN_CACHE, "r") as f:
                cache = json.load(f)
            if cache.get("expires_at", 0) > time.time() + 60:
                return cache["access_token"]
        except Exception:
            pass

    url = (
        f"{BASE}/token?grant_type=clientcred"
        f"&appid={appid}&secret={secret}"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"获取 access_token 网络失败: {e}")

    if "access_token" not in data:
        raise RuntimeError(
            f"获取 access_token 失败: errcode={data.get('errcode')} "
            f"errmsg={data.get('errmsg')}"
        )

    token = data["access_token"]
    expires_in = data.get("expires_in", 7200)
    with open(TOKEN_CACHE, "w") as f:
        json.dump({
            "access_token": token,
            "expires_at": time.time() + expires_in,
        }, f)
    _log(f"access_token 已获取，有效期 {expires_in}s")
    return token


# ─── multipart 编码 ──────────────────────────────────────────────

def _encode_multipart(fields, files):
    """
    编码 multipart/form-data。
    fields: [(name, value), ...]   value 为 str
    files:  [(name, filename, data_bytes, content_type), ...]
    返回 (content_type_str, body_bytes)
    """
    boundary = "----RedFoxAutoPublish7MAH2d"
    parts = []

    for name, value in fields:
        parts.append(f"--{boundary}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"'.encode()
        )
        parts.append(b"")
        parts.append(value.encode("utf-8") if isinstance(value, str) else value)

    for name, filename, data, ctype in files:
        parts.append(f"--{boundary}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"; '
            f'filename="{filename}"'.encode()
        )
        parts.append(f"Content-Type: {ctype}".encode())
        parts.append(b"")
        parts.append(data)

    parts.append(f"--{boundary}--".encode())
    parts.append(b"")

    body = b"\r\n".join(parts)
    ct = f"multipart/form-data; boundary={boundary}"
    return ct, body


# ─── 上传永久素材 ────────────────────────────────────────────────

def upload_image(token, image_data, filename="image.jpg"):
    """上传永久图片素材，返回 media_id"""
    url = f"{BASE}/material/add_material?access_token={token}&type=image"
    ct, body = _encode_multipart(
        [],
        [("media", filename, image_data, "image/jpeg")],
    )
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", ct)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"上传图片网络失败: {e}")

    if "media_id" not in data:
        raise RuntimeError(
            f"上传图片失败: errcode={data.get('errcode')} "
            f"errmsg={data.get('errmsg')}"
        )
    _log(f"图片已上传 media_id={data['media_id']}")
    return data["media_id"]


# ─── 新建草稿 ────────────────────────────────────────────────────

def create_draft(token, articles):
    """
    新建草稿。
    articles: list of dict，每个 dict 为一篇文章，字段参考公众号草稿 API。
    返回 media_id（草稿 ID）。
    """
    url = f"{BASE}/draft/add?access_token={token}"
    payload = json.dumps({"articles": articles}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"创建草稿网络失败: {e}")

    if "media_id" not in data:
        raise RuntimeError(
            f"创建草稿失败: errcode={data.get('errcode')} "
            f"errmsg={data.get('errmsg')}"
        )
    _log(f"草稿已创建 media_id={data['media_id']}")
    return data["media_id"]
