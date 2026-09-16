#!/usr/bin/env python3
"""Append today's SiteOps entry to site-inbox/deploy-log.json, using origin/main as base.
Keeps indent=1 / ensure_ascii=False so the diff stays small (see skill: deploy-log 格式坑).
"""
import json, subprocess, os

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True, check=True).stdout
d = json.loads(raw)
assert isinstance(d, dict) and isinstance(d["deploys"], list), "unexpected deploy-log structure"
print("base entries:", len(d["deploys"]), "| last:", d["deploys"][-1].get("date"), d["deploys"][-1].get("round"))

entry = {
    "date": "2026-09-16",
    "time": "22:0x",
    "agent": "SiteOps",
    "round": "daily-2200",
    "commit": "pending",
    "action": "主 blog/index.html 补卡 48 张：主索引 vs 品牌索引逐 slug 比对后，把 najie/mili/aipunajie 三品牌全部已上线文章补回主索引（109 → 157 卡）",
    "scope": "含 09-16 新稿 4 篇（najie/20260916-data-asset-four-step、najie/ai-faming-zhuanli-keti-2026、mili/20260916-inventor-remuneration-907、mili/ai-shengcheng-neirong-qinquan-2026）+ 如己派单 09-17~09-19 觅理 3 篇 + 09-15 BACKLOG 未补的 37 张 + 其余历史漏卡",
    "reason": "主 blog/index.html 长期滞后于品牌索引（BACKLOG-0915-main-index-cards.md 记余 37 张）；今日巡检逐 slug 比对发现 54 张缺失，剔除 6 张跳转壳/无正文页后补 48 张",
    "date_source": "品牌索引内嵌 BlogPosting JSON-LD 的 datePublished（url→日期映射）；2 篇无 JSON-LD 日期者取 git 首次入库日 2026-07-31",
    "skipped_stubs": [
        "/najie/blog/cnptes-three-layer-architecture-diagram.html (无 <p> 正文，图页)",
        "/najie/blog/uspto-tbmp-2026-update.html (473B 跳转壳)",
        "/mili/blog/enterprise-ip-compliance-system.html (514B 跳转壳 → /najie/blog/)",
        "/aipunajie/blog/20260804-ic-layout-design-regulations.html (531B 跳转壳)",
        "/mili/blog/uspto-foreign-representation-rule.html (540B 孤儿壳，不在任何品牌索引)",
        "/aipunajie/blog/catl-patent-moat-profit.html (517B 孤儿壳，不在任何品牌索引)",
    ],
    "verification": "卡片 157=109+48；<div>/</div> 316/316 配平；depth 与基线一致 (1)、无「栈空仍闭合」；每卡以 <h2><a href= 起 malformed=0；href 无重复；带日期卡降序单调 2026-09-19→2026-07-08；'**'=0、'https://***'=0",
    "seo": "najie-seocheck 全通过（sitemap 347 URL / 博客 316 页 / lastmod 2026-09-16）；najie-ogcheck 核心 4 页 0 issue；线上 vs 本地 blog/index.html 字节一致（补卡前）",
    "tools": [
        "site-inbox/gen-0916-gather-missing.py",
        "site-inbox/gen-0916-index-cards-v4.py (--apply)",
        "site-inbox/verify-0916-index-structure.py",
        "site-inbox/audit-0916-index-coverage.py",
    ],
}
d["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("wrote entry; total entries:", len(d["deploys"]))
