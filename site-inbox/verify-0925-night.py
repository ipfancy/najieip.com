#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0925 夜检线上终验：articles.json 条目数收敛 + 核心页 200 + 新文四件"""
import json, os, subprocess, time, urllib.request, hashlib

BASE = "https://najieip.com"
def get(url, t=30):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "siteops-verify"})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, r.read()

cb = int(time.time())
print("=== articles.json 收敛（期望 156） ===")
for i in range(6):
    try:
        st, body = get(f"{BASE}/articles.json?cb={cb+i}")
        d = json.loads(body.decode("utf-8"))
        a = d if isinstance(d, list) else d.get("articles", [])
        print(f"  poll{i} status={st} entries={len(a)}")
        if len(a) == 156:
            break
    except Exception as e:
        print(f"  poll{i} ERR {e}")
    time.sleep(25)

print("=== 核心页 ===")
for p in ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt", "/robots.txt"]:
    try:
        st, _ = get(BASE + p)
        print(f"  {st} {p}")
    except Exception as e:
        print(f"  ERR {p} {e}")

print("=== 新文线上四件 ===")
import re
for p in ["/mili/blog/20260925-policy-cash-value-execution-2024-instance.html",
          "/mili/blog/20260924-malicious-litigation-supervision.html"]:
    st, b = get(BASE + p + f"?cb={cb}")
    t = b.decode("utf-8", "replace")
    print(f"  {st} {p} {len(b)}B h1={len(re.findall(r'<h1', t))} h2={len(re.findall(r'<h2', t))} "
          f"ld={len(re.findall(r'application/ld.json', t))} og:image={'og:image' in t} md_star={t.count('**')}")
