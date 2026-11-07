#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1107 night fix: repair unpaid-trial page head + add 5 index cards + cover."""
import os, re, sys, json, shutil, copy

R = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
APPLY = "--apply" in sys.argv

def rd(p): return open(p, encoding="utf-8").read()
def wr(p, s): open(p, "w", encoding="utf-8").write(s)

def zh_quotes(s):
    return re.sub(r'"([^"<>]{0,200})"', "“\\1”", s)

def esc_attr(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))

def meta_of(path):
    t = rd(path)
    title = (re.search(r'<meta property="og:title" content="([^"]*)"', t) or re.search(r"<title>(.*?)</title>", t, re.S)).group(1)
    title = re.sub(r"\s*[—-]\s*纳杰觅理.*$", "", title).strip()
    desc = (re.search(r'<meta name="description" content="([^"]*)"', t) or [None, ""])[1]
    kw = (re.search(r'<meta name="keywords" content="([^"]*)"', t) or [None, ""])[1]
    tags = [x.strip() for x in kw.split(",") if x.strip()][:3]
    return title, desc, tags

# ==== A. repair unpaid-trial head ====
P = os.path.join(R, "mili/blog/20261107-mili-unpaid-trial-shigang.html")
HOUSE = os.path.join(R, "mili/blog/20261107-mili-unjust-enrichment-default-judgment.html")
t = rd(P); h = rd(HOUSE)
SLUG = "20261107-mili-unpaid-trial-shigang"
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
TITLE = "白干7天被辞，能要回的不是0，是7379元"
DESC = ("试岗7天被辞、一分不给，法律里根本没有“试岗期”。本文算清能要回的三笔钱（工资1379元＋违法解除6000元＝7379元）、"
        "为什么7天拿不到二倍工资（第82条“超过一个月”的门槛），以及仲裁前必须固定的五类证据和三步动作。")
KW = "试岗期,试岗不给工资,违法解除赔偿金,二倍工资,劳动仲裁"

head_end = t.find("</head>") + 7
head = t[:head_end]; body = t[head_end:]

head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc_attr(DESC)}">', head, count=1)
head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc_attr(TITLE)}">', head) if 'og:title' in head else head
head = re.sub(r'<title>.*?</title>', f'<title>{TITLE} — 纳杰觅理</title>', head, flags=re.S)

extra = []
if 'property="og:title"' not in head:
    extra.append(f'<meta property="og:title" content="{esc_attr(TITLE)}">')
if 'property="og:type"' not in head:
    extra.append('<meta property="og:type" content="article">')
if 'property="og:description"' not in head:
    extra.append(f'<meta property="og:description" content="{esc_attr(DESC[:70])}">')
if 'property="og:site_name"' not in head:
    extra.append('<meta property="og:site_name" content="北京觅理律师事务所">')
if 'property="og:locale"' not in head:
    extra.append('<meta property="og:locale" content="zh_CN">')
if 'name="keywords"' not in head:
    extra.append(f'<meta name="keywords" content="{esc_attr(KW)}">')
if 'property="og:url"' not in head:
    extra.append(f'<meta property="og:url" content="{URL}">')
if 'property="og:image"' not in head:
    extra.append(f'<meta property="og:image" content="https://najieip.com/img/{SLUG}.png">')
if 'name="twitter:card"' not in head:
    extra.append('<meta name="twitter:card" content="summary">')
    extra.append(f'<meta name="twitter:title" content="{esc_attr(TITLE)}">')
    extra.append(f'<meta name="twitter:description" content="{esc_attr(DESC[:60])}">')

if extra:
    ins = "\n".join(extra) + "\n"
    # insert right before canonical if present, else before </head>
    mc = re.search(r'<link rel="canonical"[^>]*>', head)
    if mc:
        head = head[:mc.start()] + ins + head[mc.start():]
    else:
        head = head.replace("</head>", ins + "</head>")

# JSON-LD via deepcopy of house
lds = [json.loads(m.group(1)) for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)]
art_obj = next(o for o in lds if o.get("@type") == "Article")
bc_obj = next(o for o in lds if o.get("@type") == "BreadcrumbList")
a = copy.deepcopy(art_obj)
a["headline"] = TITLE
a["description"] = DESC
a["image"] = f"https://najieip.com/img/{SLUG}.png"
a["datePublished"] = "2026-11-07"
a["dateModified"] = "2026-11-07"
a["url"] = URL
a["keywords"] = KW
a["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
a["publisher"]["name"] = "北京觅理律师事务所"
b = copy.deepcopy(bc_obj)
b["itemListElement"][-1]["item"] = URL
b["itemListElement"][-1]["name"] = TITLE

ld_html = ""
for o in (a, b):
    ld_html += '<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=2) + '\n</script>\n'
if 'application/ld+json' not in head:
    head = head.replace("</head>", ld_html + "</head>")

# body: text-node normalization (ASCII quotes -> zh, <p>---</p> -> <hr>)
parts = re.split(r"(<[^>]+>)", body)
parts = [zh_quotes(p) if not p.startswith("<") else p for p in parts]
body2 = "".join(parts)
body2 = re.sub(r"<p>\s*-{3,}\s*</p>", "<hr>", body2)
newt = head + body2
print("PAGE bytes", len(t.encode()), "->", len(newt.encode()), "| h1", len(re.findall(r'<h1[ >]', newt)),
      "ld", newt.count("application/ld+json"), "og:image", "og:image" in newt, "stars", newt.count("**"))

# ==== B. cover ====
src = os.path.join(ART, f"cover-{SLUG}.png")
dst = os.path.join(R, "img", f"{SLUG}.png")
if os.path.exists(src) and not os.path.exists(dst):
    print("COVER", src, "->", dst, os.path.getsize(src))

# ==== C. cards ====
def card_blocks(text, cls='article-card'):
    """return list of (start,end,block) via div depth pairing"""
    out = []
    for m in re.finditer(r'<div class="%s">' % cls, text):
        i = m.start(); depth = 0; j = i
        while True:
            nxt = min([x for x in (text.find("<div", j), text.find("</div>", j)) if x != -1] or [-1])
            if nxt == -1: break
            if text.startswith("<div", nxt):
                depth += 1; j = nxt + 4
            else:
                depth -= 1; j = nxt + 6
                if depth == 0:
                    out.append((i, j, text[i:j])); break
    return out

def find_card(text, slug):
    for s, e, blk in card_blocks(text):
        if slug in blk: return s, e, blk
    return None

def build_card(tpl, new_href, title, desc, tags, date, brand_label):
    blk = tpl
    blk = re.sub(r'(<h[23][^>]*><a href=")[^"]*(">).*?(</a></h[23]>)',
                 lambda m: m.group(1) + new_href + m.group(2) + esc_attr(title) + m.group(3), blk, flags=re.S)
    taghtml = "".join('<span class="tag">%s</span>' % esc_attr(x) for x in tags)
    blk = re.sub(r'<div class="meta">.*?</div>',
                 '<div class="meta">%s %s · %s</div>' % (taghtml, date, brand_label), blk, count=1, flags=re.S)
    if re.search(r'<p[ >].*?</p>', blk, re.S):
        blk = re.sub(r'<p[ >].*?</p>', '<p>%s</p>' % esc_attr(desc), blk, count=1, flags=re.S)
    return blk

def insert_by_date(text, block, date):
    """insert before first card whose date < date; each round rescan"""
    for s, e, blk in card_blocks(text):
        md = re.search(r'\d{4}-\d{2}-\d{2}', blk)
        if md and md.group(0) < date:
            return text[:s] + block + "\n  " + text[s:]
    # fallback: append at end of container
    i = text.rfind("</div>")
    return text[:i] + block + "\n  " + text[i:]

MILI_IDX = os.path.join(R, "mili/blog/index.html")
NAJIE_IDX = os.path.join(R, "najie/blog/index.html")
MAIN_IDX = os.path.join(R, "blog/index.html")
mi = rd(MILI_IDX); nj = rd(NAJIE_IDX); mn = rd(MAIN_IDX)
base_counts = {"mili": mi.count('<div class="article-card">'), "najie": nj.count('<div class="article-card">'), "main": mn.count('<div class="article-card">')}

plans = []
# (target index, template slug, new slug, brand dir, display label)
plans.append(("mili", "20261107-mili-unjust-enrichment-default-judgment", "20261107-mili-trademark-transition-rules-4-lines", "mili", "觅理律所"))
plans.append(("najie", "20261105-najie-examination-15plan-foreign-filers", "20261107-najie-patent-license-contract-6-clauses", "najie", "纳杰"))
plans.append(("main", "20261103-mili-guarantee-period-six-months", "20261107-mili-unjust-enrichment-default-judgment", "mili", "觅理律所"))
plans.append(("main", "20261103-mili-guarantee-period-six-months", "20261107-najie-patent-license-contract-6-clauses", "najie", "纳杰"))
plans.append(("main", "20261103-mili-guarantee-period-six-months", "20261107-mili-trademark-transition-rules-4-lines", "mili", "觅理律所"))

texts = {"mili": mi, "najie": nj, "main": mn}
added = {"mili": 0, "najie": 0, "main": 0}
for target, tpl_slug, new_slug, brand, label in plans:
    text = texts[target]
    if re.search(r'<h[23][^>]*><a href="[^"]*' + re.escape(new_slug), text):
        print("SKIP exists", target, new_slug); continue
    fc = find_card(text, tpl_slug)
    if not fc:
        print("TPL_MISS", target, tpl_slug); continue
    _, _, tpl = fc
    href = f"./{new_slug}.html" if target != "main" else f"/{brand}/blog/{new_slug}.html"
    tp, td, tt = meta_of(os.path.join(R, brand, "blog", new_slug + ".html"))
    card = build_card(tpl, href, tp, td, tt, "2026-11-07", label)
    print("\n--- NEW CARD (%s) ---\n%s" % (target, card[:600]))
    if APPLY:
        texts[target] = insert_by_date(text, card, "2026-11-07")
        added[target] += 1

if APPLY:
    wr(P, newt)
    if os.path.exists(src): shutil.copy2(src, dst)
    wr(MILI_IDX, texts["mili"]); wr(NAJIE_IDX, texts["najie"]); wr(MAIN_IDX, texts["main"])
    print("\n=== APPLIED ===")
    for k, path in (("mili", MILI_IDX), ("najie", NAJIE_IDX), ("main", MAIN_IDX)):
        t2 = rd(path)
        c = t2.count('<div class="article-card">')
        print(k, "cards", base_counts[k], "->", c, "delta", c - base_counts[k], "expect", added[k],
              "| div_open", t2.count("<div"), "div_close", t2.count("</div>"),
              "| malformed", len([b for b in card_blocks(t2) if '<h2><a href=' not in b[2][:200] and '<h3><a href=' not in b[2][:200]]),
              "| **", t2.count("**"))
    print("page ok:", len(rd(P).encode()))
