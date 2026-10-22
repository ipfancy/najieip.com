#!/usr/bin/env python3
"""Inspect template page + defective page tail for 10-22 fix."""
import re
T = "/Users/ziganghe/wiki/najieip-verify/najie/blog/20261021-goods-names-acceptable-list-q4.html"
D = "/Users/ziganghe/wiki/najieip-verify/najie/blog/20261022-najie-gaoqi-ip-30points.html"
t = open(T, encoding="utf-8").read()
print("=== TEMPLATE size", len(t))
print("--- head ---")
print(t[:t.find("</head>")][:3000])
print("--- after article start (600 chars) ---")
i = t.find("<article")
print(t[i:i+600])
print("--- tail 1500 ---")
print(t[-1500:])
d = open(D, encoding="utf-8").read()
print("\n=== DEFECT size", len(d))
print("--- tail 900 ---")
print(d[-900:])
print("\n--- h2 list in defect ---")
for m in re.finditer(r"<h2>(.*?)</h2>", d, re.S):
    print("  ", re.sub(r"<[^>]+>", "", m.group(1))[:70])
