#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify-0918-structure.py — 09-18 修复后结构终验（工作区 vs git HEAD 对比）"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)

SLUG = "20260918-eu-digital-design-three-tables"
FILES = ["blog/index.html", "najie/blog/index.html"]
fails = []


def prev(path):
    r = subprocess.run(["git", "show", "HEAD:%s" % path], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def depth_scan(t, label):
    body = t[t.find("<body"):]
    depth = 0
    stack_empty = 0
    for tag in re.findall(r"<(/?)div[^>]*>", body):
        if tag == "/":
            depth -= 1
            if depth < 0:
                stack_empty += 1
                depth = 0
        else:
            depth += 1
    return depth, stack_empty


def analyse(t, path):
    """返回 (cards, dd2, malformed, depths)"""
    cards = [m.start() for m in re.finditer(r'<div class="article-card">', t)]
    # 每张卡是否以 <h2><a href= 起
    malformed = 0
    for c in cards:
        seg = t[c + len('<div class="article-card">'):c + 200].lstrip()
        if not seg.startswith("<h2><a href="):
            malformed += 1
    # depth==2 的卡片数
    body = t[t.find("<body"):]
    depth = 0
    dd2 = 0
    for m in re.finditer(r"<(/?)div([^>]*)>", body):
        closing, attrs = m.group(1), m.group(2)
        if closing:
            depth -= 1
        else:
            depth += 1
            if depth == 2 and attrs.startswith(' class="article-card"'):
                dd2 += 1
    return len(cards), dd2, malformed


print("=== 索引结构终验 ===")
for path in FILES:
    t = open(path, encoding="utf-8").read()
    old = prev(path)
    n_new, dd2, malformed = analyse(t, path)
    n_old = len(re.findall(r'<div class="article-card">', old)) if old else -1
    d, se = depth_scan(t, path)
    ld_ok = True
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(blk)
        except Exception as e:
            ld_ok = False
    # 新卡是首卡？
    first_is_new = t.find('<div class="article-card">') >= 0 and (
        SLUG in t[t.find('<div class="article-card">'):t.find('<div class="article-card">') + 400])
    # 新卡日期 vs 第二张卡日期
    ds = re.findall(r'<div class="meta">(?:<span class="tag">[^<]*</span>)*[^<]*?(\d{4}-\d{2}-\d{2})', t)
    # 只校验插入点前缀（遗留尾部本就不全局降序）
    ok_order = bool(ds) and ds[0] >= ds[1] if len(ds) >= 2 else bool(ds)
    pos_new = t.find('/%s.html' % SLUG) if SLUG not in t[:400] else t.find(SLUG)
    first_is_new = (t.find('<div class="article-card">') <= pos_new < t.find('<div class="article-card">') + 1600)
    print("\n--", path)
    print("   cards: %s -> %s (delta %+d)" % (n_old, n_new, n_new - n_old))
    print("   depth=%d stack_empty=%d  article-card@depth2=%d/%d" % (d, se, dd2, n_new))
    print("   malformed(不以 <h2><a href= 起)=%d  ld_ok=%s" % (malformed, ld_ok))
    print("   first_card_is_new=%s  date_order_ok=%s  dates[:3]=%s" % (first_is_new, ok_order, ds[:3]))
    print("   '**'=%d  'https://***'=%d" % (t.count("**"), t.count("https://***")))
    if n_new != n_old + 1:
        fails.append("%s: card delta != +1" % path)
    if not (d == 0 and se == 0):
        fails.append("%s: div 不平衡 depth=%d stack_empty=%d" % (path, d, se))
    if dd2 != n_new:
        fails.append("%s: depth2 卡片 %d != %d" % (path, dd2, n_new))
    if malformed:
        fails.append("%s: %d 张卡结构畸形" % (path, malformed))
    if not ld_ok:
        fails.append("%s: ld+json 解析失败" % path)
    if not first_is_new:
        fails.append("%s: 新卡不是首卡" % path)
    if not ok_order:
        fails.append("%s: 日期顺序异常 %s" % (path, ds[:3]))
    if t.count("**") or t.count("https://***"):
        fails.append("%s: markdown/脱敏污染" % path)

print("\n=== 文章页终验 ===")
ap = "najie/blog/%s.html" % SLUG
a = open(ap, encoding="utf-8").read()
checks = {
    "schema.org>=2": a.count("https://schema.org") >= 2,
    "no https://***": a.count("https://***") == 0,
    "no **": a.count("**") == 0,
    "no ai_smell": "ai_smell" not in a,
    "no 合集": "合集" not in a,
    "og:url": "og:url" in a,
    "canonical": 'rel="canonical"' in a,
    "og:image": "og:image" in a,
    "twitter:image": "twitter:image" in a,
    "ld>=2": a.count("application/ld+json") >= 2,
    "Article type": '"@type": "Article"' in a,
    "BreadcrumbList type": '"@type": "BreadcrumbList"' in a,
}
for k, v in checks.items():
    print("  %-22s %s" % (k, "OK" if v else "FAIL"))
    if not v:
        fails.append("article: %s" % k)
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', a, re.S):
    json.loads(blk)
print("  ld blocks parse       OK")

print("\n=== 结论 ===")
if fails:
    print("FAIL:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("ALL CHECKS PASS")
