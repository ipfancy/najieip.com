#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 本地结构终验"""
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
pages = ["mili/blog/20261119-mili-tv-box-backdoor-four-layers.html",
         "aipunajie/blog/20261119-aipu-pct-30-months.html",
         "mili/blog/20261118-mili-foreign-law-proof.html",
         "mili/blog/20261119-mili-ai-law-firm-boundary.html",
         "mili/blog/20261119-mili-dooring-case.html"]
fails = []
for rel in pages:
    fp = os.path.join(REPO, rel)
    t = open(fp, encoding="utf-8").read()
    h1 = len(re.findall(r"<h1[\s>]", t))
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    bad_json, types = 0, []
    for raw in lds:
        try:
            o = json.loads(raw); types.append(o.get("@type"))
        except Exception:
            bad_json += 1
    op = len(re.findall(r"<div\b", t)); cl = len(re.findall(r"</div>", t))
    stars = len(re.findall(r"(?<![0-9*])\*\*", t))
    ogi = re.search(r'<meta property="og:image" content="([^"]*)"', t)
    ogi_ok = bool(ogi) and os.path.exists(os.path.join(REPO, ogi.group(1).replace("https://najieip.com/", "")))
    ctx = t.count("https://schema.org")
    ok = (h1 == 1 and len(lds) >= 2 and bad_json == 0 and stars == 0 and ogi_ok and ctx >= len(lds))
    print(f"{'PASS' if ok else 'FAIL'} {os.path.basename(rel)[:48]:48s} size={os.path.getsize(fp):6d} h1={h1} ld={len(lds)}{types} ctx={ctx} div={op}/{cl} **={stars} ogimg_local={ogi_ok}")
    if not ok: fails.append(rel)
print("FAILURES:", len(fails), fails if fails else "")
