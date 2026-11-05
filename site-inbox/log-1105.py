#!/usr/bin/env python3
"""Append today's deploy-log entry with text surgery (no full rewrite)."""
import json, os, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox", "deploy-log.json")
APPLY = "--apply" in sys.argv

raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
last = d["deploys"][-1]
keys = list(last.keys())
print("SCHEMA:", keys)
print("TAIL:", repr(raw[-40:]))
print("LAST:", json.dumps(last, ensure_ascii=False)[:300])

VAL = {
    "date": "2026-11-05",
    "time": "22:10",
    "agent": "siteops",
    "round": "daily",
    "commit": "f904e92",
    "action": "精修 mili 竞业限制页（部分裸发布：ld=0/无 og:image/描述复读标题/4 张裸 markdown 表共 21 行）→ 按 md 源整页重建套同日 mili 房屋；补十五五规划文缺失的主索引卡",
    "files_changed": [
        "mili/blog/20261105-mili-non-compete-all-staff.html",
        "blog/index.html",
        "img/20261105-mili-non-compete-all-staff.png",
        "site-inbox/diag-1105.py",
        "site-inbox/fix-1105.py",
    ],
    "cards_added": 1,
    "attribution": {"mili": 1, "najie": 0, "aipunajie": 0, "main_index": 1},
    "verification": "页面 7,453→11,310B：h1=1 / ld=2（Article+BreadcrumbList，json.loads 全通）/ og:image 自托管 / 真摘要 155 字 / 4 表转 table.data / **=0 / md 全文完整包含=True；封面 316KB 入库；主索引 263→264 卡、div 530/530 配平；核心 6 页 6/6 200；articles.json 235/235 零违例、首页 top6 全有页面",
    "defects_found": [
        "mili 20261105 页部分裸发布：ld=0、无 og:image/twitter/keywords、description 复读标题、21 行裸 markdown 表、合集注释被转义为可见文本",
        "najie 20261105 十五五规划文缺主索引卡（品牌卡已在）",
    ],
    "notes": "上游 06:14 已清 articles.json 287→235（今日无需再隔离）；sitemap 看门 exit 0（381 loc 不变）；品牌卡两篇均已在，仅补主索引 1 张",
    "result": "PASS",
}

new = {}
for k in keys:
    new[k] = VAL.get(k, last[k])
print("NEW ENTRY:", json.dumps(new, ensure_ascii=False)[:400])

if APPLY:
    body = raw
    # exact trailing shape
    assert body.rstrip("\n").endswith("\n  }\n ]\n}"), "unexpected tail shape"
    stripped = body.rstrip("\n")
    TAIL = "\n  }\n ]\n}"
    head = stripped[:-len(TAIL)] + "\n  }"
    ins = ",\n  {\n" + ",\n".join(
        '   "%s": %s' % (k, json.dumps(new[k], ensure_ascii=False)) for k in keys) + "\n  }"
    out = head + ins + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
    json.loads(out)
    open(P, "w", encoding="utf-8").write(out)
    print("APPLIED entries:", len(json.loads(out)["deploys"]))
