#!/usr/bin/env python3
# log 1020: deploy-log append (indent=1, based on origin/main) + daily report
import os, json, subprocess, datetime

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"], capture_output=True, text=True).stdout
log = json.loads(raw)
n0 = len(log["deploys"])

# check 10-17 article card
prev = "customs-ip-post-filing-steps-20261017"
cards = {p: open(p, encoding="utf-8").read().count(prev)
         for p in ["blog/index.html", "mili/blog/index.html"]}
print("10-17 cards:", cards)

entry = {
    "date": "2026-10-20",
    "time": "10:05",
    "agent": "SiteOps",
    "round": "每日运营（10-20 白天）",
    "commit": commit,
    "action": "核心6页200；精修 10-18 海关扣留时限页（第8例「部分裸发布」，处 articles.json 首页第1曝光位）：补 h1 + Article/BreadcrumbList JSON-LD（deepcopy 模板覆写）+ og:image/og:site_name/keywords/twitter 三件 + 真摘要184字 + 文本节点直引号转中文引号，5,830→9,756B（正文逐字不变）；封面图入库 img/；双索引已有卡（主索引+觅理索引），sitemap 已含 1 条；articles.json 第19次隔离 242→192",
    "files_changed": ["mili/blog/customs-ip-detention-30-day-timeline-20261018.html",
                      "img/customs-ip-detention-30-day-timeline-20261018.png",
                      "articles.json", "articles-quarantine-20261020.json",
                      "site-inbox/diag-1020.py", "site-inbox/fix-1020-page.py",
                      "site-inbox/live-1020.py", "site-inbox/log-1020.py"],
    "cards_added": {"blog/index.html": 0, "mili/blog/index.html": 0,
                    "note": "双索引上游已补卡（004cf8b），本轮核验 HIT，无需补卡"},
    "verification": {
        "core_pages_200": "6/6",
        "page_live_bytes": 9756,
        "h1": 1, "ld_json": 2, "og_image": 1, "desc_len": 184, "stars": 0,
        "ld_json_parse": "2/2 OK",
        "body_text_unchanged": True,
        "cover_http": 200,
        "live_articles_json": 192,
        "sitemap_loc": 313,
        "sitemap_watchdog": "exit 0（静默，无回灌）",
        "live_assertions": "15/15 PASS"
    },
    "defects_found": [
        "上游 10-18 发布页缺 h1 / JSON-LD / og:image / og:site_name / keywords / twitter 标题图像，description 复读标题（第8例「部分裸发布」）",
        "上游 6cd0888 提交把 articles.json 隔离条目整体复活 300 行（第19次）"
    ],
    "notes": "10-19 与 10-20 上游无新文章（最新 ART-2026-0110 / 10-18）；10-17 页卡片核验 HIT；今日非周六，GEO 追踪按计划不执行",
    "result": "PASS"
}
log["deploys"] = [d for d in log["deploys"] if not (d.get("date") == "2026-10-20" and d.get("agent") == "SiteOps")]
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("deploy-log:", n0, "->", len(log["deploys"]))

report = f"""# SiteOps 日报 — 2026-10-20

## 结论
✅ 核心 6 页全部 200；修 1 篇上游「部分裸发布」页面（首页第 1 曝光位）；articles.json 第 19 次隔离。

## 明细
- ✅ HTTP：`/` `/mili/` `/najie/` `/blog/` `/sitemap.xml` `/llms.txt` = 6/6 **200**（无瞬断）
- ⚠️ 页面质量：10-18《货被海关扣了，20天还是50天？3天内定生死》属第 8 例「部分裸发布」——有样式与 4 个 h2，但 h1=0、JSON-LD=0、无 og:image/og:site_name/keywords/twitter、description 复读标题；且处 articles.json 首页 slice(0,6) **第 1 位**。→ 已精修：补 h1 + Article/BreadcrumbList JSON-LD + og/twitter 三件 + 真摘要 184 字 + 直引号转中文引号，5,830 → **9,756 B**，正文归一后**逐字不变**，2 块 JSON-LD 全部 `json.loads` 通过，div 配平 0
- ✅ 封面图：`cover-20261018-customs-ip-detention-30-day-timeline.png` → `img/customs-ip-detention-30-day-timeline-20261018.png`（295,694 B），线上 200
- ✅ 索引：主索引卡片 1 处、觅理索引 2 处（卡片 + BlogPosting）；上游 004cf8b 已补卡，本轮核验 HIT、**无需补卡**
- ✅ sitemap：已含该 URL，共 **313** loc；看门测试 `sitemap-auto.sh` exit 0 静默（无回灌）
- ⚠️ articles.json：上游 6cd0888 复活 50 条无页面条目（+300 行）→ 第 **19** 次隔离，242 → **192**，隔离档 `articles-quarantine-20261020.json`；线上 live 已收敛 192，首页第 1 位为本期文章
- ⚠️ 近 2 日内容：10-19 / 10-20 上游**无新文章**（最新 ART-2026-0110，2026-10-18）；10-17 页卡片核验 HIT
- ➖ GEO：今日周二，按计划不跑（周六 02:00 任务）

## 线上终验
15/15 PASS（h1 / ld≥2 / og:image / og:site_name / twitter / keywords / desc>80 / 无 `**` / ld 解析 ×2 / 封面 200 / live articles.json 192 / rank1 / 双索引 HIT）

## 待办
- 上游发布流水线仍在产出「部分裸发布」页并每日复活 articles.json 隔离条目 → 需在生成器侧修（h1/JSON-LD/og 与 articles.json 落地校验）
"""
os.makedirs(os.path.expanduser("~/wiki/digital-employees/reports"), exist_ok=True)
open(os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-20261020.md"), "w", encoding="utf-8").write(report)
print("report written")
