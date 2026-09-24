#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 deploy-log 追加：取 origin 版本做底 + append，保持 indent=1"""
import os, re, json, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
APPLY = "--apply" in sys.argv
P = "site-inbox/deploy-log.json"

origin = subprocess.run(["git", "show", "origin/main:%s" % P], capture_output=True, text=True).stdout
log = json.loads(origin)
print("origin deploys:", len(log.get("deploys", [])))
print("末条:", json.dumps(log["deploys"][-1], ensure_ascii=False)[:300])

entry = {
    "date": "2026-09-24",
    "time": "22:0x CST",
    "type": "daily-operations",
    "commit": "本提交（siteops 0924 晚间）",
    "summary": ("每日运营：核心 8 页 200（含 EN/FR；fr 首轮 seocheck 报 0 = 网络瞬断，重试 3/3 全 200）；"
                "修复今日裸发布畸形页 mili/20260924-malicious-litigation-supervision（7716→10420B，正文与 md 源 30/30 段 0 差异）；"
                "mili 索引补卡 95→96（blogPost 87→88）+ 主索引补卡 181→182；articles.json 守卫 155/155 零违例；sitemap 266 loc 已含该文"),
    "changes": [
        "mili/blog/20260924-malicious-litigation-supervision.html：裸发布畸形页重建 —— 原页 h1=0/h2=0/JSON-LD=0/无 og:image+keywords/description 复读标题、正处 articles.json 首页 slice(0,6) 第 1 曝光位；按同日同品牌精修页（20260922-caichan-shouhu-07）房屋模板重建，补 6 个描述性 h2 路标 + Article/BreadcrumbList JSON-LD + og/twitter 全量 + keywords；正文段落与 md 源逐段比对 0 差异，不加一字",
        "mili/blog/index.html：新卡插首位（日期降序，09-24 > 首卡 09-22）+ blogPost JSON-LD 首插（87→88）",
        "blog/index.html：新卡插首位（09-24 > 首卡 09-23）181→182",
        "articles.json：守卫 --check 155/155 合格 0 违例（上游自动发布未复活被隔离条目）",
        "site-inbox/20260924-malicious-litigation-supervision.html：陈旧入站副本（含 frontmatter 泄漏）移出工作区至 scratch"
    ]
}
log["deploys"].append(entry)
out = json.dumps(log, ensure_ascii=False, indent=1)
print("\nnew deploy count:", len(log["deploys"]))
delta = out.count("\n") - origin.count("\n")
print("行数 delta:", delta)
if APPLY:
    with open(P, "w", encoding="utf-8") as f:
        f.write(out)
    print("已写入", P)
else:
    print("(--dry-run)")
