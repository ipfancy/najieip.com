#!/usr/bin/env python3
"""10-21 早检收尾：deploy-log 追加 + 日报"""
import json, os, subprocess, datetime

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
TODAY = "2026-10-21"

# deploy-log 以 origin/main 版本为底（indent=1）
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and isinstance(log["deploys"], list)
prev_keys = list(log["deploys"][-1].keys())
print("schema:", prev_keys)

entry = {
    "date": TODAY,
    "time": "06:20",
    "agent": "siteops",
    "round": "早检（每日运营）",
    "commit": None,
    "action": "核心6页HTTP验证 + 近3日3篇文章页六联判据 + 三品牌索引缺口扫描 + articles.json守卫 + sitemap看门",
    "files_changed": ["site-inbox/ops-1021-morning.py", "site-inbox/ops-1021-aipu-gap.py",
                      "site-inbox/deploy-log.json", "site-inbox/siteops-daily-20261021.md"],
    "cards_added": "mili 122 / najie 87 / aipunajie 18 / 主索引 220（均无新增，零缺口）",
    "verification": "核心6页 200；近3日页面六联 3/3 OK；真缺口 0（cnptes 架构图页按 09-23 口径排除）；articles.json 193/193 零违例；sitemap-auto.sh exit 0 且 315 loc 不变",
    "defects_found": "0 页面缺陷；无「已发布但站点无页」缺档",
    "notes": "content.db 最新 published=10-20（ART-2026-0111），对应页 mili/blog/20261020-mili-overtime-leave-evidence.html 已在双索引+主索引+articles.json 三处收录；.published.json 10-20 两条均已落地。",
    "result": "PASS"
}
# 字段序对齐既有 schema
entry = {k: entry.get(k, "") for k in prev_keys} if prev_keys else entry
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("deploys:", len(log["deploys"]))

report = f"""# SiteOps 日报 — {TODAY}

运行：06:07-06:25 CST（早检窗口）

## 结论
✅ 核心 6 页全部 200（/、/mili/、/najie/、/blog/、/sitemap.xml、/llms.txt），无瞬断。
✅ 近 3 日 3 篇文章页六联判据 3/3 通过（h1=1 / ld+json=2 / og:image / 描述非标题复读 / 无 ** / 无裸表）。
✅ 三品牌索引缺口扫描：mili 122、najie 87、aipunajie 18、主索引 220 卡 —— 真缺口 0。
   · 唯一命中 najie/blog/cnptes-three-layer-architecture-diagram.html 属架构图页（ld=0、无文章日期），按 09-23 口径不入主索引，非缺陷。
✅ articles.json 守卫：193/193 合格，违例 0；首页 slice(0,6) 六条全部有页面（无 404 曝光风险）。
✅ sitemap 看门：sitemap-auto.sh exit 0 静默无产出，315 loc 不变，无回灌。
✅ 「已发布但站点无页」核查：content.db 最新 published=10-20，.published.json 10-20 两条（加班费年假争议 / 保外就医门槛）均已落地为 mili 页面并在三处收录。

## 今日无新文
截至 06:07，今日（10-21）尚无新文章发布记录，故无补页/补卡动作。晚间若有新发布，按既有房屋流程接管。

## 待办提醒
· 第 43 周 GEO 追踪（周六 02:00）—— 上周 18 检查点 0 命中，秘塔需先试 1 条判断是否落墙。
· 全站 backlog：老页缺 JSON-LD 约 100+ 页（历史遗留），不批量改写，随页面改动时顺带补。
"""
open("site-inbox/siteops-daily-20261021.md", "w", encoding="utf-8").write(report)
print("report written")
