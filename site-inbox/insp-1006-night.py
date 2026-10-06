#!/usr/bin/env python3
import re, glob, os
ROOT = "/Users/ziganghe/wiki/najieip-verify"
tpl = os.path.join(ROOT, "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html")
t = open(tpl, encoding="utf-8").read()
print("=== og/twitter meta of template ===")
for m in re.findall(r'<meta (?:property|name)="(og:[^"]*|twitter:[^"]*|keywords|author)"[^>]*>', t):
    print(m)
print("=== ld blocks count ===", len(re.findall(r'<script type="application/ld\+json">', t)))
b = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
for x in b:
    print("-----")
    print(x.strip()[:600])
print("=== alternate links ===")
print(re.findall(r'<link rel="alternate"[^>]*>', t))
print("\n=== md source candidates ===")
for p in glob.glob("/Users/ziganghe/wiki/digital-employees/articles/*nobel*") + glob.glob("/Users/ziganghe/wiki/digital-employees/articles/*20261006*"):
    print(p, os.path.getsize(p))
