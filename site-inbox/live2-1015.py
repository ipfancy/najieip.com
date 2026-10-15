#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""等待 CF/Pages 传播后复验线上"""
import os, re, subprocess, time, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
SLUG = "20261015-ip-4-hard-deadlines-buju-revision"

def fetch(path):
    for _ in range(3):
        p = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "25", BASE + path], capture_output=True, text=True)
        if p.stdout and len(p.stdout) > 200:
            return p.stdout
        time.sleep(5)
    return p.stdout or ""

WAIT = int(sys.argv[1]) if len(sys.argv) > 1 else 150
print("sleep %ds ..." % WAIT)
time.sleep(WAIT)

CB = str(int(time.time()))
print("=== 新页判据 ===")
h = fetch("/mili/blog/%s.html?cb=%s" % (SLUG, CB))
print("  bytes=%d" % len(h.encode()))
checks = {}
checks["h1==1"] = len(re.findall(r"<h1[ >]", h)) == 1
checks["ld>=2"] = h.count("application/ld+json") >= 2
checks["og:image"] = 'property="og:image"' in h
checks["twitter:image"] = 'name="twitter:image"' in h
checks["keywords"] = 'name="keywords"' in h
checks["**==0"] = h.count("**") == 0
checks["schema.org>=2"] = h.count("https://schema.org") >= 2
m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', h)
checks["desc_len>120"] = bool(m) and len(m.group(1)) > 120
for k, v in checks.items():
    print("    %-18s %s" % (k, "PASS" if v else "FAIL"))

print("=== 索引卡 HIT ===")
lm = fetch("/mili/blog/?cb=%s" % CB); lb = fetch("/blog/?cb=%s" % CB)
print("  mili cards=%d (local 118) hit=%s" % (lm.count('<div class="article-card">'), SLUG in lm))
print("  main cards=%d (local 215) hit=%s" % (lb.count('<div class="article-card">'), SLUG in lb))

print("=== img 封面 ===")
p = subprocess.run(["curl", "-sI", "-L", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, "--max-time", "20",
                    BASE + "/img/%s.png" % SLUG], capture_output=True, text=True)
print("  /img/%s.png -> %s" % (SLUG, (p.stdout or "000").strip()))

print("=== articles.json ===")
aj = fetch("/articles.json?cb=%s" % CB)
try:
    d = json.loads(aj)
    n = len(d) if isinstance(d, list) else len(d.get("articles", d))
    print("  live entries =", n)
except Exception as e:
    print("  parse fail:", e, aj[:120])

print("=== sitemap ===")
sm = fetch("/sitemap.xml?cb=%s" % CB)
L = re.findall(r"<loc>(.*?)</loc>", sm)
print("  loc=%d 含新页=%s" % (len(L), any(SLUG in u for u in L)))
