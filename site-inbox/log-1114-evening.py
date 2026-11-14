#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 deploy-log 条目（文本手术，不整档重写）— 11-14 夜班"""
import json, subprocess, os

REPO = "/Users/ziganghe/wiki/najieip-verify"
P = os.path.join(REPO, "site-inbox/deploy-log.json")

raw = open(P, encoding="utf-8").read()
data = json.loads(raw)
last = data["deploys"][-1]
keys = list(last.keys())
print("上一条键序:", keys, "| 条目总数:", len(data["deploys"]))
print("上一条 round:", last.get("round"))

VALUES = {
    "date": "2026-11-14",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（周六夜班）",
    "commit": "f0c6100",
    "action": "11-14 每日巡检：核心6页6/6=200；精修 mili 刷脸考勤裸发布畸形页（h1=0/ld=0/无og:image/desc复读27字/**x6）6588->9038B；双索引补卡2篇（mili 182->183、najie 134->135、主 307->309）；articles.json 守卫第25次隔离 306->255",
    "files_changed": [
        "mili/blog/20261114-mili-face-recognition-compliance.html",
        "img/20261114-mili-face-recognition-compliance.png",
        "mili/blog/index.html", "najie/blog/index.html", "blog/index.html",
        "articles.json", "articles-quarantine-20261114.json",
    ],
    "cards_added": 4,
    "attribution": "mili x2 + najie x1（当日3篇文，按落地目录归属）",
    "verification": "本地：h1=1/ld=2(Article+BreadcrumbList, json.loads 全通)/schema.org x2/og:image 在/desc复读=False(126字真摘要)/**=0/canonical 按落地目录/md全文包含=True(1649=1649 一字未改)；三索引卡数+N、插入块外零改动、div 配平；封面 289951B 入库",
    "defects_found": "①已发布但双索引零卡 2 篇（版权融资16案例、外观设计视图两步法）②裸发布畸形页 1 篇（刷脸考勤）③articles.json 51 条无页面条目（第25次复活）",
    "notes": "sitemap 408 loc 已含当日3篇（上游 8fcf766 已补录）无需补；首页 top6 六条全部有页面；近3日 git 触及文章页 7 篇其余 4 篇六项全 OK（schema_ctx=0 属历史遗留，随页面下次改动顺带补）",
    "result": "PASS",
}

entry = {k: VALUES.get(k, "") for k in keys}
TAIL = "\n  }\n ]\n}"
stripped = raw.rstrip("\n")
assert stripped.endswith(TAIL), repr(stripped[-20:])
head = stripped[: -len(TAIL)] + "\n  }"
ins = ",\n  {\n" + ",\n".join(
    "   " + json.dumps(k, ensure_ascii=False) + ": " + json.dumps(v, ensure_ascii=False) for k, v in entry.items()
) + "\n  }"
new = head + ins + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
parsed = json.loads(new)
print("新档条目数:", len(parsed["deploys"]), "| 末条 round:", parsed["deploys"][-1]["round"])
print("末尾:", repr(new[-14:]))
open(P, "w", encoding="utf-8").write(new)
print(subprocess.run(["git", "-C", REPO, "diff", "--stat", "site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout)
