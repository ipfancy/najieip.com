#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1030: 品牌索引 + 主索引补卡 + articles.json 条目（幂等、日期降序插位）。
用法: python3 site-inbox/gen-1030-index.py [--apply]
"""
import os, re, sys, json, html

SITE = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv

TARGETS = [
    ("mili", "20261030-mili-ai-harm-outpaces-law"),
    ("najie", "20261030-najie-training-data-provenance"),
    ("najie", "20261030-najie-foreign-filing-confidentiality-review"),
    ("mili", "20261030-mili-trademark-renewal"),
    ("mili", "20261028-mili-social-insurance-subsidy"),
    ("mili", "20261021-mili-ai-creation-cost-evidence"),
]

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def wr(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def page_fields(brand, slug):
    t = rd(os.path.join(SITE, brand, "blog", slug + ".html"))
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = html.unescape(ti.group(1)).split(" — ")[0].strip() if ti else slug
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = html.unescape(d.group(1)) if d else ""
    k = re.search(r'<meta name="keywords" content="([^"]*)"', t)
    tags = [x.strip() for x in k.group(1).split(",")][:3] if k else []
    dt = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', t)
    return dict(title=title, desc=desc, tags=tags, date=dt.group(1) if dt else "2026-10-30")

def card_end(t, s):
    i, depth = s, 0
    while i < len(t):
        o = t.find("<div", i); c = t.find("</div>", i)
        if c == -1:
            return len(t)
        if o != -1 and o < c:
            depth += 1; i = o + 4
        else:
            depth -= 1; i = c + 6
            if depth == 0:
                return i
    return len(t)

def cards(t):
    res = []
    for m in re.finditer(r'<div class="article-card">', t):
        s = m.start(); e = card_end(t, s)
        blk = t[s:e]
        d = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
        res.append(dict(s=s, e=e, blk=blk, date=d.group(1) if d else ""))
    return res

def build_from(skel, f, href):
    blk = re.sub(r'(<h[23][^>]*>\s*<a [^>]*href=")([^"]*)(")', lambda m: m.group(1) + href + m.group(3), skel, count=1)
    blk = re.sub(r'(<h[23][^>]*>\s*<a [^>]*>)(.*?)(</a>)',
                 lambda m: m.group(1) + html.escape(f["title"]) + m.group(3), blk, count=1, flags=re.S)
    blk = re.sub(r"\d{4}-\d{2}-\d{2}", f["date"], blk)
    tags = "".join('<span class="tag">%s</span>' % t for t in f["tags"])
    if tags:
        blk = re.sub(r'(?:<span class="tag">[^<]*</span>)+', tags, blk, count=1)
    ps = list(re.finditer(r"<p>(.*?)</p>", blk, re.S))
    if ps and f["desc"]:
        m = ps[-1]
        blk = blk[:m.start()] + "<p>%s</p>" % html.escape(f["desc"]) + blk[m.end():]
    return blk

def insert(t, blk, date):
    cs = cards(t)
    assert cs, "no cards"
    for c in cs:
        if c["date"] and c["date"] < date:
            return t[:c["s"]] + blk + "\n  " + t[c["s"]:], c["date"]
    last = cs[-1]
    return t[:last["e"]] + "\n  " + blk + t[last["e"]:], "tail"

def depth_hist(t):
    hist, depth = {}, 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", t):
        if m.group(1):
            depth -= 1
        else:
            hist[depth] = hist.get(depth, 0) + 1
            depth += 1
    return hist, depth

def process(path, brand_filter, f_of, href_of):
    t = rd(path)
    base_hist, base_depth = depth_hist(t)
    base_cards = t.count('<div class="article-card">')
    added = []
    for brand, slug in TARGETS:
        if brand_filter and brand != brand_filter:
            continue
        if slug in t:
            continue
        f = f_of(brand, slug)
        skel = cards(t)[0]["blk"]
        blk = build_from(skel, f, href_of(brand, slug))
        t2, anchor = insert(t, blk, f["date"])
        assert t2.replace(blk + "\n  ", "", 1) == t, f"roundtrip fail {slug}"
        t = t2
        added.append(slug)
        print(f"  + {path.split('/')[-2]}/{slug} (date {f['date']}, anchor {anchor})")
    hist, depth = depth_hist(t)
    assert depth == base_depth, f"{path}: div depth {base_depth}->{depth}"
    assert t.count('<div class="article-card">') == base_cards + len(added)
    assert t.count("**") == 0
    assert hist.get(1, 0) - base_hist.get(1, 0) == len(added), f"{path}: depth hist {base_hist} -> {hist}"
    if APPLY and added:
        wr(path, t)
    return added

def main():
    total = []
    print("[brand indexes]")
    for brand in ("mili", "najie"):
        p = os.path.join(SITE, brand, "blog", "index.html")
        total += process(p, brand, page_fields, lambda b, s: "./%s.html" % s)
    print("[main index]")
    p = os.path.join(SITE, "blog", "index.html")
    total += process(p, None, page_fields, lambda b, s: "/%s/blog/%s.html" % (b, s))

    # --- articles.json ---
    ap = os.path.join(SITE, "articles.json")
    data = json.load(open(ap, encoding="utf-8"))
    have = {d.get("url", "") for d in data}
    new_entries = []
    for brand, slug in TARGETS:
        url = "/%s/blog/%s.html" % (brand, slug)
        if url in have:
            continue
        f = page_fields(brand, slug)
        new_entries.append(dict(url=url, title=f["title"], date=f["date"], site=brand))
    data.extend(new_entries)
    data.sort(key=lambda d: d.get("date", ""), reverse=True)
    if APPLY and new_entries:
        with open(ap, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    print(f"[articles.json] +{len(new_entries)} -> total {len(data)}")
    print("TOTAL index inserts:", len(total))

if __name__ == "__main__":
    main()
