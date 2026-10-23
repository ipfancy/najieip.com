import json, os, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

# --- deploy log ---
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
entry = {
    "date": "2026-10-23",
    "time": "22:05",
    "agent": "SiteOps",
    "round": "每日运营巡检（22:00 cron）",
    "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True).stdout.strip(),
    "action": "每日巡检：解决 articles.json 遗留 stash 冲突（取 HEAD 全量 200 条，零丢条目，工作区由 UU 转干净）；修复今日 mili 酒店安全页缺 og:image/twitter:image/JSON-LD image，封面 282KB 入库 img/",
    "files_changed": [
        "articles.json",
        "mili/blog/20261023-mili-hotel-safety-obligation.html",
        "img/20261023-mili-hotel-safety-obligation.png",
        "site-inbox/diag-1023-night.py",
        "site-inbox/fix-1023-ogimage.py",
        "site-inbox/fix-1023-ldimage.py",
        "site-inbox/live-1023.py",
    ],
    "cards_added": 0,
    "attribution": "无新增卡片（三索引卡已由上游 83d2cb6/4b87f33 建好，本轮仅核验 HIT）",
    "verification": "核心 6 页 200；今日 4 页线上六项判据全 OK；封面图 200；线上 articles.json=200 条；4 个索引卡线上 HIT；sitemap 看门 exit 0（323 loc 不变）；articles.json 守卫 200/200 零违例、首页 top6 全部有页",
    "defects_found": "① articles.json 遗留 stash pop 冲突标记（UU，JSON 不可解析，会打断首页 fetch）② 今日 mili 页缺 og:image/twitter:image（社交卡片无图）③ 3GPP 页 stars=2 经核为专利号掩码 20088000****.4，属正文事实非缺陷",
    "notes": "六项判据含 h1/ld>=2/og:image/desc 复读/**/裸表；星号判据按 [0-9*]\\*\\{2,\\} 排除专利号掩码；og:image 用自托管封面 img/<slug>.png 并 curl 200 验证",
    "result": "PASS",
}
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("deploy-log entries:", len(log["deploys"]))

# --- daily report ---
rep = os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-20261023.md")
os.makedirs(os.path.dirname(rep), exist_ok=True)
text = """# SiteOps 日报 — 2026-10-23

## 结论：PASS（核心 6/6 200，线上终验 15/15，修复 2 项）

## 一、站点状态
- 核心 6 页全部 200：/ 、/mili/ 、/najie/ 、/blog/ 、/sitemap.xml 、/llms.txt
- sitemap 323 loc；看门测试 `sitemap-auto.sh` 静默 exit 0、loc 不变（无回灌）

## 二、修复项
1. **articles.json 遗留 stash 冲突（严重）**：工作区处于 `UU`，文件内含 `<<<<<<< Updated upstream / >>>>>>> Stashed changes` 冲突标记，JSON 不可解析 → 线上首页 `fetch('/articles.json')` 会整块失败。经比对，HEAD 版本为 superset（含 description/tags + 2 条额外文章），stash 版为裁剪副本 → 取 HEAD 全量 200 条，零丢条目，工作区转干净。
2. **今日 mili 页缺社交卡片图**：`20261023-mili-hotel-safety-obligation` 有 h1 / 双 JSON-LD / 外链样式，但缺 og:image、twitter:image、JSON-LD image 字段 → 封面 `cover-20261023-...png`（282KB，日期前缀变体）复制入库 `img/<slug>.png`，三处补齐，正文零改动（4 项断言全 PASS）。

## 三、核验项（无缺陷）
- content.db 近 2 日 published 2 篇：酒店安全文（10-23）、高企30分文（10-22）——均在品牌索引 + 主索引有卡，页面均存在
- `.published.json` 近 3 日 4 条发布记录：4/4 均有落地页（含 10-19 补发页），无「已发布但无页」缺口
- 近 3 日 git 触及 8 篇文章页：7 篇六项判据 OK；3GPP 页 `**` 计数 2 经核为专利号掩码 `20088000****.4`（正文事实，非 markdown 泄漏，按行规排除）
- 今日 4 页线上六项判据全 OK（h1=1 / ld=2 / og:image / twitter:image / stars=0 / 裸表=0）
- 索引卡：mili / najie / aipunajie 今日新文 + 主索引 全 HIT（零缺口、零补卡）
- articles.json 守卫：200/200 零违例，首页 slice(0,6) 全部有页面（无 404 曝光风险）

## 四、待办 / 提示
- `.published.json` 为 list 结构（`file/title/published_at/publish_id`，无 slug 字段），巡检脚本需从 `file` 反推 slug，勿按 dict 解析（本轮已修正口径）
- 仓库残留 3 个 stash（`autostash`、`sysop-20260913`、`WIP e43b790`），其中 autostash 已确认与 HEAD 无增量价值，可择机清理
- GEO 周追踪（周六 02:00）与多语言同步未在本轮范围

## 五、脚本
`site-inbox/diag-1023-night.py`、`fix-1023-ogimage.py`、`fix-1023-ldimage.py`、`live-1023.py`
"""
open(rep, "w", encoding="utf-8").write(text)
print("report:", rep, os.path.getsize(rep), "B")
