#!/usr/bin/env python3
"""Inspect template page head + ld objects + today's article body/md for fix planning."""
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
TPL = os.path.join(REPO, "mili/blog/20261015-ip-4-hard-deadlines-buju-revision.html")
t = open(TPL, encoding="utf-8").read()
head = t[:t.find("</head>")]
print("=== TEMPLATE HEAD (%dB) ===" % len(head))
print(head[:3000])
print("\n=== LD OBJECTS ===")
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    o = json.loads(blk)
    print(json.dumps(o, ensure_ascii=False)[:900])
    print("---")
print("\n=== TEMPLATE BODY HEAD ===")
print(t[t.find("<body"):t.find("<body")+600])
