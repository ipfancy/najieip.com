#!/usr/bin/env python3
"""log-1009.py — 追加 deploy-log（origin 做底 indent=1）+ 写日报"""
import os, re, json, subprocess, datetime

BASE = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(BASE, "site-inbox/deploy-log.json")
REPORT_DIR = os.path.expanduser("~/wiki/digital-employees/reports")
DATE = "2026-10-09"
SLUG = "20261009-mili-ai-short-drama-token-evidence"

# origin 版本做底
r = subprocess.run(["git", "-C", BASE, "show", "origin/main:site-inbox/deploy-log.json"],
                   capture_output=True, text=True)
log = json.loads(r.stdout)
assert isinstance(log, dict) and "deploys" in log, "deploy-log schema unexpected"

commit = subprocess.run(["git", "-C", BASE, "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()

entry = {
    "date": DATE,
    "time": datetime.datetime.now().strftime("%H:%M"),
    "agent": "SiteOps",
    "round": "每日运营",
    "commit": commit,
    "action": ("修复上游「部分裸发布」页 mili/%s.html（补 JSON-LD Article+BreadcrumbList、og:image、"
               "twitter 卡、keywords、真摘要，2824→5226字，正文零改动）；双索引补卡" % SLUG),
    "files_changed": [
        "mili/blog/%s.html" % SLUG,
        "mili/blog/index.html",
        "blog/index.html",
        "articles.json",
        "articles-quarantine-20261009.json",
    ],
    "cards_added": {"mili/blog/index.html": "114->115", "blog/index.html": "209->210"},
    "verification": ("核心6页200；新页线上 ld=2/og:image=1/h1=1/**=0；双索引 slug HIT；"
                     "articles.json 线上=183；sitemap 300 loc（含本文）；结构终验 PASS"
                     "（depth 对 origin 基线校准=1，div 配平，新卡首卡日期降序）；正文与原文逐段零改动"),
    "defects_found": ("1 篇上游部分裸发布（ld=0/no-og:image/desc=title，位于 articles.json 首页第1曝光位）；"
                      "articles.json 50 条无页面条目复活（第14次）"),
    "notes": "sitemap 看门测试 exit 0 无回灌；najie 品牌博客无新文需同步",
    "result": "PASS",
}
log["deploys"].append(entry)
with open(LOG, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("deploy-log appended, total deploys =", len(log["deploys"]))

# 日报
os.makedirs(REPORT_DIR, exist_ok=True)
rp = os.path.join(REPORT_DIR, "siteops-daily-%s.md" % DATE.replace("-", ""))
report = """# SiteOps 日报 — %s

✅ 核心 6 页线上 200（首页/mili/najie/blog/sitemap.xml/llms.txt）
✅ 修复上游「部分裸发布」：mili/%s.html 补 JSON-LD×2/og:image/twitter/keywords/真摘要，2824→5226字，正文逐段零改动
✅ 双索引补卡：mili 114→115、主索引 209→210（日期降序置顶，终验 depth/div配平/首卡全 PASS）
✅ articles.json 守卫第 14 次隔离：233→183（上游复活 50 条无页面条目，已转可检出）
✅ sitemap 看门测试 exit 0（300 loc，含本文；无回灌）
✅ 线上终验：新页 ld=2/og:image=1/h1=1/**=0；双索引 slug HIT；articles.json=183
✅ najie 品牌博客无新文需同步

commit %s
""" % (DATE, SLUG, commit)
with open(rp, "w", encoding="utf-8") as f:
    f.write(report)
print("report written:", rp)
