#!/usr/bin/env python3
"""0925 线上验证：新页四件 + 三索引卡 + 字节核验（CF 缓存用 ?cb= 绕开）"""
import re
import time
import urllib.request

BASE = "https://najieip.com"
SLUG = "20260925-policy-cash-value-execution-2024-instance"


def fetch(url, tries=5, wait=20):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "siteops-verify/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                return f"__ERR__ {e}"
            time.sleep(wait)
    return "__ERR__"


def legacy_fetch(url):  # 用 ?cb= 绕 CF 缓存
    sep = "&" if "?" in url else "?"
    return fetch(f"{url}{sep}cb={int(time.time())}")

print("=== 1. 新文章页四件 ===")
for attempt in range(6):
    h = legacy_fetch(f"{BASE}/mili/blog/{SLUG}.html")
    if h.startswith("__ERR__"):
        print("  抓取失败", h[:80]); break
    h1 = len(re.findall(r"<h1", h)); h2 = len(re.findall(r"<h2", h))
    ld = len(re.findall(r"application/ld\+json", h)); og = "og:image" in h
    printed = 'name="keywords"' in h
    print(f"  第{attempt+1}次: 字节={len(h.encode())} h1={h1} h2={h2} ld+json={ld} og:image={og} keywords={printed}")
    if h1 == 1 and h2 == 8 and ld == 2 and og and printed:
        print("  ✅ 已上线（四件齐备）")
        break
    time.sleep(30)
else:
    print("  ⚠️ 超时未收敛（可能仍在 Pages 构建）")

print("\n=== 2. 索引卡是否上线 ===")
for path, needle in [("/mili/blog/", f"./{SLUG}.html"), ("/blog/", f"/mili/blog/{SLUG}.html")]:
    h = legacy_fetch(BASE + path)
    print(f"  {path}  含新卡: {needle in h}  卡计数: {h.count('class=\"article-card\"')}")

print("\n=== 3. JSON-LD blogPost 是否含新条目 ===")
h = legacy_fetch(f"{BASE}/mili/blog/")
print("  blogPost 含新文 URL:", f"/mili/blog/{SLUG}.html" in h)

print("\n=== 4. sitemap ===")
sm = legacy_fetch(f"{BASE}/sitemap.xml")
print("  含新文 URL:", f"/mili/blog/{SLUG}.html" in sm, "| loc 总数:", sm.count("<loc>"))
