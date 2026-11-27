import json, re, subprocess, time, urllib.request, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SHA = "7d10ab6"

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout

# 1) wait Pages run
for i in range(20):
    j = json.loads(sh(f"curl -s --max-time 20 'https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=6'") or "{}")
    runs = [r for r in j.get("workflow_runs", []) if r.get("head_sha", "").startswith(SHA)]
    if runs:
        r = runs[0]
        if r["status"] == "completed":
            print("PAGES RUN:", r["status"], r["conclusion"])
            break
        print("  run", r["status"])
    else:
        print("  no run yet")
    time.sleep(20)
time.sleep(45)

def get(u, tries=3):
    for k in range(tries):
        p = subprocess.run(["curl", "-s", "-L", "--max-time", "60", "-A", UA,
                            u + ("&" if "?" in u else "?") + "cb=%d" % int(time.time())],
                           capture_output=True)
        if p.returncode == 0 and len(p.stdout) > 500:
            return p.stdout.decode("utf-8", "ignore")
        time.sleep(8)
    return ""

fails = []
pages = ["20261127-mili-pregnant-blood-smuggling", "20261127-mili-eu-trademark-real-cost"]
for s in pages:
    u = f"https://najieip.com/mili/blog/{s}.html"
    t = get(u)
    if not t:
        fails.append(f"{s}: no response"); continue
    h1 = len(re.findall(r"<h1[ >]", t)); ld = t.count("application/ld+json")
    og = 'og:image' in t; stars = t.count("**"); tw = 'twitter:card' in t
    ok = h1 == 1 and ld >= 2 and og and stars == 0 and tw
    print(f"{s[:45]}: bytes={len(t.encode())} h1={h1} ld={ld} og={og} tw={tw} stars={stars} -> {'OK' if ok else 'FAIL'}")
    if not ok: fails.append(f"{s}: h1={h1} ld={ld} og={og} tw={tw} stars={stars}")

# cover
code = sh("curl -s -o /dev/null -w '%{http_code}' -A '%s' --max-time 30 https://najieip.com/img/20261127-mili-pregnant-blood-smuggling.png" % UA)
print("cover img:", code)
if code.strip() != "200": fails.append("cover not 200")

# main index card
idx = get("https://najieip.com/blog/")
for s in pages:
    n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), idx))
    print(f"main index {s[:40]}: cards={n} cards_total={idx.count('article-card')}")
    if n < 1: fails.append(f"main index missing {s}")

# feed
fd = get("https://najieip.com/feed.xml")
print("feed eu:", "20261127-mili-eu-trademark-real-cost" in fd, "feed items:", fd.count("<item>"))

# mili index
mi = get("https://najieip.com/mili/blog/")
for s in pages:
    n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), mi))
    print(f"mili index {s[:40]}: {n}")
    if n < 1: fails.append(f"mili index missing {s}")

print("\nFAILURES:", fails if fails else "NONE")
