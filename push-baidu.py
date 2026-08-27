#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度主动推送脚本（najieip.com）
================================

把 sitemap 里的 URL 增量推送给百度（普通收录/主动推送 API），
只推「新增」的 URL，避免浪费每日配额。

用法：
    python push-baidu.py

token 来源（二选一，优先环境变量）：
    1. 环境变量 BAIDU_TOKEN
    2. 本地文件 .baidu_token（已加入 .gitignore，不进 git）

已推送记录保存在 .baidu-pushed.txt（本地，不进 git）。

配额说明：百度普通收录每日有推送配额上限，用完返回 over quota，
次日凌晨自动重置。本脚本增量推送，配额用完会明确提示。
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "http://data.zz.baidu.com/urls?site=https://najieip.com&token={token}"
SITEMAP = os.path.join(ROOT, "sitemap.xml")
PUSHED = os.path.join(ROOT, ".baidu-pushed.txt")
TOKEN_FILE = os.path.join(ROOT, ".baidu_token")


def get_token():
    tok = os.environ.get("BAIDU_TOKEN", "").strip()
    if tok:
        return tok
    if os.path.isfile(TOKEN_FILE):
        with open(TOKEN_FILE, encoding="utf-8") as f:
            tok = f.read().strip()
        if tok:
            return tok
    return None


def read_sitemap_urls():
    if not os.path.isfile(SITEMAP):
        print("[错误] 找不到 sitemap.xml，请先运行 update-sitemap.py")
        return []
    with open(SITEMAP, encoding="utf-8") as f:
        raw = f.read()
    return re.findall(r"<loc>\s*([^<]+?)\s*</loc>", raw)


def read_pushed():
    if not os.path.isfile(PUSHED):
        return set()
    with open(PUSHED, encoding="utf-8") as f:
        return set(l.strip() for l in f if l.strip())


def write_pushed(urls):
    with open(PUSHED, "a", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")


def post(urls):
    body = "\n".join(urls).encode("utf-8")
    req = urllib.request.Request(
        API.format(token=get_token()),
        data=body,
        headers={"Content-Type": "text/plain"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 百度 over quota / 参数错误等返回 4xx + JSON body
        try:
            return json.loads(e.read().decode("utf-8", "ignore"))
        except Exception:
            return {"http_error": e.code}
    except Exception as e:
        return {"error": str(e)}


def main():
    token = get_token()
    if not token:
        print("[错误] 未找到百度推送 token。")
        print("       请设置环境变量 BAIDU_TOKEN，或在本目录创建 .baidu_token 文件写入 token。")
        sys.exit(1)

    urls = read_sitemap_urls()
    if not urls:
        sys.exit(1)

    pushed = read_pushed()
    new_urls = [u for u in urls if u not in pushed]
    print(f"sitemap 共 {len(urls)} 个 URL，已推送 {len(pushed)}，新增 {len(new_urls)}")

    if not new_urls:
        print("无新增 URL，无需推送。")
        return

    # 分批推送（每批最多 2000，这里按配额自适应，先一批试）
    result = post(new_urls)
    print("百度返回:", json.dumps(result, ensure_ascii=False))

    if "success" in result:
        # 成功，记录（注意：百度 success 是成功条数，但没说具体是哪些 URL，这里保守记录全部）
        # 实际百度按提交顺序成功，剩余配额不足时只成功前面部分，这里简化记录前 N 个
        n = result.get("success", 0)
        write_pushed(new_urls[:n])
        remain = result.get("remain", "?")
        print(f"✅ 成功推送 {n} 条，今日剩余配额 {remain}")
        if n < len(new_urls):
            print(f"⚠️ 有 {len(new_urls) - n} 条未推送（配额不足），明天再跑一次会自动续推。")
    elif result.get("error") == 400 or "over quota" in str(result.get("message", "")):
        print("⚠️ 今日推送配额已用完（over quota），明天凌晨重置后再跑一次即可。")
    else:
        print("⚠️ 推送失败，请检查返回信息。")


if __name__ == "__main__":
    main()
