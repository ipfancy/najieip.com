import os, json, subprocess, datetime
SITE = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(SITE, "site-inbox/deploy-log.json")
log = json.load(open(LOG, encoding="utf-8"))
commit = subprocess.check_output(["git", "-C", SITE, "rev-parse", "--short", "HEAD"]).decode().strip()
entry = {
    "date": "2026-10-20",
    "time": datetime.datetime.now().strftime("%H:%M"),
    "agent": "SiteOps",
    "round": "夜间补齐已发布缺页文章（content.db 已发布 vs 站点无页面）",
    "commit": commit,
    "action": "为 10-20《加班费年假争议…法释26号第42条》与 10-19《11月1日起保外就医门槛变了》两篇生成房屋样式页面（h1 + Article/BreadcrumbList JSON-LD + og/twitter + 真摘要 + 封面入库）+ mili/主索引补卡 + articles.json 条目 + sitemap 纳入",
    "files_changed": [
        "mili/blog/20261020-mili-overtime-leave-evidence.html",
        "mili/blog/20261019-mili-community-correction-medical-standard.html",
        "img/20261020-mili-overtime-leave-evidence.png",
        "img/20261019-mili-community-correction-medical-standard.png",
        "mili/blog/index.html", "blog/index.html", "articles.json", "sitemap.xml",
    ],
    "cards_added": {"mili/blog/index.html": "120->122", "blog/index.html": "218->220"},
    "verification": "核心6页200；两页 live 200（含封面图）；live h1=1/ld=2/og:image/**=0/JSON-LD 全部 json.loads 通过；双索引 live HIT；sitemap live 315 loc（313->315）",
    "defects_found": "上游发布仅写 .published.json 与 md，未落站点页面（10-20 10:04、10-19 10:06 两次发布均无 HTML）；另 10-19 文未登记 content.db articles 表",
    "notes": "生成器 site-inbox/gen-1020-missing-pages.py；正文与 md 源逐段比对（表格行按 <table> 渲染，非文本差异）；articles.json 守卫 194/194 零违例",
    "result": "PASS",
}
log["deploys"].append(entry)
json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("deploy-log entries:", len(log["deploys"]))

report = """# SiteOps 日报 — 2026-10-20（夜）

## 站点状态
- 核心 6 页：`/`、`/mili/`、`/najie/`、`/blog/`、`/sitemap.xml`、`/llms.txt` 全部 **200**（零瞬断）

## 今日主要动作：补齐「已发布但站点无页」2 篇
| 文章 | 日期 | 状态 |
|------|:----:|------|
| 加班费年假争议，企业拿不出记录就输：法释26号第42条 | 2026-10-20 | 新建页面 7,697B |
| 11月1日起，保外就医的门槛变了：2014年的老标准作废 | 2026-10-19 | 新建页面 10,862B |

- 房屋六件齐备：`<h1>`=1 / JSON-LD=2（Article + BreadcrumbList）/ og:image + twitter 卡 / 真摘要（150、144 字，非标题复读）/ `**`=0 / 裸表 0（社区矫正文 1 张表已渲染成 `<table>`）
- 封面图入库：`img/<slug>.png`（292KB / 318KB），线上 200
- 双索引补卡：mili 120→122、主索引 218→220，日期降序（顶部 10-20 → 10-19 → 10-18 …）
- articles.json：192→194 条，守卫 `--check` **194/194 零违例**，首页 slice(0,6) 全部有页面
- sitemap：313→315 loc（脚本自动纳入，线上 315）

## 发现的缺陷（上游）
- ⚠️ 两次发布（10-20 10:04、10-19 10:06）只写 `.published.json` 与 md，**未落站点 HTML 页面**——公众号发出去了，网站上是空的。本次由本流程补建。
- ⚠️ 10-19《保外就医》文**未登记 content.db `articles` 表**（表内仅 ART-2026-0111 有 10-20 记录），下游统计/管线对账会漏这一篇。

## 线上验证（全部通过）
- 2 篇页面 + 2 张封面：4/4 HTTP 200
- live 页面判据：h1=1 / ld=2 / og:image 有 / `**`=0 / JSON-LD 逐块 `json.loads` 通过
- 双索引与主索引：live HIT 2/2；sitemap live 315

## 待跟进
- 上游 `distribute_github` 步骤失败可疑（`.published.json` 有记录但站点无页），建议查 wechat-distribute 的 site 渠道返回；同一 run 内 10-19 文还漏登 content.db
"""
p = os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-20261020.md")
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p, "w", encoding="utf-8").write(report)
print("report:", p, len(report))
