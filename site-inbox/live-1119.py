#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 线上终验：逐页重试取终态"""
import re, json, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
CORE = ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]
PAGES = ["/mili/blog/20261119-mili-tv-box-backdoor-four-layers.html",
         "/aipunajie/blog/20261119-aipu-pct-30-months.html",
         "/mili/blog/20261118-mili-foreign-law-proof.html",
         "/mili/blog/20261119-mili-ai-law-firm-boundary.html",
         "/mili/blog/20261119-mili-dooring-case.html",
         "/img/20261119-mili-tv-box-backdoor-four-layers.png",
         "/articles.json"]


def get(u, tries=3, head=False):
    last = ("", "000")
    for _ in range(tries):
        cmd = ["curl", "-s", "--max-time", "60", "-A", UA]
        if head:
            cmd += ["-I", "-o", "/dev/null", "-w", "%{http_code}"]
        cmd.append(u)
        r = subprocess.run(cmd, capture_output=True, text=True)
        code = r.stdout.strip() if head else ""
        if not head:
            code = subprocess.run(cmd + ["-o", "/dev/null", "-w", "%{http_code}"],
                                  capture_output=True, text=True).stdout.strip()
        if code == "200":
            return r.stdout if not head else "", code
        last = (r.stdout, code)
        time.sleep(2)
    return last


fails = []
print("=== 核心页 ===")
for p in CORE:
    _, code = get(BASE + p, head=True)
    print(f"  {code} {p}")
    if code != "200": fails.append(p)

print("=== 文章页六项 ===")
for p in PAGES[:-1]:
    body, code = get(BASE + p)
    if code != "200":
        print(f"  {code} {p} !!!"); fails.append(p); continue
    if p.endswith(".png"):
        print(f"  200 {p} (binary {len(body)} chars)"); continue
    h1 = len(re.findall(r"<h1[\s>]", body))
    ld = body.count("application/ld+json")
    ogi = "og:image" in body
    stars = len(re.findall(r"(?<![0-9*])\*\*", body))
    m = re.search(r'<meta name="description" content="([^"]*)"', body)
    desc = m.group(1) if m else ""
    ok = h1 == 1 and ld >= 2 and ogi and stars == 0 and len(desc) > 60
    print(f"  {'PASS' if ok else 'FAIL'} {p.split('/')[-1][:46]:46s} h1={h1} ld={ld} ogimg={ogi} **={stars} desc={len(desc)}")
    if not ok: fails.append(p)

print("=== articles.json 前6位 ===")
body, code = get(BASE + "/articles.json?cb=%d" % int(time.time()))
try:
    arr = json.loads(body)
    arr = arr if isinstance(arr, list) else arr.get("articles", [])
    print(f"  total={len(arr)} code={code}")
    for i, it in enumerate(arr[:6]):
        slug = it.get("url", "")
        b2, c2 = get(BASE + slug, tries=2, head=True)
        print(f"   {i+1}. {c2} {slug[:60]}")
        if c2 != "200": fails.append(slug)
except Exception as e:
    print("  PARSE-ERR", e, code); fails.append("articles.json")

print("\nFAILURES:", len(fails), fails if fails else "NONE")
