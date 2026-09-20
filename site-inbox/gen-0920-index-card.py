#!/usr/bin/env python3
# 0920 主索引补卡：insert 到 body 内首个 article-card 之前（日期降序顶部）
import os, re, sys, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "blog/index.html")
SLUG = "20260920-family-wealth-isolation-three-firewalls"
HREF = f"/mili/blog/{SLUG}.html"
CARD = ('<div class="article-card">\n'
        f'    <h2><a href="{HREF}">家族信托被当存款扣走4143万！这三道隔离墙都有缝</a></h2>\n'
        '    <div class="meta"><span class="tag">家族财富</span><span class="tag">财产隔离</span>'
        '<span class="tag">家企风险</span> 2026-09-20 · 觅理律师事务所</div>\n'
        '    <p>家族信托被法院当存款扣划4143万，保单现金价值可被冻结、离婚净身出户躲债被民法典堵死。'
        '家族财产隔离三道墙各自守什么、缝在哪，附10问自检清单。</p>\n'
        '  </div>\n  ')

t = open(P, encoding="utf-8").read()
body_start = t.find("<body")
body = t[body_start:]

if re.search(r'<h2><a href="[^"]*' + re.escape(SLUG) + r'[^"]*"', body):
    print("ALREADY-PRESENT: 跳过（幂等）")
    sys.exit(0)

idx = t.find('<div class="article-card"', body_start)
assert idx > 0, "找不到首卡锚点"
before = t.count('<div class="article-card"')
t2 = t[:idx] + CARD + t[idx:]

if "--apply" not in sys.argv:
    print(f"DRY-RUN: 卡片 {before} -> {t2.count('<div class=\"article-card\"')}")
    print("插入位置前 120 字符:", repr(t[idx-120:idx]))
    sys.exit(0)

shutil.copy(P, P + ".bak-0920")
open(P, "w", encoding="utf-8").write(t2)
print(f"WROTE. article-card {before} -> {t2.count('<div class=\"article-card\"')}")
