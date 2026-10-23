#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总 1024 GEO 双平台结果 — 打印每条答案开头用于吸收度归因"""
import json, os

BASE = os.path.expanduser("~/wiki/najieip-verify/site-inbox")
mes = json.load(open(os.path.join(BASE, "geo-metaso-1024.json"), encoding="utf-8"))
yb = json.load(open(os.path.join(BASE, "geo-yuanbao-1024.json"), encoding="utf-8"))

print("=== METASO %d ===" % len(mes))
for r in mes:
    print("\n[Q]", r["query"], "| len", r["len"], "| hits", r["brand_hits"])
    print("  ANS:", r["answer"][:700].replace("\n", " ⏎ "))

print("\n\n=== YUANBAO %d ===" % len(yb))
for r in yb:
    print("\n[Q]", r.get("query"), "| len", r.get("answer_len"), "| hits", list((r.get("body_hits") or {}).keys()))
    print("  BODY:", (r.get("body_head") or "")[:700])
