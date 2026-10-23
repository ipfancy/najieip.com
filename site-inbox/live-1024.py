#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""线上终验：i18n 新页 + 封面 + 索引 + sitemap（带浏览器 UA，绕 CF 判 UA）"""
import re, subprocess, time, os, json

SLUG = "20261006-mili-gas-post-judgment-six-checklist"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
fails = []


def fetch(url, tries=3, binary=False):
    code, body = "000", ""
    cmd = ["curl", "-s", "-A", UA, "-m", "25", "-w", "\n__CODE__%{http_code}"]
    if binary:
        cmd += ["-o", "/dev/null"]
    for i in range(tries):
        cb = f"{url}{'&' if '?' in url else '?'}cb={int(time.time())}"
        r = subprocess.run(cmd + [cb], capture_output=True, text=True)
        out = r.stdout or ""
        code = out.rsplit("__CODE__", 1)[-1].strip() if "__CODE__" in out else "000"
        body = out.rsplit("__CODE__", 1)[0]
        if code == "200":
            return code, body
        time.sleep(3)
    return code, body


def chk(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


urls = {
    "zh": f"https://najieip.com/mili/blog/{SLUG}.html",
    "en": f"https://najieip.com/en/blog/{SLUG}-en.html",
    "fr": f"https://najieip.com/fr/blog/{SLUG}-fr.html",
    "en_idx": "https://najieip.com/en/blog/",
    "fr_idx": "https://najieip.com/fr/blog/",
    "img": f"https://najieip.com/img/{SLUG}.png",
    "blog": "https://najieip.com/blog/",
    "root": "https://najieip.com/",
    "mili": "https://najieip.com/mili/",
    "sitemap": "https://najieip.com/sitemap.xml",
}
bodies = {}
for k, u in urls.items():
    code, body = fetch(u, binary=(k == "img"))
    bodies[k] = body
    if k == "img":
        chk(code == "200", f"live {k} 200 (got {code})")
    else:
        chk(code == "200", f"live {k} 200 (got {code})")

for lang in ("en", "fr"):
    t = bodies.get(lang, "")
    chk(t.count("<h1") == 1, f"live {lang} h1==1 ({t.count('<h1')})")
    chk(t.count("application/ld+json") >= 1, f"live {lang} ld+json>=1 ({t.count('application/ld+json')})")
    chk(f"/img/{SLUG}.png" in t, f"live {lang} og:image self-hosted")
    chk("**" not in t, f"live {lang} no asterisks")
    chk(t.count("hreflang") == 4, f"live {lang} hreflang==4")
    chk(t.count("<table") == 1, f"live {lang} table present")
    chk("https://schema.org" in t, f"live {lang} schema present")

z = bodies.get("zh", "")
chk(z.count("hreflang") == 4, f"live zh hreflang==4 ({z.count('hreflang')})")
chk(f"/img/{SLUG}.png" in z, "live zh og:image self-hosted")

for lang, idx in (("en", "en_idx"), ("fr", "fr_idx")):
    chk(f"/{lang}/blog/{SLUG}-{lang}.html" in bodies.get(idx, ""), f"live {lang} index card HIT")

s = bodies.get("sitemap", "")
for lang in ("en", "fr"):
    chk(f"/{lang}/blog/{SLUG}-{lang}.html" in s, f"live sitemap {lang} loc HIT")
chk(s.count("<loc>") >= 325, f"live sitemap loc count {s.count('<loc>')}")

print("\nFAILURES:", len(fails))
for f in fails:
    print(" -", f)
