import os, json, re, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
log = json.loads(raw)
last = log["deploys"][-1]
print("last keys:", list(last.keys()))
print("last result:", last.get("result"), "| tail repr:", repr(raw[-14:]))

entry = {
    "date": "2026-11-01",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜间 22:00 — 非高峰）",
    "commit": "bdfe3fd",
    "action": "精修当日新文「专利出海还有第二道闸」（部分裸发布档：无JSON-LD/无og:image/description复读标题）+ 封面图入库 + articles.json 守卫第19次隔离",
    "files_changed": ["najie/blog/20261101-najie-ip-foreign-transfer-review.html", "img/20261101-najie-ip-foreign-transfer-review.png", "articles.json", "articles-quarantine-20261101.json", "feed.xml"],
    "cards_added": 0,
    "attribution": "najie（按上游落地目录 najie/blog/）",
    "verification": "线上页面 12,170B / h1=1 / ld=2 / og:image=1 / **=0 / desc 190 字 / canonical 正确；封面图 200；主索引卡 HIT=1、najie 索引卡 HIT=1；live articles.json=227；sitemap 看门 exit 0（370 loc 不变）",
    "defects_found": ["页面缺 Article+BreadcrumbList JSON-LD", "缺 og:image / og:site_name / keywords / twitter 标题与图像", "meta description 复读标题（25 字）", "正文 ASCII 直引号未转中文引号", "articles.json 上游复活 51 条无页面条目（278→227）"],
    "notes": "今日新文品牌卡与主卡上游已同步（无需补卡）；10-31 三篇经复核六项达标；mili 前缀文件名落地 najie/blog 属上游归属，canonical 与双索引一致，不改路径。deploy-log 文本手术追加。",
    "result": "PASS",
}

if "--apply" not in sys.argv:
    print(json.dumps(entry, ensure_ascii=False, indent=2)[:400])
    sys.exit(0)

assert list(entry.keys()) == list(last.keys()), "schema key order mismatch"
TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), "tail marker mismatch"
head = r[: -len(TAIL)] + "\n  }"
lines = []
for k, v in entry.items():
    lines.append(f'   "{k}": ' + json.dumps(v, ensure_ascii=False))
new_entry = ",\n  {\n" + ",\n".join(lines) + "\n  }"
out = head + new_entry + "\n ]\n}"
json.loads(out)
open(P, "w", encoding="utf-8").write(out)
print("appended. entries:", len(json.loads(out)["deploys"]))
