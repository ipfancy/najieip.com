import json, os, re

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261113-byd-netherlands-evidence-seizure"
TR = json.load(open("/Users/ziganghe/.hermes/cache/scratch/i18n-1114-translations.json"))

META = {
 "en": {
   "lang": "en", "locale": "en_US", "css_tpl": "en/blog/20261101-najie-ip-foreign-transfer-review-en.html",
   "title": "Dutch Raid Set Aside After Three Months: Three Steps Every Going-Global Company Should Know",
   "desc": "In August 2026 Dutch bailiffs seized BYD&#x27;s European records on a court order; on 11 November The Hague set that seizure aside. A practical read on the Article 1019 Rv seizure regime, the Article 1019h costs rule, and the objection file that actually decides the outcome.",
   "kw": "Dutch IP enforcement, evidence seizure, bewijsbeslag, Article 1019 Rv, Article 1019h costs, BYD JLR Ti7 dispute, cross-border IP litigation, going-global compliance",
   "meta_line": "November 13, 2026 · Cross-border IP · Evidence seizure · Mili Law Firm",
   "tags": ["Cross-border", "Evidence seizure", "Design"],
   "byline": "<p>He Zigang | Intellectual Property Lawyer | Aipunajie · Mili · Najie</p>",
   "disc1": "<p><em>This article was drafted with AI assistance; the views and judgments were reviewed and approved by the author.</em></p>",
   "disc2": "<p><em>This article reflects the author&#x27;s personal views only and does not constitute legal advice. For analysis of a specific case, please contact us.</em></p>",
   "crumb_blog": "Blog",
 },
 "fr": {
   "lang": "fr", "locale": "fr_FR", "css_tpl": "fr/blog/20261101-najie-ip-foreign-transfer-review-fr.html",
   "title": "Pays-Bas : perquisition annulée après trois mois — trois étapes à connaître avant de vous internationaliser",
   "desc": "En août 2026, des huissiers néerlandais ont saisi les documents européens de BYD sur ordonnance judiciaire ; le 11 novembre, la cour de La Haye a annulé cette saisie. Lecture pratique du régime de saisie-conservat de l&#x27;article 1019 Rv, de la règle de coûts de l&#x27;article 1019h et du mémoire d&#x27;opposition qui décide réellement de l&#x27;issue.",
   "kw": "protection de la PI aux Pays-Bas, saisie-conservat, article 1019 Rv, article 1019h, litige BYD JLR Ti7, contentieux transfrontalier de la PI, conformité à l&#x27;international",
   "meta_line": "13 novembre 2026 · PI transfrontalière · Saisie-conservat · Cabinet Mili",
   "tags": ["Transfrontalier", "Saisie-conservat", "Dessins et modèles"],
   "byline": "<p>He Zigang | Avocat en propriété intellectuelle | Aipunajie · Mili · Najie</p>",
   "disc1": "<p><em>Cet article a été rédigé avec l&#x27;aide d&#x27;une IA et révisé par l&#x27;auteur.</em></p>",
   "disc2": "<p><em>Cet article ne représente que l&#x27;opinion personnelle de l&#x27;auteur et ne constitue pas un avis juridique. Pour l&#x27;analyse d&#x27;un dossier précis, n&#x27;hésitez pas à nous contacter.</em></p>",
   "crumb_blog": "Blog",
 },
}
ZH_URL = f"https://najieip.com/mili/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"

def css_of(tpl):
    t = open(os.path.join(REPO, tpl)).read()
    m = re.search(r"<style>.*?</style>", t, re.S)
    return m.group(0)

def build(lang):
    m = META[lang]
    url = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    home = f"https://najieip.com/{lang}/"
    ld1 = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": m["title"], "description": re.sub(r"&#x27;", "'", m["desc"]),
        "inLanguage": lang,
        "author": {"@type": "Person", "name": "He Zigang", "jobTitle": "Intellectual Property Lawyer",
                   "worksFor": [{"@type": "Organization", "name": "Aipunajie Patent Firm"},
                                {"@type": "Organization", "name": "Mili Law Firm"}]},
        "publisher": {"@type": "Organization", "name": "Aipunajie Patent Firm", "url": "https://najieip.com"},
        "image": IMG, "datePublished": "2026-11-13", "dateModified": "2026-11-14",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "isBasedOn": {"@type": "Article", "@id": ZH_URL},
        "translationOfWork": {"@type": "Article", "@id": ZH_URL},
        "keywords": m["kw"],
    }
    ld2 = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": m["crumb_blog"], "item": home + "blog/"},
        {"@type": "ListItem", "position": 3, "name": m["title"], "item": url}]}
    head = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{m['desc']}">
<meta name="keywords" content="{m['kw']}">
<title>{m['title']} — Aipunajie Patent Firm</title>
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{m['title']}">
<meta property="og:description" content="{m['desc']}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{m['locale']}">
<meta property="og:site_name" content="Aipunajie Patent Firm">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{m['title']}">
<meta name="twitter:description" content="{m['desc']}">
<meta name="twitter:image" content="{IMG}">
<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">
<link rel="alternate" hreflang="en" href="https://najieip.com/en/blog/{SLUG}-en.html">
<link rel="alternate" hreflang="fr" href="https://najieip.com/fr/blog/{SLUG}-fr.html">
<link rel="alternate" hreflang="x-default" href="{ZH_URL}">
{css_of(m['css_tpl'])}
<script type="application/ld+json">
{json.dumps(ld1, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(ld2, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<div class="lang-bar">
  <a href="{ZH_URL}">中文</a>
  <a href="https://najieip.com/en/blog/{SLUG}-en.html"{' class="active"' if lang == 'en' else ''}>EN</a>
  <a href="https://najieip.com/fr/blog/{SLUG}-fr.html"{' class="active"' if lang == 'fr' else ''}>FR</a>
</div>
<header><a href="/{lang}/">Aipunajie Patent Firm</a></header>
<div class="container">
<article>
<h1>{m['title']}</h1>
<div class="meta">{m['meta_line']}</div>
{TR[lang].strip()}
{m['byline']}
{m['disc1']}
{m['disc2']}
<div class="disclaimer">This is a machine-translated version of our Chinese original article for reference. The Chinese version is the authoritative source.</div>
</article>
</div>
<footer><a href="/">Aipunajie Patent Firm</a> · Mili Law Firm · Najie IP — All rights reserved</footer>
</body>
</html>
"""
    path = os.path.join(REPO, lang, "blog", f"{SLUG}-{lang}.html")
    open(path, "w").write(head)
    print("wrote", path, len(head), "chars")
    return head

en = build("en")
fr = build("fr")

# ---- 索引卡 ----
def card(lang):
    m = META[lang]
    tags = "".join(f'<span class="tag">{t}</span>' for t in m["tags"])
    date = "November 13, 2026" if lang == "en" else "13 novembre 2026"
    org = "Mili Law Firm" if lang == "en" else "Cabinet Mili"
    short = (m["desc"][:230].rsplit(" ", 1)[0] + "…") if len(m["desc"]) > 230 else m["desc"]
    return (f'<div class="article-card">\n'
            f'    <h2><a href="/{lang}/blog/{SLUG}-{lang}.html">{m["title"]}</a></h2>\n'
            f'    <div class="meta">{tags} {date} · {org}</div>\n'
            f'    <p>{short}</p>\n'
            f'  </div>')

for lang in ("en", "fr"):
    p = os.path.join(REPO, lang, "blog", "index.html")
    t = open(p).read()
    if f"{SLUG}-{lang}.html" in t:
        print("card exists, skip", lang); continue
    c = card(lang)
    n0 = t.count('<div class="article-card">')
    t2 = t.replace('<div class="container">', '<div class="container">\n\n  ' + c, 1)
    n1 = t2.count('<div class="article-card">')
    assert n1 == n0 + 1, (n0, n1)
    assert t2.count("<div") - t.count("<div") == c.count("<div"), "div imbalance"
    open(p, "w").write(t2)
    print("card added", lang, n0, "->", n1)

# ---- 中文页 hreflang ----
zp = os.path.join(REPO, "mili/blog", f"{SLUG}.html")
zt = open(zp).read()
if 'hreflang="en"' not in zt:
    block = (f'<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">\n'
             f'<link rel="alternate" hreflang="en" href="https://najieip.com/en/blog/{SLUG}-en.html">\n'
             f'<link rel="alternate" hreflang="fr" href="https://najieip.com/fr/blog/{SLUG}-fr.html">\n'
             f'<link rel="alternate" hreflang="x-default" href="{ZH_URL}">\n')
    zt2 = zt.replace("</head>", block + "</head>", 1)
    open(zp, "w").write(zt2)
    print("zh hreflang added, hreflang count =", zt2.count("hreflang"))
else:
    print("zh hreflang already present:", zt.count("hreflang"))

# ---- sitemap ----
sp = os.path.join(REPO, "sitemap.xml")
st = open(sp).read()
adds = []
for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    if u in st:
        continue
    adds.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-11-14</lastmod>\n"
                f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n")
if adds:
    n0 = st.count("<url>")
    st2 = st.replace("</urlset>", "".join(adds) + "</urlset>", 1)
    open(sp, "w").write(st2)
    print("sitemap", n0, "->", st2.count("<url>"))
else:
    print("sitemap already has both")
