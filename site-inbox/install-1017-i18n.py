#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安装 2026-10-17 i18n 成果：EN/FR 索引卡 + 中文权威页 hreflang + sitemap 2 条 loc"""
import html, json, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
D = json.load(open(os.path.expanduser("~/.hermes/cache/scratch/i18n_1017.json"), encoding="utf-8"))
SLUG = "20261009-mili-ai-short-drama-token-evidence"
ZH_PATH = f"{REPO}/mili/blog/{SLUG}.html"
ZH_URL = f"https://najieip.com/mili/blog/{SLUG}.html"
TODAY = "2026-10-17"


def esc(s):
    return html.escape(s, quote=False)


def build_card(title, href, tags, dateline, desc):
    tagspans = "".join(f'<span class="tag">{t}</span>' for t in tags)
    return ('<div class="article-card">\n'
            f'    <h2><a href="{href}">{esc(title)}</a></h2>\n'
            f'    <div class="meta">{tagspans} {dateline} · Aipunajie Patent Firm / Mili Law Firm</div>\n'
            f'    <p>{esc(desc)}</p>\n'
            '  </div>')


JOBS = [
    ("en", f"{REPO}/en/blog/index.html", f"/en/blog/{SLUG}-en.html",
     ["AI & Copyright", "Audiovisual Work", "Evidence"], "October 09, 2026"),
    ("fr", f"{REPO}/fr/blog/index.html", f"/fr/blog/{SLUG}-fr.html",
     ["Droit d'auteur", "IA générative", "Preuves"], "9 octobre 2026"),
]

for lang, path, href, tags, dateline in JOBS:
    t = open(path, encoding="utf-8").read()
    before = t[t.find("<body"):].count('<div class="article-card">')
    if href in t:
        print(f"[{lang}] card already present, skip")
        continue
    card = build_card(D[lang]["title"], href, tags, dateline, D[lang]["description"])
    idx = t.find('  <div class="article-card">')
    assert idx > 0, f"{lang}: anchor not found"
    ins = "  " + card + "\n\n"
    t2 = t[:idx] + ins + t[idx:]
    assert t2.replace(ins, "", 1) == t, f"{lang}: text outside insert changed"
    open(path, "w", encoding="utf-8").write(t2)
    after = t2[t2.find("<body"):].count('<div class="article-card">')
    print(f"[{lang}] card inserted | cards {before} -> {after}")

z = open(ZH_PATH, encoding="utf-8").read()
if 'hreflang="en"' in z:
    print("[zh] hreflang already present, skip")
else:
    block = (f'<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">\n'
             f'<link rel="alternate" hreflang="en" href="https://najieip.com/en/blog/{SLUG}-en.html">\n'
             f'<link rel="alternate" hreflang="fr" href="https://najieip.com/fr/blog/{SLUG}-fr.html">\n'
             f'<link rel="alternate" hreflang="x-default" href="{ZH_URL}">\n')
    assert "</head>" in z
    z2 = z.replace("</head>", block + "</head>", 1)
    assert z2.replace(block, "", 1) == z
    open(ZH_PATH, "w", encoding="utf-8").write(z2)
    print("[zh] hreflang 4 values added ->", len(z2.encode()), "bytes")

SM = f"{REPO}/sitemap.xml"
s = open(SM, encoding="utf-8").read()
new = []
for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    if f"<loc>{u}</loc>" in s:
        print(f"[sitemap] {u} already present")
        continue
    new.append("  <url>\n"
               f"    <loc>{u}</loc>\n"
               f"    <lastmod>{TODAY}</lastmod>\n"
               "    <changefreq>weekly</changefreq>\n"
               "    <priority>0.8</priority>\n"
               "  </url>\n")
if new:
    assert s.count("</urlset>") == 1
    s2 = s.replace("</urlset>", "".join(new) + "</urlset>", 1)
    assert s2.replace("".join(new), "", 1) == s
    open(SM, "w", encoding="utf-8").write(s2)
    print("[sitemap] loc now:", s2.count("<loc>"), "(was", s.count("<loc>"), ")")

print("DONE")
