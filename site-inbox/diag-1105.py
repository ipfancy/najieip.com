#!/usr/bin/env python3
"""SiteOps daily 2026-11-05 diagnostics: pages six-check + cards + articles.json"""
import os, re, json, glob, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles")

TARGETS = [
    ("mili", "20261105-mili-non-compete-all-staff.html"),
    ("najie", "20261105-najie-examination-15plan-foreign-filers.html"),
]

def textify(b):
    b = re.sub(r'<h1>.*?</h1>', ' ', b, flags=re.S)
    b = re.sub(r'<figure.*?</figure>', ' ', b, flags=re.S)
    b = re.sub(r'<script.*?</script>', ' ', b, flags=re.S)
    b = re.sub(r'<style.*?</style>', ' ', b, flags=re.S)
    b = re.sub(r'<[^>]+>', ' ', b)
    b = b.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"')
    for ch in '“”"\'’*|#>-\u3000':
        b = b.replace(ch, ' ')
    b = re.sub(r'<h2>--', '', b)
    b = re.sub(r'\s+', '', b)
    return b

def mdtext(p):
    t = open(p, encoding='utf-8').read()
    if t.startswith('---'):
        e = t.find('\n---', 3)
        if e != -1:
            t = t[e+4:]
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'^#+\s*', '', t, flags=re.M)
    for ch in '“”"\'’*|#>-\u3000`':
        t = t.replace(ch, ' ')
    t = re.sub(r'\s+', '', t)
    return t

out = []
for brand, fn in TARGETS:
    p = os.path.join(REPO, brand, "blog", fn)
    slug = fn[:-5]
    rec = {"brand": brand, "file": fn, "slug": slug, "exists": os.path.exists(p)}
    if rec["exists"]:
        t = open(p, encoding='utf-8').read()
        b = t[t.find("<body"):] if "<body" in t else t
        rec["bytes"] = len(t.encode())
        rec["h1"] = len(re.findall(r'<h1[ >]', b))
        rec["ld"] = len(re.findall(r'application/ld\+json', t))
        rec["og_image"] = len(re.findall(r'property="og:image"', t))
        rec["twitter_img"] = len(re.findall(r'name="twitter:image"', t))
        rec["keywords"] = len(re.findall(r'name="keywords"', t))
        m = re.search(r'name="description"\s+content="([^"]*)"', t)
        rec["desc"] = m.group(1) if m else ""
        rec["desc_len"] = len(rec["desc"])
        h1m = re.search(r'<h1[^>]*>(.*?)</h1>', b, re.S)
        rec["h1_text"] = re.sub(r'<[^>]+>', '', h1m.group(1)).strip() if h1m else ""
        rec["desc_is_title"] = rec["desc"][:12] in rec["h1_text"] or rec["h1_text"][:12] in rec["desc"]
        body_nostar = re.sub(r'[0-9*]\*{2,}[0-9.]*', '', b)
        rec["stars"] = body_nostar.count('**')
        rec["bare_table_rows"] = len(re.findall(r'<p>\s*\|.*\|\s*</p>', b))
        rec["tables"] = len(re.findall(r'<table', b))
        rec["h2"] = len(re.findall(r'<h2[ >]', b))
        rec["style_inline"] = '<style' in t
        rec["style_ext"] = '/style.css' in t
        rec["canonical"] = (re.search(r'rel="canonical" href="([^"]+)"', t) or [None, None])[1]
        rec["ldjson_ok"] = []
        for blk in re.findall(r'application/ld\+json[^>]*>(.*?)</script>', t, re.S):
            try:
                json.loads(blk)
                rec["ldjson_ok"].append(True)
            except Exception as ex:
                rec["ldjson_ok"].append(str(ex)[:60])
        # md containment
        mdp = os.path.join(MD, slug + ".md")
        if os.path.exists(mdp):
            mt = mdtext(mdp)
            bt = textify(b)
            rec["md_exists"] = True
            rec["md_contains"] = mt in bt
            if not rec["md_contains"]:
                rec["md_len"] = len(mt); rec["body_len"] = len(bt)
        else:
            rec["md_exists"] = False
        # card presence
        for idx, key in ((os.path.join(REPO, "blog", "index.html"), "main_card"),
                         (os.path.join(REPO, brand, "blog", "index.html"), "brand_card")):
            it = open(idx, encoding='utf-8').read()
            rec[key] = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), it))
    out.append(rec)

# articles.json
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding='utf-8'))
arts = aj.get("articles", aj) if isinstance(aj, dict) else aj
out.append({"articles_json_total": len(arts),
            "top6": [a.get("url") or a.get("link") or a.get("path") for a in arts[:6]],
            "top6_exist": [os.path.exists(os.path.join(REPO, (a.get("url") or "").lstrip("/"))) for a in arts[:6]],
            "has_1105": [(a.get("url"), a.get("title", "")[:30]) for a in arts if "20261105" in str(a.get("url", ""))]})

print(json.dumps(out, ensure_ascii=False, indent=1))
