#!/usr/bin/env python3
"""1006 缺口全量分析：品牌索引 vs 主索引（href 归一）+ sitemap 覆盖"""
import re, os, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
BASE = "https://najieip.com"

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

main_idx = read(f"{REPO}/blog/index.html")
brands = {
    "mili": read(f"{REPO}/mili/blog/index.html"),
    "najie": read(f"{REPO}/najie/blog/index.html"),
}
sm = read(f"{REPO}/sitemap.xml")
locs = set(re.findall(r"<loc>(.*?)</loc>", sm))
print(f"sitemap loc 总数 = {len(locs)}")

# 品牌索引 href 归一
allbrand = {}
for b, t in brands.items():
    for h in re.findall(r'<h2><a href="([^"]+)"', t):
        if h.startswith("./"):
            full = f"/{b}/blog/" + h[2:]
        elif h.startswith("/"):
            full = h
        else:
            full = f"/{b}/blog/" + h
        allbrand[full] = b

main_hrefs = set()
for h in re.findall(r'<h2><a href="([^"]+)"', main_idx):
    main_hrefs.add(h if h.startswith("/") else "/" + h)

print(f"品牌索引归一 URL = {len(allbrand)} | 主索引 href = {len(main_hrefs)}")

# 真缺口：品牌有、主索引无，且页面存在、非跳转壳
gaps = []
for full, b in sorted(allbrand.items()):
    if full in main_hrefs:
        continue
    p = REPO + full
    if not os.path.exists(p):
        gaps.append((full, b, "FILE_MISSING"))
        continue
    size = os.path.getsize(p)
    t = read(p)
    if size < 1500 or 'http-equiv="refresh"' in t:
        continue  # 跳转壳/架构图，按口径剔除
    if "application/ld+json" not in t and "<h2" not in t:
        gaps.append((full, b, "NO_ARTICLE_MARKERS"))
        continue
    gaps.append((full, b, f"OK({size}B)"))

print("\n=== 品牌索引有、主索引无（真缺口） ===")
for g in gaps:
    print(f"  {g[2]:24s} {g[1]:6s} {g[0]}")

print("\n=== sitemap 覆盖检查（品牌索引 URL 是否在 sitemap） ===")
miss_sm = [f for f in allbrand if f not in locs]
for m in sorted(miss_sm):
    print(f"  MISSING-IN-SITEMAP {m}")

# 今日新文页面存在性与 sitemap
print("\n=== 今日新文 sitemap ===")
for slug in ["20261006-mili-gas-post-judgment-six-checklist",
             "20261005-mili-gas-supply-cutoff-justification",
             "20261005-patent-annual-fee-ledger-5-signals"]:
    hit = [l for l in locs if slug in l]
    print(f"  {slug}: {hit}")
