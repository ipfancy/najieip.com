import json, subprocess, os, re

REPO = os.path.expanduser("~/wiki/najieip-verify")
p = os.path.join(REPO, "site-inbox/deploy-log.json")
raw_origin = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"], capture_output=True, text=True, cwd=REPO).stdout
last = json.loads(raw_origin)["deploys"][-1]
KEYS = list(last.keys())

entry = {
    "date": "2026-11-20",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "349502d",
    "action": "每日巡检五段：核心6页200（零瞬断）；两篇当日觅理文补 og:image/twitter:image/twitter:card=summary_large_image（采购清单页 summary→large + 摘要卡，东城分所页从零补 5 个 twitter/og 标签），封面 340KB 入库 img/（线上 200）；主索引补「东城分所」卡 368→369（div delta 2/2、depth=0、位于首卡前）；修 mili 品牌索引该卡日期 11-19→11-20；articles.json 该条目 date 同步 11-20；articles.json 守卫第 25 次隔离 52 条（323→271，0 违例，首页 top6 六条全有页面）",
    "files_changed": 8,
    "cards_added": 1,
    "attribution": {"mili": 2, "main": 1},
    "verification": "线上 2 页六项达标（8684B/8996B，h1=1、ld=2/3 全 json.loads 通过、og:image=1、tw_large、stars=0）；封面双 200；主索引 dongcheng 卡 HIT（369 卡）；mili 索引 223,339B 卡日期=2026-11-20；live articles.json=271；6 核心页全 200；Pages run 349502d completed/success（14:02Z）",
    "defects_found": "上游两篇当日文均缺 og:image（采购清单页 twitter:card=summary 未升 large）；东城分所文主索引零卡；mili 品牌卡日期错 1 天；articles.json 条目日期错 1 天；articles.json 无页面条目复活 52 条（常态）",
    "notes": "md 包含断言本轮两例 False 全为 frontmatter 剥离不全所致（md 侧首段残留 title/date/brand/slug 字段），非正文截断；mili 品牌索引已换新卡模板（tag-litigation/tag-criminal 多标签 + 日期 11-19 误标），多标签语义错配属上游站点级遗留，本轮只修日期不做全量重写，列入 backlog",
    "result": "PASS",
}
assert list(entry.keys()) == KEYS, (list(entry.keys()), KEYS)

TAIL = "\n  }\n ]\n}"
r = raw_origin.rstrip("\n")
assert r.endswith(TAIL), repr(r[-30:])
head = r[:-len(TAIL)] + "\n  }"
lines = []
for k in KEYS:
    lines.append('   "' + k + '": ' + json.dumps(entry[k], ensure_ascii=False) + (',' if k != KEYS[-1] else ""))
new = head + ",\n  {\n" + "\n".join(lines) + "\n  }\n ]\n}"
json.loads(new)
open(p, "w", encoding="utf-8").write(new)
d = json.loads(open(p, encoding="utf-8").read())
print("entries", len(d["deploys"]), "last date", d["deploys"][-1]["date"], "keys ok", list(d["deploys"][-1].keys()) == KEYS)
