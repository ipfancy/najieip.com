#!/usr/bin/env python3
"""GEO/i18n 2026-11-07: build EN + FR pages for ART-2026-0118 (专利出海第二道闸),
insert blog index cards, add hreflang to zh page, extend sitemap."""
import json, os, re, html

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261101-najie-ip-foreign-transfer-review"
ZH_PATH = f"najie/blog/{SLUG}.html"
ZH_URL = f"https://najieip.com/najie/blog/{SLUG}.html"
EN_URL = f"https://najieip.com/en/blog/{SLUG}-en.html"
FR_URL = f"https://najieip.com/fr/blog/{SLUG}-fr.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
DATE = "2026-11-01"
TODAY = "2026-11-07"

TPL = open(os.path.join(REPO, "en/blog/20261024-mili-personal-safety-protection-order-en.html"), encoding="utf-8").read()
STYLE = re.search(r"<style>.*?</style>", TPL, re.S).group(0).replace("https://***", "https://schema.org")

data = json.load(open("/Users/ziganghe/.hermes/cache/scratch/i18n_1107.json"))

H2 = {
    "en": [
        ("1. What the gate covers: four IP categories, three triggering acts",
         "<p>First, what does it cover?</p>"),
        ("2. Four misjudgments that cost deals",
         "<p>Let me go through the four misjudgments one by one.</p>"),
        ("3. MOFCOM Announcement No. 48: a second procedure running in parallel",
         "<p>At this point, some may think this is an old 2018 document"),
        ("4. A five-question self-check to run before you sign",
         "<p>Finally, here is a self-check table with five questions"),
    ],
    "fr": [
        ("1. Ce que le verrou couvre : quatre catégories de droits, trois opérations déclenchantes",
         "<p>Voyons d'abord ce qui est couvert.</p>"),
        ("2. Quatre erreurs d'appréciation qui font échouer les opérations",
         "<p>Prenons les quatre erreurs d'appréciation, une par une.</p>"),
        ("3. Annonce n° 48 du MOFCOM : une seconde procédure menée en parallèle",
         "<p>À ce stade, certains pensent peut-être que ce régime est un vieux document de 2018"),
        ("4. Une grille de cinq questions à passer avant de signer",
         "<p>Pour finir, une grille d'auto-évaluation, cinq questions"),
    ],
}

SIG = {
    "en": "<p>He Zigang | Intellectual Property Lawyer | Aipunajie · Mili · Najie</p>",
    "fr": "<p>He Zigang | Avocat en propriété intellectuelle | Aipunajie · Mili · Najie</p>",
}
AI_NOTE = {
    "en": "<p><em>This article was drafted with AI assistance and reviewed by the author.</em></p>",
    "fr": "<p><em>Cet article a été rédigé avec l'aide d'une IA et révisé par l'auteur.</em></p>",
}
DISC = {
    "en": ("<p><em>This article represents the author's personal views only and does not constitute legal advice. "
           "For analysis of a specific case, please contact us.</em></p>"),
    "fr": ("<p><em>Cet article ne représente que l'opinion personnelle de l'auteur et ne constitue pas un avis juridique. "
           "Pour l'analyse d'un dossier précis, n'hésitez pas à nous contacter.</em></p>"),
}
MT = ("This is a machine-translated version of our Chinese original article for reference. "
      "The Chinese version is the authoritative source.")
CAT = {"en": "Cross-border IP · Technology export", "fr": "PI internationale · Exportation de technologies"}
DATE_TXT = {"en": "November 01, 2026", "fr": "1er novembre 2026"}
BRAND_FIRM = {"en": "Aipunajie Patent Firm / Mili Law Firm", "fr": "Aipunajie Patent Firm / Mili Law Firm"}
TAGS = {"en": ["IP transfer", "Technology export", "Cross-border"], "fr": ["Transfert de PI", "Exportation", "International"]}


def build_body(lang):
    hb = data[lang]["html_body"]
    orig = hb
    for title, anchor in H2[lang]:
        assert anchor in hb, f"anchor missing ({lang}): {anchor[:50]}"
        hb = hb.replace(anchor, f"<h2>{html.escape(title, quote=False)}</h2>\n{anchor}", 1)
    stripped = re.sub(r"<h2>.*?</h2>\s*", "", hb)
    assert stripped == orig, f"h2 injection altered body ({lang})"
    assert hb.count("<h2>") == 4, hb.count("<h2>")
    hb = hb.replace("</p><p>", "</p>\n\n<p>").replace("</p><ol>", "</p>\n\n<ol>").replace("</ol><p>", "</ol>\n\n<p>")
    return hb + "\n\n" + SIG[lang] + "\n\n" + AI_NOTE[lang] + "\n\n" + DISC[lang] + '\n<div class="disclaimer">' + MT + "</div>"


def jsonld(lang, title, desc):
    url = EN_URL if lang == "en" else FR_URL
    bp = {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "description": desc,
        "inLanguage": lang,
        "author": {"@type": "Person", "name": "He Zigang", "jobTitle": "Intellectual Property Lawyer",
                   "worksFor": [{"@type": "Organization", "name": "Aipunajie Patent Firm"},
                                {"@type": "Organization", "name": "Mili Law Firm"}]},
        "publisher": {"@type": "Organization", "name": "Aipunajie Patent Firm", "url": "https://najieip.com"},
        "image": IMG, "datePublished": DATE, "dateModified": TODAY,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "isBasedOn": {"@type": "Article", "@id": ZH_URL},
        "translationOfWork": {"@type": "Article", "@id": ZH_URL},
        "keywords": ", ".join(data[lang]["keywords"]),
    }
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"https://najieip.com/{lang}/blog/"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url},
    ]}
    return (json.dumps(bp, ensure_ascii=False, indent=2), json.dumps(bc, ensure_ascii=False, indent=2))


def build_page(lang):
    d = data[lang]
    title, desc = d["title"], d["description"]
    kw = ", ".join(d["keywords"]) if isinstance(d["keywords"], list) else d["keywords"]
    url = EN_URL if lang == "en" else FR_URL
    other = FR_URL if lang == "en" else EN_URL
    bp, bc = jsonld(lang, title, desc)
    esc = lambda s: html.escape(s, quote=True)
    head = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(kw)}">
<title>{esc(title)} — Aipunajie Patent Firm</title>
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'fr_FR'}">
<meta property="og:site_name" content="Aipunajie Patent Firm">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{IMG}">
<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">
<link rel="alternate" hreflang="{lang}" href="{url}">
<link rel="alternate" hreflang="{'fr' if lang == 'en' else 'en'}" href="{other}">
<link rel="alternate" hreflang="x-default" href="{ZH_URL}">
{STYLE}
<script type="application/ld+json">
{bp}
</script>
<script type="application/ld+json">
{bc}
</script>
</head>
"""
    body = f"""<body>
<div class="lang-bar">
  <a href="{ZH_URL}">中文</a>
  <a href="{EN_URL}"{' class="active"' if lang == 'en' else ''}>EN</a>
  <a href="{FR_URL}"{' class="active"' if lang == 'fr' else ''}>FR</a>
</div>
<header><a href="/{lang}/">Aipunajie Patent Firm</a></header>
<div class="container">
<article>
<h1>{esc(title)}</h1>
<div class="meta">{DATE_TXT[lang]} · {CAT[lang]} · {BRAND_FIRM[lang]}</div>
{build_body(lang)}
</article>
</div>
<footer><a href="/">Aipunajie Patent Firm</a> · Mili Law Firm · Najie IP — All rights reserved</footer>
</body>
</html>
"""
    return head + body


written = []
for lang, rel in (("en", f"en/blog/{SLUG}-en.html"), ("fr", f"fr/blog/{SLUG}-fr.html")):
    page = build_page(lang)
    assert len(re.findall(r"<h1", page)) == 1, "h1 count"
    assert page.count("<h2>") == 4, "h2 count"
    assert page.count("application/ld+json") == 2
    assert "https://***" not in page and page.count("https://schema.org") >= 2
    no_langbar = re.sub(r'<div class="lang-bar">.*?</div>', "", page, flags=re.S)
    assert len(re.findall(r"[\u4e00-\u9fff]", no_langbar)) == 0, "CJK leak"
    assert page.count("**") == 0
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        json.loads(blk)
    open(os.path.join(REPO, rel), "w", encoding="utf-8").write(page)
    written.append((rel, len(page.encode())))
    print(lang, "written", rel, len(page.encode()), "bytes | h2=4 ld=2")

# --- 顺手把 EN/FR 页 body 落盘供数字保真校验 ---
(open("/Users/ziganghe/.hermes/cache/scratch/en_body_1107.txt", "w", encoding="utf-8")
 .write(re.findall(r"<article>(.*?)</article>", open(os.path.join(REPO, f"en/blog/{SLUG}-en.html"), encoding="utf-8").read(), re.S)[0]))
(open("/Users/ziganghe/.hermes/cache/scratch/fr_body_1107.txt", "w", encoding="utf-8")
 .write(re.findall(r"<article>(.*?)</article>", open(os.path.join(REPO, f"fr/blog/{SLUG}-fr.html"), encoding="utf-8").read(), re.S)[0]))

# ---------- 索引卡片 ----------
def card(lang):
    d = data[lang]
    url = f"/{lang}/blog/{SLUG}-{lang}.html"
    tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in TAGS[lang])
    return (f'  <div class="article-card">\n'
            f'    <h2><a href="{url}">{html.escape(d["title"])}</a></h2>\n'
            f'    <div class="meta">{tags} {DATE_TXT[lang]} · {BRAND_FIRM[lang]}</div>\n'
            f'    <p>{html.escape(d["description"])}</p>\n'
            f'  </div>\n\n')

for lang in ("en", "fr"):
    p = os.path.join(REPO, f"{lang}/blog/index.html")
    t = open(p, encoding="utf-8").read()
    if SLUG in t:
        print(lang, "index: already has card, skip")
        continue
    anchor = '<div class="container">\n\n'
    assert anchor in t, "index anchor missing " + lang
    c = card(lang)
    t2 = t.replace(anchor, anchor + c, 1)
    assert t2.count('class="article-card"') == t.count('class="article-card"') + 1
    open(p, "w", encoding="utf-8").write(t2)
    print(lang, "index card inserted; cards:", t2.count('class="article-card"'))

# ---------- 中文权威页 hreflang + og:image ----------
zh_path = os.path.join(REPO, ZH_PATH)
t = open(zh_path, encoding="utf-8").read()
changed = []
if 'hreflang="en"' not in t:
    ins = (f'<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">\n'
           f'<link rel="alternate" hreflang="en" href="{EN_URL}">\n'
           f'<link rel="alternate" hreflang="fr" href="{FR_URL}">\n'
           f'<link rel="alternate" hreflang="x-default" href="{ZH_URL}">\n')
    t = t.replace("</head>", ins + "</head>", 1)
    changed.append("hreflang")
if IMG not in t:
    if 'property="og:image"' in t:
        t = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG}">', t, count=1)
    else:
        t = t.replace("</head>", f'<meta property="og:image" content="{IMG}">\n</head>', 1)
    changed.append("og:image")
open(zh_path, "w", encoding="utf-8").write(t)
print("zh page updated:", changed or "no change", "| hreflang count", t.count('hreflang="'))
