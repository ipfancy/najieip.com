#!/usr/bin/env python3
"""SiteOps 每日巡检 2026-11-25：近 3 日文章页六项 + feed 近期条目"""
import re, os, json, datetime

REPO = "/Users/ziganghe/wiki/najieip-verify"
PAGES = [
    "mili/blog/20261125-mili-ai-face-blend-portrait-1019.html",
    "najie/blog/20261125-najie-plant-variety-punitive-damages.html",
    "najie/blog/20261125-najie-patent-intensive-product-filing.html",
    "mili/blog/20261124-mili-punitive-damages-one-shot.html",
    "najie/blog/20261123-mili-gaoqi-2026-no-new-standard.html",
]

for p in PAGES:
    fp = os.path.join(REPO, p)
    t = open(fp, encoding="utf-8").read()
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    schema = t.count("https://schema.org")
    ogimg = 'property="og:image"' in t
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    title = title.group(1).strip() if title else ""
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = desc.group(1) if desc else ""
    dd = (desc.strip() == title.strip()) or (desc.strip() and desc.strip() in title)
    body = t[t.find("<body"):]
    body_nostar = re.sub(r"[0-9]\*{2,}[0-9.]*", "", body)
    stars = body_nostar.count("**")
    pipe_paras = len(re.findall(r"<p>\s*\|.*\|\s*</p>", body))
    tables = len(re.findall(r"<table", body))
    can = re.search(r'<link rel="canonical" href="([^"]*)"', t)
    can = can.group(1) if can else ""
    ok_canon = can.endswith("/" + p)
    flags = []
    if h1 != 1: flags.append(f"h1={h1}")
    if ld < 2: flags.append(f"ld={ld}")
    if schema < ld: flags.append(f"schema={schema}<ld{ld}")
    if not ogimg: flags.append("no-og:image")
    if dd: flags.append("desc=title")
    if stars: flags.append(f"stars={stars}")
    if pipe_paras: flags.append(f"pipecards={pipe_paras}")
    if not ok_canon: flags.append(f"canonical={can}")
    print(f"{'OK ' if not flags else 'FAIL'} {p} size={os.path.getsize(fp)} h1={h1} ld={ld} tbl={tables} {' '.join(flags)}")

print("\n--- feed.xml ---")
fx = os.path.join(REPO, "feed.xml")
if os.path.exists(fx):
    f = open(fx, encoding="utf-8").read()
    items = re.findall(r"<item>(.*?)</item>", f, re.S)
    if not items:
        items = re.findall(r"<entry>(.*?)</entry>", f, re.S)
    print("entries:", len(items))
    for it in items[:6]:
        link = re.search(r"<link>(.*?)</link>", it, re.S) or re.search(r'<link href="([^"]+)"', it)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S) or re.search(r"<updated>(.*?)</updated>", it, re.S)
        print("  ", (link.group(1).strip() if link else "?"), "|", (pub.group(1).strip() if pub else "?"))
    for s in ["20261125-mili-ai-face-blend-portrait-1019", "20261125-najie-plant-variety-punitive-damages", "20261125-najie-patent-intensive-product-filing"]:
        print(f"  in-feed {s}: {f.count(s)}")
