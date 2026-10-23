#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 deploy-log.json（先读 origin 版本确认现行 schema 与 indent）"""
import json, subprocess, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = subprocess.run(["git", "-C", REPO, "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
print("entries:", len(log["deploys"]), "keys:", list(log["deploys"][-1].keys()))
print("indent probe: first line ->", raw.split("\n")[1][:40])

entry = {
    "date": "2026-10-24",
    "time": "02:00-03:10",
    "agent": "SiteOps（第43周 GEO 追踪 + 多语言同步）",
    "round": "weekly-geo-i18n",
    "commit": "2922a16",
    "action": "第43周 GEO 双平台 18 检查点 + ART-2026-0103 腾冲燃气案 EN/FR 发布",
    "files_changed": [
        "en/blog/20261006-mili-gas-post-judgment-six-checklist-en.html (new, 15,909B)",
        "fr/blog/20261006-mili-gas-post-judgment-six-checklist-fr.html (new, 18,221B)",
        "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html (hreflang x4 + og:image 自托管 + twitter:image, 12,711→13,197B)",
        "img/20261006-mili-gas-post-judgment-six-checklist.png (new, 287,505B)",
        "en/blog/index.html (card 21→22)",
        "fr/blog/index.html (card 21→22)",
        "sitemap.xml (323→325 loc)",
    ],
    "cards_added": {"en_blog_index": 1, "fr_blog_index": 1, "main_blog_index": 0},
    "verification": "本地 38 项 + 线上 31 项断言全部 PASS（FAILURES=0）；线上 zh/en/fr/两索引/封面/sitemap/root/mili/blog 共 10 个 URL 全 200；sitemap 325 loc 无重复、lastmod 100%",
    "defects_found": [
        "中文权威页原本无 hreflang（四值全缺）、og:image 用 Pexels 外链 → 本轮一并升级为自托管封面",
        "FR 页 meta 栏目名首版沿用英文 'Antitrust & Public Utilities' → 已改 'Concurrence & services publics'",
    ],
    "notes": "GEO：秘塔 9/9 全通（连续第2周零登录墙，验证 IP 池轮换结论）+ 元宝 9/9，18 检查点 0 命中，累计 196、连续第11个有效周期 0%。★关键变化：(2025)最高法知民终950号腾冲案在秘塔首度被检索到（上周零收录），但 5 条来源全为官方案例摘要/最高法典型案例、0 署名 → 结论升级为「读到了、答对了，引用位归官方」，不是「读不到」。元宝仍只答他案(2023)最高法知民终1547号 → 平台分化稳定。元宝「整改台账字段清单」比 0103 正文框架更细 → 已列为补稿清单。周报 siteops: ~/wiki/digital-employees/reports/geo-weekly-20261024.md + siteops-i18n-20261024.md；DB geo_checks +18 行、3 篇文章 stats 各 total=12。",
    "result": "PASS",
}
log["deploys"].append(entry)
with open(P, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("appended ->", len(log["deploys"]), "entries")
d = subprocess.run(["diff", "-u", "/dev/stdin", P], input=raw, capture_output=True, text=True)
print("diff added lines:", sum(1 for l in d.stdout.split("\n") if l.startswith("+") and not l.startswith("+++")))
print("diff removed lines:", sum(1 for l in d.stdout.split("\n") if l.startswith("-") and not l.startswith("---")))
