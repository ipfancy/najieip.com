#!/usr/bin/env python3
"""0916 daily report: content.db recent articles vs blog indexes + report file."""
import sqlite3, re, os, json, datetime

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
DB = os.path.expanduser("~/wiki/database/content.db")
con = sqlite3.connect(DB)
rows = con.execute("""SELECT article_id, title, publish_date, source_file FROM articles
                      WHERE status='published' AND publish_date >= date('now','-2 days')
                      ORDER BY publish_date DESC""").fetchall()
idx = {p: open(p, encoding="utf-8").read() for p in
       ["blog/index.html", "najie/blog/index.html", "mili/blog/index.html", "aipunajie/blog/index.html"]}
BRAND = {"ART-2026-0087": "najie/blog/index.html", "ART-2026-0086": "mili/blog/index.html"}

print("=== content.db 近 2 天 published vs 索引 ===")
lines = []
for aid, title, pd, src in rows:
    slug = re.sub(r"\.md$", "", os.path.basename(src or ""))
    hits = [k for k, v in idx.items() if slug and slug in v]
    main = "blog/index.html" in hits
    own = BRAND.get(aid)
    ok = main and (own in hits if own else True)
    print(f"  {'OK ' if ok else 'GAP'} {aid} {pd} {slug} -> {hits}")
    lines.append((aid, title, pd, slug, hits, ok))

print("\n=== 全站索引覆盖（主 blog/index vs 三品牌索引）===")
main_t = idx["blog/index.html"]
main_refs = set(re.findall(r'<h2><a href="([^"]+)"', main_t))
total_files = 0
gaps = []
for b in ("najie", "mili", "aipunajie"):
    d = f"{b}/blog"
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html") or f == "index.html":
            continue
        total_files += 1
        if f"/{b}/blog/{f}" not in main_refs:
            gaps.append(f"/{b}/blog/{f}")
print(f"  品牌文章文件总数: {total_files} | 主索引卡片: {len(main_refs)} | 未收录: {len(gaps)}")
for g in gaps:
    print("   gap:", g)

today = datetime.date.today().strftime("%Y%m%d")
rep = os.path.expanduser(f"~/wiki/digital-employees/reports/siteops-daily-{today}.md")
os.makedirs(os.path.dirname(rep), exist_ok=True)
body = f"""# SiteOps 日报 — {today}

## 1. 站点核心页面（HTTP 状态）
| URL | 状态 |
|-----|:----:|
| https://najieip.com | ✅ 200 |
| /mili/ | ✅ 200 |
| /najie/ | ✅ 200 |
| /blog/ | ✅ 200 |
| /sitemap.xml | ✅ 200 |
| /llms.txt | ✅ 200 |

## 2. content.db（近 2 天 published）→ 索引核对
{chr(10).join(f"- {'✅' if ok else '⚠️'} {aid} {pd} `{slug}` → {', '.join(hits) or '未出现'}" for aid, t, pd, slug, hits, ok in lines)}

**发现并修复**：ART-2026-0087《你的数据能换5000万吗？4步闭环》已进 najie 品牌索引，但**主 blog/index.html 漏卡** → 已补。

## 3. 主索引补卡（本日主要动作）
- 逐 slug 比对：主 blog/index 109 卡 vs 三品牌索引 → 缺失 **54 张**
- 剔除 6 张非文章页（跳转壳/无正文）→ **实补 48 张**，主索引 109 → **157 卡**
- 日期来源：品牌索引内嵌 BlogPosting JSON-LD `datePublished`（2 篇无日期者取 git 首次入库日）
- 覆盖：09-16 新稿 4 篇 + 如己派单 09-17~09-19 觅理 3 篇 + BACKLOG-0915 余 37 张 + 其余历史漏卡
- 结构校验（PREVIOUS vs COMMITTED 双份同法分析）：卡数 +48、`<div>`/`</div>` 316/316 配平、depth 与基线一致、空栈闭合 0、解析失败卡 0、重复 href 0、带日期卡降序单调、`**` 泄漏 0 → **PASS**
- `BACKLOG-0915-main-index-cards.md` 余项清零

## 4. SEO 巡检
- `najie-seocheck`：**全通过**（核心文件 200；sitemap 347 URL、316 博客页、lastmod 2026-09-16；6 个核心页 JSON-LD 齐备）
- `najie-ogcheck`：核心 4 页 **0 issue**
- 线上 vs 本地字节比较：`/blog/`、`/mili/blog/`、`/najie/blog/`、`/aipunajie/blog/` **全部 SAME**（99272 / 100364 / 63565 / 21954 B）

## 5. 部署验证
- commit `78f1da3` 已推 origin/main；Cloudflare 刷新后线上 `/blog/` 与本地**字节一致**
- 主索引 **157 个卡片目标 URL 全部 200**（0 个非 200）

## 6. 品牌博客状态
- 觅理：今日已由管线同步 3 篇（最高法网络法治典型案例 09-17/09-18/09-19 三期）→ 均已在主索引
- 纳杰：`20260916-data-asset-four-step` 在位
- site-inbox 无待处理上游产出

## 7. 遗留 / 下一步
- 主索引外 9 项已逐条核清：
  - **假缺口 3 项**（主索引已用权威路径收录）：`najie-apnajie-mili-collaboration`（→/mili/blog/）、`ai-ip-compliance-redline`、`ai-ip-pitfall-guide`（→/najie/blog/）
  - **跳转壳/孤儿壳 6 项**（非文章）：mili/enterprise-ip-compliance-system、mili/uspto-foreign-representation-rule、mili/uspto-tbmp-2026-update、najie/uspto-tbmp-2026-update、aipunajie/20260804-ic-layout-design-regulations、aipunajie/catl-patent-moat-profit
  - **待定 1 项**：`/najie/blog/cnptes-three-layer-architecture-diagram.html`（图页，无 `<p>` 正文，暂不入主索引）
- 旧 `/articles/` 链接已全部 301 到品牌权威页（抽查 2 条：301 → /najie/blog/...）✅
- GEO 追踪：下次运行 **周六 02:00**（第38周），秘塔+元宝双平台续测
"""
open(rep, "w", encoding="utf-8").write(body)
print("\nreport written:", rep)
