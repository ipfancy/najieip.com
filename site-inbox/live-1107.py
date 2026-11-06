#!/usr/bin/env python3
"""线上终验（11-07 i18n）：逐 URL 重试取终态"""
import subprocess, time, re, json

SLUG = "20261101-najie-ip-foreign-transfer-review"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
fails = []


def get(url, binary=False):
    for i in range(3):
        cmd = ["curl", "-s", "-4", "-A", UA, "--max-time", "25", "-w", "\n__CODE__%{http_code}", url]
        r = subprocess.run(cmd, capture_output=True)
        if binary:
            out = r.stdout
            body, _, code = out.rpartition(b"\n__CODE__")
            c = code.decode().strip()
            if c == "200":
                return c, body
        else:
            out = r.stdout.decode("utf-8", "replace")
            body, _, code = out.rpartition("\n__CODE__")
            if code.strip() == "200":
                return c if False else code.strip(), body
        time.sleep(5)
    return code.strip() if not binary else c, (b"" if binary else "")


cb = str(int(time.time()))
targets = [
    (f"{BASE}/en/blog/{SLUG}-en.html?cb={cb}", "en page"),
    (f"{BASE}/fr/blog/{SLUG}-fr.html?cb={cb}", "fr page"),
    (f"{BASE}/najie/blog/{SLUG}.html?cb={cb}", "zh page"),
    (f"{BASE}/en/blog/?cb={cb}", "en index"),
    (f"{BASE}/fr/blog/?cb={cb}", "fr index"),
    (f"{BASE}/sitemap.xml?cb={cb}", "sitemap"),
]
for url, label in targets:
    code, body = get(url)
    print(f"{label}: HTTP {code} bytes={len(body)}")
    if code != "200":
        fails.append(f"{label} HTTP {code}")
        continue
    if label == "en page":
        for cond, msg in [
            (body.count("application/ld+json") == 2, "en ld=2"),
            ("og:image" in body, "en og:image"),
            (re.search(r'hreflang="(zh-CN|en|fr|x-default)"', body) is not None, "en hreflang"),
            (body.count("<h2>") == 4, "en h2=4"),
            (body.count("**") == 0, "en no **"),
        ]:
            print("   ", ("PASS " if cond else "FAIL ") + msg)
            if not cond:
                fails.append(msg)
    if label == "fr page":
        for cond, msg in [
            (body.count("application/ld+json") == 2, "fr ld=2"),
            ("og:image" in body, "fr og:image"),
            (body.count("<h2>") == 4, "fr h2=4"),
            (len(re.findall(r"[\u4e00-\u9fff]", re.sub(r'<div class="lang-bar">.*?</div>', "", body, flags=re.S))) == 0, "fr no CJK"),
        ]:
            print("   ", ("PASS " if cond else "FAIL ") + msg)
            if not cond:
                fails.append(msg)
    if label == "zh page":
        for cond, msg in [
            (body.count('hreflang="') == 4, "zh hreflang=4"),
            ("application/ld+json" in body, "zh ld"),
        ]:
            print("   ", ("PASS " if cond else "FAIL ") + msg)
            if not cond:
                fails.append(msg)
    if label in ("en index", "fr index"):
        cond = SLUG in body
        print("   ", ("PASS " if cond else "FAIL ") + f"{label} card HIT")
        if not cond:
            fails.append(label + " card missing")
    if label == "sitemap":
        for lang in ("en", "fr"):
            cond = f"{BASE}/{lang}/blog/{SLUG}-{lang}.html" in body
            print("   ", ("PASS " if cond else "FAIL ") + f"sitemap {lang} loc")
            if not cond:
                fails.append("sitemap " + lang)

code, img = get(f"{BASE}/img/{SLUG}.png", binary=True)
print("cover img: HTTP", code, "bytes", len(img))
if code != "200":
    fails.append("cover 404")

print("\nFAILURES =", len(fails))
for f in fails:
    print(" -", f)
