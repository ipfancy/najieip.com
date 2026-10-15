#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取房屋模板：mili 同日精修页 head/JSON-LD + 两索引首卡块 + 文章 summary"""
import os, re, json, sqlite3

REPO = os.path.expanduser("~/wiki/najieip-verify")
TPL = os.path.join(REPO, "mili/blog/patent-vs-trade-secret-layering-2026.html")
t = open(TPL, encoding="utf-8").read()
print("=== A. 模板页 head ===")
print(t[: t.find("</head>") + 7])

print("\n=== B. 模板页 JSON-LD 块 ===")
for i, m in enumerate(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)):
    print("--- block %d ---" % i)
    print(m.group(1).strip()[:1600])

print("\n=== C. 模板页 <br> 用法 ===")
print("  <br> count:", t.count("<br>"))

print("\n=== D. 主索引首卡（card 深度配对提取） ===")
def cards(path, n=2):
    s = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'<div class="article-card">', s):
        i = m.start(); depth = 0; j = i
        for mm in re.finditer(r"<(/?)div[^>]*>", s[i:]):
            depth += 1 if mm.group(1) == "" else -1
            if depth == 0:
                j = i + mm.end(); break
        out.append(s[i:j])
        if len(out) >= n:
            break
    return out, s

main_cards, main_s = cards(os.path.join(REPO, "blog/index.html"), 1)
mili_cards, mili_s = cards(os.path.join(REPO, "mili/blog/index.html"), 1)
print("--- main 首卡 ---"); print(main_cards[0])
print("--- mili 首卡 ---"); print(mili_cards[0])

print("\n=== E. 主索引容器开头 400 字 ===")
i = main_s.find('<div class="container">')
print(repr(main_s[i:i+400]))
print("\n=== F. mili 索引容器开头 400 字 ===")
j = mili_s.find('<div class="container">')
print(repr(mili_s[j:j+400]))

print("\n=== G. content.db summary ===")
con = sqlite3.connect(os.path.expanduser("~/wiki/database/content.db"))
cur = con.cursor()
cur.execute("SELECT summary, tags, word_count FROM articles WHERE article_id='ART-2026-0107'")
for r in cur.fetchall():
    print("  summary:", r[0][:400] if r[0] else None)
    print("  tags:", r[1], "words:", r[2])
con.close()
