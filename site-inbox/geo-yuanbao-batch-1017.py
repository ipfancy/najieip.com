#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""元宝 GEO 批量驱动 — 9 查询，写 JSON 结果。用 geo-check-yuanbao-verify.py 的 check()。"""
import json, os, importlib.util, time

SRC = os.path.expanduser("~/.local/bin/geo-check-yuanbao-verify.py")
OUT = os.path.expanduser("~/wiki/najieip-verify/site-inbox/geo-yuanbao-1017.json")

spec = importlib.util.spec_from_file_location("gcy", SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PLAN = [
    ("ART-2026-0103", "赢了官司 判决书里的合规建议 有约束力吗"),
    ("ART-2026-0103", "燃气公司 滥用市场支配地位 胜诉 最高法"),
    ("ART-2026-0103", "反垄断 判决后 合规整改 怎么留痕"),
    ("ART-2026-0104", "商标法 司法解释 征求意见 2026 截止时间"),
    ("ART-2026-0104", "商标授权确权规定 第28条 两个方案"),
    ("ART-2026-0104", "商标审查审理指南 征求意见 怎么提意见"),
    ("ART-2026-0105", "AI短剧 被搬运 赔多少钱"),
    ("ART-2026-0105", "AI生成内容 视听作品 认定标准"),
    ("ART-2026-0105", "AI创作 token 算力成本 算进赔偿"),
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
