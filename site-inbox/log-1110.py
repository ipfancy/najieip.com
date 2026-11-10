#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""log-1110.py — deploy-log 文本手术追加（现行 schema，+15 行 / 0 删除）"""
import subprocess, json, os, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
P = "site-inbox/deploy-log.json"
raw = open(P, encoding="utf-8-sig").read()
d = json.loads(raw)
last = d["deploys"][-1]
KEYS = list(last.keys())
print("schema:", KEYS)

entry = {
    "date": "2026-11-10",
    "time": "22:01",
    "agent": "SiteOps",
    "round": "daily-20261110-night",
    "commit": "12004db",
    "action": "每日运营：核心6页200；精修遗嘱部分无效裸发布页(h1=0/ld=0/无og:image/desc复读/6处**)+家事与财富传承专题页补og:image+twitter卡；articles.json守卫第24次隔离51条",
    "files_changed": ["mili/blog/20261110-mili-will-partial-invalid.html",
                      "mili/family-wealth.html", "articles.json",
                      "img/20261110-mili-will-partial-invalid.png"],
    "cards_added": 0,
    "attribution": {"mili": 0, "najie": 0, "main": 0},
    "verification": "本地：h1=1 h2=4 ld=2(JSON全解析) og:image=1 stars=0 裸表=0 遮罩=0，正文md全文包含=True(1338=1338)；专题页h1=1 ld=2 og:image=1 twitter=4。线上：10 URL 200，文章页10,158B六项达标，专题页14,309B，/mili/blog/线上207,829B与本地字节一致(cards=185，新卡HIT)，主索引卡HIT，live articles.json=246。FAILURES=NONE。",
    "defects_found": ["裸发布畸形页(第N例)：h1=0/ld=0/无og:image/desc复读标题/6处**", "家事专题页(上游1f64b27新建)缺og:image与twitter卡", "articles.json 51条无页面条目(上游复活)"],
    "notes": "md→HTML 整页重建套11-09 mili房屋；新增行规：索引页~200KB 线上读取必须 --max-time 60 且校验字节数，--max-time 30 会截断成54KB导致假「索引缺卡」；md包含断言先切<article>区间、两侧同剥落款。",
    "result": "PASS",
}
assert list(entry.keys()) == KEYS, "schema mismatch"

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), "tail marker mismatch"
head = r[:-len(TAIL)] + "\n  }"
body = ""
for k, v in entry.items():
    body += "\n   \"%s\": %s," % (k, json.dumps(v, ensure_ascii=False))
body = body.rstrip(",")
new = head + ",\n  {\n" + body.lstrip("\n") + "\n  }\n ]\n}" + ("\n" if raw.endswith("\n") else "")
d2 = json.loads(new)
assert len(d2["deploys"]) == len(d["deploys"]) + 1
print("entries", len(d["deploys"]), "->", len(d2["deploys"]))
open(P, "w", encoding="utf-8").write(new)
print("WROTE", P, os.path.getsize(P))
