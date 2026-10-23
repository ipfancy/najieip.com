#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地终验：EN/FR 新页 + 双索引 + sitemap + 中文页 hreflang"""
import json, os, re, xml.etree.ElementTree as ET

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261006-mili-gas-post-judgment-six-checklist"
fails = []


def chk(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


pages = {
    "en": f"{REPO}/en/blog/{SLUG}-en.html",
    "fr": f"{REPO}/fr/blog/{SLUG}-fr.html",
}
for lang, p in pages.items():
    t = open(p, encoding="utf-8").read()
    body = t[t.find("<body"):]
    chk(t.count("<h1") == 1, f"{lang} h1==1 ({t.count('<h1')})")
    chk(t.count("application/ld+json") == 1, f"{lang} ld+json==1")
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ok = True
    for b in blocks:
        try:
            json.loads(b)
        except Exception as e:
            ok = False
            print("   JSON_ERR", e)
    chk(ok, f"{lang} JSON-LD parses ({len(blocks)} block)")
    chk(t.count("og:image") == 1 and f"/img/{SLUG}.png" in t, f"{lang} og:image self-hosted")
    chk(t.count("twitter:image") == 1, f"{lang} twitter:image")
    chk(t.count("hreflang") == 4, f"{lang} hreflang==4")
    chk("**" not in t, f"{lang} no markdown asterisks")
    chk("https://***" not in t, f"{lang} no masked schema")
    chk(t.count("<table") == 1 and t.count("<tr") == 7, f"{lang} table 1 / rows 7")
    # 中文残留（EN/FR 页不该有中文正文，标题中的 SPC 中文案号除外）
    zh = re.findall(r"[\u4e00-\u9fff]", re.sub(r"<script.*?</script>", "", body, flags=re.S))
    chk(len(zh) <= 6, f"{lang} chinese residue {len(zh)} chars")
    # div 配平
    depth = 0
    bad = False
    for m in re.finditer(r"<(/?)div\b", body):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            bad = True
    chk(depth == 0 and not bad, f"{lang} div balanced (depth={depth})")

# 中文页
z = open(f"{REPO}/mili/blog/{SLUG}.html", encoding="utf-8").read()
chk(z.count("hreflang") == 4, f"zh hreflang==4 ({z.count('hreflang')})")
chk(f"/img/{SLUG}.png" in z, "zh og:image self-hosted")
chk(z.count("<h1") == 1, "zh h1==1")
chk("**" not in z, "zh no asterisks")

# 索引卡
for lang, p in (("en", f"{REPO}/en/blog/index.html"), ("fr", f"{REPO}/fr/blog/index.html")):
    t = open(p, encoding="utf-8").read()
    body = t[t.find("<body"):]
    chk(f"/{lang}/blog/{SLUG}-{lang}.html" in body, f"{lang} index card HIT")
    chk(body.count(f"/{lang}/blog/{SLUG}-{lang}.html") == 1, f"{lang} index card unique")
    depth = 0
    bad = False
    for m in re.finditer(r"<(/?)div\b", body):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            bad = True
    chk(depth == 0 and not bad, f"{lang} index div balanced")

# sitemap
sm = f"{REPO}/sitemap.xml"
try:
    ET.parse(sm)
    smok = True
except Exception as e:
    smok = False
    print("   XML_ERR", e)
s = open(sm, encoding="utf-8").read()
chk(smok, "sitemap XML parses")
for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    chk(s.count(f"<loc>{u}</loc>") == 1, f"sitemap {lang} loc unique")
chk(s.count("<url>") == s.count("</url>"), "sitemap url tags balanced")
locs = re.findall(r"<loc>([^<]+)</loc>", s)
chk(len(locs) == len(set(locs)), f"sitemap no dup loc ({len(locs)} loc)")
nomod = [u for u in re.findall(r"<url>(.*?)</url>", s, re.S) if "<lastmod>" not in u]
chk(len(nomod) == 0, f"sitemap all lastmod ({len(nomod)} missing)")

print("\nFAILURES:", len(fails))
for f in fails:
    print(" -", f)
