#!/usr/bin/env python3
"""2026-11-28 线上终验：EN/FR 页 + 索引卡 + 中文页 hreflang + sitemap + 封面"""
import re, subprocess, time

SLUG = "20261124-mili-punitive-damages-one-shot"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
F = []


def curl(url, tries=3, timeout=60):
    for i in range(tries):
        p = subprocess.run(["curl", "-4", "-s", "-m", str(timeout), "-A", UA, url],
                           capture_output=True, text=True, errors="replace")
        if p.stdout and len(p.stdout) > 500:
            return p.stdout, len(p.stdout)
        time.sleep(3)
    return p.stdout or "", len(p.stdout or "")


def code(url, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-4", "-sI", "-o", "/dev/null", "-m", "30", "-A", UA,
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        if p.stdout.strip() == "200":
            return "200"
        time.sleep(3)
    return p.stdout.strip()


def chk(c, msg):
    print(("PASS " if c else "FAIL ") + msg)
    if not c:
        F.append(msg)


ts = int(time.time())
for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html?cb={ts}"
    body, n = curl(u)
    chk(n > 9000, f"{lang} page bytes {n}")
    chk(body.count("<h1") == 1, f"{lang} live h1 == 1")
    ld = len(re.findall(r'application/ld\+json', body))
    chk(ld == 2, f"{lang} live ld+json == 2 (got {ld})")
    chk("og:image" in body and "twitter:image" in body, f"{lang} live og/twitter image")
    hl = re.findall(r'hreflang="([^"]+)"', body)
    chk(hl == ["zh-CN", "en", "fr", "x-default"], f"{lang} live hreflang {hl}")
    b2 = re.sub(r'<div class="lang-bar">.*?</div>', "", body, flags=re.S)
    chk(len(re.findall(r"[\u4e00-\u9fff]", b2)) == 0, f"{lang} live zero CJK outside lang-bar")

for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/?cb={ts}"
    body, n = curl(u)
    chk(f"{SLUG}-{lang}.html" in body, f"{lang} index live has card (bytes {n})")

zh = curl(f"https://najieip.com/mili/blog/{SLUG}.html?cb={ts}")[0]
hl = re.findall(r'hreflang="([^"]+)"', zh)
chk(hl == ["zh-CN", "en", "fr", "x-default"], f"zh live hreflang {hl}")

sm = curl(f"https://najieip.com/sitemap.xml?cb={ts}")[0]
chk(sm.count("<loc>") == 448, f"sitemap live loc == 448 (got {sm.count('<loc>')})")
chk(f"{SLUG}-en.html" in sm and f"{SLUG}-fr.html" in sm, "sitemap live has both new locs")

chk(code(f"https://najieip.com/img/{SLUG}.png") == "200", "cover png 200")
for u in ("https://najieip.com/", "https://najieip.com/en/", "https://najieip.com/fr/",
          "https://najieip.com/mili/", "https://najieip.com/najie/"):
    chk(code(u) == "200", f"{u} 200")

print("\nFAILURES:", F if F else "NONE")
