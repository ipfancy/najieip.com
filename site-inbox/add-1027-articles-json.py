#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepend today's aipunajie article to articles.json (native indent=2 list)."""
import json, os, sys

BASE = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(BASE, "articles.json")
APPLY = "--apply" in sys.argv

entry = {
    "url": "/aipunajie/blog/20261027-aipunajie-oa-phone-amendment-decision.html",
    "title": "审查员打电话让你改，当场答应对不对",
    "date": "2026-10-27",
    "site": "aipunajie",
    "description": "审查员电话要求把某特征并入独立权利要求，当场答应还是先拖？接受限缩意味着保护范围永久收缩，拒绝则影响审查进程甚至增加驳回风险。《专利法》第33条只允许在原始范围内修改，写进去就退不出来。本文给三分支判断法（该特征是否属于独权核心区别特征）、从权下放的用法、为什么不能在电话里口头答应，以及挂断后必须做的三件事（书面修改稿、修改依据说明、对外口径统一）。",
}

items = json.load(open(P, encoding="utf-8"))
items = [x for x in items if x.get("url") != entry["url"]]
items.insert(0, entry)
items.sort(key=lambda x: str(x.get("date", "")), reverse=True)
print("n =", len(items), "| top3:", [x["url"] for x in items[:3]])
if APPLY:
    with open(P, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("WRITTEN")
else:
    print("DRY-RUN")
