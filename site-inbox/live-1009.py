#!/usr/bin/env python3
"""live-1009.py — 线上部署终验（带 UA + ?cb= 绕缓存，重试3次）"""
import urllib.request, re, json, time, os

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "Chrome/120 Safari/537.36")
SLUG = "20261009-mili-ai-short-drama-token-evidence"

def fetch(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except Exception as e:
            last = str(e)
            time.sleep(3)
    return 0, last

def status(url):
    for k in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status
        except Exception:
            time.sleep(2)
    return 0

cb = str(int(time.time()))
print("=== CORE PAGES (fresh) ===")
for u in ["https://najieip.com/", "https://najieip.com/mili/", "https://najieip.com/najie/",
          "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]:
    print(status(u), u)

print("\n=== NEW PAGE LIVE ===")
s, t = fetch("https://najieip.com/mili/blog/%s.html?cb=%s" % (SLUG, cb))
print("status", s, "len", len(t))
ld = t.count("application/ld+json"); og = t.count('property="og:image"')
h1 = len(re.findall(r"<h1[ >]", t)); stars = t.count("**")
print("ld=%d og:image=%d h1=%d **=%d" % (ld, og, h1, stars))
if ld >= 2 and og == 1 and h1 == 1 and stars == 0:
    print("PAGE LIVE OK")
else:
    print("PAGE LIVE PENDING/FAIL")

print("\n=== INDEX CARD HIT ===")
for name, u in [("mili", "https://najieip.com/mili/blog/"), ("main", "https://najieip.com/blog/")]:
    s, t = fetch(u + "?cb=" + cb)
    print(name, "status", s, "slug_hit", t.count(SLUG))

print("\n=== articles.json live ===")
s, t = fetch("https://najieip.com/articles.json?cb=" + cb)
try:
    j = json.loads(t)
    arr = j if isinstance(j, list) else j.get("articles", [])
    print("status", s, "entries", len(arr))
except Exception as e:
    print("status", s, "parse fail", e)
