#!/usr/bin/env python3
"""SiteOps GEO 第48周 元宝批量检测 — 9 查询，结果落 JSON"""
import importlib.util, json, sys, time

spec = importlib.util.spec_from_file_location("yb", "/Users/ziganghe/.local/bin/geo-check-yuanbao-verify.py")
yb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yb)

QUERIES = [
    ("ART-2026-0134", "离婚前把游戏账号卖给朋友 钱还要分吗"),
    ("ART-2026-0134", "游戏账号离婚能分割吗 民法典127条"),
    ("ART-2026-0134", "抖音号离婚怎么估值 一般分几成"),
    ("ART-2026-0135", "食品贴牌 只授权商标 算不算委托生产"),
    ("ART-2026-0135", "12月1日 食品委托生产 标签还能写监制吗"),
    ("ART-2026-0135", "食品委托生产合同 商标许可 要补哪些条款"),
    ("ART-2026-0136", "高企认定2026新规 是真的吗"),
    ("ART-2026-0136", "高新技术企业 发明专利权重 45% 有文件吗"),
    ("ART-2026-0136", "高企证书 每年5月报表 忘了报会怎样"),
]

OUT = "/Users/ziganghe/wiki/najieip-verify/site-inbox/geo-yuanbao-1128.json"
results = []
for aid, q in QUERIES:
    rec = {"article_id": aid, "query": q, "platform": "yuanbao"}
    try:
        r = yb.check(q)
        rec.update({
            "answer_len": r.get("answer_len"),
            "body_len": r.get("body_len"),
            "body_hits": r.get("body_hits") or {},
            "body_head": (r.get("body_head") or "")[:300],
            "error": r.get("error"),
        })
    except Exception as e:
        rec["error"] = f"EXC: {e}"
    rec["found_real"] = bool(rec.get("body_hits"))
    results.append(rec)
    print(json.dumps({"i": len(results), "art": aid, "q": q,
                      "body_len": rec.get("body_len"),
                      "found": rec["found_real"],
                      "hits": list((rec.get("body_hits") or {}).keys()),
                      "head": (rec.get("body_head") or "")[:120]}, ensure_ascii=False), flush=True)
    time.sleep(2)

with open(OUT, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("WROTE", OUT, len(results))
