#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断 20261015 新页 + 取 md 源 + 取同日同品牌房屋模板"""
import os, sqlite3, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
PAGE = os.path.join(REPO, "mili/blog/20261015-ip-4-hard-deadlines-buju-revision.html")

print("=== A. content.db 源头 ===")
con = sqlite3.connect(os.path.expanduser("~/wiki/database/content.db"))
cur = con.cursor()
cur.execute("PRAGMA table_info(articles)")
print("  cols:", [c[1] for c in cur.fetchall()])
for aid in ("ART-2026-0107", "ART-2026-0106"):
    cur.execute("SELECT article_id,title,source_file,publish_date,status,tags FROM articles WHERE article_id=?", (aid,))
    for r in cur.fetchall():
        print("  ", r)
con.close()

print("\n=== B. 破页结构快照 ===")
t = open(PAGE, encoding="utf-8").read()
print("  bytes=%d" % len(t.encode()))
print("  <title>:", re.search(r"<title>(.*?)</title>", t, re.S).group(1).strip()[:160])
for m in re.finditer(r'<meta[^>]*>', t):
    s = m.group(0)
    if any(k in s for k in ("description", "og:", "twitter:", "keywords", "canonical")):
        print("   ", s.strip()[:200])
print("  link stylesheet:", re.findall(r'<link[^>]*stylesheet[^>]*>', t))
print("  h1:", re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S))
print("  h2 count:", len(re.findall(r"<h2[ >]", t)))
print("  style block len:", len(re.findall(r"<style>.*?</style>", t, re.S)))
print("\n  --- head 前半 ---")
print(t[:1400])
print("\n  --- 正文首 900 字 ---")
b = t[t.find("<body"):]
print(b[:900])
print("\n  --- 尾 600 字 ---")
print(t[-600:])

print("\n=== C. md 源 ===")
slug = "20261015-ip-4-hard-deadlines-buju-revision"
cands = []
for root, dirs, fs in os.walk(os.path.expanduser("~/wiki/digital-employees/articles")):
    for f in fs:
        if slug in f or "硬时限" in f:
            cands.append(os.path.join(root, f))
print("  candidates:", cands)
