#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""log-0918.py — deploy-log 追加 2 条 + 生成 siteops-daily-20260918.md"""
import json
import os
import subprocess
from datetime import datetime

SITE = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(SITE, "site-inbox/deploy-log.json")
REPORT = os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-20260918.md")

ENTRIES = [
    {
        "date": "2026-09-18",
        "time": "22:1x",
        "agent": "SiteOps",
        "round": "daily-2200",
        "commit": "b0a6ba2",
        "action": "修复 09-18 新文《游戏界面中国不给专利，欧盟7月1日起能注册》（欧盟外观设计三张表）四类缺陷，并补 najie 品牌索引 + 主索引卡片",
        "scope": ("① 文章页 najie/blog/20260918-eu-digital-design-three-tables.html：清 YAML frontmatter 泄漏（<p>---</p><p>ai_smell: 10.5</p>）；"
                  "删「合集」标记行；免责声明去 markdown * 号改 .disclaimer；"
                  "补 og:image + twitter:summary_large_image(title/desc/image)；"
                  "补 Article + BreadcrumbList JSON-LD（publisher=北京纳杰，inLanguage=zh-CN，keywords 取合集标签）；"
                  "meta/og:description 由「等于标题」富化为 3 句结论式摘要；"
                  "② najie/blog/index.html 首位插卡（66→67）+ blogPost 数组首插 BlogPosting；"
                  "③ blog/index.html 插卡（158→159），置于 09-19 卡之后以保持日期降序；"
                  "④ 顺手清 najie 索引遗留 markdown 泄漏：wipo-ai-ip-dialogue 卡片与 JSON-LD description 由抓取碎片（含原始 ** 与「← 首页」导航残渣）替换为文章页 meta description"),
        "reason": ("上游 Agent5-Outreach 06:46 上线该文时只写了文章页 + articles.json，未同步任何索引卡片；"
                   "且页面是 markdown 直转产物，带 frontmatter 泄漏与 markdown 残渣。"
                   "招牌动作「内容上线 ≠ 可被发现」：无卡片 = 站内零入口，无 JSON-LD = AI 抓不到结构化事实。"),
        "date_source": "文章页 h1 + 源 md frontmatter + content.db ART-2026-0089（publish_date 2026-09-18）",
        "skipped_stubs": "无（该页 5468B，非跳转壳）",
        "verification": {
            "live_article": "HTTP 200；schema.org×2 / og:image / twitter:image / canonical / ld+json×2 / Article 类型 全部就位；ai_smell=0，合集=0，md **=0",
            "live_najie_index": "HTTP 200，卡片命中 2 处（卡 href + BlogPosting url）",
            "live_main_index": "HTTP 200，卡片命中 1 处，位次 #2（09-19 卡之下）",
            "structure": "verify-0918-structure.py：depth=0、无栈空闭合、article-card@depth2 = 卡片总数、malformed=0、ld 全可解析",
            "revert_path": "git revert b0a6ba2",
        },
        "seo": "sitemap 241 loc 不变（该页 loc 已在 0cc3dfb 补录）",
        "tools": ["fix-0918-eu-design.py", "fix2-0918.py", "verify-0918-structure.py"],
    },
    {
        "date": "2026-09-18",
        "time": "22:2x",
        "agent": "SiteOps",
        "round": "daily-2200",
        "commit": "57967d3",
        "action": "articles.json 二次卫生隔离：50 条「无页面」条目被上游自动发布复活（182→132），并新增幂等守卫脚本",
        "scope": ("① articles.json：剔除 50 条（47 条 {机构}/blog/ 从未建页 + 3 条 /site-inbox/ 工作区路径），182 → 132；"
                  "沿用原生 indent=2，diff 为纯删除；"
                  "② 50 条完整移入 articles-quarantine-20260918.json（含 _quarantine_reason / _quarantined_at），可一键还原；"
                  "③ 新增 site-inbox/guard-0918-articles-json.py（--check / --apply 幂等）：文件存在性 + 品牌路径白名单双校验，"
                  "内置首页 slice(0,6) 曝光位次断言（top6 出现无页面条目即断）"),
        "reason": ("09-17 的隔离被 09-18 06:46 的上游自动发布 commit 5945206 整体复活（+300 行 / 0 删除，同一「更新: HH:MM」自动化），"
                   "属第 2 次乒乓。根因确认在上游发布流水线：只按 slug 拼规范址写数据源，不校验页面是否落地。"
                   "本次除再隔离外，把校验固化成可每日复跑的守卫脚本，将「静默复活」转为可检出状态。"),
        "date_source": "文件存在性实测 + 首页 slice(0,6) 位次计算",
        "skipped_stubs": "无",
        "verification": {
            "guard_check": "总 182 | 合格 132 | 违例 50（原因分布：文件不存在 50 / 路径不在白名单 3）",
            "homepage_exposure": "slice(0,6) 六条全部命中真实页面（09-19×1、09-18×2、09-17×2、09-16×1）→ 无顾客可见死链",
            "sitemap": "sitemap 241 loc、唯一 241、死链 loc = 0（隔离前后不变：刷新脚本本就只补 200 的规范页）",
            "sitemap_watchdog": "bash ~/.hermes/scripts/sitemap-auto.sh → exit 0 静默、loc 241 不变（09-17 双写加固仍有效，无回灌）",
            "revert_path": "articles-quarantine-20260918.json（50 条）",
        },
        "seo": "sitemap 241 loc 不变；三索引 306 卡口径延续 09-17 的「非 200 = 0」",
        "tools": ["guard-0918-articles-json.py"],
    },
]


def append_log():
    out = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                         cwd=SITE, capture_output=True, text=True).stdout
    log = json.loads(out)
    added = 0
    for e in ENTRIES:
        if any(x.get("commit") == e["commit"] for x in log["deploys"]):
            print("⏭ 已存在，跳过", e["commit"])
            continue
        log["deploys"].append(e)
        added += 1
    if added:
        with open(LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
    print("✅ deploy-log: %d 条（+%d，indent=1）" % (len(log["deploys"]), added))


REPORT_MD = """# SiteOps 日报 — 2026-09-18（每日 22:00 运营检查）

## 一句话
✅ 站点全绿；修复了当日新文《欧盟外观设计》的四类缺陷并补齐两处索引卡片；articles.json 的无页面条目第 2 次被上游复活，已再隔离并**固化成守卫脚本**。

## 1. 核心页面 HTTP 状态（全部 200）
| 页面 | 状态 |
|------|:----:|
| https://najieip.com | ✅ 200 |
| /mili/ | ✅ 200 |
| /najie/ | ✅ 200 |
| /blog/ | ✅ 200 |
| /sitemap.xml | ✅ 200 |
| /llms.txt | ✅ 200 |
| /robots.txt · /CNAME | ✅ 200 |

## 2. 近 2 天发布文章 × 索引覆盖（content.db 对比）
| article_id | 文章 | 主索引 | 品牌索引 | 结论 |
|-----------|------|:-----:|:-------:|------|
| ART-2026-0089 | 游戏界面中国不给专利，欧盟7月1日起能注册（09-18） | ❌→✅ | ❌→✅ | **本轮修复**（najie 卡 + 主索引卡） |
| ART-2026-0088 | 禁令突袭反被撤销：出海企业3招反打（09-17） | ✅ | ✅ mili | 已覆盖，无需动作 |
| ART-2026-0087 | 你的数据能换5000万吗？4步闭环（09-16） | ✅ | ✅ najie | 已覆盖 |
| ART-2026-0086 | 被判赔117万美元？跨境卖家3招反杀TRO（09-15） | ✅ | ✅ | 已覆盖 |
| ART-2026-0085 | 商标被举报别慌（09-13） | ✅ | ✅ | 已覆盖 |

## 3. 本轮修复明细（09-18 新文）
文章页级：清 YAML frontmatter 泄漏（`ai_smell: 10.5` 曾直接展示在正文首屏）／删「合集」标记行／免责声明去 markdown 星号／补 og:image + twitter 大图卡／补 Article + BreadcrumbList JSON-LD／description 由「等于标题」富化为 3 句结论式摘要。
索引级：najie 品牌索引 66→67 卡（首位）＋ blogPost 数组首插；主索引 158→159 卡（置于 09-19 卡之后，保持降序）。
顺手清：najie 索引 wipo 卡遗留 markdown 泄漏（卡片与 JSON-LD description 长期显示原始 `**` 与「← 首页」导航残渣）→ 换成文章页 meta description。

**线上终验**：文章页 200，schema.org×2 / og:image / twitter:image / canonical / ld+json×2 全就位，`ai_smell`=0、`合集`=0、md `**`=0；两索引卡片线上均命中；结构校验 depth=0、无栈空闭合、卡片全部 `.container` 直接子节点。

## 4. SEO / 部署
- najie-seocheck：**所有检查通过**（核心页 200 + JSON-LD 6/6 + sitemap 新鲜度 241 loc、博客 210 页）
- najie-ogcheck：4/4 通过，0 issues
- sitemap：241 loc、唯一 241、**死链 loc = 0**
- sitemap 看门测试：`bash ~/.hermes/scripts/sitemap-auto.sh` → **exit 0 静默、loc 不变**（09-17 的「cron 副本双写」加固仍有效，无回灌）

## 5. ⚠️ 需上游处理（非本机可根治）
1. **articles.json 无页面条目第 2 次复活**：09-18 06:46 上游自动发布 commit `5945206`（+300 行 / 0 删除）整体还原了 09-17 的隔离，属乒乓第 2 轮。根因在上游发布流水线：按 slug 拼规范址写数据源、**不校验页面是否落地**。本机已再隔离（182→132，可逆档 `articles-quarantine-20260918.json`）并新增幂等守卫 `guard-0918-articles-json.py`（文件存在性 + 品牌路径白名单 + 首页 top6 曝光断言），但**上游不修则该守卫需每日复跑**。
2. **主索引顶部有 date=2026-09-19 的卡片**（`20260918-personality-rights-injunction`，今日为 09-18）——疑上游日期口径把次日排期当天写死。本次未改动该卡（新卡已按其下方插入以保持降序），但若口径不改，新文将永远压在它下面。
3. **上游发布不补索引**：本日新文只落了文章页 + articles.json，两个索引都没有卡片（与 09-17 upc 同类）。建议上游发布脚本固定追加「索引卡片 + BlogPosting」步骤。

## 6. 本轮新增可复用工具
| 脚本 | 用途 |
|------|------|
| `site-inbox/fix-0918-eu-design.py` | 单篇文章精修（frontmatter/合集/星号清理 + og/twitter/JSON-LD + description 富化） |
| `site-inbox/fix2-0918.py` | 索引卡位次微调（保持日期降序）+ 历史 description 污染清理 |
| `site-inbox/verify-0918-structure.py` | 索引结构终验（depth/栈空/depth2 卡数/malformed/ld 解析/插位与日期前缀） |
| `site-inbox/guard-0918-articles-json.py` | articles.json 卫生守卫（`--check` / `--apply`，幂等，可每日复跑） |
"""


def write_report():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(REPORT_MD)
    print("✅ 日报写入", REPORT)


if __name__ == "__main__":
    append_log()
    write_report()
    print("now:", datetime.now().isoformat(timespec="seconds"))
