#!/usr/bin/env python3
# 线上终验：文章页六项 + 封面 + 双索引卡 + articles.json 计数
import subprocess, re, time, sys, json, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "20261113-byd-netherlands-evidence-seizure"
BASE = "https://najieip.com"
TMP = "/Users/ziganghe/.hermes/cache/scratch"

def get(url, tries=4, wait=20, max_time=60, binary=False):
    for i in range(tries):
        cmd = ["curl", "-s", "-A", UA, "--max-time", str(max_time)]
        if binary:
            cmd += ["-o", "/dev/null", "-w", "%{http_code}", "-I"]
        cmd.append(url)
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = r.stdout
        if binary:
            if out.strip() in ("200",):
                return True, "200"
        else:
            if out and len(out) > 300:
                return True, out
        time.sleep(wait)
    return False, (out[:60] if not binary else out.strip())

fails = []
cb = int(time.time())

ok, body = get(f"{BASE}/mili/blog/{SLUG}.html?cb={cb}")
if not ok:
    fails.append(f"article page unreachable")
    body = ""
print(f"article page: {'200 len=' + str(len(body)) if ok else 'FAIL'}")

if body:
    h1 = len(re.findall(r'<h1[ >]', body))
    ld = len(re.findall(r'application/ld\+json', body))
    ogimg = bool(re.search(r'property="og:image" content="https://najieip.com/img/', body))
    desc = re.findall(r'<meta name="description" content="([^"]*)"', body)
    stars = body.count('**')
    naked = len(re.findall(r'<p>\|', body))
    schema = body.count('https://schema.org')
    print(f"  h1={h1} ld={ld} schema={schema} og:image={ogimg} desc_len={len(desc[0]) if desc else 0} stars={stars} naked_tbl={naked}")
    for cond, msg in [(h1 == 1, "h1!=1"), (ld >= 2, "ld<2"), (schema >= 2, "no @context"),
                      (ogimg, "no og:image"), (bool(desc) and len(desc[0]) > 80, "desc short"),
                      (stars == 0, "** leak"), (naked == 0, "naked table")]:
        if not cond: fails.append(msg)

ok, _ = get(f"{BASE}/img/{SLUG}.png", binary=True, wait=8, tries=4)
print("cover img:", "200" if ok else "FAIL")
if not ok: fails.append("cover img")

for path, name in [("/mili/blog/index.html", "mili index"), ("/blog/index.html", "main index")]:
    ok, b = get(f"{BASE}{path}?cb={cb}", max_time=90)
    if not ok:
        fails.append(f"{name} unreachable"); print(f"{name}: FAIL"); continue
    hit = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(SLUG), b))
    print(f"{name}: len={len(b)} card_hit={hit}")
    if hit < 1: fails.append(f"{name} no card")

ok, b = get(f"{BASE}/articles.json?cb={cb}")
try:
    data = json.loads(b)
    print("articles.json:", len(data), "| has today:", any(SLUG in (x.get('url') or '') for x in data))
except Exception as e:
    fails.append(f"articles.json parse {e}")
    print("articles.json: FAIL", e)

print("FAILURES:", fails if fails else "NONE")
