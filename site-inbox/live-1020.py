#!/usr/bin/env python3
# live verify 1020
import subprocess, re, json, time, random

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "customs-ip-detention-30-day-timeline-20261018"
PAGE = f"https://najieip.com/mili/blog/{SLUG}.html"

def get(url, tries=3):
    for i in range(tries):
        u = f"{url}{'&' if '?' in url else '?'}cb={int(time.time())}{random.randint(100,999)}"
        r = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, u], capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout
        time.sleep(3)
    return ""

fails = []
t = get(PAGE)
print("PAGE bytes:", len(t.encode()))
def chk(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (" " + str(detail) if detail else ""))
    if not cond: fails.append(name)

chk("h1==1", t.count("<h1") == 1, t.count("<h1"))
chk("ld>=2", t.count("application/ld+json") >= 2, t.count("application/ld+json"))
chk("og:image", t.count('property="og:image"') == 1)
chk("og:site_name", "og:site_name" in t)
chk("twitter:title", "twitter:title" in t)
chk("keywords", 'name="keywords"' in t)
m = re.search(r'<meta name="description" content="([^"]*)"', t)
dl = len(m.group(1)) if m else 0
chk("desc>80", dl > 80, dl)
chk("no **", t.count("**") == 0, t.count("**"))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    try:
        json.loads(b); ok = True
    except Exception as e:
        ok = False; print("   ld error", e)
    chk("ld parses", ok)

# image
r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, "--max-time", "25",
                    f"https://najieip.com/img/{SLUG}.png"], capture_output=True, text=True)
chk("cover 200", r.stdout.strip() == "200", r.stdout.strip())

# articles.json live
aj = get("https://najieip.com/articles.json")
try:
    d = json.loads(aj); arr = d if isinstance(d, list) else d["articles"]
    chk("articles.json live == 192", len(arr) == 192, len(arr))
    chk("rank1 is today's page", arr[0]["url"].endswith(SLUG + ".html"), arr[0]["url"])
except Exception as e:
    chk("articles.json parse", False, str(e))

# index cards live
for name, url in [("main blog index", "https://najieip.com/blog/"), ("mili index", "https://najieip.com/mili/blog/")]:
    h = get(url)
    chk(f"{name} card HIT", SLUG in h, h.count(SLUG))

print("\nFAILURES:", fails if fails else "NONE")
