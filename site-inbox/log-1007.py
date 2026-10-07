#!/usr/bin/env python3
"""SiteOps 1007 close-out: remove .bak files, append deploy-log entry, write daily report."""
import os, re, json, subprocess, datetime

REPO = os.path.expanduser("~/wiki/najieip-verify")
REPORTS = os.path.expanduser("~/wiki/digital-employees/reports")
os.chdir(REPO)
DATE = "2026-10-07"

# 1) remove backup files (no shell globs: BLOCKED in cron)
removed = []
for root, _dirs, files in os.walk("."):
    if "/.git" in root:
        continue
    for f in files:
        if f.endswith(".bak-1007"):
            p = os.path.join(root, f)
            os.remove(p)
            removed.append(p)
print("removed baks:", removed)

# 2) deploy-log append (base = origin/main version, native indent=1)
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
entry = {
    "date": DATE,
    "time": datetime.datetime.now().strftime("%H:%M"),
    "agent": "SiteOps",
    "round": "每日运营（cron 22:00 前置）",
    "commit": head,
    "action": "核心 10 页 HTTP 200；精修 3 篇页面缺陷（mili 20261007 商标司法解释意见稿：补 JSON-LD Article+BreadcrumbList / og:image / twitter 卡 / description 去标题复读；mili geely-wm 08-14 与 najie jp18 09-01：markdown ** 40+38 处转 <strong>、裸 markdown 表 1 块转 <table>、泄漏 blockquote/hr 标记清理、文本节点 ASCII 引号转中文引号、补 JSON-LD）；articles.json 守卫第 12 次隔离 228→178；全站 254 页缺陷普查（105 页遗留）归档待排期",
    "files_changed": [
        "mili/blog/20261007-trademark-judicial-interpretation-opinion.html",
        "mili/blog/geely-wm-trade-secret-20260814.html",
        "najie/blog/20260901-copyright-jp18-compliance-checklist.html",
        "articles.json",
    ],
    "cards_added": 0,
    "verification": "本地：三页 h1=1 / ld=2 / og:image=1 / desc≠标题 / **=0 / 裸表=0 / div 配平 / 全部 ld+json json.loads 通过 / 正文文本节点归一后逐字相等；articles.json 178 条、首页 slice(0,6) 全部有页面；线上：核心 10 URL 200 + 修复后三页 200 且 ld=2（重试取终态）",
    "defects_found": [
        "上游裸发布/半裸发布：mili 20261007 缺 JSON-LD 与 og:image、description 复读标题（该文在 articles.json 首页第 3 曝光位）",
        "遗留 markdown 泄漏：mili geely-wm-trade-secret-20260814（**×40 + 裸表）与 najie 20260901 jp18（**×38）访客可见",
        "articles.json 又复活 50 条无页面条目（第 12 次）",
        "全站遗留缺陷 105/254 页（多为老页无 JSON-LD / h1=2），未纳入本次修复",
    ],
    "notes": "本次不新建索引卡（缺口扫描仅 cnptes-three-layer-architecture-diagram.html 一项，按 09-23 口径属架构图页，不入主索引）。site-inbox/ 出现未跟踪的 20261007 商标文交接副本（raw 版，description 复读），已在仓库留档但未以其为源（以 mili/blog 精修版为准）。",
    "result": "PASS",
}
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print(f"deploy-log: entry {len(log['deploys'])} appended")

# 3) daily report
os.makedirs(REPORTS, exist_ok=True)
report = f"""# SiteOps 日报 — {DATE}

## 线上状态
- 核心页面 10/10 = 200（首页 / mili / najie / blog / sitemap.xml / llms.txt / en / fr / mili-blog / najie-blog）
- 修复后三篇文章页线上 200，ld+json=2

## 内容同步
- content.db 近 3 日 published 4 篇（ART-2026-0101~0104），均已在品牌索引 + 主索引（205 卡）中
- 索引缺口扫描（href 归一，三品牌 vs 主索引）：真缺口 0；唯一候选中 cnptes-three-layer-architecture-diagram.html 按口径剔除
- 主索引无缺卡 → 本次不新增卡片

## 本次修复（3 篇页面缺陷）
| 页面 | 缺陷 | 修复 | 体积 |
|------|------|------|------|
| mili/20261007-trademark-judicial-interpretation-opinion | 无 JSON-LD、无 og:image、description=标题复读（首页曝光第 3 位） | Article+BreadcrumbList、og:image/twitter、真摘要 | 3,165→5,623 B |
| mili/geely-wm-trade-secret-20260814 | `**`×40、裸 markdown 表 1 块、无 JSON-LD、泄漏 blockquote/hr | strong/table/JSON-LD/hr 清理 | 4,797→6,477 B |
| najie/20260901-copyright-jp18-compliance-checklist | `**`×38、无 JSON-LD | strong/JSON-LD + 真摘要 | 4,543→6,599 B |

正文文本节点归一后逐字相等（仅格式转换，未改一字）；每页 ld+json 均通过 json.loads；div 配平。

## 守卫
- articles.json：228 → **178**（第 12 次隔离 50 条无页面条目，隔离档 articles-quarantine-20261007.json）

## 待排期 / 观察
- 全站普查：254 页中 **105 页遗留缺陷**（多为老页无 JSON-LD、h1 重复；含 en/fr 早期机翻页含裸表）→ 建议按「高曝光页优先」分批补 JSON-LD，不批量改写
- 上游继续产出"半裸发布"页（连续第 7 个工作日）→ 根治位仍在上游发布模板
"""
with open(os.path.join(REPORTS, f"siteops-daily-{DATE.replace('-', '')}.md"), "w", encoding="utf-8") as f:
    f.write(report)
print("report written:", os.path.join(REPORTS, f"siteops-daily-{DATE.replace('-', '')}.md"))
