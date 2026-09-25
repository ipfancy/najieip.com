#!/usr/bin/env python3
"""0925 诊断：sitemap + 三索引 对 09-21~09-25 文章的覆盖实况（本地 vs 线上）"""
import os, re, subprocess, urllib.request, json

BASE = "https://najieip.com"
REPO = "/Users/ziganghe/wiki/najieip-verify"
ART_DIR = f"{REPO}/digital-employees/articles"  # 不存在也没关系
SLUGS_DATE = "20260921", "20260922", "20260923", "20260924", "20260925"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "siteops-audit/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

print("=" * 70)
print("A. 今日(09-25)新文在各处的落地情况")
print("=" * 70)
# 找 09-25 的文章文件
files_0925 = []
for root, dirs, fs in os.walk(REPO):
    if "/.git" in root:
        continue
    for f in fs:
        if re.match(r"2026092[1-5].*\.html$", f):
            files_0925.append(os.path.relpath(os.path.join(root, f), REPO))
print("仓库内 09-21~09-25 文章 HTML:")
for f in sorted(files_0925):
    print("   ", f, os.path.getsize(os.path.join(REPO, f)), "B")

print()
print("=" * 70)
print("B. sitemap（线上 vs 本地）逐日期段命中")
print("=" * 70)
try:
    live_sm = fetch(BASE + "/sitemap.xml?cb=0925diag")
    print("线上 sitemap 字节:", len(live_sm.encode()))
except Exception as e:
    live_sm = ""
    print("线上 sitemap 抓取失败:", e)
local_sm = open(f"{REPO}/sitemap.xml", encoding="utf-8").read()
print("本地 sitemap 字节:", len(local_sm.encode()))
for d in SLUGS_DATE:
    lv = len(re.findall(r"<loc>[^<]*" + d + r"[^<]*</loc>", live_sm))
    lc = len(re.findall(r"<loc>[^<]*" + d + r"[^<]*</loc>", local_sm))
    print(f"   {d}: 线上 {lv} 条 | 本地 {lc} 条")
print("线上 sitemap 最新 5 个 <loc>:")
for m in re.findall(r"<loc>([^<]+)</loc>", live_sm)[-5:]:
    print("   ", m)

print()
print("=" * 70)
print("C. 三个索引页 最新卡片日期（线上）")
print("=" * 70)
for path in ("/blog/", "/mili/blog/", "/najie/blog/"):
    try:
        h = fetch(BASE + path + "?cb=0925diag")
    except Exception as e:
        print(f"  {path} 抓取失败 {e}")
        continue
    cards = re.findall(r'<div class="article-card">(.*?)</div>\s*</div>', h, re.S)
    dates = re.findall(r'(\d{4}-\d{2}-\d{2})', h)
    body = h[h.find("<body"):]
    hrefs = re.findall(r'<h2><a href="([^"]+)"', body)
    print(f"  {path}  卡片数={len(re.findall(chr(60)+'div class=.article-card.', body))} 前3个 href:")
    for x in hrefs[:3]:
        print("       ", x)
    print(f"       页面内出现的日期(前8): {sorted(set(dates), reverse=True)[:8]}")

print()
print("=" * 70)
print("D. 缺口比对：09-21~09-25 文章 是否在三索引 + sitemap 出现")
print("=" * 70)
allhtml = sorted(files_0925)
for f in allhtml:
    slug = os.path.basename(f)[:-5]
    row = {"file": f, "slug": slug}
    for path in ("/blog/", "/mili/blog/", "/najie/blog/"):
        try:
            h = fetch(BASE + path + "?cb=0925diag2")
            row[path] = "HIT" if slug in h else "-"
        except Exception:
            row[path] = "ERR"
    row["sitemap"] = "HIT" if f"/{slug}.html" in live_sm or slug in live_sm else "-"
    print(f"  {slug[:52]:54} main={row['/blog/']:4} mili={row['/mili/blog/']:4} najie={row['/najie/blog/']:4} sitemap={row['sitemap']}")
