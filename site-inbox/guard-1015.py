#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sitemap 看门 + articles.json 守卫 + 新页 URL 收录确认"""
import os, re, subprocess, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
SLUG = "20261015-ip-4-hard-deadlines-buju-revision"
URL_NEW = "/mili/blog/%s.html" % SLUG
SM = os.path.join(REPO, "sitemap.xml")

def locs():
    t = open(SM, encoding="utf-8").read()
    return t, re.findall(r"<loc>(.*?)</loc>", t)

t, L = locs()
print("=== A. sitemap 前状态 ===")
print("  loc=%d  lastmod缺失=%d  含新页=%s" % (
    len(L), sum(1 for u in re.findall(r"<url>(.*?)</url>", t, re.S) if "<lastmod>" not in u),
    any(URL_NEW in u for u in L)))

print("\n=== B. 跑看门 sitemap-auto.sh ===")
p = subprocess.run(["bash", os.path.expanduser("~/.hermes/scripts/sitemap-auto.sh")],
                   capture_output=True, text=True, timeout=180)
print("  rc=%d" % p.returncode)
print("  stdout:", (p.stdout or "").strip()[:1200])
print("  stderr:", (p.stderr or "").strip()[:600])

t2, L2 = locs()
print("\n=== C. sitemap 后状态 ===")
print("  loc=%d -> %d  含新页=%s" % (len(L), len(L2), any(URL_NEW in u for u in L2)))

print("\n=== D. articles.json 守卫 ===")
g = os.path.join(REPO, "site-inbox/guard-0918-articles-json.py")
if os.path.exists(g):
    p = subprocess.run(["python3", g, "--check"], capture_output=True, text=True, timeout=180)
    print("  rc=%d" % p.returncode)
    print((p.stdout or "").strip()[:2500])
    print((p.stderr or "").strip()[:800])
else:
    print("  guard script missing:", g)

print("\n=== E. git 状态 ===")
p = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
print(p.stdout.strip() or "(clean)")
p = subprocess.run(["git", "log", "origin/main", "--oneline", "-3"], capture_output=True, text=True)
print(p.stdout.strip())
