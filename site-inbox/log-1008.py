#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append deploy-log entry (schema-matched, indent=1, origin-based) + write daily report."""
import subprocess, json, os, re

REPO = os.path.expanduser("~/wiki/najieip-verify")

# --- base = origin version (avoid clobbering concurrent history) ---
base = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                      cwd=REPO, capture_output=True, text=True).stdout
log = json.loads(base)
deploys = log["deploys"]
print("existing entries:", len(deploys))
print("last entry keys:", list(deploys[-1].keys()))

commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                        capture_output=True, text=True).stdout.strip()

entry = {k: "" for k in deploys[-1].keys()}
entry.update({
    "date": "2026-10-08",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（cron 22:00）",
    "commit": commit,
    "action": "核心 10 页巡检 + 精修 1 篇「部分裸发布」页 + articles.json 守卫隔离 + sitemap 看门测试",
    "files_changed": "mili/blog/20261008-mili-labor-contract-four-clauses.html（6414→11677B）、articles.json（232→182）、articles-quarantine-20261008.json（+50 条）、site-inbox/fix-1008-mili-labor.py 等脚本",
    "cards_added": "0（10-08 四篇新文索引卡已由日间并发任务补齐，href 归一扫描确认无缺口）",
    "verification": "线上 4 篇 10-08 新文 + 双索引卡 HIT 全 PASS（live bytes 与本地一致 11677B）；核心 8 页 HTTP 200；sitemap 看门 exit 0 / 299 loc 不变；每页 ld+json json.loads 通过；正文 25 段零改动",
    "defects_found": "1 篇「部分裸发布」（mili 劳动用工文：ld=0 / 无 og:image / description 复读标题；有 h1 与外链样式，故四联判据会漏判）；articles.json 上游复活 50 条无页面条目",
    "notes": "「部分裸发布」第 5 例；本页原处 articles.json 首页 slice(0,6) 第 4 曝光位。修复补 JSON-LD Article+BreadcrumbList、og:image、twitter 卡、keywords、真摘要，并按段落前缀插 4 条 h2 路标（不改一字正文）。全站 254 页普查口径维持：只报近 3 日窗口实修项。",
    "result": "PASS — 0 线上失败项",
})
deploys.append(entry)

open(os.path.join(REPO, "site-inbox", "deploy-log.json"), "w", encoding="utf-8").write(
    json.dumps(log, ensure_ascii=False, indent=1))
print("appended, total:", len(deploys))

# --- daily report ---
rd = os.path.expanduser("~/wiki/digital-employees/reports")
os.makedirs(rd, exist_ok=True)
rp = os.path.join(rd, "siteops-daily-20261008.md")
open(rp, "w", encoding="utf-8").write("""# SiteOps 日报 — 2026-10-08（22:00 班）

## 1. HTTP 核心页面
✅ 8/8 全 200（首页 / mili / najie / blog / sitemap.xml / llms.txt / en / fr），首轮即通，无瞬断

## 2. content.db 近期文章 → 索引落地
✅ 近 4 日 4 篇（ART-0101~0104）全部 IN-INDEX：
- 0104 商标司法解释意见稿（10-07）→ main + mili
- 0103 执行后六条合规清单（10-06）→ main + mili
- 0102 年费足缴第9年作废（10-05）→ main + mili + najie
- 0101 竹材 FTO 决策树（10-04）→ main + mili

## 3. 索引缺口扫描（href 归一）
✅ 品牌索引 mili 114 / najie 84 卡 vs 主索引 209 卡 → 真缺口 0
（唯一“缺口” najie/blog/cnptes-three-layer-architecture-diagram.html 属架构图页，按 09-23 口径不入主索引）
✅ 今日 4 篇 10-08 新文卡片已由日间并发任务补齐（mili×3 + aipunajie×1），sitemap 299 loc 含全部 4 条

## 4. 页面质量六联判据（近 3 日 git 触及窗口）
⚠️ 修复 1 篇「部分裸发布」— mili/blog/20261008-mili-labor-contract-four-clauses.html
- 症状：ld+json=0、无 og:image、description 复读标题；**有 h1 + 外链样式**（故只跑四联的 h1/style 两项会漏判）
- 该页正处 articles.json 首页 slice(0,6) 第 4 曝光位
- 修复：补 Article + BreadcrumbList JSON-LD、og:image、twitter 卡、keywords、按原文事实重写摘要；按段落前缀插 4 条描述性 h2 路标（不改一字正文）
- 6414 B → 11677 B；正文 25 段逐段比对零差异；2 个 ld+json 块 json.loads 全通过
✅ 其余 10-08 新文（AI解题成果归谁 / 抢号软件获刑 / EV专利FTO）六项全达标

## 5. articles.json 守卫
⚠️ 第 13 次隔离：232 → 182（50 条「页面不存在」条目，均为上游自动发布复活）
✅ 首页 slice(0,6) 六条条目全部有落地页，零死链曝光风险

## 6. sitemap 看门测试
✅ 干净树下 exit 0，299 loc 无变化 → 无回灌

## 7. 部署
✅ commit 7024235 → origin/main；线上终验 7/7 PASS，修复页 live bytes=11677 与本地字节一致

## 待办 / 信号
- 上游自动发布仍在产出「部分裸发布」页（今日 1 篇，累计第 5 例）→ 根治位在发布流水线（补 JSON-LD/og:image/摘要分离）
- 全站 254 页普查：105 页历史遗留缺陷（老页无 JSON-LD、h1=2、EN/FR 早期机翻页裸表），只量化不批量改；建议后续按高曝光页分批补 JSON-LD
- GEO 周追踪（周六 02:00）本周待跑；上一轮 10-03 双平台 18 检查点 0 命中，累计 142
""")
print("report:", rp)
