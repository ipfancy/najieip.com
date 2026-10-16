#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-17 线上终验：核心页 200 + 新 EN/FR 页判据 + 索引卡 HIT + 封面图 + sitemap/articles.json"""
import os, re, subprocess, time, difflib

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261009-mili-ai-short-drama-token-evidence"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
FAILS = []


def curl(url, head=False, retries=3):
    for i in range(retries):
        args = ["curl", "-s", "-A", UA, "-m", "30", "-L"]
        if head:
            args += ["-o", "/dev/null", "-w", "%{http_code}"]
        args.append(url + ("&" if "?" in url else "?") + "cb=%d" % int(time.time()))
        r = subprocess.run(args, capture_output=True, text=True)
        out = r.stdout
        code = out.strip() if head else None
        if head:
            if code == "200":
                return code, ""
        else:
            if len(out) > 200:
                return "200", out
        time.sleep(3)
    return (code if head else "000"), (out if not head else "")


def chk(cond, label, extra=""):
    print(("PASS " if cond else "FAIL ") + label + (" " + extra if extra else ""))
    if not cond:
        FAILS.append(label)


print("== A. 核心页 HTTP ==")
CORE = ["https://najieip.com/", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/mili/blog/", "https://najieip.com/najie/blog/",
        "https://najieip.com/en/", "https://najieip.com/fr/", "https://najieip.com/sitemap.xml",
        "https://najieip.com/robots.txt", "https://najieip.com/articles.json"]
for u in CORE:
    code, _ = curl(u, head=True)
    chk(code == "200", f"HTTP 200 {u}", f"(got {code})")

print("\n== B. 新 EN/FR 页 ==")
for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    code, body = curl(u)
    chk(code == "200" and len(body) > 1000, f"{lang} page 200", f"({len(body)}B)")
    if body:
        chk(body.count("application/ld+json") >= 1, f"{lang} ld+json>=1", str(body.count("application/ld+json")))
        chk("og:image" in body, f"{lang} og:image")
        chk(body.count("**") == 0, f"{lang} no ** ")
        chk(body.count("<h1") == 1, f"{lang} h1==1")
        chk(body.count("hreflang") == 4, f"{lang} hreflang==4")
        chk("https://schema.org" in body, f"{lang} schema.org live")
        local = open(f"{REPO}/{lang}/blog/{SLUG}-{lang}.html", encoding="utf-8").read()
        lb, ob = len(local.encode()), len(body.encode())
        if lb == ob:
            chk(True, f"{lang} bytes identical", f"({lb})")
        else:
            d = [l for l in difflib.unified_diff(local.splitlines(), body.splitlines(), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
            beacon_only = all(("beacon" in l or "cloudflare" in l or l.strip() in ("+", "-")) for l in d)
            chk(beacon_only and abs(lb - ob) < 800, f"{lang} bytes diff attributable", f"local={lb} live={ob} lines={len(d)}")

print("\n== C. 索引卡 HIT + 封面图 ==")
for lang in ("en", "fr"):
    _, body = curl(f"https://najieip.com/{lang}/blog/")
    chk(f"/{lang}/blog/{SLUG}-{lang}.html" in body, f"{lang} index card HIT")
code, _ = curl(f"https://najieip.com/img/{SLUG}.png", head=True)
chk(code == "200", "cover img 200", f"(got {code})")

print("\n== D. 中文权威页 hreflang + sitemap/articles.json ==")
_, z = curl(f"https://najieip.com/mili/blog/{SLUG}.html")
chk(z.count("hreflang") == 4, "zh page hreflang==4 live", str(z.count("hreflang")))
_, sm = curl("https://najieip.com/sitemap.xml")
chk(sm.count("<loc>") == 311, f"sitemap loc==311 live (got {sm.count('<loc>')})")
for lang in ("en", "fr"):
    chk(f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html" in sm, f"sitemap {lang} loc live")
_, aj = curl("https://najieip.com/articles.json")
try:
    import json
    n = len(json.loads(aj))
    chk(n == 190, f"articles.json live == 190 (got {n})")
except Exception as e:
    chk(False, f"articles.json parse ({e})")

print("\nFAILURES:", len(FAILS))
for f in FAILS:
    print(" -", f)
