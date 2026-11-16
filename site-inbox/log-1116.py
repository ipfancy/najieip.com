#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 deploy-log 条目（文本手术，期望 +15 行 / 0 删除）"""
import json, os, re

P = os.path.expanduser("~/wiki/najieip-verify/site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
last = d["deploys"][-1]
KEYS = list(last.keys())

entry = {
    "date": "2026-11-16",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（周一夜班）",
    "commit": "a1ff6c9",
    "action": "11-16 每日巡检：核心6页 6/6=200（零瞬断）；精修 mili「一年6000份保护令」部分裸发布页（h1=0/无og:image/twitter仅summary/无keywords）10,068→10,719B，补 h1+og:image+twitter:title/image+keywords+Article image 字段，封面 337KB 入库 img/，正文剥 h1 后逐字不变；najie「AI生成图权属三层」补主索引卡（309→310，depth0 delta+1）+ articles.json 条目（307→308）；articles.json 守卫隔离 2 条 stub（无落地页/跳转壳）→306，0 违例、首页 top6 全有页面；sitemap 看门 exit 0（414 loc 不变）；线上 23 项判据 FAILURES=NONE",
    "files_changed": [
        "mili/blog/20261116-mili-protection-order-72hours.html",
        "blog/index.html",
        "articles.json",
        "articles-quarantine-20261116.json",
        "img/20261116-mili-protection-order-72hours.png",
        "site-inbox/diag-1116.py",
        "site-inbox/diag2-1116.py",
        "site-inbox/fix-1116-page.py",
        "site-inbox/gen-1116-index-card.py",
        "site-inbox/live-1116.py",
        "site-inbox/probe-log-1116.py"
    ],
    "cards_added": 1,
    "attribution": {"main": 1, "mili": 0, "najie": 0, "aipunajie": 0},
    "verification": {
        "core_http": "6/6=200",
        "page_six": "保护令页 h1=1 / ld=2 / og:image=1 / desc 115字 / **=0 / 裸表=0",
        "md_contained": "保护令页正文完整（md 1835 归一，唯一 diff 为有序列表序号）",
        "index_structure": "主索引 310 卡 div 622/622 配平 malformed=0 hist{0:+1}",
        "articles_json": "306 条 0 违例 top6 全有页面",
        "sitemap": "414 loc 看门 exit 0 无 diff",
        "live": "23 项 PASS FAILURES=NONE"
    },
    "defects_found": [
        "mili 保护令页缺 h1/og:image/twitter 标题图像（部分裸发布）",
        "najie AI图权属文缺主索引卡 + articles.json 条目",
        "articles.json 2 条 stub 条目（无落地页/跳转壳）"
    ],
    "notes": "两篇 11-15/11-14 mili 文经六项复核全达标（md 包含断言唯一 diff 为 md 有序列表序号，属归一化预期）；sitemap 无缺口。新行规：主索引卡块含 meta div，div delta 应为 +2/+2（不是 +1/+1）；避免对品牌索引整行 grep（Blog JSON-LD 单行 40KB，一次烧掉大量 token），改 python 定位。",
    "result": "PASS"
}

assert list(entry.keys()) == KEYS, (list(entry.keys()), KEYS)

TAIL = "\n  }\n ]\n}"
assert raw.endswith(TAIL), repr(raw[-20:])
head = raw[:-len(TAIL)] + "\n  }"

lines = [",\n  {\n"]
for i, k in enumerate(KEYS):
    v = json.dumps(entry[k], ensure_ascii=False)
    comma = "," if i < len(KEYS) - 1 else ""
    lines.append(f'   "{k}": {v}{comma}\n')
lines.append("\n  }")
new = head + "".join(lines) + "\n ]\n}"

d2 = json.loads(new)
assert d2["deploys"][-1]["commit"] == "a1ff6c9"
assert len(d2["deploys"]) == len(d["deploys"]) + 1
open(P, "w", encoding="utf-8").write(new)
print("OK entries:", len(d2["deploys"]))
