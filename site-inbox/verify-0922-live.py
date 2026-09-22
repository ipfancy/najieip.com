#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0922 线上验证：字节一致性 + 核心页 + JSON-LD + sitemap"""
import os, re, json, subprocess, time, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
TS = str(int(time.time()))


def curl(url, retries=3):
    for i in range(retries):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 200:
            return r.stdout
        time.sleep(3)
    return b""


def curl_code(url, retries=3):
    for i in range(retries):
        r = subprocess.run(["curl", "-sI", "-L", "-o", "/dev/null", "-w", "%{http_code}",
                            "--max-time", "30", url], capture_output=True, text=True)
        if r.stdout.strip() not in ("000", ""):
            return r.stdout.strip()
        time.sleep(3)
    return "000"


def rb(p):
    with open(p, "rb") as f:
        return f.read()


fails = []
print("=== A. 核心页 HTTP ===")
for u in ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
          "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt",
          "https://najieip.com/najie/blog/"]:
    c = curl_code(u)
    print("   %s %s" % (c, u))
    if c != "200":
        fails.append("HTTP %s %s" % (c, u))

print("\n=== B. 新修文章页 ===")
art = "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html"
u = "https://najieip.com/" + art
online = curl(u + "?cb=" + TS)
local = rb(art)
print("   online %d B / local %d B" % (len(online), len(local)))
ok = online == local
print("   字节一致:", ok)
if not ok:
    fails.append("article page bytes DIFF")
t = online.decode("utf-8", "replace")
for name, cond in [("og:url", "og:url" in t), ("canonical", "canonical" in t),
                   ("ld+json>=2", t.count("application/ld+json") >= 2),
                   ("schema.org>=2", t.count("https://schema.org") >= 2),
                   ("无脱敏***", "https://***" not in t), ("无'**'", t.count("**") == 0),
                   ("h1==1", t.count("<h1") == 1), ("og:image", "og:image" in t),
                   ("有style", "<style>" in t)]:
    print("   %-14s %s" % (name, "PASS" if cond else "FAIL"))
    if not cond:
        fails.append("article " + name)

print("\n=== C/D. 索引字节一致 ===")
for art2, url2 in [("najie/blog/index.html", "https://najieip.com/najie/blog/?cb=" + TS),
                   ("blog/index.html", "https://najieip.com/blog/?cb=" + TS)]:
    o = curl(url2)
    l = rb(art2)
    same = o == l
    print("   %-26s online %d B / local %d B  一致=%s" % (art2, len(o), len(l), same))
    if not same:
        import difflib
        dl = list(difflib.unified_diff(l.decode("utf-8", "replace").splitlines(),
                                       o.decode("utf-8", "replace").splitlines(), lineterm="", n=0))
        print("      diff 行数:", len(dl))
        for x in dl[:12]:
            print("      ", x[:120])
        if not any("email-protection" in x for x in dl):
            fails.append(art2 + " bytes DIFF")

print("\n=== E. articles.json ===")
o = curl("https://najieip.com/articles.json?cb=" + TS)
l = rb("articles.json")
print("   online %d B / local %d B  一致=%s" % (len(o), len(l), o == l))
if o != l:
    fails.append("articles.json DIFF")
try:
    aj = json.loads(o.decode())
    print("   条数:", len(aj), " 首条:", (aj[0].get("url") if aj else None))
    bad = [e.get("url") for e in aj if not os.path.exists(str(e.get("url", "")).lstrip("/"))]
    print("   线上无页面条目:", len(bad))
    if bad:
        fails.append("articles.json has %d dead entries" % len(bad))
except Exception as e:
    fails.append("articles.json parse: %s" % e)

print("\n=== F. 新卡线上可见 ===")
idx = curl("https://najieip.com/najie/blog/?cb=" + TS).decode("utf-8", "replace")
idxm = curl("https://najieip.com/blog/?cb=" + TS).decode("utf-8", "replace")
print("   najie 索引含新卡:", "three-step-selfcheck" in idx, " cards:", idx.count('<div class="article-card">'))
print("   主索引含新卡:", "three-step-selfcheck" in idxm, " cards:", idxm.count('<div class="article-card">'))
for nm, cond in [("najie新卡", "three-step-selfcheck" in idx), ("main新卡", "three-step-selfcheck" in idxm),
                 ("najie卡数73", idx.count('<div class="article-card">') == 73),
                 ("main卡数171", idxm.count('<div class="article-card">') == 171)]:
    if not cond:
        fails.append(nm)

print("\n=== G. sitemap ===")
sm = curl("https://najieip.com/sitemap.xml?cb=" + TS).decode("utf-8", "replace")
print("   loc:", sm.count("<loc>"), " lastmod:", sm.count("<lastmod>"))
print("   含 0922 三步自查:", "three-step-selfcheck" in sm)
if sm.count("<loc>") < 255 or "three-step-selfcheck" not in sm:
    fails.append("sitemap")

print("\n==== 失败项 ====")
print("  ", fails if fails else "无（全部 PASS）")
print("\n最后部署 commit:")
r = subprocess.run(["git", "log", "-1", "--pretty=%h %ci %s"], capture_output=True, text=True)
print("  ", r.stdout.strip())
