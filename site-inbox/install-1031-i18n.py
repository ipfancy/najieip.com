#!/usr/bin/env python3
"""EN/FR 索引补卡 + sitemap 补 2 条 loc"""
import json, os, re, html

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261024-mili-personal-safety-protection-order"
data = json.load(open("/tmp/i18n_1031.json"))
TAGS = {"en": ["Family law", "Domestic violence", "Evidence"],
        "fr": ["Droit de la famille", "Violences domestiques", "Preuves"]}
DATE_TXT = {"en": "October 24, 2026", "fr": "24 octobre 2026"}

for lang in ("en", "fr"):
    p = os.path.join(REPO, f"{lang}/blog/index.html")
    t = open(p, encoding="utf-8").read()
    href = f"/{lang}/blog/{SLUG}-{lang}.html"
    if href in t:
        print(lang, "card already present — skip")
        continue
    tags = "".join(f'<span class="tag">{x}</span>' for x in TAGS[lang])
    card = (f'<div class="article-card">\n'
            f'    <h2><a href="{href}">{html.escape(data[lang]["title"])}</a></h2>\n'
            f'    <div class="meta">{tags} {DATE_TXT[lang]} · Aipunajie Patent Firm / Mili Law Firm</div>\n'
            f'    <p>{html.escape(data[lang]["description"])}</p>\n'
            f'  </div>')
    m = re.search(r'<div class="container">\s*', t)
    assert m, "container anchor not found"
    pos = m.end()
    t2 = t[:pos] + card + "\n\n  " + t[pos:]
    # 断言：只插入了卡块
    assert t2.replace(card + "\n\n  ", "", 1) == t, "insertion touched other content"
    assert '<div' in card and card.count("<div") == card.count("</div>")
    open(p, "w", encoding="utf-8").write(t2)
    print(lang, "card added | cards:", t2.count('<div class="article-card">'))

# sitemap
sm = os.path.join(REPO, "sitemap.xml")
s = open(sm, encoding="utf-8").read()
added = []
for lang in ("en", "fr"):
    loc = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    if loc not in s:
        entry = f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>2026-10-31</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
        s = s.replace("</urlset>", entry + "</urlset>", 1)
        added.append(loc)
open(sm, "w", encoding="utf-8").write(s)
print("sitemap added:", len(added), "| total loc:", s.count("<loc>"))
import xml.dom.minidom as md
md.parseString(s)
print("sitemap XML OK")
