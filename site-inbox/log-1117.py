import json, os, subprocess
REPO = "/Users/ziganghe/wiki/najieip-verify"
P = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
cur = json.loads(raw)
last = cur["deploys"][-1]
keys = list(last.keys())

entry = {
    "date": "2026-11-17",
    "time": "22:22",
    "agent": "SiteOps",
    "round": "每日运营（周二夜班）",
    "commit": "531a5e1",
    "action": "精修 20261117 德芙广告法裸发布页（md 源整页重建套 11-16 mili 房屋）+ 双索引补卡 + articles.json 摘要补全",
    "files_changed": [
        "mili/blog/20261117-mili-dove-ad-role.html (6105→9432B)",
        "mili/blog/index.html (194→195 卡)",
        "blog/index.html (334→335 卡)",
        "articles.json (description 标题复读→真摘要 137 字)",
        "img/20261117-mili-dove-ad-role.png (313KB 入库)"
    ],
    "cards_added": 2,
    "attribution": "mili（落地目录 /mili/blog/，canonical 与 og:url 一致）",
    "verification": "核心 6 页 6/6=200；线上页 h1=1 / h2=3 / ld=2(@context=2) / og:image / summary_large_image / desc 137 字 / stars=0 / canonical=mili / 封面 200；mili 索引 195 卡 HIT、主索引 335 卡 HIT、feed HIT、live articles.json 259 条且新条 desc 137 字；FAILURES=NONE",
    "defects_found": [
        "本页：h1=0 h2=0 ld=0 无 og:image twitter:card=summary description=标题复读 30 字 ** ×6（部分裸发布+缺卡）",
        "articles.json 该条 description 亦为标题复读（首页 slice(0,6) 第 1 曝光位）"
    ],
    "notes": "md 全文包含断言 1330==1330（md 侧整行丢弃 **小标题**）；卡片深度 delta +2/+2 对称；sitemap 看门 exit 0 静默（415 loc 不变，loc 上游 1e8e126 已录）；najie 索引 11-16 AI 图文复核有卡（此前 set 去重误读为缺卡，count=3 系 1 卡 + 2 处 JSON-LD）",
    "result": "PASS",
}
assert list(entry.keys()) == keys, (list(entry.keys()), keys)

idx = raw.rfind("\n ]\n}")
assert idx > 0
body = raw[:idx].rstrip("\n")
assert body.rstrip().endswith("}"), body[-40:]
lines = ",\n  {\n" + ",\n".join('   "%s": %s' % (k, json.dumps(entry[k], ensure_ascii=False)) for k in keys) + "\n  }"
new = body + lines + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
d2 = json.loads(new)
assert len(d2["deploys"]) == len(cur["deploys"]) + 1
assert list(d2["deploys"][-1].keys()) == keys
open(P, "w", encoding="utf-8").write(new)
print("OK entries", len(d2["deploys"]))
