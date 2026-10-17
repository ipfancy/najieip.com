#!/usr/bin/env python3
"""Insert card for today's article into mili/blog/index.html and blog/index.html
(date-descending position) + BlogPosting JSON-LD entry. Verifies structure.
"""
import os, re, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "customs-ip-post-filing-steps-20261017"
DATE = "2026-10-17"
TITLE = "货被海关扣了怎么办？备案后的三步处置（10月14日新规）"
DESC = ("海关总署审核通过知识产权备案3.52万件、全国海关查扣侵权货物8642万件。备案不等于海关替你拦货："
        "依职权扣留要你在通知送达后3个工作日内申请扣留并交担保，错过即依法放行。本文讲清依申请与依职权的区别、"
        "担保怎么算，以及货被扣后按10月14日新规走的三步处置流程。")
TAGS = ["海关备案", "知识产权海关保护", "三步处置"]
APPLY = "--apply" in sys.argv

def card_block(t):
    start = t.find('<div class="article-card">')
    i, depth = start, 0
    while i < len(t):
        m = re.match(r'</?div\b[^>]*>', t[i:])
        if m:
            depth += -1 if m.group(0).startswith("</") else 1
            i += m.end()
            if depth == 0:
                return t[start:i]
        else:
            i += 1
    raise RuntimeError("card not closed")

def depth_stats(s):
    bad, depth, maxd = 0, 0, 0
    for m in re.finditer(r'</?div\b[^>]*>', s):
        if m.group(0).startswith("</"):
            if depth == 0:
                bad += 1
            else:
                depth -= 1
        else:
            depth += 1
            maxd = max(maxd, depth)
    return depth, bad, maxd

def card_depths(s):
    """count article-card nodes at each depth (depth of parent chain)."""
    hist = {}
    depth = 0
    for m in re.finditer(r'<(/?)div\b[^>]*>', s):
        if m.group(1) == "/":
            depth -= 1
        else:
            if 'class="article-card"' in m.group(0):
                hist[depth] = hist.get(depth, 0) + 1
            depth += 1
    return hist

def patch_index(idx, href_prefix):
    p = os.path.join(REPO, idx)
    t = open(p, encoding="utf-8").read()
    if SLUG in t:
        print(f"{idx}: already has card, skip")
        return False
    tpl = card_block(t)
    card = tpl
    card = re.sub(r'(<h2><a href=")[^"]*(")', lambda m: m.group(1) + href_prefix + SLUG + ".html" + m.group(2), card, count=1)
    # title
    card = re.sub(r'(<h2><a href="[^"]*">).*?(</a></h2>)', lambda m: m.group(1) + TITLE + m.group(2), card, count=1, flags=re.S)
    # tag span group (inline, no separators) + date
    tag_html = "".join(f'<span class="tag">{x}</span>' for x in TAGS)
    card = re.sub(r'(<div class="meta">)(?:\s*<span class="tag">[^<]*</span>)+',
                  lambda m: m.group(1) + tag_html, card, count=1)
    card = re.sub(r'\d{4}-\d{2}-\d{2}', DATE, card, count=1)
    # description paragraph
    card = re.sub(r'<p>.*?</p>', f'<p>{DESC}</p>', card, count=1, flags=re.S)

    # find insertion point: before first card whose date < DATE
    pos = None
    for m in re.finditer(r'<div class="article-card">', t):
        seg = t[m.start():m.start() + 4000]
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
        if dm and dm.group(1) < DATE:
            pos = m.start()
            break
    if pos is None:
        raise RuntimeError(f"{idx}: no insertion point found")

    t2 = t[:pos] + card + "\n  " + t[pos:]
    if t2.replace(card + "\n  ", "", 1) != t:
        raise RuntimeError(f"{idx}: outside-card mutation detected")

    # BlogPosting JSON-LD
    added_ld = 0
    if '"blogPost": [' in t2:
        ld_anchor = '"blogPost": ['
        entry = {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": TITLE, "description": DESC, "inLanguage": "zh-CN",
            "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师"},
            "publisher": {"@type": "Organization", "name": "北京觅理律师事务所",
                          "url": "https://najieip.com/mili/"},
            "datePublished": DATE, "dateModified": DATE,
            "url": f"https://najieip.com/mili/blog/{SLUG}.html",
        }
        i = t2.find(ld_anchor)
        ins = ld_anchor + json.dumps(entry, ensure_ascii=False) + ", "
        t2 = t2[:i] + ins + t2[i + len(ld_anchor):]
        added_ld = 1
        for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
            json.loads(blk)

    # checks
    before = t.count('class="article-card"')
    after = t2.count('class="article-card"')
    d0, b0, _ = depth_stats(t)
    d1, b1, _ = depth_stats(t2)
    h0 = card_depths(t)
    h1 = card_depths(t2)
    mal = len([c for c in re.findall(r'(?=<div class="article-card">)(.{0,80})', t2) if not c.startswith('<div class="article-card">\n    <h2><a href=')])
    print(f"{idx}: cards {before}->{after} (+{after-before}) | div depth {d0}->{d1} bad {b0}->{b1} | depth_hist {h0} -> {h1} | blogPost+{added_ld}")
    assert after == before + 1
    assert d1 == d0 and b1 == b0
    assert t2.count("**") == 0
    assert sum(h1.values()) == after, (h1, after)
    assert set(h1.keys()) == set(h0.keys()), (h0, h1)
    assert all(h1[k] == h0[k] + 1 for k in h1), (h0, h1)
    # assert new card is the first card after insertion point
    if APPLY:
        open(p, "w", encoding="utf-8").write(t2)
        print("  WRITTEN", os.path.getsize(p), "B")
    return True

patch_index("mili/blog/index.html", "./")
patch_index("blog/index.html", "/mili/blog/")
