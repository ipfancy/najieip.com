#!/usr/bin/env python3
"""2026-11-28 i18n 本地结构终验"""
import json, os, re

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261124-mili-punitive-damages-one-shot"
F = []


def chk(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        F.append(msg)


for lang in ("en", "fr"):
    p = os.path.join(REPO, f"{lang}/blog/{SLUG}-{lang}.html")
    t = open(p, encoding="utf-8").read()
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ok_json = all([json.loads(s) is not None for s in lds])
    chk(len(lds) == 2 and ok_json, f"{lang} ld+json == 2 & parses")
    chk(t.count("<h1") == 1, f"{lang} h1 == 1")
    chk(t.count('name="description"') == 1 and len(re.search(r'name="description" content="([^"]*)"', t).group(1)) > 120,
        f"{lang} description > 120 chars")
    chk('og:image' in t and 'twitter:image' in t, f"{lang} og:image + twitter:image")
    hl = re.findall(r'hreflang="([^"]+)"', t)
    chk(hl == ["zh-CN", "en", "fr", "x-default"], f"{lang} hreflang 4 values {hl}")
    body_only = re.sub(r'<div class="lang-bar">.*?</div>', "", t, flags=re.S)
    chk(len(re.findall(r"[\u4e00-\u9fff]", body_only)) == 0, f"{lang} zero CJK outside lang-bar")
    chk("https://schema.org" in t and "https://***" not in t, f"{lang} schema.org intact")
    chk(t.count("*") >= 0 and "**" not in re.sub(r"<script.*?</script>", "", t, flags=re.S), f"{lang} no markdown ** leak")
    chk(f'{SLUG}-{lang}.html' in open(os.path.join(REPO, f"{lang}/blog/index.html"), encoding="utf-8").read(),
        f"{lang} index has card")
    chk(os.path.getsize(p) > 9000, f"{lang} page > 9000B")

zh = open(os.path.join(REPO, "mili/blog", f"{SLUG}.html"), encoding="utf-8").read()
hlz = re.findall(r'hreflang="([^"]+)"', zh)
chk(hlz == ["zh-CN", "en", "fr", "x-default"], f"zh hreflang 4 values {hlz}")

sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
for u in (f"https://najieip.com/en/blog/{SLUG}-en.html", f"https://najieip.com/fr/blog/{SLUG}-fr.html"):
    chk(u in sm, f"sitemap has {u.split('najieip.com')[1]}")
chk(sm.count("<loc>") == 448, f"sitemap loc == 448 (got {sm.count('<loc>')})")
blk = sm[sm.find(f"{SLUG}-en.html") - 200: sm.find(f"{SLUG}-en.html") + 200]
chk("2026-11-28" in blk, "sitemap lastmod 2026-11-28 near new loc")

print("\nFAILURES:", F if F else "NONE")
