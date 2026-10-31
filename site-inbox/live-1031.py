#!/usr/bin/env python3
"""Live verification after push (2026-10-31)."""
import subprocess, re, json, time, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
TS = int(time.time())
fails = []

def get(url, tries=3, head=False):
    for _ in range(tries):
        cmd = f'curl -s -A "{UA}" -m 25 ' + ("-I -o /dev/null -w '%{http_code}' " if head else "") + f'"{url}"'
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        out = r.stdout
        if head:
            c = out.strip()
            if c == "200":
                return c, ""
        elif out and "<html" in out.lower():
            return "200", out
        time.sleep(8)
    return (out.strip() if head else "000"), ("" if head else out)

print("=== HTTP + six-check on live article pages ===")
pages = ["najie/blog/20261031-najie-specialized-sme-patent-screen.html",
         "najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html",
         "mili/blog/20261031-mili-mofcom-trade-secret-sanctions.html"]
for p in pages:
    code, body = get(f"https://najieip.com/{p}?cb={TS}")
    if code != "200":
        fails.append(f"{p} HTTP {code}"); print(code, p); continue
    h1 = len(re.findall(r"<h1[ >]", body)); ld = body.count("application/ld+json")
    og = 'property="og:image"' in body; desc = re.search(r'<meta name="description" content="([^"]*)"', body)
    dl = len(desc.group(1)) if desc else 0
    stars = body.count("**")
    ok = h1 == 1 and ld >= 2 and og and dl > 80 and stars == 0
    print(f"{code} {p} h1={h1} ld={ld} ogimage={og} desc={dl} stars={stars} {'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append(f"{p} six-check h1={h1} ld={ld} og={og} desc={dl} stars={stars}")

print("\n=== cover image ===")
code, _ = get(f"https://najieip.com/img/20261031-mili-ai-product-image-review-tool-neutrality.png", head=True)
print(code, "img png"); 
if code != "200": fails.append("cover png " + code)

print("\n=== index cards on live ===")
for url, slugs in [("https://najieip.com/blog/", [s.split("/")[-1] for s in pages]),
                   ("https://najieip.com/najie/blog/", ["20261031-najie-specialized-sme-patent-screen.html", "20261031-mili-ai-product-image-review-tool-neutrality.html"]),
                   ("https://najieip.com/mili/blog/", ["20261031-mili-mofcom-trade-secret-sanctions.html"])]:
    code, body = get(f"{url}?cb={TS}")
    if code != "200":
        fails.append(f"{url} HTTP {code}"); print(code, url); continue
    for s in slugs:
        hit = s in body
        print(("HIT  " if hit else "MISS ") + s + "  <- " + url)
        if not hit: fails.append(f"card miss {s} at {url}")

print("\n=== aipunajie dead cards removed on live ===")
code, body = get(f"https://najieip.com/aipunajie/blog/?cb={TS}")
for s in ["20260723-weituo-chuangzuo-banquan-xieyi-bi-keng.html", "wipo-ai-ip-dialogue-20260725.html", "wipo-free-databases-20260726.html"]:
    print(("STILL " if s in body else "GONE  ") + s)
    if s in body: fails.append("dead card still live " + s)

print("\n=== live articles.json ===")
code, body = get(f"https://najieip.com/articles.json?cb={TS}")
try:
    arr = json.loads(body)
    print("entries:", len(arr))
    if len(arr) != 226: fails.append(f"articles.json live {len(arr)} != 226")
except Exception as e:
    print("parse err", e); fails.append("articles.json parse")

print("\nFAILURES:", fails if fails else "NONE")
