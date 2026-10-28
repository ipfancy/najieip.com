#!/usr/bin/env python3
"""1028 deploy-log 追加（文本手术，禁止整档重写）— 对齐现行 schema（含 attribution，result=PASS）"""
import json, subprocess, os, sys

ROOT = "/Users/ziganghe/wiki/najieip-verify"
LOG = os.path.join(ROOT, "site-inbox/deploy-log.json")

raw = subprocess.check_output(["git", "-C", ROOT, "show", "origin/main:site-inbox/deploy-log.json"]).decode("utf-8")
d = json.loads(raw)
last = d["deploys"][-1]
KEYS = list(last.keys())

commit = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "origin/main"]).decode().strip()

entry = {
    "date": "2026-10-28",
    "time": "22:20",
    "agent": "SiteOps",
    "round": "daily-20261028",
    "commit": commit,
    "action": "每日运营：核心 6 页 200（/mili/ /najie/ 首轮 000 瞬断，重试 3 次全 200）；主索引补 4 张当日卡（mili 变换主体598号 / 孕期辞退 / mili 软著60页 + najie 地理标志异议）240→244；mili 品牌索引补 1 张（孕期辞退文）135→136；近 3 日 9 篇品牌页六联判据 0 缺陷；articles.json 守卫 --check 264 条 0 缺页、首页 slice(0,6) 全部有页面",
    "files_changed": ["blog/index.html", "mili/blog/index.html",
                      "site-inbox/ops-1028-scan.py", "site-inbox/gen-1028-index-cards.py"],
    "cards_added": 5,
    "attribution": "上游发布只写品牌索引：mili 孕期辞退文双索引均无卡、另 3 篇（mili 变换主体 / mili 软著 / najie 地理标志）只写品牌索引 → 主索引零卡，需 SiteOps 补齐",
    "verification": "本地：主索引 cards 240→244、div 深度归零无栈空闭合、malformed=0、`**`=0；mili 索引 135→136 同法定验；四 slug 在主索引各出现 1 次、mili 孕期卡用 ./ 相对 href；sitemap 4/4 已含（343 loc）",
    "defects_found": ["mili 孕期辞退文品牌索引与主索引双缺卡 1 处",
                      "主索引漏收当日 4 篇（品牌索引已收录）"],
    "notes": "site-inbox/20261028-mili-pregnancy-disguised-dismissal-evidence.html 为上游 raw 副本（9,927B），已发布版为精修版（13,239B / ld=2 / og:image=1），md 源保留在 digital-employees/articles，raw 副本按“已接管”口径不纳入提交。",
    "result": "PASS",
}
if list(entry.keys()) != KEYS:
    print("!! schema mismatch\nentry:", list(entry.keys()), "\nlast :", KEYS)
    sys.exit(1)

r = raw.rstrip("\n")
TAIL = "\n  }\n ]\n}"
assert r.endswith(TAIL), "unexpected tail: %r" % r[-30:]
head = r[: -len(TAIL)] + "\n  }"
parts = []
for k, v in entry.items():
    parts.append('   %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)))
new = head + ",\n  {\n" + ",\n".join(parts) + "\n  }" + "\n ]\n}" + "\n"

d2 = json.loads(new)
assert len(d2["deploys"]) == len(d["deploys"]) + 1
assert list(d2["deploys"][-1].keys()) == KEYS
with open(LOG, "w", encoding="utf-8") as f:
    f.write(new)
print("OK appended, deploys:", len(d2["deploys"]))
