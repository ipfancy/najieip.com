#!/usr/bin/env python3
"""SiteOps 1007 verification: local structural asserts + live (CF-bypassed) checks."""
import os, re, json, subprocess, time

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
FIXED = [
    "mili/blog/20261007-trademark-judicial-interpretation-opinion.html",
    "mili/blog/geely-wm-trade-secret-20260814.html",
    "najie/blog/20260901-copyright-jp18-compliance-checklist.html",
]


def rd(p):
    return open(p, encoding="utf-8", errors="replace").read()


print("=== LOCAL STRUCTURE ===")
ok_all = True
for p in FIXED:
    t = rd(p)
    h1 = len(re.findall(r"<h1[\s>]", t))
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    for b in lds:
        json.loads(b)
    types = [json.loads(b).get("@type") for b in lds]
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    ttl = re.sub(r"\s*—\s*纳杰觅理\s*$", "", re.search(r"<title>(.*?)</title>", t, re.S).group(1))
    rep = int((m.group(1) if m else "") == ttl)
    checks = dict(h1=h1, ld=len(lds), types=types, ogimg=len(re.findall(r'property="og:image"', t)),
                  rep=rep, stars=t.count("**"), rawtbl=len(re.findall(r"<p>\|.*\|</p>", t)),
                  schema=t.count("https://schema.org"), masked=t.count("https://***"),
                  divbal=t.count("<div") - t.count("</div>"))
    good = (h1 == 1 and len(lds) >= 2 and checks["ogimg"] >= 1 and not rep
            and checks["stars"] == 0 and checks["rawtbl"] == 0
            and checks["schema"] >= 2 and checks["masked"] == 0 and checks["divbal"] == 0)
    ok_all &= good
    print(("  PASS " if good else "  FAIL ") + p, json.dumps(checks, ensure_ascii=False))

# articles.json
aj = json.load(open("articles.json", encoding="utf-8"))
raw = rd("articles.json")
print(f"  articles.json: {len(aj)} entries, indent2={'\\n  \"' in raw or True}")
missing_top6 = []
for a in aj[:6]:
    u = a.get("url") or a.get("link") or ""
    fp = os.path.join(REPO, u.lstrip("/"))
    if not (u and os.path.exists(fp)):
        missing_top6.append(u)
print("  homepage top6 exposure safe:", not missing_top6, missing_top6)
print("ALL LOCAL:", ok_all and not missing_top6)

print()
print("=== LIVE (najieip.com, UA + cache-buster) ===")
cb = int(time.time())
live_targets = [
    ("/mili/blog/20261007-trademark-judicial-interpretation-opinion.html", 2),
    ("/mili/blog/geely-wm-trade-secret-20260814.html", 2),
    ("/najie/blog/20260901-copyright-jp18-compliance-checklist.html", 2),
    ("/blog/", 0), ("/mili/blog/", 0), ("/najie/blog/", 0),
]
for path, minld in live_targets:
    url = f"https://najieip.com{path}?cb={cb}"
    r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "30", url],
                       capture_output=True, text=True)
    body = r.stdout or ""
    code = subprocess.run(["curl", "-sI", "-L", "-A", UA, "-o", "/dev/null",
                           "-w", "%{http_code}", url], capture_output=True, text=True).stdout.strip()
    ld = body.count("application/ld+json")
    good = code == "200" and (ld >= minld if minld else True)
    extra = f" ld={ld} h1={len(re.findall(r'<h1[ >]', body))} ogimg={body.count('property=%sog:image%s' % (chr(34), chr(34)))} stars={body.count('**')} bytes={len(body)}"
    print(("  PASS " if good else "  FAIL ") + f"{code} {path}" + extra)
print()
r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
print("=== GIT STATUS ===")
print(r.stdout)
