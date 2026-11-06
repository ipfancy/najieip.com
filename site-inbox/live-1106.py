#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""live verification 2026-11-06"""
import subprocess, re, json, time, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def fetch(url, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-s", "-L", "-A", UA, url], capture_output=True, text=True, errors="replace")
        if p.returncode == 0 and len(p.stdout) > 500:
            return p.stdout
        time.sleep(3)
    return ""

def status(url, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, url],
                           capture_output=True, text=True)
        if p.stdout.strip() == "200":
            return "200"
        time.sleep(3)
    return p.stdout.strip()

CB = str(int(time.time()))
fails = []
PAGES = ["20261103-mili-guarantee-period-six-months", "20261104-mili-inventor-reward-5-percent",
         "20261106-mili-nda-vs-noncompete", "20261106-mili-appraisal-opinion-review"]
for s in PAGES:
    url = f"https://najieip.com/mili/blog/{s}.html?cb={CB}"
    t = fetch(url)
    st = status(f"https://najieip.com/mili/blog/{s}.html")
    chk = dict(status=st, bytes=len(t.encode()), h1=len(re.findall(r'<h1[ >]', t)),
               ld=len(re.findall(r'application/ld\+json', t)),
               og=1 if 'property="og:image"' in t else 0,
               stars=t.count("**"), bare=len(re.findall(r'<p>\s*\|', t)))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    chk["desc_len"] = len(m.group(1)) if m else 0
    img = f"https://najieip.com/img/{s}.png"
    chk["img"] = status(img)
    ok = (st == "200" and chk["h1"] == 1 and chk["ld"] >= 2 and chk["og"] == 1
          and chk["desc_len"] > 80 and chk["stars"] == 0 and chk["bare"] == 0 and chk["img"] == "200")
    print(("PASS " if ok else "FAIL ") + s, json.dumps(chk, ensure_ascii=False))
    if not ok: fails.append(s)

# index cards live
for idx, slugs in [("https://najieip.com/mili/blog/", PAGES[:3]),
                   ("https://najieip.com/blog/", PAGES)]:
    t = fetch(idx + "?cb=" + CB)
    for s in slugs:
        n = len(re.findall(r'<h2><a href="[^"]*' + re.escape(s), t))
        print(f"   live card {idx}{s}: {n}")
        if n != 1: fails.append(f"card {s} on {idx}")

# live articles.json
p = subprocess.run(["curl", "-s", "-L", "-A", UA, f"https://najieip.com/articles.json?cb={CB}"],
                   capture_output=True, text=True)
try:
    aj = json.loads(p.stdout)
    print("live articles.json:", len(aj))
    if len(aj) != 239: fails.append(f"articles.json live={len(aj)}")
except Exception as e:
    print("articles.json parse fail", e); fails.append("articles.json")

print("\nFAILURES:", fails if fails else "NONE")
