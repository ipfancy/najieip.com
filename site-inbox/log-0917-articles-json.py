#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""log-0917-articles-json.py — deploy-log 追加第二条（articles.json 无页面条目隔离）"""
import json, os, subprocess

SITE = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(SITE, "site-inbox/deploy-log.json")

ENTRY = {
    "date": "2026-09-17",
    "time": "22:4x",
    "agent": "SiteOps",
    "round": "daily-2200",
    "commit": "8eb9155",
    "action": "articles.json 隔离 50 条「无页面」条目（181 → 131），消除首页 slice(0,6) 将渲染 404 卡片的顾客可见风险",
    "scope": ("① articles.json：剔除 47 条 {机构}/blog/ 从未建页（线上 47/47 = 404）+ 3 条 /site-inbox/ 工作区路径；"
              "diff 为纯删除（0 插入 / 300 删除，沿用原生 indent=2）；"
              "② 原始 50 条完整移入 articles-quarantine-20260917.json（含 _quarantine_reason），go/no-go 决定建规范页时可一键还原；"
              "③ 复核：线上 /articles.json = 131 条且本地逐条有文件，首页前 6 条全部为真实页面"),
    "reason": ("index.html 前端 fetch('/articles.json') 后 articles.slice(0, 6) 渲染首页最新 6 篇；"
               "按 date 降序，第一条无页面条目已在第 10 位 → 再上线 4 篇即进入首页卡片区 = 顾客可见死链。"
               "根因在生成方（db22bd2 的发布流水线把无页面/工作区路径写进数据源），已按 NOTE-20260917 推荐 A 执行数据侧隔离，"
               "生成方校验仍需上游修（否则每次运行会复活）。"),
    "date_source": "文件存在性实测 + 线上 curl 复核（门丞 NOTE-20260917-articles-json-bogus-entries.md 的 47/47=404 结论复现）",
    "skipped_stubs": "无",
    "verification": {
        "live_articles_json": "HTTP 200，131 条，本地无文件条目 = 0",
        "live_homepage": "HTTP 200；前端 top6 全部命中真实页面",
        "sitemap_guardian_after": "python3 ~/.hermes/scripts/update-sitemap.py --check → 待新增 0、跳过 0（131 条全部有效）",
        "revert_path": "articles-quarantine-20260917.json（50 条，含隔离原因）",
    },
    "seo": "sitemap 240 loc 不变（三条口径仍全零）",
    "tools": ["quarantine-0917-articles-json.py", "check-0917-homepage-exposure.py"],
}


def main():
    out = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                         cwd=SITE, capture_output=True, text=True).stdout
    log = json.loads(out)
    if any(e.get("commit") == ENTRY["commit"] for e in log["deploys"]):
        print("⏭ 已存在，跳过")
        return
    log["deploys"].append(ENTRY)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    print("✅ deploy-log: %d 条（+1，indent=1）" % len(log["deploys"]))


if __name__ == "__main__":
    main()
