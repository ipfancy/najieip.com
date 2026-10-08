#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live post-deploy verification for 2026-10-08 SiteOps run."""
import subprocess, re, json, time, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get(url, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "30",
                            url + ("&" if "?" in url else "?") + "cb=%d" % int(time.time())],
                           capture_output=True, text=True)
        if p.stdout and len(p.stdout) > 500:
            return p.stdout
        time.sleep(5)
    return ""

TARGETS = [
    "https://najieip.com/mili/blog/20261008-mili-labor-contract-four-clauses.html",
    "https://najieip.com/mili/blog/20261008-mili-ai-math-solution-copyright.html",
    "https://najieip.com/mili/blog/20261008-ticket-grabbing-software-crime.html",
    "https://najieip.com/aipunajie/blog/20261008-aipunajie-ev-patent-fto.html",
]
fails = []
for u in TARGETS:
    t = get(u)
    if not t:
        print("FAIL(no body)", u); fails.append(u); continue
    h1 = len(re.findall(r"<h1", t))
    ld = t.count("application/ld+json")
    oi = t.count('property="og:image"')
    stars = t.count("**")
    ok = h1 == 1 and ld >= 2 and oi == 1 and stars == 0
    print(("OK   " if ok else "FAIL ") + f"{u.split('/')[-1]}  bytes={len(t.encode())} h1={h1} ld={ld} og:image={oi} stars={stars}")
    if not ok:
        fails.append(u)

# articles.json live
t = get("https://najieip.com/articles.json")
try:
    aj = json.loads(t)
    n = len(aj if isinstance(aj, list) else aj.get("articles", []))
    print(f"live articles.json entries = {n}")
except Exception as e:
    print("articles.json parse FAIL", e, t[:120]); n = -1

# index card HIT
for idx in ["https://najieip.com/blog/", "https://najieip.com/mili/blog/"]:
    t = get(idx)
    hit = t.count("20261008-mili-labor-contract-four-clauses")
    print(f"{'OK  ' if hit else 'FAIL'} card HIT {idx} -> {hit}")
    if not hit:
        fails.append(idx)

print("\nLIVE FAILS =", len(fails))
for f in fails:
    print("  !", f)
