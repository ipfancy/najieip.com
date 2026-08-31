#!/usr/bin/env python3
"""更新 articles.json — 商标"用或死"文章 URL 指向精修版路径"""
import json

path = "/Users/ziganghe/wiki/najieip-verify/articles.json"
data = json.load(open(path, encoding="utf-8"))
print("total entries:", len(data))

for i, it in enumerate(data):
    u = it.get("url", "")
    if "use-or-die" in u or "trademark-law-use" in u:
        print("BEFORE", i, json.dumps(it, ensure_ascii=False)[:250])
        # 更新 /articles/ 版本 → /blog/ 精修版
        if u.startswith("/articles/trademark-law-use-or-die"):
            it["url"] = "/blog/trademark-law-use-or-die-countdown-20260831.html"
            print("UPDATED →", json.dumps(it, ensure_ascii=False)[:250])

# 补充 najie/blog 品牌条目（若无）
has_najie_blog = any(
    it.get("url", "") == "/najie/blog/trademark-law-use-or-die-countdown-20260831.html"
    for it in data
)
if not has_najie_blog:
    data.append({
        "url": "/najie/blog/trademark-law-use-or-die-countdown-20260831.html",
        "title": "倒计时4个月！4987万件商标迎来“用或死”大限",
        "date": "2026-08-31",
        "site": "najie",
    })
    print("ADDED najie/blog entry")

json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("saved, total:", len(data))
