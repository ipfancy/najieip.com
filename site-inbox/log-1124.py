#!/usr/bin/env python3
"""追加 deploy-log 条目（文本手术，禁整档重写）。2026-11-24 夜班"""
import json, subprocess

P = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
last = d["deploys"][-1]
KEYS = list(last.keys())

ORDER = KEYS
vals = {
    "date": "2026-11-24",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "see-HEAD",
    "action": "精修当日 mili 裸发布页（漏写请求·惩罚性赔偿五倍）按 md 源整页重建；六核心页 HTTP 验证；articles.json 守卫；sitemap 看门；索引/feed 对账",
    "files_changed": [
        "mili/blog/20261124-mili-punitive-damages-one-shot.html",
        "img/20261124-mili-punitive-damages-one-shot.png",
        "site-inbox/diag-1124.py",
        "site-inbox/fix-1124-page.py",
        "site-inbox/log-1124.py",
        "site-inbox/deploy-log.json",
    ],
    "cards_added": 0,
    "attribution": "mili（落地目录 /mili/blog/，canonical/og:url 与落地一致）",
    "verification": "6/6 核心页 200；修复页 h1=1 h2=3 ld=2 og:image=1 stars=0 裸表=0 frontmatter=0，正文 md 全文包含=True（1643=1643）；封面 288,626B 入库；索引品牌卡/主卡各 1（上游已同步，零补卡）；articles.json 276/276 零违例、首页 top6 全有页面；feed 40 条含当日文；sitemap 看门 exit 0 无 diff；线上 6 页 200 + 修复页六项达标 + img 200",
    "defects_found": "上游 05:04 裸发布：h1=0 / ld+json=0 / 无 og:image / description 11 字复读标题（且处 articles.json 首页第 1 曝光位）；页面 6,634B→10,159B",
    "notes": "本次零补卡（品牌索引 + 主索引上游均已写卡，逐 slug 判定各命中 1 次）；feed 已于 12a3df8 由并发会话修正 pubDate 并收敛至 40 条；articles.json 已于 a2a55c2 收敛至 276 条全 200",
    "result": "PASS",
}
entry = {k: vals[k] for k in KEYS}
assert list(entry.keys()) == KEYS, "键序不一致"

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), "尾部标记不匹配"
head = r[: -len(TAIL)] + "\n  }"
block = ",\n  {\n" + ",\n".join(
    f"   {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in entry.items()
) + "\n  }"
new = head + block + "\n ]\n}"
chk = json.loads(new)
assert len(chk["deploys"]) == len(d["deploys"]) + 1
assert list(chk["deploys"][-1].keys()) == KEYS
open(P, "w", encoding="utf-8").write(new)
print("OK deploys=", len(chk["deploys"]))
