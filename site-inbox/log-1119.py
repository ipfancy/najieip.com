#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 deploy-log 追加（文本手术，+15 行 / 0 删除）"""
import os, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox/deploy-log.json")

raw_origin = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                            capture_output=True, text=True, cwd=REPO).stdout
d = json.loads(raw_origin)
last = d["deploys"][-1]
print("LAST KEYS:", list(last.keys()))
print("COUNT:", len(d["deploys"]))

entry = {}
vals = {
    "date": "2026-11-19",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "pending",
    "action": "每日巡检：核心6页200（llms.txt首轮000瞬断,重试3/3=200）；精修畸形页 20261119-mili-tv-box-backdoor-four-layers（h1=0/ld=0/无og:image/description复读标题）→ 补 h1 + Article+BreadcrumbList JSON-LD + og:image/twitter/keywords/og:site_name + 真摘要142字，6449→9819B（正文逐字不变1694=1694，md全文包含True 1604=1604）；4 页补 og:image（aipunajie PCT / mili foreign-law-proof / ai-law-firm-boundary / dooring-case）+ twitter:card 升级 + og:site_name；封面 296KB 入库 img/",
    "files_changed": 6,
    "cards_added": 0,
    "attribution": "零补卡（6 篇新文品牌卡与主卡上游均已同步，逐 slug grep 各命中 1 次）",
    "verification": "本地 5 页结构终验 PASS（h1=1/ld>=2/JSON-LD全部json.loads/div配平/**=0/og:image本地存在/ctx==ld）；articles.json 321→269 隔离52条（0违例，首页top6全有页面）；sitemap 看门 exit 0（425 loc 不变）",
    "defects_found": "1 篇畸形页(ld=0,h1=0,desc复读,处articles.json首页第1曝光位) + 4 篇缺og:image + articles.json 52条无页面条目(上游第N次复活)",
    "notes": "新增行规：md包含断言页面侧须剥<h1-6>标题文字（md侧整行丢弃后残留标题文字会造成永久假失败，本次为唯一假失败点）",
    "result": "PASS",
}
# 严格沿用上一条键序
for k in last.keys():
    entry[k] = vals.get(k, "")

raw = open(P, encoding="utf-8").read()
TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), repr(r[-40:])
head = r[:-len(TAIL)] + "\n  }"
body = ",\n  {\n" + ",\n".join(
    "   " + json.dumps(k, ensure_ascii=False) + ": " + json.dumps(v, ensure_ascii=False)
    for k, v in entry.items()) + "\n  }"
new = head + body + "\n ]\n}"
json.loads(new)
open(P, "w", encoding="utf-8").write(new)
print("APPENDED OK, count now", len(json.loads(new)["deploys"]))
