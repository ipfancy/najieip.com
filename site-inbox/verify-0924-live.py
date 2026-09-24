#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 线上验证：HTTP 状态 + 文章页严格字节一致 + 索引新卡 HIT + 结构四件"""
import os, re, subprocess, urllib.request, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260924-malicious-litigation-supervision"
ART_URL = "https://najieip.com/mili/blog/%s.html" % SLUG


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 siteops-verify"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read().decode("utf-8", "replace")


def head(url):
    try:
        out = subprocess.run(["curl", "-sI", "-L", "--max-time", "30", url],
                             capture_output=True, text=True).stdout
        return out.split("\n")[0].strip()
    except Exception as e:
        return "ERR %s" % e


print("=== [1] HTTP 状态 ===")
for u in ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
          "https://najieip.com/blog/", "https://najieip.com/mili/blog/",
          "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt", ART_URL]:
    print("  %s  %s" % (head(u), u))

print("\n=== [2] 文章页线上结构四件 ===")
st, live = fetch(ART_URL)
local = open(os.path.join(REPO, "mili/blog/%s.html" % SLUG), encoding="utf-8").read()
print("  status=%s bytes(live)=%d bytes(local)=%d" % (st, len(live.encode()), len(local.encode())))
print("  字节严格一致:", "IDENTICAL" if live == local else "DIFF")
print("  h1=%d h2=%d ld=%d og:image=%s keywords=%s" % (
    live.count("<h1"), live.count("<h2"), live.count("application/ld+json"),
    "og:image" in live, 'name="keywords"' in live))
print("  og/canonical/ld 合计=%d (>=4 期望)  **=%d  ***字面量=%d  schema.org=%d" % (
    len(re.findall(r"og:url|canonical|application/ld\+json", live)),
    live.count("**"), live.count("https://***"), live.count("https://schema.org")))

print("\n=== [3] 索引新卡 HIT + 卡片计数 ===")
for idx, needle in [("mili/blog/index.html", "./%s.html" % SLUG), ("blog/index.html", "/mili/blog/%s.html" % SLUG)]:
    st2, t = fetch("https://najieip.com/%s" % idx.replace("index.html", ""))
    loc = open(os.path.join(REPO, idx), encoding="utf-8").read()
    n_live = t.count('<div class="article-card">')
    n_loc = loc.count('<div class="article-card">')
    print("  %-22s live卡=%d local卡=%d | 新卡HIT=%s | Δ字节=%d" % (
        idx, n_live, n_loc, needle in t, len(t.encode()) - len(loc.encode())))

print("\n=== [4] sitemap 含该文 ===")
st3, sm = fetch("https://najieip.com/sitemap.xml")
print("  loc HIT:", ART_URL in sm, "| 总 loc:", sm.count("<loc>"))
