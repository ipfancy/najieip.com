#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1014 夜：deploy-log 追加（origin 版做底 + indent=1）+ 日报"""
import json, os, subprocess, datetime
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))

raw = subprocess.run("git show origin/main:site-inbox/deploy-log.json", shell=True,
                     capture_output=True, text=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and "deploys" in log, "schema drift"
prev = dict(log["deploys"][-1])
n = len(log["deploys"])
entry = {
    "date": "2026-10-14",
    "time": "22:0x",
    "agent": "SiteOps",
    "round": "daily-1014-night",
    "commit": "pending",
    "action": "每日巡检：核心 6 页 200 + 近 3 日 6 页六联判据（0 真缺陷）+ 主索引缺 2 卡补齐 + najie 20261014 页补 BreadcrumbList + articles.json 守卫 187/187",
    "files_changed": ["blog/index.html",
                      "najie/blog/20261014-trademark-pattern-packaging-confusion.html"],
    "cards_added": {"blog/index.html": 2, "brand": 0},
    "verification": "主索引 212→214 卡（div 深度 0 / depth1 卡 214 / 无重复 href / 无 **）；3 新页线上 200；sitemap 307 loc 已含 3 新页；articles.json 187/187 零违例、首页 top6 全部有页面",
    "defects_found": ["主索引缺 mili/lajie 2 张 10-14 新卡（上游 13:40 提交只补了 1 张）",
                      "najie 20261014 页只有 Article JSON-LD，缺 BreadcrumbList（同批其他新页为 2-3 块）",
                      "site-inbox/20261010-mili-aigc-trade-secret-two-leaks.html 保留上游原始副本（ld=0/16 处 **），线上可访问但未被索引/未进 sitemap"],
    "notes": "index 页 ld=1（CollectionPage/WebSite）与 i18n 页 ld=1（单 BlogPosting）经 origin 基线核对为站点规范，非缺陷；行规更新：六联判据的 ld>=2 只对文章页生效，index 与 i18n 页按各自基线判定",
    "result": "success",
}
log["deploys"].append(entry)
open("site-inbox/deploy-log.json", "w", encoding="utf-8").write(
    json.dumps(log, ensure_ascii=False, indent=1) + "\n")
print("deploy-log: %d -> %d entries" % (n, len(log["deploys"])))

rep = os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-20261014.md")
os.makedirs(os.path.dirname(rep), exist_ok=True)
body = """
## 22:00 夜间巡检（SiteOps 每日运营）

- ✅ 核心 6 页线上 200（/ /mili/ /najie/ /blog/ /sitemap.xml /llms.txt）
- ✅ 今日 3 篇新页线上 200：najie 别把大牌花纹印包装、najie 布图设计322号、mili 专利＋商业秘密分层
- ✅ 六联判据（近 3 日 7 页）：0 真缺陷 —— index/i18n 页 ld=1 经基线核对为规范（非缺陷）
- ✅ articles.json 守卫：187/187 零违例（未复活）；首页 slice(0,6) 全部有页面
- ✅ sitemap 307 loc，已含今日 3 篇新页
- 🔧 修复 1：主索引补 2 张缺口卡（mili 专利＋商业秘密分层 / najie 布图设计322号）→ 212→214 卡，结构终验全 PASS（深度 0 / depth1 卡 214 / 无重复 href）
- 🔧 修复 2：najie 20261014 页补 BreadcrumbList JSON-LD（11,021→11,628 B，body 逐字不变）→ 该页 1→2 块
- ⚠️ 遗留（非阻塞）：site-inbox/20261010-mili-aigc-trade-secret-two-leaks.html 上游原始副本线上可访问（16 处 `**` 未转、无 JSON-LD）；未被索引、未进 sitemap，属交付留档，建议上游入库后清理
- ℹ️ 未做：GEO 追踪（周六 02:00 任务）、多语言同步（本周六）
"""
mode = "a" if os.path.exists(rep) else "w"
if mode == "w":
    body = "# SiteOps 日报 — 2026-10-14\n" + body
with open(rep, mode, encoding="utf-8") as fh:
    fh.write(body)
print("report:", rep, "mode", mode)
