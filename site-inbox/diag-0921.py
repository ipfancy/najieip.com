#!/usr/bin/env python3
# 0921 站点缺口诊断：品牌索引 vs 主索引（href 归一）+ 孤儿文章页 + sitemap/JSON-LD 覆盖
import os, re, json, glob
from urllib.parse import unquote
from collections import Counter

REPO = os.path.expanduser("~/wiki/najieip-verify")
MAIN = os.path.join(REPO, "blog/index.html")
BRANDS = {
    "mili": os.path.join(REPO, "mili/blog/index.html"),
    "najie": os.path.join(REPO, "najie/blog/index.html"),
    "aipunajie": os.path.join(REPO, "aipunajie/blog/index.html"),
}


def norm(href, brand):
    u = unquote(href.strip()).split("#")[0].split("?")[0]
    if u.startswith("http"):
        u = "/" + u.split("najieip.com/", 1)[-1] if "najieip.com/" in u else u
    elif u.startswith("./"):
        u = f"/{brand}/blog/" + u[2:]
    elif not u.startswith("/"):
        u = f"/{brand}/blog/" + u
    return u


main_t = open(MAIN, encoding="utf-8").read()
main_body = main_t[main_t.find("<body"):]
main_hrefs = {norm(h, "main") for h in re.findall(r'<h2><a href="([^"]+)"', main_body)}
print(f"主索引卡片 {main_body.count('<div class=\"article-card\"')}  唯一 href {len(main_hrefs)}")

brand_hrefs = {}
print("\n=== 缺口：品牌索引有、主索引无 ===")
gap_total = 0
for brand, path in BRANDS.items():
    t = open(path, encoding="utf-8").read()
    body = t[t.find("<body"):]
    hs = [norm(h, brand) for h in re.findall(r'<h2><a href="([^"]+)"', body)]
    uniq = sorted(set(hs))
    brand_hrefs[brand] = uniq
    miss = [u for u in uniq if u not in main_hrefs]
    gap_total += len(miss)
    print(f"[{brand}] 卡片 {body.count('<div class=\"article-card\"')} 唯一 {len(uniq)} 缺主索引 {len(miss)}")
    for u in miss:
        print("   MISS", u)
print("缺口合计:", gap_total)

# 孤儿文章页：文件存在但三个索引 + 主索引都没引用
print("\n=== 孤儿文章页（页面存在但无任何索引卡）===")
all_urls = set(main_hrefs)
for hs in brand_hrefs.values():
    all_urls |= set(hs)
orphans = []
for brand in ("mili", "najie", "aipunajie"):
    for f in sorted(glob.glob(os.path.join(REPO, brand, "blog/*.html"))):
        name = os.path.basename(f)
        if name == "index.html":
            continue
        url = f"/{brand}/blog/{name}"
        if url in all_urls:
            continue
        raw = open(f, encoding="utf-8", errors="ignore").read()
        size = os.path.getsize(f)
        stub = size < 1500 or 'http-equiv="refresh"' in raw or raw.count("<p") < 2
        orphans.append((brand, name, size, stub))
        print(f"   {'[STUB]' if stub else '[REAL]'} {url}  {size}B")

# 主 blog 目录下的孤儿
print("\n=== /blog/*.html 孤儿 ===")
for f in sorted(glob.glob(os.path.join(REPO, "blog/*.html"))):
    name = os.path.basename(f)
    if name == "index.html":
        continue
    url = f"/blog/{name}"
    if url not in main_hrefs and url not in all_urls:
        size = os.path.getsize(f)
        raw = open(f, encoding="utf-8", errors="ignore").read()
        stub = size < 1500 or 'http-equiv="refresh"' in raw
        print(f"   {'[STUB]' if stub else '[REAL]'} {url}  {size}B")

# sitemap 覆盖
print("\n=== sitemap 覆盖 ===")
sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>(.*?)</loc>", sm)
print("sitemap loc 总数:", len(locs))
for u in sorted(all_urls):
    if not u.endswith(".html"):
        continue
    if not any(l.endswith(u) or l == "https://najieip.com" + u for l in locs):
        print("   缺 loc:", u)

# articles.json 与本地文件比对
print("\n=== articles.json 本地文件存在性 ===")
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
missing = []
for a in aj:
    u = a.get("url") or a.get("link") or ""
    p = os.path.join(REPO, u.lstrip("/"))
    if not os.path.exists(p):
        missing.append((u, a.get("date"), a.get("title", "")[:28]))
print(f"条目 {len(aj)}  无本地文件 {len(missing)}")
for u, d, ti in missing:
    # 首页 top6 曝光位次
    order = [x for x in sorted(aj, key=lambda z: z.get("date", ""), reverse=True)]
    rank = [i for i, x in enumerate(order) if (x.get("url") or x.get("link")) == u]
    print(f"   {d} rank={rank[0]+1 if rank else '?'}  {u}  {ti}")
