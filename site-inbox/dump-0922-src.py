#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取重建素材：畸形页全文 / md 源全文 / 同日品牌精修页房屋模板"""
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

print("######## MALFORMED PAGE (full) ########")
print(rd(os.path.join(REPO, "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html")))
print("\n######## MD SOURCE (full) ########")
print(rd(os.path.expanduser("~/wiki/digital-employees/articles/20260922-us-trademark-sanction-three-step-selfcheck.md")))
