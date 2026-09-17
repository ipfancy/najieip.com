#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inspect-0917-live.py — 线上 vs 本地终验（字节同口径 + 线上文章精修版判定）"""
import difflib, os, re, subprocess, time

SITE = os.path.expanduser("~/wiki/najieip-verify")
CB = str(int(time.time()))


def live(url):
    return subprocess.run(["curl", "-s", url], capture_output=True).stdout


print("== 线上文章精修版判定 ==")
raw = live("https://najieip.com/mili/blog/20260917-upc-injunction-counterattack.html?cb=" + CB).decode("utf-8", "ignore")
print("  bytes=%d og:image=%d canonical=%d ld+json=%d schema.org=%d '**'=%d"
      % (len(raw.encode()), raw.count("og:image"), raw.count("canonical"),
         len(re.findall(r"application/ld\+json", raw)), raw.count("https://schema.org"), raw.count("**")))
print("  leak ai_smell=%s '<p>---</p>'=%s" % ("ai_smell" in raw, "<p>---</p>" in raw))
print("  下一轮巡检口令：curl najieip.com 文章页 grep 'og:url|canonical|application/ld+json' 应 >=4，grep '\\*\\*' = 0")

print("== 线上 vs 本地字节比较 ==")
for f, url in [("blog/index.html", "https://najieip.com/blog/"),
               ("mili/blog/index.html", "https://najieip.com/mili/blog/")]:
    loc = open(os.path.join(SITE, f), "rb").read()
    rem = live(url + "?cb=" + CB)
    same = loc == rem
    print("  %-22s local=%d live=%d 字节一致=%s" % (f, len(loc), len(rem), same))
    if not same:
        a = loc.decode("utf-8", "ignore").splitlines()
        b = rem.decode("utf-8", "ignore").splitlines()
        d = [l for l in difflib.unified_diff(a, b, "local", "live", n=0, lineterm="")][:12]
        for l in d:
            print("     ", l[:160])

print("== 线上索引是否已含新卡 ==")
for f, url, needle in [("mili/blog/index.html", "https://najieip.com/mili/blog/", "20260917-upc-injunction-counterattack"),
                       ("blog/index.html", "https://najieip.com/blog/", "20260917-upc-injunction-counterattack")]:
    t = live(url + "?cb=" + CB).decode("utf-8", "ignore")
    print("  %-22s 卡数=%d 命中新 slug=%d" % (f, len(re.findall(r'<div class="article-card">', t)), t.count(needle)))
