#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-22: mili/blog 精修版覆盖(并发版缺OG/残留markdown)"""
import re, json, html, os, sys

BASE = '/Users/ziganghe/wiki/najieip-verify'
sys.path.insert(0, f'{BASE}/site-inbox')
# 复用 gen-siteops-0822.py 的函数
from gen_siteops import ARTICLES, extract_article, build_article_html

def main():
    for a in ARTICLES:
        path = os.path.join(BASE, 'mili', 'blog', f"{a['slug']}.html")
        content = build_article_html(
            a, '觅理律师事务所', '觅理律所',
            f"https://najieip.com/mili/blog/{a['slug']}.html",
            '觅理博客', 'https://najieip.com/mili/blog/', '/mili/')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"OK mili/blog/{a['slug']}.html")

if __name__ == '__main__':
    main()
