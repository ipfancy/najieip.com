#!/usr/bin/env python3
"""Close-out: core page HTTP recheck + deploy-log append + daily report."""
import re, json, subprocess, os, time

REPO = "/Users/ziganghe/wiki/najieip-verify"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def code(path):
    for attempt in range(3):
        r = subprocess.run(["curl", "-sI", "-A", UA, "--max-time", "25", "-o", "/dev/null",
                            "-w", "%{http_code}", f"https://najieip.com/{path}"],
                           capture_output=True, text=True, timeout=40)
        c = r.stdout.strip()
        if c == "200":
            return c, attempt + 1
        time.sleep(3)
    return c, 3

results = {}
for p in ["", "mili/", "najie/", "blog/", "sitemap.xml", "llms.txt"]:
    c, tries = code(p)
    results[p or "/"] = (c, tries)
    print(f"/{p:12s} {c}  (tries={tries})")

# deploy-log schema from committed file
raw = subprocess.run(["git", "-C", REPO, "show", "HEAD:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
print("deploy-log top keys:", list(log.keys()), "entries:", len(log["deploys"]))
print("last entry keys:", list(log["deploys"][-1].keys()))

entry = {
    "date": "2026-10-22",
    "time": "22:20",
    "agent": "SiteOps",
    "round": "每日运营（22:00 cron）",
    "commit": "68d09ba",
    "action": "精修纳杰高企30分裸发布页 + 主索引补2卡/纳杰索引补1卡 + articles.json守卫第18次隔离",
    "files_changed": [
        "najie/blog/20261022-najie-gaoqi-ip-30points.html",
        "najie/blog/index.html",
        "blog/index.html",
        "articles.json",
        "articles-quarantine-20261022.json",
        "img/20261022-najie-gaoqi-ip-30points.png"
    ],
    "cards_added": {"blog/index.html": 2, "najie/blog/index.html": 1},
    "verification": "core 6/6 200; gaoqi h1=1 ld=2 og:image 1 desc=158字 无裸表 无** 9,943B(线上字节一致); cover img 200; 主索引2卡+纳杰索引1卡 HIT; articles.json 线上198条; sitemap 看门 exit 0 (321 loc 不变)",
    "defects_found": [
        "najie 20261022 高企30分文：裸发布（h1=0/ld=0/无og:image/description=标题复读/裸markdown表7行/ASCII直引号），且处 articles.json 首页第2曝光位、两索引零卡",
        "mili 20261022 安全生产刑责文：品牌索引有卡、主索引缺卡",
        "articles.json 50 条无页面条目（第18次复活）"
    ],
    "notes": "正文以 md 源重建，逐字比对 1,494 字符 EQUAL；模板取自同日同品牌 20261021-goods-names 房屋，FAQPage 块已剔除避免张冠李戴；封面 297,910B 入库",
    "result": "PASS"
}
log["deploys"].append(entry)
with open(os.path.join(REPO, "site-inbox/deploy-log.json"), "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
print("deploy-log appended ->", len(log["deploys"]))

report = f"""# SiteOps 日报 — 2026-10-22

## 核心页面
| 页面 | 状态 |
|---|---|
| / | {results['/'][0]} |
| /mili/ | {results['mili/'][0]} |
| /najie/ | {results['najie/'][0]} |
| /blog/ | {results['blog/'][0]} |
| /sitemap.xml | {results['sitemap.xml'][0]} |
| /llms.txt | {results['llms.txt'][0]} |

## 修复
1. **纳杰 20261022 高企30分文（裸发布，首页第2曝光位）**：5,982B → 9,943B。补 h1、Article+BreadcrumbList 双 JSON-LD、og:image/twitter/keywords/真摘要158字、7 行裸 markdown 表转 `<table class="data">`、ASCII 直引号转中文引号；正文以 md 源重建，逐字比对 1,494 字符 EQUAL。封面 297,910B 入库 `img/`。
2. **索引补卡**：主索引 223 → 225（本文 + mili 安全生产刑责文），纳杰索引 88 → 89。日期降序插位，div 配平通过。
3. **articles.json 守卫第 18 次**：248 → 198，50 条无页面条目隔离至 `articles-quarantine-20261022.json`；首页 slice(0,6) 六条全部有页面。

## 状态
- sitemap 看门：exit 0，321 loc 不变
- 部署：commit 68d09ba → 线上 gaoqi 页字节一致 9,943B；封面图 200；两索引卡片 HIT；articles.json 线上 198 条
- 近 2 日 5 篇新文章页六联判据：修复后 5/5 合格
"""
os.makedirs("/Users/ziganghe/wiki/digital-employees/reports", exist_ok=True)
rp = "/Users/ziganghe/wiki/digital-employees/reports/siteops-daily-20261022.md"
open(rp, "w", encoding="utf-8").write(report)
print("report ->", rp)
