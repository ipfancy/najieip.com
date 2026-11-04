#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04 线上终验（直连 + ?cb 绕 CF 缓存）"""
import subprocess, re, json, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CB = str(int(time.time()))
FAIL = []

def get(url, binary=False):
    for i in range(3):
        try:
            r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "30", url],
                               capture_output=True, timeout=45)
            if binary:
                return r.stdout if r.stdout else b""
            return r.stdout.decode("utf-8", "ignore")
        except Exception:
            time.sleep(2)
    return b"" if binary else ""

def code(url):
    for i in range(3):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, "--max-time", "30", url],
                           capture_output=True, text=True, timeout=45)
        if r.stdout.strip() == "200":
            return 200
        time.sleep(2)
    return r.stdout.strip()

CASES = [
    ("https://najieip.com/mili/blog/20261104-mili-anti-involution-low-price.html", 2),
    ("https://najieip.com/mili/blog/20261104-mili-provisional-protection-fee.html", 2),
    ("https://najieip.com/najie/blog/20261104-najie-priority-right-reform-agenda.html", 2),
]
for url, need_ld in CASES:
    t = get(url + "?cb=" + CB)
    slug = url.rsplit("/", 1)[1]
    ld = len(re.findall(r"application/ld\+json", t))
    og = len(re.findall(r'property="og:image"', t))
    h1 = len(re.findall(r"<h1", t))
    stars = len(re.findall(r"(?<![0-9*])\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    rawtbl = len(re.findall(r"<p>\|", t))
    ok = ld >= need_ld and og == 1 and h1 == 1 and stars == 0 and rawtbl == 0
    print(f"{'OK ' if ok else 'FAIL'} {slug}: bytes={len(t.encode())} h1={h1} ld={ld} og:image={og} stars={stars} rawtbl={rawtbl}")
    if not ok: FAIL.append(slug)

print("\ncover:", code("https://najieip.com/img/20261104-mili-anti-involution-low-price.png"))
for u in ("https://najieip.com/blog/", "https://najieip.com/mili/blog/", "https://najieip.com/najie/blog/"):
    print(u, code(u))

print("\n=== live 索引卡 HIT ===")
for u, slugs in (("https://najieip.com/blog/", ["20261104-mili-anti-involution-low-price",
                                                "20261104-mili-provisional-protection-fee",
                                                "20261104-najie-priority-right-reform-agenda"]),
                 ("https://najieip.com/mili/blog/", ["20261104-mili-anti-involution-low-price",
                                                     "20261104-mili-provisional-protection-fee"]),
                 ("https://najieip.com/najie/blog/", ["20261104-najie-priority-right-reform-agenda"])):
    t = get(u + "?cb=" + CB)
    for s in slugs:
        n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), t))
        print(f"  {u} {s}: {n}")
        if n != 1: FAIL.append(u + s)

print("\n=== live articles.json ===")
aj = get("https://najieip.com/articles.json?cb=" + CB)
try:
    d = json.loads(aj)
    print("count:", len(d))
    if len(d) != 234: FAIL.append("articles.json count")
except Exception as e:
    print("ERR", e); FAIL.append("articles.json parse")

print("\nFAILURES =", FAIL if FAIL else "NONE")
