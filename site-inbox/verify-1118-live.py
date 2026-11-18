#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-18 夜班线上终验：5 页六项 + 封面 + 三索引卡 + articles.json"""
import subprocess, re, json, time, random

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"

def get(path, tries=3, binary=False):
    for i in range(tries):
        url = BASE + path + (("?cb=%d" % random.randint(10**6, 10**7)) if not binary else "")
        if binary:
            r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA,
                                "--max-time", "30", BASE + path], capture_output=True, text=True)
            return r.stdout.strip()
        r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "60", url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 200:
            return r.stdout.decode("utf-8", "ignore")
        time.sleep(4)
    return ""

SLUGS = [("mili", "20261118-mili-ai-tool-trade-secret"),
         ("mili", "20261118-mili-drug-linkage-9-cases"),
         ("mili", "20261118-mili-finland-labor-four-gates"),
         ("mili", "20261118-mili-refusal-execute-five-cases"),
         ("najie", "20261118-najie-gi-15plan-2030")]

fails = []
print("=== A. 线上页面六项 ===")
for b, s in SLUGS:
    t = get(f"/{b}/blog/{s}.html")
    if t == "":
        fails.append(f"{s}: NO_RESPONSE"); print(f"  [NO_RESPONSE] {s}"); continue
    h1 = len(re.findall(r"<h1[ >]", t)); ld = re.findall(r'application/ld\+json', t)
    ogimg = bool(re.search(r'property="og:image"', t))
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    dl = len(d.group(1)) if d else 0
    stars = t.count("**")
    ok = h1 == 1 and len(ld) >= 2 and ogimg and dl > 60 and stars == 0 and "https://***" not in t
    if not ok: fails.append(s)
    print(f"  [{'PASS' if ok else 'FAIL'}] {b}/{s} bytes={len(t.encode())} h1={h1} ld={len(ld)} og:image={ogimg} desc={dl} **={stars}")

print("=== B. 封面图 ===")
c = get("/img/20261118-mili-finland-labor-four-gates.png", binary=True)
print(f"  {c} /img/20261118-mili-finland-labor-four-gates.png")
if c != "200": fails.append("img")

print("=== C. 索引卡（线上）===")
for path, key in [("/blog/", "main"), ("/mili/blog/", "mili"), ("/najie/blog/", "najie")]:
    t = get(path)
    print(f"  {key}: bytes={len(t.encode())}")
    for b, s in SLUGS:
        need = (key == "main") or (key == b)
        if not need: continue
        n = len(re.findall(r'href="[^"]*' + re.escape(s), t))
        flag = "HIT" if n >= 1 else "MISS"
        if n < 1: fails.append(f"{key}:{s}")
        print(f"    {flag} {s} ({n})")

print("=== D. articles.json ===")
aj = get("/articles.json")
try:
    arr = json.loads(aj)
    print(f"  total={len(arr)}")
    for i, it in enumerate(arr[:6], 1):
        print(f"   {i}. {it.get('url')}")
    if len(arr) != 264: fails.append(f"articles.json={len(arr)}")
except Exception as e:
    fails.append("articles.json parse")
    print("  parse fail", e)

print("=== FAILS ===")
print("  " + (", ".join(fails) if fails else "NONE"))
