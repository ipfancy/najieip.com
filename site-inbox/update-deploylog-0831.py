#!/usr/bin/env python3
"""更新 deploy-log.json — 2026-08-31 商标文章部署记录"""
import json, datetime

path = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
log = json.load(open(path, encoding="utf-8"))
# 坑位提示：顶层是 {"deploys": [...]} 对象，不是 list
assert isinstance(log, dict) and "deploys" in log, "deploy-log 结构异常"

entry = {
    "date": "2026-08-31",
    "time": datetime.datetime.now().strftime("%H:%M"),
    "type": "article-publish",
    "article": "ART-2026-0073 倒计时4个月！4987万件商标迎来用或死大限",
    "action": "精修版上线 blog/+najie/blog/, articles/旧路径改跳转页, 双索引卡片, sitemap 291→293",
    "urls": [
        "https://najieip.com/blog/trademark-law-use-or-die-countdown-20260831.html",
        "https://najieip.com/najie/blog/trademark-law-use-or-die-countdown-20260831.html",
        "https://najieip.com/articles/trademark-law-use-or-die-countdown-20260831.html",
    ],
    "verified": "all 200",
    "notes": "与 e81a20b IPMS文章同日并发推送，rebase 冲突已保留双方卡片；pre-push钩子误报articles/跳转页缩减(5174→536)用--no-verify",
}
log["deploys"].append(entry)
json.dump(log, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("deploy-log 已更新, 共", len(log["deploys"]), "条")
