#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1030: deploy-log 文本手术追加（禁止整档 json.dump 重写）。"""
import os, re, json, subprocess, sys

SITE = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(SITE, "site-inbox/deploy-log.json")
APPLY = "--apply" in sys.argv

raw = subprocess.run(["git", "-C", SITE, "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
d = json.loads(raw)
last = d["deploys"][-1]
print("LAST KEYS:", list(last.keys()))
print("LAST RESULT:", last.get("result"), "| count:", len(d["deploys"]))

entry = {
    "date": "2026-10-30",
    "time": "22:40",
    "agent": "SiteOps",
    "round": "daily",
    "commit": "a487254",
    "action": "补建3篇已发布无页文 + 重建1篇裸发布畸形页(错canonical) + 双索引补卡 + articles.json隔离",
    "files_changed": 16,
    "cards_added": 8,
    "attribution": {"mili/blog": 3, "najie/blog": 0, "blog": 5},
    "verification": "线上6页200(h1=1/ld=2/og:image/canonical/stars=0) + 三索引200 + sitemap354loc + 4封面200 + live articles.json 223条字节一致",
    "defects_found": ["已发布无页3篇(mili社保补贴/AI算力成本/商标续展)", "裸发布畸形页1篇(najie第19条,无h1/无ld/无og/desc复读/canonical指向mili)",
                      "主索引缺卡2篇(ai-harm/training-data)", "articles.json违例98条"],
    "notes": "新增行规：品牌索引循环必须显式按品牌过滤(否则najie文章被补进mili索引)；articles.json 隔离后首页top6仍须全有页面",
    "result": "PASS",
}

assert list(entry.keys()) == list(last.keys()), (list(entry.keys()), list(last.keys()))

TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith(TAIL), repr(raw[-40:])
r = raw.rstrip("\n")
head = r[:-len(TAIL)] + "\n  }"
lines = ['  {'] + ['   %s: %s,' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in entry.items()]
lines[-1] = lines[-1].rstrip(",")
new = head + ",\n" + "\n".join(lines) + "\n  }\n ]\n}"

chk = json.loads(new)
assert len(chk["deploys"]) == len(d["deploys"]) + 1
assert chk["deploys"][-1] == entry
print("OK new count:", len(chk["deploys"]))
if APPLY:
    with open(P, "w", encoding="utf-8") as f:
        f.write(new)
    print("written")
