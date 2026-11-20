#!/usr/bin/env python3
"""2026-11-21 i18n 本地终验"""
import json, re, os
REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261112-maldives-trademark-law"
ZH = f"{REPO}/najie/blog/{SLUG}.html"
FILES = {
    "en": f"{REPO}/en/blog/{SLUG}-en.html",
    "fr": f"{REPO}/fr/blog/{SLUG}-fr.html",
    "zh": ZH,
}
FAIL = []

def chk(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAIL.append(msg)

for lang, p in FILES.items():
    t = open(p, encoding="utf-8").read()
    print(f"--- {lang} {len(t.encode())} bytes ---")
    chk(t.lower().startswith("<!doctype html"), f"{lang} doctype")
    chk(t.count("<h1") == 1, f"{lang} h1==1 ({t.count('<h1')})")
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    chk(len(lds) >= 2, f"{lang} ld>={len(lds)}")
    ok = True
    for s in lds:
        try:
            json.loads(s)
        except Exception as e:
            ok = False
            print("   bad ld:", e)
    chk(ok, f"{lang} ld json parses")
    chk(t.count("https://schema.org") == len(lds), f"{lang} schema.org count==ld")
    chk("https://***" not in t, f"{lang} no masked schema.org")
    chk(t.count("<div") == t.count("</div>"), f"{lang} div balanced {t.count('<div')}/{t.count('</div>')}")
    chk("og:image" in t and f"img/{SLUG}.png" in t, f"{lang} og:image self-hosted")
    chk("twitter:card" in t and "twitter:image" in t, f"{lang} twitter card")
    chk('rel="canonical"' in t, f"{lang} canonical")
    hl = re.findall(r'hreflang="([^"]+)"', t)
    chk(sorted(set(hl)) == ["en", "fr", "x-default", "zh-CN"] and len(hl) == 4, f"{lang} hreflang four unique: {hl}")
    if lang != "zh":
        body = t[t.find("<article"):t.find("</article>")]
        chk(len(re.findall(r"[\u4e00-\u9fff]", body)) < 30, f"{lang} no CJK in article ({len(re.findall(r'[一-龥]', body))})")
        chk("**" not in body, f"{lang} no markdown **")
        chk("<table" in body or True, f"{lang} table check n/a")
        chk(f"{SLUG}-{lang}.html" in t and f'lang="{lang}"' in t, f"{lang} self url + lang attr")
    else:
        chk("**" not in t, "zh no markdown **")
        chk(t.count("og:image") == 1, "zh og:image")

# 索引卡
for lang in ("en", "fr"):
    idx = open(f"{REPO}/{lang}/blog/index.html", encoding="utf-8").read()
    n = len(re.findall(rf'<h[23][^>]*><a href="[^"]*{SLUG}-{lang}', idx))
    chk(n == 1, f"{lang} index card exactly 1 ({n})")
    chk(idx.count("<div") == idx.count("</div>"), f"{lang} index div balanced")
# 主索引：中文文是否已有卡
main = open(f"{REPO}/blog/index.html", encoding="utf-8").read()
nzh = len(re.findall(rf'<h[23][^>]*><a href="[^"]*{SLUG}', main))
print(f"INFO main index zh cards = {nzh}")
nj = open(f"{REPO}/najie/blog/index.html", encoding="utf-8").read()
print(f"INFO najie index zh cards = {len(re.findall(rf'<h[23][^>]*><a href=\"[^\"]*' + SLUG, nj))}")

sm = open(f"{REPO}/sitemap.xml", encoding="utf-8").read()
for u in (f"{SLUG}-en.html", f"{SLUG}-fr.html", f"/najie/blog/{SLUG}.html"):
    chk(u in sm, f"sitemap has {u}")
print(f"\nFAILURES={len(FAIL)}")
for f in FAIL:
    print("  -", f)
