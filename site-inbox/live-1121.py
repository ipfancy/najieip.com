#!/usr/bin/env python3
"""2026-11-21 线上终验（i18n）"""
import json, re, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "20261112-maldives-trademark-law"
URLS = {
    "en": f"https://najieip.com/en/blog/{SLUG}-en.html",
    "fr": f"https://najieip.com/fr/blog/{SLUG}-fr.html",
    "zh": f"https://najieip.com/najie/blog/{SLUG}.html",
}
FAIL = []

def chk(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAIL.append(m)

def get(url, tries=3, binary=False):
    for i in range(tries):
        cmd = ["curl", "-s", "--max-time", "60", "-A", UA, f"{url}?cb={int(time.time())}"]
        if binary:
            code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "40", "-A", UA, url],
                                  capture_output=True, text=True).stdout.strip()
            return code
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout.decode("utf-8", "ignore")
        time.sleep(3)
    return ""

def code_of(url):
    for i in range(3):
        c = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "30", "-A", UA, url],
                           capture_output=True, text=True).stdout.strip()
        if c == "200":
            return c
        time.sleep(3)
    return c

for lang, u in URLS.items():
    c = code_of(u)
    chk(c == "200", f"{lang} HTTP {c}")
    t = get(u)
    if not t:
        chk(False, f"{lang} body empty")
        continue
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    chk(len(lds) >= 2, f"{lang} ld={len(lds)}")
    chk("og:image" in t, f"{lang} og:image")
    hl = sorted(set(re.findall(r'hreflang="([^"]+)"', t)))
    chk(hl == ["en", "fr", "x-default", "zh-CN"], f"{lang} hreflang {hl}")
    chk(t.count("<h1") == 1, f"{lang} h1==1")
    if lang != "zh":
        art = t[t.find("<article"):t.find("</article>")]
        n = len(re.findall(r"[\u4e00-\u9fff]", art))
        chk(n < 30, f"{lang} CJK in article = {n}")
        chk("**" not in art, f"{lang} no ** leak")
    else:
        chk("**" not in t, "zh no ** leak")

# 索引卡
for lang in ("en", "fr"):
    t = get(f"https://najieip.com/{lang}/blog/")
    n = len(re.findall(rf'<h[23][^>]*><a href="[^"]*{SLUG}-{lang}', t)) if t else 0
    chk(n == 1, f"{lang} index card online = {n} (len={len(t)})")

# 封面图
chk(code_of(f"https://najieip.com/img/{SLUG}.png") == "200", "img 200")

# sitemap
sm = get("https://najieip.com/sitemap.xml")
chk(f"{SLUG}-en.html" in sm, "sitemap EN loc")
chk(f"{SLUG}-fr.html" in sm, "sitemap FR loc")
chk(sm.count("<loc>") == 428, f"sitemap loc = {sm.count('<loc>')}")

print(f"\nFAILURES={len(FAIL)}")
for f in FAIL:
    print("  -", f)
