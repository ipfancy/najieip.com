#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re
REPO = os.path.expanduser("~/wiki/najieip-verify")
md = os.path.expanduser("~/wiki/digital-employees/articles/20261104-mili-anti-involution-low-price.md")
t = open(md, encoding="utf-8").read()
print("MD len", len(t))
print("--- md 前 60 行 ---")
for i, l in enumerate(t.split("\n")[:70]):
    print(f"{i:03d}|{l[:110]}")
p = open(os.path.join(REPO, "mili/blog/20261104-mili-anti-involution-low-price.html"), encoding="utf-8").read()
print("\n--- PAGE h1/h2 ---")
for m in re.finditer(r"<(h1|h2)[^>]*>(.*?)</\1>", p, re.S):
    print(m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()[:80])
print("\n--- PAGE 裸表区 ---")
i = p.find("<p>|")
print(p[max(0, i-300):i+1200])
print("\n--- PAGE head 前 900 ---")
print(p[:900])
print("\n--- 模板(同日 mili 精修页) head 结构 ---")
q = open(os.path.join(REPO, "mili/blog/20261104-mili-provisional-protection-fee.html"), encoding="utf-8").read()
print("tmpl size", len(q), "style inline:", "<style>" in q, "css link:", q.count('/style.css'))
print(q[:1200])
