#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0922 部署日志 entry —— 以 origin/main 版本为底 append，原生 indent=1"""
import os, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout.strip()
if not raw:
    raw = open("site-inbox/deploy-log.json", encoding="utf-8").read()
log = json.loads(raw)
assert isinstance(log, dict) and "deploys" in log, "结构异常：顶层必须是 {'deploys': [...]}"
print("现有条目:", len(log["deploys"]))

entry = {
    "date": "2026-09-22",
    "time": "22:0x CST",
    "type": "daily-operations",
    "commit": "8ed5f8d",
    "summary": "修复上游裸发布畸形页（美国商标三步自查）+ 双索引补卡 + articles.json 守卫第6次隔离",
    "changes": [
        "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html：裸发布页（无 h1/h2/JSON-LD/og:image，desc 复读标题，5878B）→ 按同日同品牌精修页房屋模板重建 11747B；正文与 md 源 13/13 段 0 差异；补 6 个 h2 路标 + Article/BreadcrumbList JSON-LD + og/twitter 全量 + meta description",
        "blog/index.html：170→171 卡（日期降序插位）",
        "najie/blog/index.html：72→73 卡，blogPost JSON-LD 70→71",
        "articles.json：194→144（守卫第 6 次隔离 50 条无页面条目；首页 slice(0,6) 全部有页面，含 rank1 本文）",
    ],
    "verification": {
        "core_pages_200": "首页/mili/najie/blog/sitemap/llms/najie-blog = 6+1/6+1 全 200",
        "article_page_bytes": "11747 B online == local",
        "brand_index_bytes": "72076 B online == local",
        "main_index_bytes": "108885 B online == local",
        "articles_json_bytes": "42023 B online == local（144 条，0 死链）",
        "sitemap": "255 loc / 255 lastmod（100%），含本文 URL",
        "structure_assertions": "2 索引 × 8 项全 PASS（卡数/div深度归零/depth2卡数/malformed/重复href/插位降序/JSON-LD可解析/'**'泄漏）",
        "seocheck": "核心 4 页 OG 0 issues；seocheck 报 3 个页面错误经 curl 重试全 200 = 网络瞬断误报",
        "sitemap_gate": "sitemap-auto.sh 看门测试：loc 255 不变（无回灌）",
    },
    "issues_found": [
        "上游自动发布第 N 次产生裸发布畸形页，且落位 articles.json 首页第 1 顺位（曝光最高位）——HTTP 200 + sitemap 有 = 不等于页面合格",
        "articles.json 违例条目第 6 次整体复活（09-17/09-20/09-21/09-22），隔离非一次性",
        "品牌索引与主索引仍可能漏卡（上游只写品牌索引或都不写）——每日必须做 href 归一缺口比对",
    ],
    "unresolved": [
        "根因在上游发布流水线（不校验页面是否落地 + 不写索引卡），本机只能把静默故障转成可检出",
        "GITHUB_TOKEN 全失效，Pages 部署挂起只能靠空提交触发",
    ],
}
log["deploys"].append(entry)

with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("写入后条目:", len(log["deploys"]))
r = subprocess.run(["git", "diff", "--stat", "site-inbox/deploy-log.json"], capture_output=True, text=True)
print(r.stdout.strip())
