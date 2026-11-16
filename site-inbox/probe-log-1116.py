#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy-log 文本手术追加（+15 行 / 0 删除）"""
import json, os

P = os.path.expanduser("~/wiki/najieip-verify/site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
last = d["deploys"][-1]
print("keys:", list(last.keys()))
print("count:", len(d["deploys"]))
print("tail repr:", repr(raw[-14:]))
