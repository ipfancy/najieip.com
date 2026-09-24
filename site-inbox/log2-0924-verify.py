#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 deploy-log：给末条（本日）补 verify 字段。取 origin 版做底 + indent=1"""
import os, json, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
APPLY = "--apply" in sys.argv
P = "site-inbox/deploy-log.json"

origin = subprocess.run(["git", "show", "origin/main:%s" % P], capture_output=True, text=True).stdout
log = json.loads(origin)
last = log["deploys"][-1]
print("末条 date=%s type=%s" % (last.get("date"), last.get("type")))
assert last.get("date") == "2026-09-24", "末条不是本日条目，停止"

last["verify"] = {
    "core_pages": "8/8 HTTP 200（含 /en/ /fr/ /mili/blog/；fr 首轮 0 = 瞬断，重试 3/3 全 200）",
    "article_page_live": "h1=1 h2=6 ld=2 og:image=1 keywords=1; og/canonical/ld=4; **=0; schema.org=2; 线上/本地唯一差异 = CF 注入 beacon（Δ367B，difflib 归因）",
    "mili_index_live": "96 卡（本地 96）；新卡 HIT；Δ367B（CF beacon）",
    "main_index_live": "182 卡（本地 182）；新卡 HIT；Δ367B（CF beacon）",
    "sitemap": "266 loc，含该文；看门测试 sitemap-auto.sh 静默 exit 0 且 loc 不变",
    "articles_json_guard": "155/155 合格 0 违例；首页 top6 六条均有实体页面（rank1 = 本文，修复后）",
    "ogcheck_core4": "4/4 通过 0 issues",
    "recent2days_coverage": "近 2 日 3 篇已发布：主索引/品牌索引/articles.json/sitemap/线上 全 True",
}
out = json.dumps(log, ensure_ascii=False, indent=1)
print("行数 delta:", out.count("\n") - origin.count("\n"))
if APPLY:
    with open(P, "w", encoding="utf-8") as f:
        f.write(out)
    print("已写入", P)
else:
    print("(--dry-run)")
