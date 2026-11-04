#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04 收尾：清理 site-inbox 上游副本 + deploy-log 文本手术追加"""
import os, subprocess, json, re

REPO = os.path.expanduser("~/wiki/najieip-verify")

# 1. 上游副本清理（与已发布页字节相同 → 已接管）
copy = os.path.join(REPO, "site-inbox/20261104-mili-anti-involution-low-price.html")
pub = "mili/blog/20261104-mili-anti-involution-low-price.html"
if os.path.exists(copy):
    head = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + pub], capture_output=True, text=True).stdout
    body = open(copy, encoding="utf-8").read()
    print("copy == origin published?", body == head, len(body), len(head))
    if body == head:
        os.remove(copy); print("removed redundant site-inbox copy")

# 2. deploy-log 追加（文本手术：+15 行 / 0 删除）
logp = os.path.join(REPO, "site-inbox/deploy-log.json")
remote = subprocess.run(["git", "-C", REPO, "show", "origin/main:site-inbox/deploy-log.json"],
                        capture_output=True, text=True).stdout
raw = open(logp, encoding="utf-8").read()
d = json.loads(raw)
last = d["deploys"][-1]
print("schema:", list(last.keys()))
print("entries:", len(d["deploys"]))

entry = {
    "date": "2026-11-04",
    "time": "22:20",
    "agent": "SiteOps",
    "round": "daily-2026-11-04",
    "commit": "(this)",
    "action": "每日运营：核心8页HTTP巡检 + 精修1篇部分裸发布页(反法14条) + 封面入库 + 三篇双索引补卡 + articles.json守卫第21次隔离",
    "files_changed": [
        "mili/blog/20261104-mili-anti-involution-low-price.html",
        "img/20261104-mili-anti-involution-low-price.png",
        "blog/index.html",
        "mili/blog/index.html",
        "najie/blog/index.html",
        "articles.json",
        "articles-quarantine-20261104.json",
    ],
    "cards_added": 6,
    "attribution": "三篇均为上游 wechat-distribute 当日发布（mili×2 + najie×1），归属按落地目录判定，未改路径",
    "verification": "核心8页200(3次重试取终态) / 精修页11878B: h1=1 h2=4 ld=2(Article+BreadcrumbList, json.loads全通) og:image=1 stars=0 rawtbl=0 desc149字非复读 / md全文完整包含=True / 三索引卡 delta +3+2+1 = 6 sum=2N 无负delta / malformed=0 / 首卡日期降序 / 封面321967B",
    "defects_found": "1篇部分裸发布(ld=0 og:image=0 desc复读标题 裸markdown表2张共10行) / 三篇当日文品牌索引与主索引全零卡(共6张) / articles.json 51条违例(文件不存在+路径不在白名单)",
    "notes": "articles.json 285→234 隔离档 articles-quarantine-20261104.json; 首页slice(0,6)六条全有页面; 新增行规: 表格分隔行在md包含断言里需剥 -{3,} 归一化",
    "result": "PASS",
}
if list(entry.keys()) != list(last.keys()):
    print("SCHEMA MISMATCH", list(entry.keys()), "vs", list(last.keys())); raise SystemExit(1)

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
if not r.endswith(TAIL):
    # 兼容末行无换行
    if not r.endswith("\n  }\n ]\n}"):
        print("TAIL MISMATCH", repr(r[-40:])); raise SystemExit(1)
head = r[:-len(TAIL)] + "\n  }"
lines = []
keys = list(entry.keys())
for k in keys:
    v = entry[k]
    pre = "   " if k == keys[0] else "   "
    if isinstance(v, list):
        s = json.dumps(v, ensure_ascii=False)
        lines.append(f"{pre}\"{k}\": {s}")
    elif isinstance(v, int):
        lines.append(f"{pre}\"{k}\": {v}")
    else:
        lines.append(f"{pre}\"{k}\": {json.dumps(v, ensure_ascii=False)}")
ins = ",\n  {\n" + ",\n".join(lines) + "\n  }"
new = head + ins + "\n ]\n}"
chk = json.loads(new)
print("new entries:", len(chk["deploys"]), "last result:", chk["deploys"][-1]["result"])
open(logp, "w", encoding="utf-8").write(new + ("\n" if raw.endswith("\n") else ""))
print("written")
