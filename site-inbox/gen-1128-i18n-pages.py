#!/usr/bin/env python3
"""2026-11-28 i18n 页面生成：惩罚性赔偿漏写请求 → en/blog + fr/blog + 索引卡 + 中文页 hreflang + sitemap
用法: python3 gen-1128-i18n-pages.py [--apply]
"""
import json, os, re, sys, html

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261124-mili-punitive-damages-one-shot"
BRAND = "mili"
ZH_URL = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
EN_URL = f"https://najieip.com/en/blog/{SLUG}-en.html"
FR_URL = f"https://najieip.com/fr/blog/{SLUG}-fr.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
TPL = os.path.join(REPO, "en/blog/20261113-byd-netherlands-evidence-seizure-en.html")
APPLY = "--apply" in sys.argv
PUB = "2026-11-24"
MOD = "2026-11-28"


def trim_desc(s, lo=140, hi=250):
    s = s.strip()
    if len(s) <= hi:
        return s
    parts = re.split(r"(?<=[.!?])\s+", s)
    out = ""
    for p in parts:
        cand = (out + " " + p).strip()
        if len(cand) > hi and len(out) >= lo:
            break
        out = cand
        if len(out) >= lo:
            break
    return out if len(out) >= lo else s[:hi].rsplit(" ", 1)[0] + "."


CSS = re.search(r"<style>.*?</style>", open(TPL, encoding="utf-8").read(), re.S).group(0)


def esc(s):
    return html.escape(s, quote=True)


def build(lang, d):
    LANGNAME = lang
    canon = EN_URL if lang == "en" else FR_URL
    site = "Aipunajie Patent Firm"
    title = d["title"].strip()
    desc = trim_desc(d["description"])
    kw = d["keywords"].strip()
    body = d["html_body"].strip()
    if lang == "en":
        meta_line = "November 24, 2026 · IP litigation · Punitive damages · Najie IP"
        byline = "He Zigang | Intellectual Property Lawyer | Aipunajie · Mili · Najie"
        ai_note = "This article was drafted with AI assistance; the views and judgments were reviewed and approved by the author."
        disc = "This article reflects the author&#x27;s personal views only and does not constitute legal advice. For analysis of a specific case, please contact us."
        mt = "This is a machine-translated version of our Chinese original article for reference. The Chinese version is the authoritative source."
        locale = "en_US"
        tags = ('<span class="tag">IP litigation</span><span class="tag">Punitive damages</span>'
                '<span class="tag">China</span>')
        card_meta = f"{tags} November 24, 2026 · Najie IP"
    else:
        meta_line = "24 novembre 2026 · Contentieux PI · Dommages-intérêts punitifs · Najie IP"
        byline = "He Zigang | Avocat en propriété intellectuelle | Aipunajie · Mili · Najie"
        ai_note = "Cet article a été rédigé avec l&#x27;aide d&#x27;une IA ; les opinions et jugements ont été revus et approuvés par l&#x27;auteur."
        disc = "Cet article ne reflète que l&#x27;opinion personnelle de l&#x27;auteur et ne constitue pas un avis juridique. Pour l&#x27;analyse d&#x27;un cas particulier, veuillez nous contacter."
        mt = "Ceci est une traduction automatique de notre article original chinois, fournie à titre de référence. La version chinoise fait foi."
        locale = "fr_FR"
        tags = ('<span class="tag">Contentieux PI</span><span class="tag">Dommages-intérêts punitifs</span>'
                '<span class="tag">Chine</span>')
        card_meta = f"{tags} 24 novembre 2026 · Najie IP"

    ld1 = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": desc,
        "inLanguage": LANGNAME,
        "author": {"@type": "Person", "name": "He Zigang", "jobTitle": "Intellectual Property Lawyer",
                   "worksFor": [{"@type": "Organization", "name": "Aipunajie Patent Firm"},
                                {"@type": "Organization", "name": "Mili Law Firm"}]},
        "publisher": {"@type": "Organization", "name": site, "url": "https://najieip.com"},
        "image": IMG,
        "datePublished": PUB,
        "dateModified": MOD,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canon},
        "isBasedOn": {"@type": "Article", "@id": ZH_URL},
        "translationOfWork": {"@type": "Article", "@id": ZH_URL},
        "keywords": kw,
    }
    ld2 = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"https://najieip.com/{lang}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"https://najieip.com/{lang}/blog/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": canon},
        ],
    }

    page = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(kw)}">
<title>{esc(title)} — {site}</title>
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{locale}">
<meta property="og:site_name" content="{site}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{IMG}">
<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">
<link rel="alternate" hreflang="en" href="{EN_URL}">
<link rel="alternate" hreflang="fr" href="{FR_URL}">
<link rel="alternate" hreflang="x-default" href="{ZH_URL}">
{CSS}
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
  <a href="{EN_URL}"{' class="active"' if lang == 'en' else ''}>EN</a>
  <a href="{FR_URL}"{' class="active"' if lang == 'fr' else ''}>FR</a>
</div>
<header><a href="/{lang}/">{site}</a></header>
<div class="container">
<article>
<h1>{esc(title)}</h1>
<div class="meta">{meta_line}</div>
{body}
<p>{byline}</p>
<p><em>{ai_note}</em></p>
<p><em>{disc}</em></p>
<div class="disclaimer">{mt}</div>
</article>
</div>
<footer><a href="/">Aipunajie Patent Firm</a> · Mili Law Firm · Najie IP — All rights reserved</footer>
</body>
</html>
"""
    return page, card_meta


def card(lang, d, card_meta):
    title = esc(d["title"].strip())
    desc = esc(trim_desc(d["description"]))
    url = f"/{lang}/blog/{SLUG}-{lang}.html"
    return (f'  <div class="article-card">\n'
            f'    <h2><a href="{url}">{title}</a></h2>\n'
            f'    <div class="meta">{card_meta}</div>\n'
            f'    <p>{desc[:230]}…</p>\n'
            f'  </div>\n\n')


def apply_index(lang, d, card_meta):
    p = os.path.join(REPO, f"{lang}/blog/index.html")
    t = open(p, encoding="utf-8").read()
    if f"{SLUG}-{lang}.html" in t:
        print(f"  [{lang}] index already has card, skip")
        return 0
    anchor = '<div class="container">\n\n'
    assert t.count(anchor) == 1, f"{lang} anchor count {t.count(anchor)}"
    c = card(lang, d, card_meta)
    t2 = t.replace(anchor, anchor + c, 1)
    assert t2.replace(c, "", 1) == t
    op0, cl0 = t.count("<div"), t.count("</div>")
    op1, cl1 = t2.count("<div"), t2.count("</div>")
    assert op1 - op0 == cl1 - cl0 and op1 > op0, f"{lang} div delta {op1-op0}/{cl1-cl0}"
    print(f"  [{lang}] index cards {t.count('article-card')} -> {t2.count('article-card')}, div +{op1-op0}/+{cl1-cl0}")
    if APPLY:
        open(p, "w", encoding="utf-8").write(t2)
    return 1


def apply_zh_hreflang():
    p = os.path.join(REPO, BRAND, "blog", f"{SLUG}.html")
    t = open(p, encoding="utf-8").read()
    have = re.findall(r'hreflang="([^"]+)"', t)
    if have:
        print("  [zh] hreflang already:", have)
        return 0
    links = (f'<link rel="alternate" hreflang="zh-CN" href="{ZH_URL}">\n'
             f'<link rel="alternate" hreflang="en" href="{EN_URL}">\n'
             f'<link rel="alternate" hreflang="fr" href="{FR_URL}">\n'
             f'<link rel="alternate" hreflang="x-default" href="{ZH_URL}">\n')
    anchor = f'<link rel="canonical" href="{ZH_URL}">\n'
    assert t.count(anchor) == 1, f"zh canonical anchor {t.count(anchor)}"
    t2 = t.replace(anchor, anchor + links, 1)
    assert t2.replace(links, "", 1) == t
    print("  [zh] hreflang +4 values")
    if APPLY:
        open(p, "w", encoding="utf-8").write(t2)
    return 1


def apply_sitemap():
    p = os.path.join(REPO, "sitemap.xml")
    t = open(p, encoding="utf-8").read()
    add = [u for u in (EN_URL, FR_URL) if u not in t]
    if not add:
        print("  [sitemap] already has both")
        return 0
    blocks = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{MOD}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n" for u in add)
    idx = t.rfind("</urlset>")
    t2 = t[:idx] + blocks + t[idx:]
    n0, n1 = t.count("<loc>"), t2.count("<loc>")
    assert n1 - n0 == len(add), f"sitemap loc {n0}->{n1}"
    print(f"  [sitemap] loc {n0} -> {n1}")
    if APPLY:
        open(p, "w", encoding="utf-8").write(t2)
    return 1


if __name__ == "__main__":
    en = json.load(open("/Users/ziganghe/wiki/digital-employees/reports/_i18n_en_1128.json"))
    fr = json.load(open("/Users/ziganghe/wiki/digital-employees/reports/_i18n_fr_1128.json"))
    for lang, d in (("en", en), ("fr", fr)):
        page, card_meta = build(lang, d)
        assert page.count("<h1") == 1, f"{lang} h1 {page.count('<h1')}"
        assert "<h1" not in d["html_body"]
        n_cjk = len(re.findall(r"[\u4e00-\u9fff]", d["html_body"]) + re.findall(r"[\u4e00-\u9fff]", d["title"]))
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
        for s in lds:
            json.loads(s)
        print(f"[{lang}] page={len(page)}B h1=1 ld={len(lds)} cjk={n_cjk} schema_org={page.count('https://schema.org')} "
              f"tables={page.count('<table')} h2={page.count('<h2')}")
        assert page.count("https://schema.org") == len(lds), "schema.org count mismatch"
        assert "https://***" not in page
        assert n_cjk < 30, f"{lang} CJK leak {n_cjk}"
        out = os.path.join(REPO, f"{lang}/blog/{SLUG}-{lang}.html")
        if APPLY:
            open(out, "w", encoding="utf-8").write(page)
        apply_index(lang, d, card_meta)
    apply_zh_hreflang()
    apply_sitemap()
    print("APPLY" if APPLY else "DRY-RUN")
