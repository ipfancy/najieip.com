#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""log-0917-daily.py — 追加 09-17 日报 deploy-log 条目 + 写 sitemap 回灌根因 NOTE

deploy-log 结构：顶层 {"deploys":[...]}；格式 indent=1（单空格）。
规则：以 origin/main 版本为底 append，写回 indent=1，保证 diff 只有 +40 行左右。
"""
import json, os, subprocess

SITE = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(SITE, "site-inbox/deploy-log.json")
NOTE = os.path.join(SITE, "site-inbox/NOTE-20260917-sitemap-loop-rootcause.md")

ENTRY = {
    "date": "2026-09-17",
    "time": "22:2x",
    "agent": "SiteOps",
    "round": "daily-2200",
    "commit": "904d6be",
    "action": ("日常巡检 6/6 核心页 200；根治 sitemap 回灌死循环（摘除 151 条违规 loc：104 跳转壳 + 47 无页面）；"
               "修复 20260917-upc 文章可见缺陷并补 mili/主索引卡片"),
    "scope": ("① sitemap.xml 391 → 240 loc（唯一 240，XML 校验通过）；"
              "② ~/.hermes/scripts/update-sitemap.py 由 112 行未加固版同步为 155 行加固版（备份 .bak-20260917）；"
              "③ mili/blog/20260917-upc-injunction-counterattack.html：清 frontmatter 泄漏（<p>---</p>/ai_smell）、"
              "去免责声明星号、补 og:image + twitter:title/description + Article/BreadcrumbList JSON-LD；"
              "④ mili/blog/index.html 81→82 卡 + Blog JSON-LD blogPost 首插 1 条；blog/index.html 157→158 卡"),
    "reason": ("sitemap 回灌：cron 2ddb76c2dd9a「sitemap自动纳入守护(每6h)」调用的 "
               "~/.hermes/scripts/update-sitemap.py 是未加固副本（112 行），门丞 09-17 的加固只落在仓库副本 "
               "（155 行，c265124）→ 15:42/21:43 两次把 siteops 刚摘除的 151 条原样加回，形成 6h 一次的乒乓。 "
               "文章缺陷：db22bd2 发布流水线产出的 HTML 带 markdown frontmatter 残留，且未生成索引卡片。"),
    "date_source": "content.db articles ART-2026-0088 publish_date=2026-09-17；文章页 canonical + sitemap self-canonical",
    "skipped_stubs": "无（本轮未做全量补卡）",
    "verification": {
        "core_pages_200": ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"],
        "sitemap": "240 loc，全唯一；三条口径（跳转/别名/非200）全零",
        "loop_closed": "实跑 bash ~/.hermes/scripts/sitemap-auto.sh → exit 0 且 loc 未变（加固版拒绝回灌）",
        "article": "og:image=1 twitter:title=1 ld+json=2（Article/BreadcrumbList 均解析通过）'**'=0 schema.org=2",
        "indexes": "mili 82 卡 / 主索引 158 卡；div 深度归零；JSON-LD 1/1 解析通过",
        "live": "待 Cloudflare 刷新后 curl 复核（见日报）",
    },
    "seo": "najie-seocheck 例行巡检",
    "tools": ["curl", "sitemap-hygiene.py", "fix-0917-upc-article.py", "gen-0917-upc-cards.py",
              "update-sitemap.py(加固版同步至 cron 路径)"],
}

NOTE_TEXT = """# NOTE 2026-09-17 — sitemap「摘除→加回」乒乓根因：cron 跑的是未加固副本

**发现者**：SiteOps 22:00 日检（对 09-17 三次同题提交的复盘）
**症状**：`sitemap: 自动纳入新文章URL (已新增 N 条)` 与 siteops 的「摘除违规 loc」交替出现，
一天内 4 次（13:20 +47、15:42 +151、21:43 +151，siteops 各摘除一次），最后 HEAD 停在「已加回 151 条」。

## 根因（实测）

| 路径 | 行数 | 校验 | 谁在用 |
|------|:----:|------|--------|
| `~/wiki/najieip-verify/update-sitemap.py` | 155 | 有（文件存在/跳转壳/重复登记三条） | 人类/agent 手工调用 |
| `~/.hermes/scripts/update-sitemap.py` | 112 | **无任何校验** | **cron `2ddb76c2dd9a` → `~/.hermes/scripts/sitemap-auto.sh` 每 6h** |

09-17 的加固（c265124）只改了**仓库副本**，cron 实际执行的副本没动 → 每 6 小时把 siteops 刚摘掉的
跳转壳/无页面 loc 原样加回。**修复：已把加固版覆盖到 cron 路径（旧版备份 `.bak-20260917`），
并实跑 `bash ~/.hermes/scripts/sitemap-auto.sh` 验证 exit 0 且 loc 不变。**

## 口径（沿用 2026-09-16 三条全零）

跳转/别名 loc = 0；重复登记 loc = 0；非 200 loc = 0。当前 **391 → 240**，全唯一。

## 给下一轮巡检的口径

1. 见到 `sitemap: 自动纳入新文章URL (已新增 N 条)` 提交 → 先 diff 新增 loc 是否含跳转壳/无页面，
   若有 → 说明加固又被覆盖（检查是否有人从别处拷回旧脚本），**不要只做摘除，先修副本**。
2. 巡检收尾必跑 `bash ~/.hermes/scripts/sitemap-auto.sh`（应为静默 no-op）——这是防回灌的看门测试。
3. 仓库副本与 `~/.hermes/scripts/` 副本是**两套**，任何 sitemap 脚本改动必须双写。
"""


def main():
    out = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                         cwd=SITE, capture_output=True, text=True).stdout
    log = json.loads(out)
    assert isinstance(log, dict) and "deploys" in log, "deploy-log 结构异常"
    if any(e.get("commit") == ENTRY["commit"] for e in log["deploys"]):
        print("⏭ 该 commit 条目已存在，跳过")
    else:
        before = len(log["deploys"])
        log["deploys"].append(ENTRY)
        with open(LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
        print("✅ deploy-log: %d → %d 条（indent=1）" % (before, len(log["deploys"])))

    if os.path.exists(NOTE):
        print("⏭ NOTE 已存在")
    else:
        open(NOTE, "w", encoding="utf-8").write(NOTE_TEXT)
        print("✅ 已写 NOTE:", os.path.basename(NOTE))


if __name__ == "__main__":
    main()
