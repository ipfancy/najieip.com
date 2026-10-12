#!/usr/bin/env python3
# 2026-10-12 i18n 结构终验
import json, os, re, xml.etree.ElementTree as ET

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "bambu-stratasys-fto-decision-tree-20261004"
FAIL = []


def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        FAIL.append(msg)


def div_balance(t):
    depth = 0
    bad = False
    for m in re.finditer(r"<(/?)div\b", t):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            bad = True
    return depth, bad


print("=== EN/FR pages ===")
for lang in ("en", "fr"):
    p = f"{REPO}/{lang}/blog/{SLUG}-{lang}.html"
    t = open(p, encoding="utf-8").read()
    print(f"[{lang}] {os.path.getsize(p)} bytes")
    check(t.count("<h1") == 1, f"{lang} h1 == 1")
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    check(len(lds) >= 1, f"{lang} ld+json blocks >= 1 ({len(lds)})")
    for i, b in enumerate(lds):
        try:
            json.loads(b)
            print(f"    JSON-LD[{i}] parses OK")
        except Exception as e:
            check(False, f"{lang} JSON-LD[{i}] parse: {e}")
    check(t.count("og:image") == 1, f"{lang} og:image".strip())
    check("**" not in t, f"{lang} no markdown asterisks")
    check("<!--" not in t, f"{lang} no HTML comments")
    check(t.count("https://schema.org") >= 1, f"{lang} schema.org literal present")
    check("https://***" not in t, f"{lang} no masked schema")
    check(t.count("hreflang") == 4, f"{lang} hreflang x4")
    check(t.count("<h2>") >= 4, f"{lang} h2 >= 4")
    check(t.count("<table") == 1 and t.count("</table>") == 1, f"{lang} one table")
    d, bad = div_balance(t)
    check(d == 0 and not bad, f"{lang} div balance == 0 (depth={d}, neg={bad})")
    # 数字保真：按语言各自的写法核（EN 用小数点，FR 用逗号；见 2026-09-19 行规）
    NUMS = {"en": ["27.6 million", "82.8 million", "14.2 million", "10.6 million", "2.8 million", "190 million", "3.62 million", "9.6 billion"],
            "fr": ["27,6 millions", "82,8 millions", "14,2 millions", "10,6 millions", "2,8 millions", "190 millions", "3,62 millions", "9,6 milliards"]}
    for tok in NUMS[lang] + ["9,421,713", "7,555,357", "EP2964450", "337"]:
        check(tok in t, f"{lang} token {tok}")

print("\n=== indexes ===")
for lang in ("en", "fr"):
    p = f"{REPO}/{lang}/blog/index.html"
    t = open(p, encoding="utf-8").read()
    body = t[t.find("<body"):]
    n = body.count('<div class="article-card">')
    check(n == 20, f"{lang}/blog cards == 20 (got {n})")
    d, bad = div_balance(t)
    check(d == 0 and not bad, f"{lang}/blog div balance == 0 ({d}, neg={bad})")
    href = f"/{lang}/blog/{SLUG}-{lang}.html"
    i = body.find(href)
    check(i > 0, f"{lang}/blog contains new card href")
    # 新卡须为容器首卡
    first = body.find('<div class="article-card">')
    check(body.find(href) < body.find('<div class="article-card">') + 400,
          f"{lang}/blog new card near top")

print("\n=== zh authoritative page ===")
p = f"{REPO}/mili/blog/{SLUG}.html"
t = open(p, encoding="utf-8").read()
check(t.count("hreflang") == 4, "zh hreflang x4")
d, bad = div_balance(t)
check(d == 0 and not bad, f"zh div balance == 0 ({d}, neg={bad})")
check("<h1" in t, "zh has h1")

print("\n=== sitemap ===")
s = open(f"{REPO}/sitemap.xml", encoding="utf-8").read()
try:
    ET.fromstring(s)
    print("  PASS  sitemap valid XML")
except Exception as e:
    check(False, f"sitemap XML: {e}")
check(s.count("<loc>") == 304, f"sitemap loc == 304 (got {s.count('<loc>')})")
for lang in ("en", "fr"):
    check(f"<loc>https://najieip.com/{lang}/blog/{SLUG}-{lang}.html</loc>" in s, f"sitemap has {lang} loc")

print("\n=== RESULT ===")
print("FAILURES:", len(FAIL))
for f in FAIL:
    print("  -", f)
