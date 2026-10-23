#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安装 2026-10-24 i18n 成果：EN/FR 索引卡 + sitemap 2 条 loc（中文页面 hreflang 已在 pages 脚本完成）"""
import html, json, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
D = json.load(open(os.path.expanduser("~/.hermes/cache/scratch/i18n_1024.json"), encoding="utf-8"))
SLUG = "20261006-mili-gas-post-judgment-six-checklist"
TODAY = "2026-10-24"


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
     ["Antitrust", "Public Utilities", "Compliance"], "October 06, 2026"),
    ("fr", f"{REPO}/fr/blog/index.html", f"/fr/blog/{SLUG}-fr.html",
     ["Concurrence", "Services publics", "Conformité"], "6 octobre 2026"),
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
    print(f"[{lang}] card inserted | cards {before} -> {after} | bytes {len(t2.encode())}")

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
               "    <changefreq>monthly</changefreq>\n"
               "    <priority>0.7</priority>\n"
               "  </url>\n")
if new:
    assert s.count("</urlset>") == 1
    s2 = s.replace("</urlset>", "".join(new) + "</urlset>", 1)
    assert s2.replace("".join(new), "", 1) == s
    open(SM, "w", encoding="utf-8").write(s2)
    print("[sitemap] loc now:", s2.count("<loc>"), "(was", s.count("<loc>"), ")")

print("DONE")
