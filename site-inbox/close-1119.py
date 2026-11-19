#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 收尾：description 句子边界修正 + articles.json 隔离 + sitemap 看门"""
import os, re, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
BAD = "20261119-mili-tv-box-backdoor-four-layers"
fp = os.path.join(REPO, "mili/blog", BAD + ".html")
t = open(fp, encoding="utf-8").read()

m = re.search(r'<meta name="description" content="([^"]*)"', t)
old = m.group(1)
cut = old
if not cut.endswith("。"):
    j = old.rfind("。")
    if j > 80:
        cut = old[:j + 1]
print("OLD:", len(old), old[-20:])
print("NEW:", len(cut), cut[-20:])
if cut != old:
    t = t.replace(f'content="{old}"', f'content="{cut}"')
    open(fp, "w", encoding="utf-8").write(t)
    print("desc fixed")

# ---- articles.json 守卫 ----
g = os.path.join(REPO, "site-inbox/guard-0918-articles-json.py")
r = subprocess.run(["python3", g, "--apply"], capture_output=True, text=True, cwd=REPO)
print("=== GUARD APPLY ===")
print(r.stdout[-1200:], r.stderr[-300:])
r2 = subprocess.run(["python3", g, "--check"], capture_output=True, text=True, cwd=REPO)
print("=== GUARD CHECK ===")
print(r2.stdout[-900:])

# ---- sitemap 看门 ----
print("=== SITEMAP 看门 ===")
before = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read().count("<loc>")
r3 = subprocess.run(["bash", os.path.expanduser("~/.hermes/scripts/sitemap-auto.sh")],
                    capture_output=True, text=True, cwd=REPO)
print("exit:", r3.returncode, r3.stdout[-400:], r3.stderr[-300:])
after = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read().count("<loc>")
print(f"loc {before} -> {after}")
