#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-02 deploy-log 追加（文本手术：+15 行 / 0 删除）"""
import os, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
data = json.loads(raw)
last = data["deploys"][-1]
print("last entry keys:", list(last.keys()))
print("last result:", last.get("result"), "| cards_added:", last.get("cards_added"))

ENTRY = {
    "date": "2026-11-02",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "daily-1102",
    "commit": "b36e101",
    "action": "精修上游裸发布页20261102技术出口48号公告（7948B→12087B：补6个h2路标/Article+BreadcrumbList JSON-LD/og:image自托管/twitter+keywords/真摘要193字/正文补全至md全文/**转strong/直引号转中文）+ 封面302KB入库 + 双索引补卡3张（主255→257、najie100→101）+ articles.json守卫第20次隔离51条（280→229）",
    "files_changed": ["najie/blog/20261102-najie-tech-export-catalog-48.html",
                      "img/20261102-najie-tech-export-catalog-48.png",
                      "najie/blog/index.html", "blog/index.html",
                      "articles.json", "articles-quarantine-20261102.json"],
    "cards_added": 3,
    "attribution": {"mili": 0, "najie": 3, "main_index": 3},
    "verification": {"core_pages": "6/6 200", "pages": "2/2 ld=2 h1=1 og:image=1 stars=0 desc非标题复读",
                     "bytes": "2/2 线上与本地严格一致（12087B / 10239B）",
                     "cards_live": "4/4 HIT", "cover": "200",
                     "articles_json_live": 229, "sitemap_watchdog": "exit 0 静默（372 loc）",
                     "structure": "双索引 div 配平归零/深度分布差==新增数/无重复href/星号0 全 PASS"},
    "defects_found": ["上游裸发布页：ld=0 无 og:image/twitter/keywords/h2、** 11 处未转、description 27 字复读标题、正文截断（md 未完整包含）",
                      "当日两篇文主索引均零卡（najie 索引仅 B 有卡，A 双索引全无）",
                      "articles.json 上游复活 51 条无页面条目"],
    "notes": "48号公告文为10-16新政解读，属涉外/技术出口线；A 页按 md 源整页重建套 B 页房屋（同日同品牌，deepcopy JSON-LD 覆写，正文归一后 md 完整包含断言通过）；articles.json 隔离第20次，首页 top6 六条全有页面",
    "result": "PASS",
}

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
trailing_nl = raw.endswith("\n")
if not r.endswith(TAIL):
    sys.exit("TAIL 不匹配，中止")
head = r[:-len(TAIL)] + "\n  }"
lines = []
for k, v in ENTRY.items():
    lines.append("   " + json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False))
new = head + ",\n  {\n" + ",\n".join(lines) + "\n  }" + "\n ]\n}" + ("\n" if trailing_nl else "")
d2 = json.loads(new)
assert list(d2["deploys"][-1].keys()) == list(last.keys()), "schema 键序不一致"
assert len(d2["deploys"]) == len(data["deploys"]) + 1
open(P, "w", encoding="utf-8").write(new)
print(f"appended: deploys {len(data['deploys'])} -> {len(d2['deploys'])}")
