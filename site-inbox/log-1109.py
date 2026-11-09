import json, subprocess, os, re, sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
P = os.path.join(REPO, "site-inbox/deploy-log.json")
APPLY = "--apply" in sys.argv

raw = subprocess.run(["git", "show", "HEAD:site-inbox/deploy-log.json"], cwd=REPO, capture_output=True, text=True).stdout
obj = json.loads(raw)
last = obj["deploys"][-1]
print("LAST KEYS", list(last.keys()))
print("count", len(obj["deploys"]))

entry = {
    "date": "2026-11-09",
    "time": "22:20",
    "agent": "SiteOps",
    "round": "每日运营（22:00 cron）",
    "commit": "3d97e42",
    "action": "精修「办卡的钱能退回多少」（mili 预付卡退款）部分裸发布页 + 双索引补卡 + articles.json 守卫隔离",
    "files_changed": [
        "mili/blog/20261109-mili-prepaid-card-refund.html",
        "mili/blog/index.html",
        "blog/index.html",
        "img/20261109-mili-prepaid-card-refund.png",
        "articles.json",
        "articles-quarantine-20261109.json"
    ],
    "cards_added": 2,
    "attribution": "mili（觅理 / 消费者权益·预付卡）",
    "verification": "本地：h1=1 / ld=2 且 json.loads 全通 / og:image+og:site_name+twitter+keywords 齐备 / desc 167 字非标题复读 / **=0 / md 全文完整包含=True（1517=1517）；mili 索引 156→157（div delta +2/+2 与基线 338/337 同差）、主索引 274→275（552/552 配平、malformed=0、dups=0、首卡日期降序 11-09→11-08）；articles.json 守卫第24次 296→245（首页 top6 六条全有页面）；sitemap 看门 exit 0（395 loc，新文已收录）；线上：Actions run 3d97e42 completed/success，页面 10,606B 与本地字节一致、九项判据 PASS、封面图 200、双索引卡 HIT（157/275）、live articles.json 245 含新文。FAILURES=NONE",
    "defects_found": [
        "上游部分裸发布：ld=0 / 无 og:image+og:site_name+keywords / description 复读标题（25 字）/ ** 8 处未转",
        "mili 索引仅有 BlogPosting JSON-LD 条目、无文章卡；主索引零卡",
        "site-inbox 遗留与已发布页字节相同的上游副本"
    ],
    "notes": "正文按 md 源重建套 11-08 同日 mili 文房屋（/style.css + nav/footer + Article/BreadcrumbList deepcopy 覆写），正文 md 全文包含断言通过（一字未改）；卡片模板 href 用正则改属性（串替换会把 /mili/blog 前缀叠加成 /mili/blog/mili/blog）；md 包含归一需剥列表序号 1. 与标题行；上游 articles.json 条目已在（未提交），守卫 --apply 隔离 51 条。",
    "result": "PASS",
}

assert list(entry.keys()) == list(last.keys()), (list(entry.keys()), list(last.keys()))

lines = []
for k, v in entry.items():
    lines.append('   "%s": %s' % (k, json.dumps(v, ensure_ascii=False)))
block = ",\n  {\n" + ",\n".join(lines) + "\n  }"

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), repr(r[-30:])
head = r[:-len(TAIL)] + "\n  }"
new = head + block + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
json.loads(new)
print("new entries", len(json.loads(new)["deploys"]))

if APPLY:
    open(P, "w", encoding="utf-8").write(new)
    print("WROTE", len(new))
