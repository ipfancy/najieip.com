#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""元宝 GEO 批量驱动 — 9 查询，写 JSON 结果。用 geo-check-yuanbao-verify.py 的 check()。"""
import json, os, sys, time, importlib.util

SRC = os.path.expanduser("~/.local/bin/geo-check-yuanbao-verify.py")
OUT = os.path.expanduser("~/wiki/najieip-verify/site-inbox/geo-yuanbao-1012.json")

spec = importlib.util.spec_from_file_location("gcy", SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PLAN = [
    ("ART-2026-0100", "有商标注册证 还被判侵权 怎么办"),
    ("ART-2026-0100", "商标被判无效 顶格判赔500万"),
    ("ART-2026-0100", "注册商标 能不能对抗在先商标权"),
    ("ART-2026-0101", "同一专利族 美国判赔 欧洲驳回禁令"),
    ("ART-2026-0101", "拓竹被Stratasys起诉 判赔多少钱"),
    ("ART-2026-0101", "FTO自由实施检索 怎么做 步骤"),
    ("ART-2026-0102", "专利年费交了 为什么还被终止"),
    ("ART-2026-0102", "专利年费台账 怎么自查"),
    ("ART-2026-0102", "代理机构变更 没办著录事项变更 后果"),
]

results = []
for aid, q in PLAN:
    try:
        r = m.check(q)
        r["article"] = aid
        results.append(r)
        print(f"[{aid}] {q} -> len={r.get('answer_len')} hits={list((r.get('body_hits') or {}).keys())}", flush=True)
    except Exception as e:
        results.append({"article": aid, "query": q, "error": str(e)})
        print(f"[{aid}] {q} -> EXC {e}", flush=True)
    json.dump(results, open(OUT, "w"), ensure_ascii=False, indent=1)
    time.sleep(2)

print("DONE", len(results), "->", OUT)
