#!/usr/bin/env python3
"""Append 11-23 evening entry to deploy-log.json by TEXT SURGERY (+15 lines / 0 deletions)."""
import json, subprocess, sys, os

REPO = "/Users/ziganghe/wiki/najieip-verify"
LOG = os.path.join(REPO, "site-inbox/deploy-log.json")

raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     cwd=REPO, capture_output=True, text=True).stdout
d = json.loads(raw)
last = d["deploys"][-1]
KEYS = list(last.keys())
print("LAST_KEYS", KEYS)

entry = {
    "date": "2026-11-23",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "a4be0bc",
    "action": "夜巡：核心 6 页 HTTP 验证 + 当日三篇（高企/食品贴牌/游戏账号）五段对账；清高企页残留 frontmatter(brand:mili)/裸 <p>---</p>/blockquote &gt; 泄漏，正文 md 全量比对",
    "files_changed": 4,
    "cards_added": 0,
    "attribution": "无新增归属变更：三篇落地目录（najie×2 + mili×1）与 canonical/双索引 href 一致，一卡一页无重复",
    "verification": "6 核心页 6/6=200；高企页线上 9,214B 与本地字节一致，h1=1/ld=2/og:image/h2=5 且 brand 泄漏、裸 hr、&gt; 泄漏均为 0；三篇品牌卡+主卡各 HIT=1；live articles.json=276、封面图 2/2=200、sitemap 433 loc；articles.json 0 条无页面、首页 top6 全有页面；sitemap 看门 exit 0 无回灌",
    "defects_found": "① 11-23 早班宣称已清 frontmatter 泄漏，实际残留 <p>---</p><p>brand: mili</p><p>---</p> 三段仍在正文顶部（可见文本）② 高企页另有两处泄漏：裸 <p>---</p> 分隔行、段落内 &gt; blockquote 前缀 ③ md 尾部两句重复 AI 声明，页面仅保留一句（等价声明，非内容缺失）",
    "notes": "md 全量包含比对通过（食品贴牌 1575/1575、游戏账号 1599/1599 严格相等；高企页仅缺 md 侧重复 AI 声明句，正文零缺失）。frontmatter 泄漏判据需按『keys 逐行』而非『整块』——上游把 brand 混排在 title/date/slug 之后，早班只删了前三行。push 首次被拒（远端已有 429a3e2），sitemap-auto.sh 的 pull --rebase 已自动变基后推送成功。",
    "result": "PASS",
}
assert list(entry.keys()) == KEYS, ("SCHEMA_MISMATCH", list(entry.keys()))

TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith("'") is False
body = raw.rstrip("\n")
if not body.endswith(TAIL):
    print("TAIL_MISMATCH", repr(body[-20:])); sys.exit(1)

head = body[:-len(TAIL)] + "\n  }"
lines = [",\n  {\n"]
for i, k in enumerate(KEYS):
    v = json.dumps(entry[k], ensure_ascii=False)
    comma = "," if i < len(KEYS) - 1 else ""
    lines.append('   "%s": %s%s\n' % (k, v, comma))
new = head + "".join(lines) + "  }" + "\n ]\n}"

# validate
d2 = json.loads(new)
assert len(d2["deploys"]) == len(d["deploys"]) + 1
assert list(d2["deploys"][-1].keys()) == KEYS
print("VALIDATED entries", len(d2["deploys"]))

if "--apply" in sys.argv:
    open(LOG, "w", encoding="utf-8").write(new)
    print("APPLIED bytes", os.path.getsize(LOG))
else:
    print("DRYRUN")
