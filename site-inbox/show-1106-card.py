#!/usr/bin/env python3
"""print one card block from a given index for inspection"""
import re, os, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")

def cards(t):
    res = []
    for m in re.finditer(r'<div class="article-card">', t):
        start = m.start(); d = 0; i = start
        while i < len(t):
            nx = t.find("<div", i); nc = t.find("</div>", i)
            if nc == -1: break
            if nx != -1 and nx < nc:
                d += 1; i = nx + 4
            else:
                d -= 1; i = nc + 6
                if d == 0: break
        res.append((start, i, t[start:i]))
    return res

path, slug = sys.argv[1], sys.argv[2]
t = open(path, encoding="utf-8").read()
for s, e, b in cards(t):
    if slug in b:
        print("### " + path + f"  ({s}-{e})")
        print(b)
        break
