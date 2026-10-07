#!/usr/bin/env python3
"""SiteOps 1007 live post-deploy verification (UA + cache buster; retry to final state)."""
import subprocess, time, json, re, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
cb = int(time.time())


def get(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "30",
                            f"{url}{'&' if '?' in url else '?'}cb={cb}"],
                           capture_output=True, text=True)
        if r.stdout:
            return r.stdout
        time.sleep(3)
    return ""


def head_code(url, tries=3):
    for i in range(tries):
        c = subprocess.run(["curl", "-sI", "-L", "-A", UA, "-o", "/dev/null", "-w", "%{http_code}",
                            "--max-time", "25", url], capture_output=True, text=True).stdout.strip()
        if c == "200":
            return c
        time.sleep(3)
    return c


print("=== LIVE POST-DEPLOY ===")
pages = [
    "/mili/blog/20261007-trademark-judicial-interpretation-opinion.html",
    "/mili/blog/geely-wm-trade-secret-20260814.html",
    "/najie/blog/20260901-copyright-jp18-compliance-checklist.html",
]
allok = True
for p in pages:
    b = get("https://najieip.com" + p)
    ld = b.count("application/ld+json")
    ogi = b.count('property="og:image"')
    st = b.count("**")
    h1 = len(re.findall(r"<h1[ >]", b))
    ttl = re.search(r"<title>(.*?)</title>", b, re.S)
    m = re.search(r'<meta name="description" content="([^"]*)"', b)
    good = ld >= 2 and ogi >= 1 and st == 0 and h1 == 1 and bool(m) and \
        (m.group(1).strip() != re.sub(r"\s*—\s*纳杰觅理\s*$", "", ttl.group(1).strip()))
    allok &= good
    print(("  PASS " if good else "  FAIL ") + f"{p} ld={ld} og:image={ogi} h1={h1} stars={st} bytes={len(b)}")

# articles.json live
raw = get("https://najieip.com/articles.json")
try:
    n = len(json.loads(raw))
except Exception as e:
    n = f"parse-error {e}"
print(f"  live articles.json entries = {n} (expected 178)")
allok &= (n == 178)

# core pages
for p in ("/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt", "/en/", "/fr/",
          "/mili/blog/", "/najie/blog/"):
    c = head_code("https://najieip.com" + p)
    if c != "200":
        allok = False
    print(f"  {c} {p}")

# index cards present
mi = get("https://najieip.com/mili/blog/")
bi = get("https://najieip.com/blog/")
for label, t, needle in (("mili-idx", mi, "20261007-trademark-judicial-interpretation-opinion.html"),
                         ("main-idx", bi, "technical-secret-presumed-infringement-1590-2026.html")):
    hit = needle in t
    allok &= hit
    print(f"  {'PASS' if hit else 'FAIL'} {label} card {needle[:52]}")
print("LIVE ALL:", allok)
