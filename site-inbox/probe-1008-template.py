#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print head of a polished same-brand page to use as house template."""
import re, os, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")

tpl = sys.argv[1] if len(sys.argv) > 1 else "mili/blog/20261008-mili-ai-math-solution-copyright.html"
t = open(os.path.join(REPO, tpl), encoding="utf-8").read()
head = t[t.find("<head>"):t.find("</head>") + 7]
print("=== HEAD of", tpl, "===")
print(head)
print("\n=== BODY first 1200 chars ===")
b = t[t.find("<body>"):]
print(b[:1200])
print("\n=== ld json blocks ===")
for i, m in enumerate(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)):
    print(f"--- block {i} ---")
    print(m.group(1).strip()[:1200])
