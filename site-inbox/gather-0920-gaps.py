#!/usr/bin/env python3
# href 归一化全量缺口比对：品牌索引 -> 主索引
import os, re, json, sys
from urllib.parse import unquote

REPO = os.path.expanduser("~/wiki/najieip-verify")
MAIN = os.path.join(REPO, "blog/index.html")
brands = {
    "mili": os.path.join(REPO, "mili/blog/index.html"),
    "najie": os.path.join(REPO, "najie/blog/index.html"),
    "aipunajie": os.path.join(REPO, "aipunajie/blog/index.html"),
}

main = open(MAIN, encoding="utf-8").read()


def norm(href, brand):
    u = unquote(href.strip())
    u = u.split("#")[0].split("?")[0]
    if u.startswith("http"):
        u = "/" + u.split("najieip.com/", 1)[-1] if "najieip.com/" in u else u
    if u.startswith("./"):
        u = f"/{brand}/blog/" + u[2:]
    elif not u.startswith("/"):
        u = f"/{brand}/blog/" + u
    return u


gaps = []
total = 0
for brand, path in brands.items():
    if not os.path.exists(path):
        print(f"!! {brand} index missing"); continue
    t = open(path, encoding="utf-8").read()
    body = t[t.find("<body"):]
    cards = re.findall(
        r'<div class="article-card">\s*<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>.*?'
        r'(?:<p>(.*?)</p>)?.*?(?:<span class="tag">[^<]*</span>)*\s*(\d{4}-\d{2}-\d{2})',
        body, re.S)
    seen = set()
    for href, title, desc, date in cards:
        n = norm(href, brand)
        if n in seen:
            continue
        seen.add(n)
        total += 1
        # 主索引是否含该 URL（容忍任意 href 形式）
        slug = n.rstrip("/").split("/")[-1]
        # 精确：主索引中是否有指向同一路径的 h2 链接
        main_hrefs = set()
        for mh in re.findall(r'<h2><a href="([^"]+)"', main[main.find("<body"):]):
            main_hrefs.add(norm(mh, "main"))
        if n not in main_hrefs:
            gaps.append({
                "brand": brand, "path": n, "slug": slug,
                "title": re.sub(r"<[^>]+>", "", title).strip(),
                "desc": re.sub(r"<[^>]+>", "", desc or "").strip(),
                "date": date,
            })

print(f"品牌索引卡片总数(去重)={total}  缺口={len(gaps)}")
for g in gaps:
    print(f"  [{g['brand']}] {g['date']}  {g['path']}")
    print(f"        #{g['title']}")
json.dump(gaps, open(os.path.join(REPO, "site-inbox/missing-cards-20260920.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("已写 site-inbox/missing-cards-20260920.json")
