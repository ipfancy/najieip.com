#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify-0917-upc.py — 文章修复 + 索引补卡后的本地终验；同时打印 deploy-log 尾部供追加"""
import json, os, re, subprocess

SITE = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.join(SITE, "mili/blog/20260917-upc-injunction-counterattack.html")

t = open(ART, encoding="utf-8").read()
print("== 文章 ==")
print("  og:image=%d twitter:title=%d ld+json=%d bytes=%d"
      % (t.count("og:image"), t.count("twitter:title"),
         len(re.findall(r"application/ld\+json", t)), len(t.encode())))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    o = json.loads(b)
    print("  ld+json OK:", o.get("@type"))
print("  leak('---' p)=%s ai_smell=%s '**'=%d schema.org=%d star_免责=%s"
      % ("<p>---</p>" in t, "ai_smell" in t, t.count("**"),
         t.count("https://schema.org"), "*本文" in t))
print("  head 顺序:", re.findall(r'<meta property="og:[a-z]+"', t))

print("== 索引 ==")
for f in ["mili/blog/index.html", "blog/index.html"]:
    x = open(os.path.join(SITE, f), encoding="utf-8").read()
    print("  %s cards=%d slug=%d" % (f, len(re.findall(r'<div class="article-card">', x)),
                                     x.count("20260917-upc-injunction-counterattack")))

print("== deploy-log 远端尾部 ==")
out = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     cwd=SITE, capture_output=True, text=True).stdout
d = json.loads(out)
print("  keys=%s n=%d" % (list(d.keys()), len(d["deploys"])))
print("  last:", json.dumps(d["deploys"][-1], ensure_ascii=False)[:500])
print("  last keys:", list(d["deploys"][-1].keys()))
