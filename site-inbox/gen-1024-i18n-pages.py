#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-24 生成 EN/FR 页（ART-2026-0103 腾冲燃气案·六条清单）— 复用 1012/1017 house style
另：中文页补 4 条 hreflang + og:image 改自托管真实封面
"""
import json, os, re, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
D = json.load(open(os.path.expanduser("~/.hermes/cache/scratch/i18n_1024.json"), encoding="utf-8"))

SLUG = "20261006-mili-gas-post-judgment-six-checklist"
ZH = f"https://najieip.com/mili/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"

# 1) 封面入库
src = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-{SLUG}.png")
dst = f"{REPO}/img/{SLUG}.png"
if not os.path.exists(src):
    raise SystemExit("cover not found: " + src)
shutil.copy2(src, dst)
print("cover copied ->", dst, os.path.getsize(dst), "bytes")

# 2) 中文页：hreflang 四值 + 自托管 og:image
zhp = f"{REPO}/mili/blog/{SLUG}.html"
zt = open(zhp, encoding="utf-8").read()
if 'hreflang="zh-CN"' not in zt:
    links = (f'<link rel="alternate" hreflang="zh-CN" href="{ZH}">\n'
             f'<link rel="alternate" hreflang="en" href="https://najieip.com/en/blog/{SLUG}-en.html">\n'
             f'<link rel="alternate" hreflang="fr" href="https://najieip.com/fr/blog/{SLUG}-fr.html">\n'
             f'<link rel="alternate" hreflang="x-default" href="{ZH}">\n')
    zt = zt.replace("</head>", links + "</head>", 1)
zt = re.sub(r'<meta property="og:image" content="[^"]*">',
            f'<meta property="og:image" content="{IMG}">', zt, count=1)
if 'twitter:image' not in zt:
    zt = zt.replace("</head>", f'<meta name="twitter:image" content="{IMG}">\n</head>', 1)
open(zhp, "w", encoding="utf-8").write(zt)
print("zh patched: hreflang=", zt.count("hreflang"), "| og:image self-hosted:", IMG in zt,
      "| twitter:image:", "twitter:image" in zt, "| bytes:", len(zt.encode()))

TPL = """<!DOCTYPE html>
<html lang="@@LANG@@">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="@@DESC@@">
<meta name="keywords" content="@@KW@@">
<title>@@TITLE@@ — Aipunajie Patent Firm</title>
<link rel="canonical" href="@@URL@@">
<meta property="og:type" content="article">
<meta property="og:title" content="@@TITLE@@">
<meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@URL@@">
<meta property="og:locale" content="@@LOCALE@@">
<meta property="og:image" content="@@IMG@@">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="@@TITLE@@">
<meta name="twitter:description" content="@@DESC@@">
<meta name="twitter:image" content="@@IMG@@">
<link rel="alternate" hreflang="zh-CN" href="@@ZH@@">
<link rel="alternate" hreflang="en" href="https://najieip.com/en/blog/@@SLUG@@-en.html">
<link rel="alternate" hreflang="fr" href="https://najieip.com/fr/blog/@@SLUG@@-fr.html">
<link rel="alternate" hreflang="x-default" href="@@ZH@@">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<style>
:root { --primary: #1F4E79; --accent: #C0A060; --text: #333; --text-light: #666; --bg: #F8F9FA; --white: #fff; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Inter', 'Noto Sans SC', sans-serif; color: var(--text); line-height:1.9; }
.lang-bar { background: #1a1a2e; padding: 6px 48px; display: flex; justify-content: flex-end; align-items: center; gap: 6px; font-size: 12px; }
.lang-bar a { color: rgba(255,255,255,0.5); text-decoration: none; padding: 4px 12px; border-radius: 14px; }
.lang-bar a.active { color: var(--accent); background: rgba(192,160,96,0.15); font-weight: 700; }
header { background: var(--primary); padding: 20px 48px; text-align:center; }
header a { color: var(--white); text-decoration:none; font-size:20px; font-weight:700; }
.container { max-width: 740px; margin: 0 auto; padding: 48px 24px; }
article h1 { font-size:32px; color: var(--primary); margin-bottom:8px; line-height:1.3; }
article .meta { font-size:14px; color: var(--text-light); margin-bottom:32px; }
article h2 { font-size:22px; color: var(--primary); margin: 40px 0 12px; padding-bottom:6px; border-bottom:2px solid var(--accent); }
article h3 { font-size:18px; color: var(--primary); margin: 24px 0 8px; }
article p { margin-bottom:16px; font-size:16px; }
article ul, article ol { margin: 12px 0 12px 24px; }
article li { margin-bottom:6px; }
article strong { color: var(--primary); }
article a { color: var(--primary); text-decoration:underline; }
article blockquote { background: #fefce8; border-left:4px solid var(--accent); padding:12px 20px; margin:20px 0; font-style:italic; }
article table { width:100%; border-collapse:collapse; margin:20px 0; font-size:14px; }
article th { background: var(--primary); color:#fff; padding:10px 12px; text-align:left; font-weight:600; }
article td { border-bottom:1px solid #e5e7eb; padding:10px 12px; vertical-align:top; }
article tr:nth-child(even) td { background:#f8f9fa; }
.disclaimer { background:#fefce8; border-left:4px solid #e5b73c; padding:14px 20px; margin:24px 0; font-size:13px; color:#666; }
footer { background:#1a1a2e; color:rgba(255,255,255,0.6); padding:32px; text-align:center; font-size:13px; margin-top:48px; }
footer a { color: var(--accent); text-decoration:none; }
</style>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "@@TITLE@@",
  "description": "@@DESC@@",
  "inLanguage": "@@LANG@@",
  "author": {"@type": "Person", "name": "@@AUTHOR@@", "jobTitle": "Intellectual Property Lawyer",
             "worksFor": [{"@type": "Organization", "name": "Aipunajie Patent Firm"},
                          {"@type": "Organization", "name": "Mili Law Firm"}]},
  "publisher": {"@type": "Organization", "name": "Aipunajie Patent Firm", "url": "https://najieip.com"},
  "datePublished": "2026-10-06",
  "dateModified": "2026-10-24",
  "mainEntityOfPage": {"@type": "WebPage", "@id": "@@URL@@"},
  "isBasedOn": {"@type": "Article", "@id": "@@ZH@@"},
  "translationOfWork": {"@type": "Article", "@id": "@@ZH@@"}
}
</script>
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "c80241f3caa4e708a12ed93baec1bde"}'></script>
</head>
<body>
<div class="lang-bar">
  <a href="@@ZH@@">中文</a>
  <a href="/en/blog/@@SLUG@@-en.html"@@ACT_EN@@>EN</a>
  <a href="/fr/blog/@@SLUG@@-fr.html"@@ACT_FR@@>FR</a>
</div>
<header><a href="/en/">Aipunajie Patent Firm</a></header>
<div class="container">
<article>
<h1>@@TITLE@@</h1>
<div class="meta">@@DATELINE@@ · Antitrust &amp; Public Utilities · Mili Law Firm / Aipunajie Patent Firm</div>
@@BODY@@
<p><em>@@DISCLAIM@@</em></p>
<div class="disclaimer">This is a machine-translated version of our Chinese original article for reference. The Chinese version is the authoritative source.</div>
</article>
</div>
<footer><a href="/">Aipunajie Patent Firm</a> · Mili Law Firm · Najie IP — All rights reserved</footer>
</body>
</html>
"""

CFG = {
    "en": {
        "lang": "en", "locale": "en_US", "author": "He Zigang",
        "dateline": "October 6, 2026",
        "disclaim": "This article represents only the author's personal views and does not constitute legal advice. For specific case analysis, welcome to contact us.",
        "path": f"{REPO}/en/blog/{SLUG}-en.html",
        "url": f"https://najieip.com/en/blog/{SLUG}-en.html",
        "h2n": 5,
    },
    "fr": {
        "lang": "fr", "locale": "fr_FR", "author": "He Zigang",
        "dateline": "6 octobre 2026",
        "disclaim": "Cet article ne représente que l'opinion personnelle de l&#x27;auteur et ne constitue pas un avis juridique. Pour l&#x27;analyse d&#x27;un dossier précis, n&#x27;hésitez pas à nous contacter.",
        "path": f"{REPO}/fr/blog/{SLUG}-fr.html",
        "url": f"https://najieip.com/fr/blog/{SLUG}-fr.html",
        "h2n": 5,
    },
}

for lang, c in CFG.items():
    d = D[lang]
    t = TPL
    t = t.replace("@@SLUG@@", SLUG).replace("@@ZH@@", ZH).replace("@@IMG@@", IMG)
    t = t.replace("@@LANG@@", c["lang"]).replace("@@LOCALE@@", c["locale"])
    t = t.replace("@@AUTHOR@@", c["author"]).replace("@@DATELINE@@", c["dateline"])
    t = t.replace("@@DISCLAIM@@", c["disclaim"]).replace("@@URL@@", c["url"])
    t = t.replace("@@TITLE@@", d["title"]).replace("@@DESC@@", d["description"])
    t = t.replace("@@KW@@", ", ".join(d["keywords"]))
    t = t.replace("@@ACT_EN@@", ' class="active"' if lang == "en" else "")
    t = t.replace("@@ACT_FR@@", ' class="active"' if lang == "fr" else "")
    t = t.replace("@@BODY@@", d["html_body"])
    assert "@@" not in t, f"{lang}: unreplaced placeholder"
    assert t.count("<h1") == 1, f"{lang}: h1 count {t.count('<h1')}"
    assert "**" not in t, f"{lang}: markdown leak"
    assert "https://***" not in t, f"{lang}: masked schema"
    assert t.count("https://schema.org") == 1, f"{lang}: schema {t.count('https://schema.org')}"
    assert t.count("hreflang") == 4, f"{lang}: hreflang {t.count('hreflang')}"
    assert t.count("<h2>") == c["h2n"], f"{lang}: h2 count {t.count('<h2>')}"
    assert t.count("<table") == 1, f"{lang}: table {t.count('<table')}"
    assert t.count("<tr") == 7, f"{lang}: tr {t.count('<tr')}"
    for k, v in re.findall(r'<meta (?:property|name)="((?:og|twitter):[a-z_]+)" content="([^"]*)"', t):
        if k in ("og:type", "twitter:card", "og:locale"):
            continue
        assert len(v) > 20, f"{lang}: suspicious short meta {k}: {v[:40]}"
    open(c["path"], "w", encoding="utf-8").write(t)
    print(lang, "->", c["path"], len(t.encode()), "bytes | ld:", t.count("application/ld+json"),
          "| og:image:", t.count("og:image"), "| hreflang:", t.count("hreflang"),
          "| h2:", t.count("<h2>"), "| table:", t.count("<table"))
