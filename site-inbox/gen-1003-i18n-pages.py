#!/usr/bin/env python3
# 2026-10-03 生成 EN/FR 页面（ART-2026-0097 德国实用新型）
import json, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
D = json.load(open("/Users/ziganghe/.hermes/cache/scratch/i18n_1003.json", encoding="utf-8"))

SLUG = "20260928-german-utility-model-offense"
ZH = f"https://najieip.com/mili/blog/{SLUG}.html"
IMG = "https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200"

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
article table { width:100%; border-collapse:collapse; margin:20px 0; font-size:15px; }
article th, article td { border:1px solid #e2e8f0; padding:10px 12px; text-align:left; }
article th { background:#f1f5f9; color:var(--primary); }
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
  "datePublished": "2026-09-28",
  "dateModified": "2026-10-03",
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
<header><a href="/">Aipunajie Patent Firm</a></header>
<div class="container">
<article>
<h1>@@TITLE@@</h1>
<div class="meta">@@DATELINE@@ · Cross-border IP · Aipunajie Patent Firm / Mili Law Firm</div>
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
        "dateline": "September 28, 2026",
        "disclaim": "This article represents only the author's personal views and does not constitute legal advice. For specific case analysis, welcome to contact us.",
        "path": f"{REPO}/en/blog/{SLUG}-en.html",
        "url": f"https://najieip.com/en/blog/{SLUG}-en.html",
    },
    "fr": {
        "lang": "fr", "locale": "fr_FR", "author": "He Zigang",
        "dateline": "28 septembre 2026",
        "disclaim": "Cet article ne représente que l'opinion personnelle de l'auteur et ne constitue pas un avis juridique. Pour l'analyse d'un dossier précis, n'hésitez pas à nous contacter.",
        "path": f"{REPO}/fr/blog/{SLUG}-fr.html",
        "url": f"https://najieip.com/fr/blog/{SLUG}-fr.html",
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
    open(c["path"], "w", encoding="utf-8").write(t)
    print(lang, "->", c["path"], len(t.encode()), "bytes | ld:", t.count("application/ld+json"),
          "| og:image:", t.count("og:image"), "| hreflang:", t.count("hreflang"))
