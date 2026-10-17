#!/usr/bin/env python3
"""Live verification after push (2026-10-17 evening)."""
import subprocess, re, json, time, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
SLUG = "customs-ip-post-filing-steps-20261017"
CB = str(int(time.time()))
fails = []

def get(url, tries=3):
    for i in range(tries):
        out = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30", url],
                             capture_output=True, text=True).stdout
        if out and len(out) > 200:
            return out
        time.sleep(3)
    return out

def code(url):
    return subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA,
                           "-L", "--max-time", "25", url], capture_output=True, text=True).stdout.strip()

print("waiting 150s for Pages build...")
time.sleep(150)

# 1) page
url = f"{BASE}/mili/blog/{SLUG}.html?cb={CB}"
t = get(url)
checks = {
    "h1==1": len(re.findall(r"<h1[\s>]", t)) == 1,
    "ld>=2": len(re.findall(r"application/ld\+json", t)) >= 2,
    "og:image": 'property="og:image"' in t,
    "og:site_name": "og:site_name" in t,
    "twitter:title": "twitter:title" in t,
    "keywords": 'name="keywords"' in t,
    "stars==0": t.count("**") == 0,
    "desc>80": len(re.search(r'<meta name="description" content="([^"]*)"', t).group(1)) > 80,
    "schema_org": t.count("https://schema.org") >= 2,
}
print("PAGE", len(t), "chars")
for k, v in checks.items():
    print(("  OK   " if v else "  FAIL ") + k)
    if not v:
        fails.append("page:" + k)

# 2) cover image
c = code(f"{BASE}/img/{SLUG}.png")
print("IMG", c)
if c != "200":
    fails.append("img:" + c)

# 3) indexes
for p in ["/mili/blog/", "/blog/"]:
    txt = get(f"{BASE}{p}?cb={CB}")
    hit = SLUG in txt
    print(f"INDEX {p} slug_hit={hit} cards={txt.count('class=\"article-card\"')}")
    if not hit:
        fails.append("index:" + p)

# 4) live articles.json
aj = get(f"{BASE}/articles.json?cb={CB}")
try:
    n = len(json.loads(aj))
    print("articles.json live:", n)
    if n != 191:
        fails.append(f"articles.json:{n}")
except Exception as e:
    print("articles.json parse fail", e)
    fails.append("articles.json:parse")

# 5) core pages
for p in ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]:
    c = code(BASE + p)
    if c != "200":
        c = code(BASE + p)  # one retry
    print(f"CORE {c} {p}")
    if c != "200":
        fails.append("core:" + p)

print("\nFAILURES:", fails if fails else "NONE")
