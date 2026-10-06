#!/usr/bin/env python3
"""1006 缺口分析 v2 — sitemap 比较修正 + 页面头部取证"""
import re, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
BASE = "https://najieip.com"

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

main_idx = read(f"{REPO}/blog/index.html")
brands = {"mili": read(f"{REPO}/mili/blog/index.html"),
          "najie": read(f"{REPO}/najie/blog/index.html")}
sm = read(f"{REPO}/sitemap.xml")
locs = set(re.findall(r"<loc>(.*?)</loc>", sm))
print(f"sitemap loc = {len(locs)}")

allbrand = {}
for b, t in brands.items():
    for h in re.findall(r'<h2><a href="([^"]+)"', t):
        full = (f"/{b}/blog/" + h[2:]) if h.startswith("./") else (h if h.startswith("/") else f"/{b}/blog/" + h)
        allbrand[full] = b

main_hrefs = set(h if h.startswith("/") else "/" + h
                 for h in re.findall(r'<h2><a href="([^"]+)"', main_idx))
print(f"品牌归一 = {len(allbrand)} | 主索引 = {len(main_hrefs)}")

gaps = []
for full, b in sorted(allbrand.items()):
    if full in main_hrefs:
        continue
    p = REPO + full
    if not os.path.exists(p):
        continue
    size = os.path.getsize(p)
    t = read(p)
    if size < 1500 or 'http-equiv="refresh"' in t:
        continue
    if "application/ld+json" not in t and "<h2" not in t:
        continue
    gaps.append((full, b, size))
print(f"\n=== 真缺口（品牌有 / 主索引无） 共 {len(gaps)} ===")
for full, b, size in gaps:
    print(f"  {b:6s} {size}B  {full}")

miss = sorted(f for f in allbrand if (BASE + f) not in locs)
print(f"\n=== 品牌 URL 不在 sitemap 共 {len(miss)} ===")
for m in miss[:15]:
    print(f"  {m}")

print("\n=== 今日新文页面头部取证 ===")
p = f"{REPO}/mili/blog/20261006-mili-gas-post-judgment-six-checklist.html"
t = read(p)
print("  SIZE", os.path.getsize(p))
print("  ld+json:", t.count("application/ld+json"), "| og:image:", "og:image" in t,
      "| og:title:", "og:title" in t, "| canonical:", "rel=\"canonical\"" in t,
      "| twitter:card:", "twitter:card" in t)
i = t.find("</head>")
print("  --- head tail ---")
print(t[max(0, i-1400):i+20])
