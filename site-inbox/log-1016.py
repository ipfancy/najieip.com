#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-16 deploy-log + 日报"""
import os, subprocess, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
DATE, TIME = "2026-10-16", "22:0x CST"

# 以 origin/main 版本做底，append（indent=1，避免全档 diff）
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
print("现有条目 =", len(log["deploys"]))
print("上一 entry 字段 =", sorted(log["deploys"][-1].keys()))

entry = {
    "date": DATE,
    "time": TIME,
    "agent": "SiteOps",
    "round": "daily-2200",
    "commit": "c79dcfb",
    "action": "精修 najie 今日新页「部分裸发布」（补 h1 + 3 个 h2 路标 + BreadcrumbList JSON-LD + og:image/og:site_name/twitter/keywords/真摘要，描述去标题复读）+ 封面图入库 + articles.json 第17次隔离 + 接管 site-inbox 冗余副本",
    "files_changed": ["najie/blog/customs-ip-filing-3-things-20261016.html",
                      "img/customs-ip-filing-3-things-20261016.png",
                      "articles.json", "articles-quarantine-20261016.json"],
    "cards_added": 0,
    "verification": "线上 8/8 核心页 200；精修页 11 项判据全 PASS（h1=1/h2=3/ld=2/og:image/og:site_name/keywords/twitter:title/**=0/desc!=title/schema.org/无脱敏）；封面图 200；live articles.json=190；sitemap 309 loc；双索引卡 HIT",
    "defects_found": ["najie/blog/customs-ip-filing-3-things-20261016.html: h1=0, 无 og:image, 无 og:site_name, 无 keywords, 无 twitter:title/description, description 复读标题, 缺 BreadcrumbList, 3 个小标题仍为 <p>（处 articles.json 首页 slice(0,6) 第 1 曝光位）",
                      "articles.json: 上游复活 50 条无页面条目（190→240）"],
    "notes": "本页由上游 publish 提交 e1f745f/58bf10f 直落 najie/blog/，site-inbox 同步副本与已发布页字节相同 → 无待同步内容，按已接管删除（零信息损失）。封面图命名用日期前缀变体 cover-20261016-customs-...（与文章 slug 顺序相反），修复脚本已加候选回退。正文剥离标签后逐字相等（h1 位除外）。sitemap 看门测试 exit 0、309 loc 不变（无回灌）。",
    "result": "success"
}
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("deploy-log 条目 =", len(log["deploys"]))

# 日报
rep = os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-%s.md" % DATE.replace("-", ""))
os.makedirs(os.path.dirname(rep), exist_ok=True)
body = """# SiteOps 每日运营日报 — %s

## ✅ 核心页面健康（8/8 = 200）
`/` `/mili/` `/najie/` `/blog/` `/sitemap.xml` `/llms.txt` `/en/` `/fr/`

## ✅ 修复：今日新页「部分裸发布」（第 6 例）
`najie/blog/customs-ip-filing-3-things-20261016.html` — 海关知产备案文（ART-2026-0108）
- 缺陷：h1=0 / 无 og:image / 无 og:site_name / 无 keywords / 无 twitter:title+description / description 复读标题 / 缺 BreadcrumbList JSON-LD / 3 个小标题仍是 `<p>`
- 修复：补 h1 + 3 个 h2 路标 + BreadcrumbList + og:image（封面图入库）+ og:site_name + keywords + twitter 卡 + 真摘要 91 字；6,286 → 7,895 B（线上 8,262 B 含 CF beacon）
- 断言：**正文剥离标签后逐字相等**（仅新增 h1 位）；2 个 ld+json 块 `json.loads` 全通；div 配平
- 位置：该页正处 `articles.json` 首页 `slice(0,6)` **第 1 曝光位**（第 6 例「最高曝光位 + 缺陷页」并发）

## ✅ 内容同步
- 近 4 日 3 篇文章（ART-2026-0106/0107/0108）在主索引与各自品牌索引 **全部 HIT**，无缺口、无需补卡
- `site-inbox/customs-ip-filing-3-things-20261016.html` 为上游发布副本，与已发布页字节相同 → 按「已接管」删除（零信息损失）

## ✅ articles.json 守卫（第 17 次隔离）
- 240 条 → 上游复活 50 条无页面条目 → 隔离至 `articles-quarantine-20261016.json` → 写回 **190 条**
- 首页 slice(0,6) 6 条**全部有页面**（曝光位安全）

## ✅ sitemap 看门测试
- `sitemap-auto.sh` exit 0，309 loc 不变（无回灌）；今日新页 loc 已由上游自动纳入

## ✅ 线上终验（FAILS = NONE）
核心 8 页 200 / 精修页 11 项判据全 PASS / 封面图 200 / live articles.json=190 / 双索引卡 HIT

## ⚠️ 观察
- 「部分裸发布」已连续多日出现（09-21/22/24/25、10-06×7、10-10、10-13、10-15、10-16），**根治位仍在上游发布流水线**：文章页生成器不写 h1、不写 og:image/keywords/twitter、description 直接复制标题、小标题不转 h2。本机只能每日拦截修复。
""" % DATE
with open(rep, "w", encoding="utf-8") as f:
    f.write(body)
print("report:", rep)
