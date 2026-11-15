#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-15 夜班 deploy-log 文本手术追加（+15 行 / 0 删除）"""
import json

P = "site-inbox/deploy-log.json"
raw = open(P, encoding="utf-8").read()
r = raw.rstrip("\n")
TAIL = "\n  }\n ]\n}"
assert r.endswith(TAIL), "tail mismatch"
head = r[: -len(TAIL)] + "\n  }"

entry = {
    "date": "2026-11-15",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（周日夜班）",
    "commit": "27c6f0f",
    "action": "11-15 每日巡检：核心6页6/6=200（零瞬断）；精修 mili「收到上家款再付」背靠背条款裸发布页（h1=0/ld=0/无og:image/无keywords/desc复读标题/**未转/有序列表裸<p>）7,140->9,704B；封面68KB入库 img/；两索引卡上游已同步（零补卡）；articles.json 257/257 零违例、首页top6全有页面",
    "files_changed": [
        "mili/blog/20261115-mili-payment-60days-b2b.html",
        "img/20261115-mili-payment-60days-b2b.png",
        "site-inbox/diag-1115.py",
        "site-inbox/fix-1115-page.py",
        "site-inbox/live-1115.py",
        "site-inbox/log-1115.py",
    ],
    "cards_added": 0,
    "attribution": "mili x1（当日1篇文，品牌卡与主卡上游已同步）",
    "verification": "线上 9704B 六项达标（h1=1/ld=2 Article+BreadcrumbList/@context=2/og:image=1/**=0/真摘要179字）；封面 img/...png 200；mili 索引 211,236B 卡1 HIT、主索引 206,302B 卡1 HIT；articles.json 线上 257 首条为本篇；sitemap 409 loc 看门 exit 0 零 diff；Pages run 27c6f0f completed/success",
    "defects_found": 1,
    "notes": "上游 2526f1b 裸发布只落页面+索引卡；本班按 11-14 同日 mili 房屋（Article/BreadcrumbList deepcopy + 覆写）重建，md 源逐字包含断言 1851=1851；落款两侧同剥（md 用「何自刚｜知识产权律师｜…」与页面 house 落款不同）后 contained=True",
    "result": "PASS",
}

body = []
items = list(entry.items())
for i, (k, v) in enumerate(items):
    comma = "," if i < len(items) - 1 else ""
    body.append("   " + json.dumps(k, ensure_ascii=False) + ": " + json.dumps(v, ensure_ascii=False) + comma)
new = head + ",\n  {\n" + "\n".join(body) + "\n  }" + "\n ]\n}"

# 自检
d = json.loads(new)
assert len(d["deploys"]) == 140, len(d["deploys"])
assert list(d["deploys"][-1].keys()) == list(d["deploys"][-2].keys())
open(P, "w", encoding="utf-8").write(new)
print("OK entries", len(d["deploys"]), "bytes", len(new.encode()))
