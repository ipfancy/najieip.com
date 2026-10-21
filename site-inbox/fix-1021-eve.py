#!/usr/bin/env python3
"""SiteOps 1021晚修复：主索引补3卡 + judge页og/twitter image + articles.json补judge条目
幂等：已存在则跳过。用法: python3 site-inbox/fix-1021-eve.py [--apply]
"""
import os, re, json, sys, shutil

APPLY = "--apply" in sys.argv
REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

CARDS = [
    # (brand, file, abs_path, date)
    ("mili", "20261022-judge-liability-verdict-reversed.html", "/mili/blog/20261022-judge-liability-verdict-reversed.html", "2026-10-22"),
    ("mili", "20261021-3gpp-proposal-prior-art-date.html", "/mili/blog/20261021-3gpp-proposal-prior-art-date.html", "2026-10-21"),
    ("najie", "20261021-goods-names-acceptable-list-q4.html", "/najie/blog/20261021-goods-names-acceptable-list-q4.html", "2026-10-21"),
]

def read(p): return open(p, encoding="utf-8").read()

def blocks_with_date(t):
    """返回 [(start, date)] —— div 深度配对取每张卡，日期从卡内 meta 提取"""
    out = []
    i = 0
    while True:
        i = t.find('<div class="article-card">', i)
        if i < 0: break
        j, d = i, 0
        while j < len(t):
            n = re.search(r'<div|</div>', t[j:])
            if not n: raise SystemExit("unbalanced div")
            k = j + n.start()
            d += 1 if n.group().startswith('<div') else -1
            j = k + len(n.group())
            if d == 0: break
        blk = t[i:j]
        md = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
        out.append((i, j, md.group(1) if md else ""))
        i = j
    return out

def card_block(t, slug, brand):
    """从品牌索引取卡块（div 深度配对），href 归一为品牌绝对路径"""
    m = re.search(r'<h2><a href="[^"]*' + re.escape(slug), t)
    if not m: raise SystemExit(f"card anchor not found: {slug}")
    st = t.rfind('<div class="article-card">', 0, m.start())
    i, d = st, 0
    while i < len(t):
        n = re.search(r'<div|</div>', t[i:])
        if not n: raise SystemExit("unbalanced div in template")
        j = i + n.start()
        d += 1 if n.group().startswith('<div') else -1
        i = j + len(n.group())
        if d == 0: break
    blk = t[st:i]
    blk = blk.replace('href="./', f'href="/{brand}/blog/')
    assert f'href="/{brand}/blog/' in blk, blk[:200]
    assert blk.rstrip().endswith('</div>')
    return blk

def depth_stats(t):
    """统计 article-card 出现的 div 深度分布"""
    from collections import Counter
    c = Counter(); i = 0; d = 0
    while True:
        n = re.search(r'<div|</div>', t[i:])
        if not n: break
        j = i + n.start()
        if n.group().startswith('<div'):
            if t[j:j+22].startswith('<div class="article-card"'):
                c[d] += 1
            d += 1
        else:
            d -= 1
        i = j + len(n.group())
    return c, d

# ---------- 1. 主索引补卡 ----------
p = "blog/index.html"
t = read(p)
before_cards = t.count('<div class="article-card">')
print(f"[1] 主索引卡片基线 = {before_cards}")
added = []
for brand, fn, href, date in CARDS:
    if href in t or fn in t:
        print(f"    skip (already present): {fn}")
        continue
    brand_idx = read(f"{brand}/blog/index.html")
    blk = card_block(brand_idx, fn[:-5], brand)
    # 找插入点：第一张日期 < 新卡日期的卡之前（保持降序），每轮重扫
    cands = blocks_with_date(t)
    pos = None
    for st, en, d in cands:
        if d and d < date:
            pos = st; break
    if pos is None:
        pos = cands[0][0] if cands else -1
    if pos < 0: raise SystemExit("no cards in main index")
    t = t[:pos] + blk + "\n  " + t[pos:]
    added.append(fn)
    print(f"    + insert {fn} @ date {date} (pos {pos})")
if APPLY and added:
    after = t.count('<div class="article-card">')
    assert after == before_cards + len(added), (before_cards, after)
    for fn in added:
        assert fn in t
    shutil.copy(p, p + ".bak-1021eve")
    open(p, "w", encoding="utf-8").write(t)
    print(f"  APPLIED: cards {before_cards} -> {after}")
elif not APPLY:
    print(f"  DRY-RUN: would become {t.count('<div class=\"article-card\">')}")

# ---------- 2. judge 页 og:image / twitter:image ----------
p2 = "mili/blog/20261022-judge-liability-verdict-reversed.html"
j = read(p2)
IMG = "https://images.pexels.com/photos/5669619/pexels-photo-5669619.jpeg?auto=compress&cs=tinysrgb&w=1200"
if 'property="og:image"' in j:
    print("[2] judge 页 og:image 已存在，跳过")
else:
    head_end = j.find("</head>") + 7
    head, body = j[:head_end], j[head_end:]
    m = re.search(r'(<meta property="og:url" content="[^"]*">\n)', head)
    if not m: raise SystemExit("og:url anchor missing")
    ins = (f'<meta property="og:image" content="{IMG}">\n'
           f'<meta property="og:image:alt" content="案件被改判，法官会被追责吗？最高法新规划了三条线">\n')
    head2 = head[:m.end()] + ins + head[m.end():]
    head2 = head2.replace('<meta name="twitter:card" content="summary">',
                          '<meta name="twitter:card" content="summary_large_image">')
    m2 = re.search(r'(<meta name="twitter:description" content="[^"]*">\n)', head2)
    if not m2: raise SystemExit("twitter:description anchor missing")
    head2 = head2[:m2.end()] + f'<meta name="twitter:image" content="{IMG}">\n' + head2[m2.end():]
    j2 = head2 + body
    assert j2.count("</head>") == 1 and j2.count("<h1") == j.count("<h1") == 1
    assert 'property="og:image"' in j2 and 'name="twitter:image"' in j2
    # body 必须原样
    assert j2[j2.find("</head>")+7:] == body
    if APPLY:
        shutil.copy(p2, p2 + ".bak-1021eve")
        open(p2, "w", encoding="utf-8").write(j2)
        print(f"[2] judge 页补 og:image + twitter:image (len {len(j)} -> {len(j2)})")
    else:
        print(f"[2] DRY-RUN judge 页将补 og/twitter image (len {len(j)} -> {len(j2)})")

# ---------- 3. articles.json 补 judge 条目 ----------
p3 = "articles.json"
arts = json.load(open(p3, encoding="utf-8"))
slug = "20261022-judge-liability-verdict-reversed"
if any(slug in a.get("url", "") for a in arts):
    print("[3] articles.json 已有 judge 条目，跳过")
else:
    idx_html = read("mili/blog/index.html")
    mm = re.search(r'<p>(.*?)</p>', idx_html[idx_html.find("20261022-judge")-2000:idx_html.find("20261022-judge")+2000])
    entry = {
        "title": "案件被改判，法官会被追责吗？最高法新规划了三条线",
        "url": f"/mili/blog/{slug}.html",
        "date": "2026-10-22",
        "description": "改判不等于错案，错案不等于追责。最高法《人民法院司法责任追究条例》（六章四十七条）给出三要素判定标准，同时把诬告、辱骂法官的代价摆上明面：一人以诬告陷害罪被追刑责，一人被行政拘留五日。附三条救济路径与时限表。",
        "tags": ["司法责任", "改判与再审", "诉讼救济"],
        "site": "mili",
    }
    arts2 = [entry] + arts
    assert len(arts2) == len(arts) + 1
    if APPLY:
        shutil.copy(p3, p3 + ".bak-1021eve")
        json.dump(arts2, open(p3, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(p3, "a", encoding="utf-8").write("\n")
        print(f"[3] articles.json 补 judge 条目: {len(arts)} -> {len(arts2)}")
    else:
        print(f"[3] DRY-RUN articles.json 将补 judge 条目: {len(arts)} -> {len(arts2)}")
print("\nDONE apply=", APPLY)
