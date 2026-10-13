#!/usr/bin/env python3
"""追加 1013 部署日志条目 — 以 origin/main 版本为底，indent=1，只 +N 行。"""
import os, json, subprocess, sys

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


raw = sh("git show origin/main:site-inbox/deploy-log.json")
log = json.loads(raw)
assert isinstance(log, dict) and isinstance(log.get("deploys"), list), "deploy-log 顶层必须是 {deploys:[...]}"

entry = {
    "date": "2026-10-13",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（第42周·周一）",
    "commit": "(本次提交)",
    "action": "核心 6 页 HTTP 验证 + 精修 1 篇部分裸发布页（mili 10-10 AIGC 商业秘密文，处 articles.json 首页第 1 曝光位）+ 索引缺口扫描 + articles.json 守卫 + sitemap 看门测试",
    "files_changed": [
        "mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html",
        "site-inbox/fix-1013-page.py",
        "site-inbox/diag-1013.py",
        "site-inbox/gather-1013.py",
    ],
    "cards_added": 0,
    "verification": "核心 6 页 200（首页首轮 000 = 瞬断，重试 200）；修复页 8,045→12,201B，h1=1 / ld+json=2 / og:image=1 / **=0 / 裸表=0，body 文本归一后逐字相等；两索引 0 重复 href、0 ** 泄漏、div 深度归零；articles.json 守卫 184/184 零违例、首页 top6 全部有页面；索引缺口（href 归一）真缺口 0；sitemap 304 loc 且无缺失 lastmod",
    "defects_found": "mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html 属「部分裸发布」档：有 h1 与外链 style.css，但缺 JSON-LD / og:image / og:site_name / keywords / twitter:title，description 复读标题；且正处 articles.json 首页 slice(0,6) 第 1 位（曝光最高位）",
    "notes": "brand index 页 h1=0 属站点规范（blog/mili/najie/en/fr 五个索引一致），勿按缺陷处理；近 6 日窗口其他页面六联全过；无新文章需补卡（content.db 最新 ART-2026-0105 / 10-09）",
    "result": "PASS",
}
log["deploys"].append(entry)

with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
    f.write("\n")

n = json.loads(open("site-inbox/deploy-log.json", encoding="utf-8").read())
print(f"deploys 条数 = {len(n['deploys'])} (原 {len(json.loads(raw)['deploys'])})")
print("diff 行数:", sh("git diff --numstat site-inbox/deploy-log.json").strip())
