#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对齐 deploy-log 最后一条的 schema：cards_added 改为 int + 补 attribution 键"""
import json, os

P = os.path.expanduser("~/wiki/najieip-verify/site-inbox/deploy-log.json")
log = json.load(open(P, encoding="utf-8"))
e = log["deploys"][-1]
e["cards_added"] = 2
e["attribution"] = "EN/FR 双语索引卡各 1 张（本轮新建）；主索引 blog/index.html 无新增（本文中文卡已由上游发布时建好，本轮核验线上 HIT）"
# 保持键序与上一 entry 一致
order = list(log["deploys"][-2].keys())
fixed = {k: e[k] for k in order if k in e}
for k in e:
    if k not in fixed:
        fixed[k] = e[k]
log["deploys"][-1] = fixed
json.dump(log, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(P, "a", encoding="utf-8").write("\n")
print("keys:", list(log["deploys"][-1].keys()))
print("entries:", len(log["deploys"]))
