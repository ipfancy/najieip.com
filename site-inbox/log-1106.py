#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""append deploy-log entry 2026-11-06 (text surgery, +15 lines / 0 deletions)"""
import json, os, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox", "deploy-log.json")
raw = open(P, encoding="utf-8").read()
orig = raw
d = json.loads(raw)
last_keys = list(d["deploys"][-1].keys())

entry = {
    "date": "2026-11-06",
    "time": "22:15",
    "agent": "siteops",
    "round": "daily",
    "commit": "b12448b",
    "action": "精修 3 篇 mili「部分裸发布」页（ld=0 / 无 og:image / description 复读标题 / 两页共 24 行裸 markdown 表 / `**` 10 处）→ 按 md 源整页重建套同日 mili 房屋；补品牌索引卡 3 张 + 主索引卡 4 张；articles.json 守卫第 22 次隔离",
    "files_changed": [
        "mili/blog/20261103-mili-guarantee-period-six-months.html",
        "mili/blog/20261104-mili-inventor-reward-5-percent.html",
        "mili/blog/20261106-mili-nda-vs-noncompete.html",
        "mili/blog/index.html",
        "blog/index.html",
        "articles.json",
        "articles-quarantine-20261106.json",
        "img/20261103-mili-guarantee-period-six-months.png",
        "img/20261104-mili-inventor-reward-5-percent.png",
        "img/20261106-mili-nda-vs-noncompete.png",
        "site-inbox/diag-1106.py",
        "site-inbox/fix-1106.py",
        "site-inbox/verify-1106-structure.py",
        "site-inbox/live-1106.py",
        "site-inbox/clean-1106.py",
    ],
    "cards_added": 7,
    "attribution": "3 篇落地 mili/blog/，canonical/og:url 与落地目录一致，未改路径；20261106 鉴定意见文为上游新增（品牌卡已有、主索引缺）",
    "verification": "核心 6 页 6/6 200；3 页 7168/7336/6225 → 10764/10917/9495 B（ld=2 json.loads 全通 / og:image 自托管 / 真摘要 138-119 字 / 裸表 0 / `**` 0）；品牌索引 148→151、主索引 264→268 卡，div 深度 0、malformed 0、dups 0，新卡各命中 1 次；articles.json 290→239 且首页 top6 六条全有页面；sitemap 看门 exit 0（386 loc 不变）；线上 4 页六项 + 封面 200 + 7 处卡 HIT + live articles.json 239 = FAILURES NONE",
    "defects_found": [
        "上游 3 篇 mili 部分裸发布（无 JSON-LD / 无 og:image / 描述复读标题 / 裸表 24 行 / `**` 10 处）",
        "三篇新文品牌索引与主索引全零卡（上游只发页面与 articles.json）",
        "上游新增 20261106 鉴定意见文品牌卡已有但主索引缺卡",
        "articles.json 上游复活 51 条无页面条目（第 22 次）",
    ],
    "notes": "1040B 级跳转壳无；md 包含断言取 <article> 区间并剥 `-{3,}`/`:` 后全 True；公开仓 Actions run in_progress 期间新页仍读旧版，run completed 后 45s 内 4/4 生效",
    "result": "PASS",
}
assert list(entry.keys()) == last_keys, f"schema mismatch {list(entry.keys())} vs {last_keys}"

body = ",\n  {\n" + ",\n".join(
    '   "%s": %s' % (k, json.dumps(v, ensure_ascii=False)) for k, v in entry.items()) + "\n  }"

r = raw.rstrip("\n")
had_nl = raw.endswith("\n")
TAIL = "\n ]\n}"
assert r.endswith(TAIL), repr(r[-12:])
new = r[:-len(TAIL)] + body + TAIL + ("\n" if had_nl else "")
json.loads(new)  # self-check
print("entries before", len(d["deploys"]), "after", len(json.loads(new)["deploys"]))
if "--apply" in sys.argv:
    open(P, "w", encoding="utf-8").write(new)
    print("written, bytes", len(new.encode()) - len(orig.encode()))
