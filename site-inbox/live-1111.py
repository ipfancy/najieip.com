#!/usr/bin/env python3
"""2026-11-11 线上终验"""
import subprocess, re, json, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B = "https://najieip.com"
fails = []

def get(url, tries=3, binary=False):
    for i in range(tries):
        cmd = ["curl", "-s", "-A", UA, "--max-time", "60", "-o", "/dev/null" if binary else "/dev/stdout",
               "-w", "%{http_code}", url + (("?cb=%d" % int(time.time())) if not binary else "")]
        if binary:
            r = subprocess.run(cmd, capture_output=True, text=True)
            code = r.stdout.strip()[-3:]
            return code, ""
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        body = r.stdout[:-3]
        code = r.stdout.strip()[-3:]
        if code == "200":
            return code, body
        time.sleep(4)
    return code, body

pages = [
    f"/mili/blog/20261111-mili-earnest-money-cap.html",
    f"/mili/blog/20261112-mili-year-end-bonus-cancel.html",
    f"/mili/blog/20261111-mili-fake-patent-marking-line.html",
    f"/najie/blog/20261111-najie-same-day-dual-filing-one-choice.html",
]
for p in pages:
    code, body = get(B + p)
    h1 = len(re.findall(r"<h1[ >]", body)); ld = len(re.findall(r"application/ld\+json", body))
    ogi = 'og:image' in body
    stars = len(re.findall(r'(?<![0-9*])\*\*', body)); bt = len(re.findall(r'<p>\|', body))
    ok = code == "200" and h1 == 1 and ld >= 2 and ogi and stars == 0 and bt == 0
    print(f"{'OK ' if ok else 'FAIL'} {code} h1={h1} ld={ld} og:image={ogi} stars={stars} bt={bt} {len(body)}B {p}")
    if not ok: fails.append(p)

for p in ("/img/20261111-mili-earnest-money-cap.png", "/img/20261112-mili-year-end-bonus-cancel.png"):
    code, _ = get(B + p, binary=True)
    print(f"{'OK ' if code == '200' else 'FAIL'} {code} {p}")
    if code != "200": fails.append(p)

idx = [
    ("/mili/blog/", ["20261111-mili-earnest-money-cap", "20261111-mili-fake-patent-marking-line"], 180),
    ("/najie/blog/", ["20261111-najie-same-day-dual-filing-one-choice"], 133),
    ("/blog/", ["20261111-mili-earnest-money-cap", "20261111-mili-fake-patent-marking-line",
                "20261111-najie-same-day-dual-filing-one-choice"], 304),
]
for p, slugs, expect_cards in idx:
    code, body = get(B + p)
    n = len(re.findall(r'<div class="article-card">', body))
    hits = {s: body.count(s) for s in slugs}
    ok = code == "200" and n == expect_cards and all(v >= 1 for v in hits.values())
    print(f"{'OK ' if ok else 'FAIL'} {code} cards={n}(exp {expect_cards}) hits={hits} {len(body)}B {p}")
    if not ok: fails.append(p)

code, body = get(B + "/articles.json")
try:
    n = len(json.loads(body))
except Exception as e:
    n = -1
print(f"{'OK ' if (code == '200' and n == 250) else 'FAIL'} {code} articles.json={n}(exp 250)")
if n != 250: fails.append("/articles.json")

print("FAILURES=", fails if fails else "NONE")
