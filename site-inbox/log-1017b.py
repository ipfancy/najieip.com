#!/usr/bin/env python3
"""Append daily deploy-log entry (indent=1, origin version as base) + daily report md."""
import os, json, subprocess, datetime

REPO = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(REPO, "site-inbox/deploy-log.json")
REPORTS = os.path.expanduser("~/wiki/digital-employees/reports")
os.makedirs(REPORTS, exist_ok=True)

raw = subprocess.run(["git", "-C", REPO, "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
entry = {
    "date": "2026-10-17",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（晚检）",
    "commit": subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True).stdout.strip(),
    "action": "精修今日新页「部分裸发布」第7例 + 双索引补卡 + articles.json 第18次隔离",
    "files_changed": [
        "mili/blog/customs-ip-post-filing-steps-20261017.html",
        "img/customs-ip-post-filing-steps-20261017.png",
        "mili/blog/index.html",
        "blog/index.html",
        "articles.json",
        "articles-quarantine-20261017.json",
    ],
    "cards_added": {"mili_blog_index": 1, "main_blog_index": 1, "total": 2},
    "verification": {
        "core_pages": "6/6 200 (/ /mili/ /najie/ /blog/ /sitemap.xml /llms.txt)",
        "page_live": "h1=1 ld=2 og:image=1 og:site_name twitter:title keywords desc>80 stars=0 schema_org=2",
        "cover_image": "200",
        "indexes_live": "mili 119 cards HIT / main 217 cards HIT",
        "articles_json_live": 191,
        "sitemap_watchdog": "exit 0, 312 loc unchanged",
        "body_text": "归一后逐字相等（新增 h1 之外零改动）",
    },
    "defects_found": [
        "今日新页 h1=0 / ld+json=0 / 无 og:image / 无 og:site_name / 无 twitter:title / 无 keywords / description 复读标题（28字）",
        "页面位于 articles.json 首页 slice(0,6) 第 1 曝光位",
        "双索引零卡（mili 与主索引均无该文）",
        "articles.json 50 条无页面条目（上游整体复活）",
    ],
    "notes": "7,095->10,423B；body_text_identical=True；2 块 ld+json json.loads 全通；mili 索引 118->119（含 BlogPosting+1）、主索引 216->217；articles.json 241->191",
    "result": "PASS",
}
log["deploys"].append(entry)
with open(LOG, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("deploy-log entries:", len(log["deploys"]))

report = f"""# SiteOps 日报 — 2026-10-17（晚检）

✅ 核心 6 页全部 200（/ /mili/ /najie/ /blog/ /sitemap.xml /llms.txt）
✅ 修复今日新页「部分裸发布」第 7 例：mili/blog/customs-ip-post-filing-steps-20261017.html
   h1=0 / ld+json=0 / 无 og:image / description 复读标题（28 字）→ 7,095B → 10,423B
   补 h1 + Article/BreadcrumbList JSON-LD + og:image/og:site_name/twitter/keywords + 真摘要 149 字
   正文归一后逐字相等（除新增 h1 零改动）；2 块 ld+json 全部 json.loads 通过；封面图入库 278,890B（线上 200）
✅ 双索引补卡：mili 118→119（BlogPosting 同步 +1）、主索引 216→217（日期降序置首）
✅ articles.json 守卫第 18 次隔离：241 → 191（50 条无页面条目，首页 top6 全部有页面）
✅ sitemap 看门 exit 0，312 loc 不变（上游已自动纳入新页）
✅ 线上终验 FAILURES = NONE（9 项页面判据 + 封面 200 + 双索引 HIT + 线上 articles.json=191 + 6 核心页 200）

⚠️ 上游缺陷仍在：今日文章仍是「部分裸发布」+ 零索引卡 + 占据首页第 1 曝光位，与 10-06/10-13/10-15/10-16 同源。
建议推动上游发布流水线在写入时即带 h1/JSON-LD/og:image 并同步双索引，否则每晚需人工补偿。

无新增缺口；content.db 近 3 日 4 篇文章（0106–0109）均已在上线页面与索引中。
"""
p = os.path.join(REPORTS, "siteops-daily-20261017.md")
with open(p, "w", encoding="utf-8") as f:
    f.write(report)
print("report:", p, os.path.getsize(p), "B")
