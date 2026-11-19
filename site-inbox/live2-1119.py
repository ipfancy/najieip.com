#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 线上终验 v2（单次 curl 取体+码，逐页重试）"""
import re, json, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
CORE = ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]
PAGES = ["/mili/blog/20261119-mili-tv-box-backdoor-four-layers.html",
         "/aipunajie/blog/20261119-aipu-pct-30-months.html",
         "/mili/blog/20261118-mili-foreign-law-proof.html",
         "/mili/blog/20261119-mili-ai-law-firm-boundary.html",
         "/mili/blog/20261119-mili-dooring-case.html",
         "/img/20261119-mili-tv-box-backdoor-four-layers.png"]


def get(u, tries=3):
    body, code = "", "000"
    for _ in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "35", "-A", UA, "-w", "\n@@CODE@@%{http_code}", u],
                           capture_output=True, text=True)
        out = r.stdout
        if "@@CODE@@" in out:
            body, code = out.rsplit("@@CODE@@", 1)
            body = body[:-1] if body.endswith("\n") else body
        if code == "200":
            return body, code
        time.sleep(2)
    return body, code


fails = []
print("=== 核心页 ===")
for p in CORE:
    _, c = get(BASE + p)
    print(f"  {c} {p}")
    if c != "200": fails.append(p)

print("=== 文章页六项 ===")
for p in PAGES:
    body, c = get(BASE + p)
    if c != "200":
        print(f"  {c} {p} !!!"); fails.append(p); continue
    if p.endswith(".png"):
        print(f"  200 {p} bytes={len(body)}")
        if len(body) < 100000: fails.append(p + " (size)")
        continue
    h1 = len(re.findall(r"<h1[\s>]", body)); ld = body.count("application/ld+json")
    ogi = "og:image" in body; stars = len(re.findall(r"(?<![0-9*])\*\*", body))
    m = re.search(r'<meta name="description" content="([^"]*)"', body)
    d = m.group(1) if m else ""
    ok = h1 == 1 and ld >= 2 and ogi and stars == 0 and len(d) > 60
    print(f"  {'PASS' if ok else 'FAIL'} {p.split('/')[-1][:44]:44s} h1={h1} ld={ld} ogimg={ogi} **={stars} desc={len(d)}")
    if not ok: fails.append(p)

print("=== articles.json ===")
body, c = get(BASE + "/articles.json?cb=%d" % int(time.time()))
try:
    arr = json.loads(body); arr = arr if isinstance(arr, list) else arr.get("articles", [])
    print(f"  total={len(arr)}")
    for i, it in enumerate(arr[:3]):
        print(f"   {i+1}. {it.get('url','')[:64]}")
except Exception as e:
    print("  PARSE-ERR", e, c); fails.append("articles.json")

print("\nFAILURES:", len(fails), fails if fails else "NONE")
