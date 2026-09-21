#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""log-0921-evening.py — 追加 deploy-log 条目（以远端版本为底，indent=1，只增不删）"""
import json
import os
import subprocess
import sys

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
P = "site-inbox/deploy-log.json"
APPLY = "--apply" in sys.argv

# 以 origin/main 版本为底（防并发巡检写入被覆盖）
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True)
base = raw.stdout if raw.returncode == 0 and raw.stdout.strip() else open(P, encoding="utf-8").read()
d = json.loads(base)
assert isinstance(d, dict) and isinstance(d.get("deploys"), list), "deploy-log 结构异常"
before = len(d["deploys"])

entry = {
    "date": "2026-09-21",
    "time": "22:05",
    "agent": "SiteOps（晚间运营）",
    "round": "每日运营 cron 4c121698279a",
    "commit": "（本次）",
    "action": "每日运营：核心 6 页 200 + 修复 09-21 美国商标制裁文畸形页 + 三索引补卡 + articles.json 守卫",
    "classification": "站点运营 / 内容同步 / 索引与数据源卫生",
    "scope": [
        "① 核心页面 6/6 = 200（首页 /mili/ /najie/ /blog/ /sitemap.xml /llms.txt）；sitemap 253 loc lastmod 100%；najie-seocheck 全通过",
        "② 修复 najie/blog/20260921-us-trademark-sanction-defense-window.html：上游裸发布（无 <style> 整页无样式、无 h1、无 JSON-LD、无 og:image/keywords、meta description 复读标题、残留合集/检索词注释行）→ 按同日同品牌房屋样式重建（CSS/导航/h1+4×h2/Article+BreadcrumbList/OG+Twitter/落款标准三行），正文 10 段与 md 源逐段比对 0 差异；该文在 articles.json 首页 slice(0,6) 第 3 位，原畸形页正处首页曝光位",
        "③ 索引补卡：najie 品牌索引 71→72（含 blogPost JSON-LD 69→70）；主索引 166→169（补本文 + 09-09 批次补发两篇 querren-buqinquan-zhisu-2026 / xin-shangbiaofa-2027，均按日期降序插位）",
        "④ articles.json 卫生守卫第 5 次隔离：上游自动发布再次整体复活 50 条无页面条目（192→142，隔离档 articles-quarantine-20260921.json），首页 top6 全有页面",
        "⑤ 终验独立脚本 verify-0921-structure.py：文章页 18 项 + najie 索引 6 项 + 主索引 11 项 全 PASS（div 深度归零 / depth=2 卡数=总数 / href 唯一 / 无 ** 泄漏）",
    ],
    "artifacts": [
        "site-inbox/fix-0921-siteops.py", "site-inbox/verify-0921-structure.py",
        "site-inbox/diag-0921.py", "articles-quarantine-20260921.json",
    ],
    "note": "cards: blog/index.html 169 / najie 72 / mili 87 / aipunajie 24；sitemap 253 loc",
}
d["deploys"].append(entry)
print("deploy-log: %d -> %d 条" % (before, len(d["deploys"])))
if APPLY:
    with open(P, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    json.load(open(P, encoding="utf-8"))
    print("WROTE", P)
else:
    print("(dry-run)")
