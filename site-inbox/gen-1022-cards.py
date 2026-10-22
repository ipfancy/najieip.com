#!/usr/bin/env python3
"""Add missing index cards for 10-22 pages. Usage: python3 site-inbox/gen-1022-cards.py [--apply]"""
import re, os, sys, html, shutil

REPO = "/Users/ziganghe/wiki/najieip-verify"
APPLY = "--apply" in sys.argv

def read(p):
    return open(os.path.join(REPO, p), encoding="utf-8").read()

def esc(s):
    return html.escape(s, quote=True)

def extract_card(t, slug):
    """Return (card_html, date) for card containing slug, using div-depth pairing."""
    m = re.search(r'<h2><a href="[^"]*' + re.escape(slug), t)
    if not m:
        return None, None
    start = t.rfind('<div class="article-card">', 0, m.start())
    assert start != -1, "card start not found"
    depth, i = 0, start
    while i < len(t):
        nxt_open = t.find("<div", i)
        nxt_close = t.find("</div>", i)
        if nxt_close == -1:
            raise RuntimeError("unbalanced")
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + 4
        else:
            depth -= 1
            i = nxt_close + 6
            if depth == 0:
                card = t[start:i]
                dm = re.search(r"(\d{4}-\d{2}-\d{2})", card)
                return card, (dm.group(1) if dm else None)
    raise RuntimeError("no end")

def card_starts(t):
    """[(pos, date)] for every article-card by div pairing."""
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        start = m.start()
        depth, i = 0, start
        while i < len(t):
            o = t.find("<div", i); c = t.find("</div>", i)
            if c == -1: break
            if o != -1 and o < c:
                depth += 1; i = o + 4
            else:
                depth -= 1; i = c + 6
                if depth == 0:
                    blk = t[start:i]
                    dm = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
                    out.append((start, dm.group(1) if dm else "0000-00-00"))
                    break
    return out

def insert(t, card, date):
    pos = None
    for p, d in card_starts(t):
        if d < date:
            pos = p
            break
    if pos is None:
        pos = t.rfind("</div>")
    t2 = t[:pos] + card + "\n  " + t[pos:]
    assert t2.replace(card + "\n  ", "", 1) == t, "outer text modified"
    return t2

def build_card(slug, brand, title, desc, tags, date, tpl_card, tpl_slug):
    """Clone template card, replace href/title/desc/tags/date."""
    c = tpl_card
    c = c.replace(f'href="./{tpl_slug}.html"', f'href="./{slug}.html"')
    # title text inside h2 anchor
    c = re.sub(r'(<h2><a href="[^"]*">)(.*?)(</a></h2>)',
               lambda m: m.group(1) + esc(title) + m.group(3), c, count=1, flags=re.S)
    # description paragraph
    c = re.sub(r"<p>.*?</p>", "<p>" + esc(desc) + "</p>", c, count=1, flags=re.S)
    # tag spans (whole group)
    if tags:
        spans = "".join(f'<span class="tag">{esc(x)}</span>' for x in tags)
        c, n = re.subn(r'(?:\s*<span class="tag">[^<]*</span>)+', spans, c, count=1)
        assert n == 1, "tag group not replaced"
    # date
    c = re.sub(r"\d{4}-\d{2}-\d{2}", date, c)
    return c

JOBS = [
    dict(idx="najie/blog/index.html", brand="najie", slug="20261022-najie-gaoqi-ip-30points",
         title="高企那30分，纯买专利这一格天花板只有3分",
         desc="高企评分里知识产权占 30 分，但纯买专利这一格天花板只有 3 分：官方写的是「仅有受让、受赠和并购 1–3 分」。拆官方评价表四格、三类凑数逐格对账、算清另外三块要凑多少分。",
         tags=["高企认定", "知识产权评分"], date="2026-10-22",
         tpl_slug="20261021-goods-names-acceptable-list-q4"),
    dict(idx="blog/index.html", brand="najie", slug="20261022-najie-gaoqi-ip-30points",
         title="高企那30分，纯买专利这一格天花板只有3分",
         desc="高企评分里知识产权占 30 分，但纯买专利这一格天花板只有 3 分：官方写的是「仅有受让、受赠和并购 1–3 分」。拆官方评价表四格、三类凑数逐格对账、算清另外三块要凑多少分。",
         tags=["高企认定", "知识产权评分"], date="2026-10-22",
         tpl_slug="20261021-goods-names-acceptable-list-q4"),
    dict(idx="blog/index.html", brand="mili", slug="20261022-safety-production-crimes",
         title="安全生产出事，追的不只是老板：12 个罪名与刑责边界",
         desc=None,  # take from mili index card
         tags=None, date="2026-10-22", tpl_slug=None),
]

for job in JOBS:
    idx = job["idx"]
    t = read(idx)
    if job["slug"] in t:
        print(f"SKIP {idx} (already has {job['slug']})")
        continue
    brand = job["brand"]
    bidx = read(f"{brand}/blog/index.html")
    tpl_card, tpl_date = extract_card(bidx, job["tpl_slug"] or job["slug"])
    if tpl_card is None:
        print(f"FAIL {idx}: template card not found in {brand}/blog/index.html")
        continue
    title, desc, tags = job["title"], job["desc"], job["tags"]
    if desc is None or job["tpl_slug"] is None:
        own, _ = extract_card(bidx, job["slug"])
        assert own, "own card missing in brand index"
        m = re.search(r"<h2><a href=\"[^\"]*\">(.*?)</a></h2>", own, re.S)
        title = re.sub(r"<[^>]+>", "", m.group(1))
        mp = re.search(r"<p>(.*?)</p>", own, re.S)
        desc = re.sub(r"<[^>]+>", "", mp.group(1))
        tags = re.findall(r'<span class="tag">([^<]*)</span>', own)
    card = build_card(job["slug"], brand, title, desc, tags, job["date"], tpl_card, job["tpl_slug"] or job["slug"])
    if idx == "blog/index.html":
        card = card.replace(f'href="./{job["slug"]}.html"', f'href="/{brand}/blog/{job["slug"]}.html"')
        if 'class="tag"' in card:
            pass
    t2 = insert(t, card, job["date"])
    # validations
    assert t2.count('<div class="article-card">') == t.count('<div class="article-card">') + 1
    assert re.search(r"<h2><a href=", card)
    opens, closes = t2.count("<div"), t2.count("</div>")
    assert opens == closes, f"div imbalance {opens}/{closes}"
    print(f"OK {idx}: cards {t.count('<div class=\"article-card\">')} -> {t2.count('<div class=\"article-card\">')} href={'/' + brand + '/blog/' + job['slug'] + '.html' if idx=='blog/index.html' else './' + job['slug'] + '.html'}")
    if APPLY:
        shutil.copyfile(os.path.join(REPO, idx), os.path.join(REPO, idx) + ".bak-1022")
        open(os.path.join(REPO, idx), "w", encoding="utf-8").write(t2)
