import json, sys, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
p = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(p, encoding="utf-8").read()
had_nl = raw.endswith("\n")
TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), "尾结构不符: " + repr(r[-40:])
head = r[: -len(TAIL)] + "\n  }"
prev = json.loads(head + "\n ]\n}")["deploys"][-1]
keys = list(prev.keys())
print("schema keys:", keys)

sha = sys.argv[1] if len(sys.argv) > 1 else "pending"
entry = {
    "date": "2026-11-21",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（周六夜班）",
    "commit": sha,
    "action": "每日运营：核心页 6/6=200；精修 mili 离婚游戏账号文（补 og:image/og:site_name/twitter:card+title+image/真摘要94字，Article image+description；正文未改一字）；封面318KB入库；三索引补卡3张（34家代理机构吊销→mili+主，SEP行政裁决37条→najie+主）；articles.json 守卫隔离52条 326→274",
    "files_changed": [
        "mili/blog/20261121-mili-divorce-game-account-88w.html",
        "img/20261121-mili-divorce-game-account-88w.png",
        "mili/blog/index.html",
        "najie/blog/index.html",
        "blog/index.html",
        "articles.json",
        "articles-quarantine-20261121.json",
        "site-inbox/diag-1121.py",
        "site-inbox/fix-1121-head.py",
        "site-inbox/gen-1121-cards.py",
        "site-inbox/gen-1121-main.py",
        "site-inbox/check-1121-sm.py"
    ],
    "cards_added": 3,
    "attribution": {"mili": 1, "najie": 1, "main": 2},
    "verification": "6/6 核心页 200；三篇当日文 h1=1 / ld>=2 / og:image 齐；主索引 370->372 div 746/746 配平 malformed=0；mili 215（历史 unclosed 1，delta 对称）；najie 165 配平；articles.json 274 全合格 top6 有页；sitemap 431 loc lastmod 100%；feed 三篇齐",
    "defects_found": "① 离婚游戏账号文缺 og:image/og:site_name/twitter 卡片、description 复读标题 ② 两篇当日文（34家代理吊销 / SEP37条）品牌索引与主索引全零卡",
    "notes": "上游 59029f9 已修 frontmatter/管道表格/星号/h1，本轮只补 head 缺失项；articles.json 违例为上游自动发布长期缺陷，守卫幂等可复跑",
    "result": "PASS",
}
missing = [k for k in keys if k not in entry]
extra = [k for k in entry if k not in keys]
if missing or extra:
    print("MISSING", missing, "EXTRA", extra)
    sys.exit(1)
lines = []
for k in keys:
    lines.append('   "%s": %s' % (k, json.dumps(entry[k], ensure_ascii=False)))
ins = ",\n  {\n" + ",\n".join(lines) + "\n  }"
out = head + ins + "\n ]\n}" + ("\n" if had_nl else "")
json.loads(out)
open(p, "w", encoding="utf-8").write(out)
print("appended, total entries:", len(json.loads(out)["deploys"]))
