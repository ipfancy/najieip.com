#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 deploy-log 条目（文本手术，+15 行 / 0 删除）"""
import json, os, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(LOG, encoding='utf-8').read()
d = json.loads(raw)
last = d['deploys'][-1]
print("last keys:", list(last.keys()))
assert len(d['deploys']) == 131, len(d['deploys'])

entry = {
  "date": "2026-11-08",
  "time": "22:00",
  "agent": "SiteOps",
  "round": "每日运营",
  "commit": "4e295cf",
  "action": "精修 mili 家事盗窃文「部分裸发布」页为房屋版 + 补主索引 11-01 AI 文书卡 + articles.json 守卫第24次隔离",
  "files_changed": ["mili/blog/20261108-mili-family-theft-leniency.html", "blog/index.html", "articles.json", "img/20261108-mili-family-theft-leniency.png"],
  "cards_added": 1,
  "attribution": {"brand": "mili", "landing_dir": "mili/blog/", "canonical_ok": True, "main_index": "+1", "brand_index": "already present"},
  "verification": "live 13 项全 PASS：ld=2 / h1=1 / og:image / **=0 / table.data=4 / desc 147 字 / schema.org 完整 / canonical / 封面 200 / 三处索引卡 HIT / articles.json 244；Pages run 42487809293 completed success",
  "defects_found": ["ld=0 无 JSON-LD", "无 og:image/og:site_name/keywords", "description 复读标题 23 字", "** ×2 未转 strong", "裸 markdown 表 4 张共 20 行", "主索引缺 11-01 补发文卡", "articles.json 复活 51 条违例"],
  "notes": "按 md 源整页重建套同日 mili 房屋（20261107 试岗文），正文 md 全文包含断言=True；新增行规：md 包含归一须剥 `>`（blockquote 标记）与 `#{1,2} ` 标题行",
  "result": "PASS"
}
# 旧条目可能的键序差异 → 按上一条键序重排
order = list(last.keys())
entry = {k: entry.get(k, last.get(k)) for k in order}
print("new keys:", list(entry.keys()))

TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith(TAIL), "TAIL 不匹配"
r = raw.rstrip("\n")
head = r[:-len(TAIL)] + "\n  }"
lines = []
for k, v in entry.items():
    lines.append(f'   "{k}": ' + json.dumps(v, ensure_ascii=False))
insert = ",\n  {\n" + ",\n".join(lines) + "\n  }"
new = head + insert + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
d2 = json.loads(new)
assert len(d2['deploys']) == 132
assert list(d2['deploys'][-1].keys()) == order
open(LOG, 'w', encoding='utf-8').write(new)
print("OK entries:", len(d2['deploys']))
print(subprocess.run(["git","-C",REPO,"diff","--stat","site-inbox/deploy-log.json"],capture_output=True,text=True).stdout)
