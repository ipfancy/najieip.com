#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""live-1110.py — 线上部署验证"""
import subprocess, re, json, time, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
fails = []


def get(url, binary=False, tries=3):
    for i in range(tries):
        cmd = ["curl", "-s", "-A", UA, "--max-time", "30",
               url + ("?cb=%d" % int(time.time()) if "?" not in url else "")]
        if binary:
            cmd = ["curl", "-sI", "-A", UA, "--max-time", "30", url]
            r = subprocess.run(cmd, capture_output=True, text=True)
            return r.stdout
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout and len(r.stdout) > 500:
            return r.stdout
        time.sleep(8)
    return ""


def code(url):
    for i in range(3):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA,
                            "--max-time", "30", url], capture_output=True, text=True)
        c = r.stdout.strip()
        if c == "200":
            return c
        time.sleep(6)
    return c


print("=== A. HTTP 200 ===")
for u in [BASE + "/", BASE + "/mili/", BASE + "/najie/", BASE + "/blog/", BASE + "/sitemap.xml",
          BASE + "/llms.txt", BASE + "/mili/blog/", BASE + "/mili/family-wealth.html",
          BASE + "/mili/blog/20261110-mili-will-partial-invalid.html",
          BASE + "/img/20261110-mili-will-partial-invalid.png"]:
    c = code(u)
    print(c, u)
    if c != "200":
        fails.append("HTTP %s %s" % (c, u))

print("\n=== B. 文章页六项 ===")
h = get(BASE + "/mili/blog/20261110-mili-will-partial-invalid.html")
print("bytes", len(h.encode()), "h1", len(re.findall(r"<h1", h)), "h2", len(re.findall(r"<h2", h)),
      "ld", h.count("application/ld+json"), "og:image", h.count("og:image"),
      "stars", h.count("**"), "masked", h.count("https://***"), "rawtable", len(re.findall(r"<p>\|", h)))
if len(re.findall(r"<h1", h)) != 1: fails.append("article h1")
if h.count("application/ld+json") != 2: fails.append("article ld")
if h.count("og:image") != 1: fails.append("article og:image")
if h.count("**") != 0: fails.append("article stars")
if "6亿遗产" not in h: fails.append("article content missing")

print("\n=== C. 专题页 ===")
f = get(BASE + "/mili/family-wealth.html")
print("bytes", len(f.encode()), "h1", len(re.findall(r"<h1", f)), "ld", f.count("application/ld+json"),
      "og:image", f.count("og:image"), "twitter", f.count("twitter:"))
if f.count("og:image") < 1: fails.append("topic og:image")
if f.count("twitter:card") != 1: fails.append("topic twitter:card")

print("\n=== D. 索引卡 HIT ===")
for name, url in [("mili/blog", BASE + "/mili/blog/"), ("main blog", BASE + "/blog/")]:
    b = get(url)
    n = b.count("20261110-mili-will-partial-invalid")
    print(name, "hits", n, "bytes", len(b.encode()))
    if n < 1:
        fails.append("index card missing " + name)

print("\n=== E. live articles.json ===")
a = get(BASE + "/articles.json")
try:
    arr = json.loads(a)
    print("entries", len(arr))
    if len(arr) != 246:
        fails.append("articles.json live count %d != 246" % len(arr))
except Exception as e:
    fails.append("articles.json parse %s" % e)

print("\nFAILURES =", fails or "NONE")
sys.exit(1 if fails else 0)
