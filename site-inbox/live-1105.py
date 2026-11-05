#!/usr/bin/env python3
"""Live verification after Pages build (2026-11-05) - v2 simple."""
import subprocess, time, re, json

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def fetch(url, tries=3, wait=8):
    last = (0, "")
    for i in range(tries):
        u = url + ("&" if "?" in url else "?") + "cb=%d%d" % (int(time.time()), i)
        r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "25", "-w", "\n@@CODE@@%{http_code}", u],
                           capture_output=True, text=True)
        out = r.stdout
        code_s = out.rsplit("@@CODE@@", 1)[-1].strip() if "@@CODE@@" in out else "0"
        body = out.rsplit("\n@@CODE@@", 1)[0] if "@@CODE@@" in out else ""
        code = int(code_s) if code_s.isdigit() else 0
        last = (code, body)
        if code == 200:
            return last
        time.sleep(wait)
    return last

def head_code(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sI", "-A", UA, "--max-time", "25", "-o", "/dev/null", "-w", "%{http_code}", url + "?cb=%d%d" % (int(time.time()), i)],
                           capture_output=True, text=True)
        if r.stdout.strip() == "200":
            return 200
        time.sleep(6)
    return int(r.stdout.strip() or 0) if r.stdout.strip().isdigit() else 0

fails = []
SLUG = "20261105-mili-non-compete-all-staff"
code, body = fetch("https://najieip.com/mili/blog/%s.html" % SLUG)
print("mili page", code, len(body))
if code == 200:
    tb = body[body.find("<body"):]
    checks = {
        "h1": len(re.findall(r'<h1[ >]', tb)),
        "ld": body.count("application/ld+json"),
        "og_image": 'property="og:image"' in body,
        "tables": body.count("<table"),
        "stars": tb.count("**"),
        "desc_len": len((re.search(r'name="description"\s+content="([^"]*)"', body) or [None, ""])[1]),
    }
    print(" live checks", checks)
    if checks["h1"] != 1 or checks["ld"] != 2 or not checks["og_image"] or checks["tables"] != 4 or checks["stars"] != 0 or checks["desc_len"] < 80:
        fails.append(("page-checks", checks))
else:
    fails.append(("mili-page-http", code))

c2 = head_code("https://najieip.com/img/%s.png" % SLUG)
print("cover png", c2)
if c2 != 200: fails.append(("cover", c2))

c3, main = fetch("https://najieip.com/blog/")
print("main index", c3, len(main))
if c3 == 200:
    hit = len(re.findall(r'20261105-najie-examination-15plan-foreign-filers', main))
    print(" main hits", hit, "cards", main.count('class="article-card"'))
    if hit == 0: fails.append(("main-card-missing", hit))
else:
    fails.append(("main-index-http", c3))

for u in ["https://najieip.com/najie/blog/20261105-najie-examination-15plan-foreign-filers.html",
          "https://najieip.com/mili/blog/", "https://najieip.com/najie/blog/"]:
    c = head_code(u)
    print(" ", c, u)
    if c != 200: fails.append((u, c))

c4, aj = fetch("https://najieip.com/articles.json")
if c4 == 200:
    try:
        n = len(json.loads(aj).get("articles", []))
    except Exception as e:
        n = -1
    print(" live articles.json", n)
    if n != 235: fails.append(("articles.json", n))
else:
    fails.append(("articles.json-http", c4))

print("FAILURES:", fails if fails else "NONE")
