#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
najieip.com sitemap.xml 自动生成器（标准版）
=============================================

解决的问题：
    旧流程靠 site-inbox/ 里按日期临时写的脚本手动更新 sitemap，
    文章改名/迁移（中文文件名 ↔ URL 编码）后 sitemap 跟不上，
    导致新文章漏进 sitemap、旧链接变成死链。

本脚本：
    扫描站点全部 .html，自动生成完整、无漏、无死链的 sitemap.xml。

用法：
    python update-sitemap.py

输出：
    覆盖站点根目录下的 sitemap.xml

依赖：仅 Python 标准库（3.6+）。
"""

import os
from datetime import datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://najieip.com"

# 不收录的目录（后台、构建脚本、依赖）
EXCLUDE_DIRS = {".git", "node_modules", "site-inbox", "dashboard"}
# 不收录的文件前缀（站长平台验证文件等，非内容页）
EXCLUDE_PREFIXES = ("baidu_verify_",)


def url_path_of(rel: str) -> str:
    """把仓库相对路径转成站点 URL 路径（index.html 归一化 + URL 编码）。"""
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        path = "/"
    elif rel.endswith("/index.html"):
        path = "/" + rel[: -len("index.html")]
    elif rel.endswith("/index.htm"):
        path = "/" + rel[: -len("index.htm")]
    else:
        path = "/" + rel
    # URL 编码（保留 / 分隔符），中文文件名自动转 %E5%8F%91 形式
    return quote(path, safe="/")


def priority_of(path: str) -> str:
    if path == "/":
        return "1.0"
    if path.count("/") == 1:
        return "0.9"   # 栏目页（/najie/ /mili/ 等）
    return "0.7"       # 文章页


def main():
    entries = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # 剪枝：跳过排除目录
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if not fn.lower().endswith((".html", ".htm")):
                continue
            if fn.startswith(EXCLUDE_PREFIXES):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, ROOT)
            path = url_path_of(rel)
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d")
            prio = priority_of(path)
            entries.append((path, mtime, prio))

    # 额外收录根目录特殊文件（llms.txt / robots.txt，用于 AI 爬虫 GEO 优化）
    for extra in ("llms.txt", "robots.txt"):
        fp = os.path.join(ROOT, extra)
        if os.path.isfile(fp):
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d")
            entries.append((f"/{extra}", mtime, "0.5"))

    # 去重（同一路径可能因 index.html 与目录重复），按路径排序
    entries = sorted(set(entries), key=lambda x: x[0])

    blocks = []
    for path, mtime, prio in entries:
        loc = DOMAIN + path
        blocks.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{mtime}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>{prio}</priority>\n"
            f"  </url>"
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(blocks)
        + "\n</urlset>\n"
    )

    out = os.path.join(ROOT, "sitemap.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write(sitemap)

    print(f"[完成] 已生成 {len(entries)} 个 URL -> {out}")


if __name__ == "__main__":
    main()
