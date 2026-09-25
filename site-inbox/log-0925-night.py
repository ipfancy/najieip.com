#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0925 夜检留档：deploy-log 追加（origin 版为底、indent=1）+ 日报追加夜间段"""
import json, os, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
LOG = f"{REPO}/site-inbox/deploy-log.json"

base = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                      cwd=REPO, capture_output=True, text=True, check=True).stdout
d = json.loads(base)
n0 = len(d["deploys"])
if any(e.get("commit", "").startswith("293b085") for e in d["deploys"]):
    print("SKIP: deploy-log 已有本条")
else:
    d["deploys"].append({
        "date": "2026-09-25",
        "time": "22:0x CST",
        "type": "nightly-ops (cron)",
        "commit": "293b085",
        "summary": "22:00 夜检：核心 6 页终态 200（sitemap.xml 首轮 000、robots.txt/najie//fr/ 首轮 0，全部重试 3/3 通 = 瞬断非故障）；articles.json 隔离定稿提交（206→156，守卫 156/156 零违例，首页 slice(0,6) 六条页面四件齐备）；缺口扫描 1 处候选经核为假缺口（najie/uspto-tbmp-2026-update.html 是跳转壳指向 mili 精修页，主索引已收 /mili/blog/ 路径）；近 6 天 21 个新增文章页房屋四件全 PASS（第 5 例裸发布未出现）；sitemap 267 loc 线上字节一致 + 看门测试 rc=0 静默。无新增修复项。",
        "changes": [
            "articles.json：隔离条目定稿提交（删 50 条无页面条目，206→156）",
            "articles-quarantine-20260925.json：隔离档留档（可逆）",
            "site-inbox/seocheck-report.json：常规刷新",
            "site-inbox/daily-0925-check.py：巡检脚本留档（卡片计数/缺口扫描/房屋四联判据）",
            "未改动：sitemap.xml（267 loc 不变）/ blog index / CNAME / DNS",
        ],
        "verify": {
            "core_pages": "6/6 终态 200（首轮 5/6 含 sitemap 000，重试 3/3 全 200；seocheck 另报 home/robots/najie//fr/ 4 处 0 亦全部重试 200）",
            "byte_compare": "article 2/2 IDENTICAL（11,574B / 10,420B）、blog/index 115,393B IDENTICAL、sitemap.xml cmp IDENTICAL（267 loc）",
            "index_cards": "main 183 / mili 97 / najie 76；09-25、09-24 两篇近 2 日 published 文章主索引与品牌索引卡片均在",
            "malformed_scan": "articles.json top6 + 近 6 天 21 个新增页：house(style||/style.css)、h1=1、ld>=1、og:image ✓ 全 PASS，bad=0",
            "articles_json_guard": "156 总 / 156 合格 / 0 违例（--check）",
            "sitemap_watchdog": "bash ~/.hermes/scripts/sitemap-auto.sh → exit 0、loc 267 不变（无回灌）",
        },
    })
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"OK deploy-log: {n0} -> {len(d['deploys'])}")

rp = f"{REPO}/../digital-employees/reports/siteops-daily-20260925.md"
night = """

---

# SiteOps 夜检补充 — 2026-09-25 22:00（cron）

> 触发：SiteOps 每日运营 cron（非高峰窗口）。结论：**无新增缺陷，零修复**。

## 一、状态

| 检查项 | 结果 |
|:--|:--|
| 核心 6 页 HTTP | ✅ 终态 6/6 = 200 |
| 近 2 日 published 文章在索引 | ✅ 2/2（09-25 mili 文、09-24 mili 文，主索引 + mili 索引卡片均在） |
| 品牌索引缺口扫描 | ✅ 1 处候选经核为**假缺口**（najie/uspto-tbmp-2026-update.html 529B 跳转壳 → 指向 /mili/blog/ 精修页，主索引已收 mili 路径） |
| 畸形页四联判据 | ✅ articles.json top6 + 近 6 天 21 个新增页全部 PASS（第 5 例裸发布未出现） |
| articles.json 守卫 | ✅ 156/156 零违例 |
| sitemap | ✅ 267 loc，线上 cmp 字节一致，看门测试 rc=0 |
| 线上/本地字节 | ✅ 文章 2/2 IDENTICAL、blog 索引 IDENTICAL |

## 二、瞬断误报（按行规重试后全部通过，非故障）

- `sitemap.xml` 首轮 **000**（10.7s 无响应）→ 重试 3/3 = 200（52,059B）
- `najie-seocheck` 另报 `https://najieip.com/`、`robots.txt`、`/najie/`、`/fr/` **首轮 0** → 逐个重试 3/3 = 200（`/najie/` 首试 17.0s 属慢响应）

## 三、本次动作

1. **articles.json 隔离定稿提交**（`293b085`）：13:38 交互式会话做的隔离一直悬在工作区未提交 → 本次提交（-300 行 / 206→156），守卫 `--check` 复核 **0 违例**，首页 `slice(0,6)` 六条均有落地页。
2. 隔离档 `articles-quarantine-20260925.json` 与巡检脚本 `site-inbox/daily-0925-check.py` 留档（可逆、可复跑）。
3. sitemap 看门测试通过（rc=0、loc 不变），确认 09-25 上午对 `update-sitemap.py` 的双数据源加固**未产生回灌**。

## 四、待跟进（不变）

| 项 | 说明 |
|:--|:--|
| GEO 抓取层（CF robots 屏蔽 GPTBot 等） | 第 17 日，待何律确认（唯一有引用胜算的赛道） |
| 裸发布畸形页上游根治 | 累计 4 例；需上游发布流水线补房屋模板 |
| articles.json 上游复活 | 守卫每日跑；上游写数据源不校验页面落地，属根治位 |
"""
with open(rp, "a", encoding="utf-8") as f:
    f.write(night)
print("OK report appended:", rp)
