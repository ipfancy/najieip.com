#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-16 线上终验"""
import re, json, time, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "customs-ip-filing-3-things-20261016"
PAGE = "https://najieip.com/najie/blog/%s.html" % SLUG

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url + ("&" if "?" in url else "?") + "cb=%d" % int(time.time()),
                                         headers={"User-Agent": UA, "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except Exception as e:
            last = e
            time.sleep(3)
    return 0, str(last)

fails = []
print("=== A. 核心页 ===")
for u in ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
          "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt",
          "https://najieip.com/en/", "https://najieip.com/fr/"]:
    st, _ = get(u)
    print("  %s  %s" % (st, u))
    if st != 200:
        fails.append(u)

print("\n=== B. 精修页线上判据 ===")
st, t = get(PAGE)
print("  status =", st, "bytes =", len(t.encode("utf-8")))
m = re.search(r'<meta name="description" content="([^"]*)"', t)
desc = m.group(1) if m else ""
tm = re.search(r"<title>(.*?)</title>", t, re.S)
tit = tm.group(1).split(" — ")[0].strip() if tm else ""
crit = [("h1==1", t.count("<h1") == 1), ("h2==3", t.count("<h2") == 3),
        ("ld+json>=2", t.count("application/ld+json") >= 2),
        ("og:image", "og:image" in t), ("og:site_name", "og:site_name" in t),
        ("keywords", 'name="keywords"' in t), ("twitter:title", "twitter:title" in t),
        ("**==0", t.count("**") == 0),
        ("desc!=title", bool(desc) and desc.replace("&quot;", '"').strip() != tit),
        ("schema.org", "https://schema.org" in t), ("no脱敏***", "https://***" not in t)]
for n, v in crit:
    print("  %s %s" % ("PASS" if v else "FAIL", n))
    if not v:
        fails.append(n)

print("\n=== C. 封面图 ===")
st, _ = get("https://najieip.com/img/%s.png" % SLUG)
print("  %s  img/%s.png" % (st, SLUG))
if st != 200:
    fails.append("img")

print("\n=== D. live articles.json / sitemap ===")
st, aj = get("https://najieip.com/articles.json")
try:
    d = json.loads(aj)
    n = len(d["articles"] if isinstance(d, dict) else d)
except Exception as e:
    n = "parse-error:%s" % e
print("  articles.json 条目 =", n, "(期望 190)")
if n != 190:
    fails.append("articles.json=%s" % n)
st, sm = get("https://najieip.com/sitemap.xml")
print("  sitemap loc =", len(re.findall(r"<loc>", sm)), "(本地 309)")
print("  slug in sitemap =", SLUG in sm)

print("\n=== E. 索引卡（线上） ===")
for u, key in [("https://najieip.com/blog/", SLUG), ("https://najieip.com/najie/blog/", SLUG)]:
    st, it = get(u)
    print("  %s  %s  HIT=%s" % (st, u, key in it))
    if key not in it:
        fails.append("index %s" % u)

print("\nFAILS =", fails if fails else "NONE")
