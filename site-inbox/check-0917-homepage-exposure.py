#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-0917-homepage-exposure.py — 首页 articles.slice(0,6) 是否会把「无页面条目」渲染出去"""
import json, os, re

SITE = os.path.expanduser("~/wiki/najieip-verify")
html = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
i = html.find("articles.slice(0, 6)")
print("== index.html 渲染片段 ==")
print(html[max(0, i - 700):i + 260].strip()[-900:])

arts = json.load(open(os.path.join(SITE, "articles.json"), encoding="utf-8"))
print("\n== articles.json 排序键 ==")
print([k for k in arts[0].keys()])
key = "date" if "date" in arts[0] else None
print("样本:", json.dumps(arts[0], ensure_ascii=False)[:200])


def exists(a):
    u = a.get("url", "")
    return os.path.exists(os.path.join(SITE, u.lstrip("/")))


bogus = [a for a in arts if not exists(a)]
print("\n条目总数 %d，无页面 %d" % (len(arts), len(bogus)))
if key:
    s = sorted(arts, key=lambda a: a.get(key, ""), reverse=True)
    pos = [n for n, a in enumerate(s, 1) if not exists(a)]
    print("按 %s 降序后，第一个无页面条目在第 %s 位（首页只渲染前 6）" % (key, pos[0] if pos else "-"))
else:
    pos = [n for n, a in enumerate(arts, 1) if not exists(a)]
    print("按文件顺序，第一个无页面条目在第 %s 位" % (pos[0] if pos else "-"))
