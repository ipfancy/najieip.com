#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-14 夜班 线上终验"""
import subprocess, os, re, json, time

REPO = "/Users/ziganghe/wiki/najieip-verify"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
TS = str(int(time.time()))
fails = []

def fetch(url, out=None, tries=3):
    for i in range(tries):
        cmd = ["curl", "-s", "-A", UA, "--max-time", "60"]
        if out:
            cmd += ["-o", out, url]
            subprocess.run(cmd, capture_output=True, text=True)
            if os.path.exists(out) and os.path.getsize(out) > 500:
                return True
        else:
            cmd += [url]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.stdout.strip():
                return r.stdout
    return False if out else None

def code(url):
    last = "000"
    for i in range(3):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA,
                            "--max-time", "40", url], capture_output=True, text=True)
        last = r.stdout.strip()
        if last == "200":
            return last
    return last

pairs = [
    ("mili/blog/20261114-mili-face-recognition-compliance.html", "https://najieip.com/mili/blog/20261114-mili-face-recognition-compliance.html"),
    ("mili/blog/20261114-mili-copyright-financing-16-cases.html", "https://najieip.com/mili/blog/20261114-mili-copyright-financing-16-cases.html"),
    ("najie/blog/20261114-najie-design-view-projection-rejection.html", "https://najieip.com/najie/blog/20261114-najie-design-view-projection-rejection.html"),
]
print("=== 文章页 ===")
for rel, url in pairs:
    c = code(url + "?cb=" + TS)
    ok = c == "200"
    print(f"  {c} {rel}")
    if not ok:
        fails.append(f"http {rel} {c}"); continue
    tmp = f"/tmp/so1114e_{os.path.basename(rel)}_{TS}.html"
    fetch(url + "?cb=" + TS, out=tmp)
    t = open(tmp, encoding="utf-8", errors="ignore").read()
    loc = open(os.path.join(REPO, rel), encoding="utf-8").read()
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ctx = t.count("https://schema.org")
    og = "og:image" in t
    stars = re.sub(r"[0-9*]\*{2}[0-9.]*", "", t).count("**")
    print(f"     live {len(t.encode())}B vs local {len(loc.encode())}B | h1={h1} ld={ld} ctx={ctx} og={og} stars={stars}")
    if h1 != 1 or ld < 2 or not og or stars != 0:
        fails.append(f"page6 {rel} h1={h1} ld={ld} og={og} stars={stars}")

print("=== 封面 ===")
c = code(f"https://najieip.com/img/20261114-mili-face-recognition-compliance.png?cb={TS}")
print("  ", c)
if c != "200": fails.append("cover " + c)

print("=== 索引卡 HIT ===")
for name, url, slugs in [
    ("mili", "https://najieip.com/mili/blog/", ["20261114-mili-face-recognition-compliance", "20261114-mili-copyright-financing-16-cases"]),
    ("najie", "https://najieip.com/najie/blog/", ["20261114-najie-design-view-projection-rejection"]),
    ("main", "https://najieip.com/blog/", ["20261114-mili-face-recognition-compliance", "20261114-mili-copyright-financing-16-cases", "20261114-najie-design-view-projection-rejection"]),
]:
    tmp = f"/tmp/so1114e_idx_{name}_{TS}.html"
    fetch(url + "?cb=" + TS, out=tmp)
    t = open(tmp, encoding="utf-8", errors="ignore").read()
    for s in slugs:
        n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + s, t))
        print(f"   {name} ...{s[-28:]}: {n} (page {len(t.encode())}B)")
        if n != 1: fails.append(f"idx {name} {s} n={n}")

print("=== live articles.json ===")
t = fetch("https://najieip.com/articles.json?cb=" + TS)
try:
    arr = json.loads(t)
    print("   条数:", len(arr))
    if len(arr) != 255: fails.append(f"articles.json live={len(arr)} expect 255")
except Exception as e:
    fails.append("articles.json " + str(e)[:40])

print("\nFAILURES:", fails if fails else "NONE")
