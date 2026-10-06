#!/usr/bin/env python3
"""SiteOps 1006 修复：上游裸发布页精修 + 索引补卡
用法: python3 fix-1006-siteops.py [--apply]
"""
import re, os, sys, json, shutil, copy

APPLY = "--apply" in sys.argv
REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles")
TODAY = "2026-10-06"

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)

def strip_fm(s):
    if s.startswith("---"):
        e = s.find("\n---", 3)
        if e > 0:
            return s[e + 4:].lstrip()
    return s

def zh_quotes(s):
    out, open_ = [], True
    for ch in s:
        if ch == '"':
            out.append("\u201c" if open_ else "\u201d")
            open_ = not open_
        else:
            out.append(ch)
    return "".join(out)

def esc_attr(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))

def md_desc(mdf, title):
    p = f"{MD}/{mdf}"
    if not os.path.exists(p):
        return None
    body = strip_fm(read(p))
    paras = [x.strip() for x in body.split("\n\n") if x.strip()]
    parts = []
    for para in paras:
        if para.startswith("#") or para.startswith("<!--") or para.startswith("|"):
            continue
        clean = re.sub(r"\*+", "", para)
        clean = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        if len(clean) < 25:
            continue
        parts.append(clean)
        if sum(len(x) for x in parts) >= 240:
            break
    if not parts:
        return None
    d = "".join(parts)
    d = d[:300].rstrip()
    if d.startswith(title[:20]):
        return None
    return d

def md_h2s(mdf):
    p = f"{MD}/{mdf}"
    if not os.path.exists(p):
        return []
    body = strip_fm(read(p))
    out = []
    for m in re.finditer(r"^##\s+(.+)$", body, re.M):
        t = m.group(1).strip()
        if t and not t.startswith("合集"):
            out.append(t)
    return out

def md_paras(mdf):
    p = f"{MD}/{mdf}"
    if not os.path.exists(p):
        return []
    body = strip_fm(read(p))
    out = []
    for x in body.split("\n\n"):
        x = x.strip()
        if not x or x.startswith("#") or x.startswith("<!--"):
            continue
        if x.startswith("|"):
            continue
        out.append(x)
    return out

# ---------- 房屋模板 ----------
TPL = {
    "mili": f"{REPO}/mili/blog/20261005-trade-secret-confidentiality-measures.html",
    "najie": f"{REPO}/najie/blog/20261005-trademark-squatting-3-remedies.html",
}
tpl_cache = {}
for b, p in TPL.items():
    t = read(p)
    blocks = json.loads("[" + ",".join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)) + "]") if False else None
    arts = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            arts.append(json.loads(blk))
        except Exception:
            pass
    article = next(x for x in arts if x.get("@type") in ("Article", "BlogPosting"))
    crumb = next((x for x in arts if x.get("@type") == "BreadcrumbList"), None)
    ogimg = re.search(r'<meta property="og:image" content="([^"]*)"', t).group(1)
    site = re.search(r'<meta property="og:site_name" content="([^"]*)"', t).group(1)
    tpl_cache[b] = {"article": article, "crumb": crumb, "ogimg": ogimg, "site": site}
    print(f"[tpl:{b}] og:image={ogimg[:60]} site={site} crumb2={crumb['itemListElement'][1]['name'] if crumb else None}")

# ---------- 目标页 ----------
TARGETS = [
    ("mili", "20261006-mili-gas-post-judgment-six-checklist", "20261006-mili-gas-post-judgment-six-checklist.md", "2026-10-06"),
    ("mili", "20261005-mili-gas-supply-cutoff-justification", "20261005-mili-gas-supply-cutoff-justification.md", "2026-10-05"),
    ("mili", "20261004-mili-gas-deviation-settlement-account", "20261004-mili-gas-deviation-settlement-account.md", "2026-10-04"),
    ("mili", "bambu-stratasys-fto-decision-tree-20261004", "bambu-stratasys-fto-decision-tree-20261004.md", "2026-10-04"),
    ("najie", "20261005-patent-annual-fee-ledger-5-signals", "20261005-patent-annual-fee-ledger-5-signals.md", "2026-10-05"),
    ("najie", "20261005-trademark-law-2027-implementing-rules", None, "2026-10-05"),
    ("najie", "20261003-trademark-invalidated-500w", "20261003-trademark-invalidated-500w.md", "2026-10-03"),
]

summary = []
for brand, slug, mdf, date in TARGETS:
    path = f"{REPO}/{brand}/blog/{slug}.html"
    if not os.path.exists(path):
        summary.append((slug, "MISSING"))
        continue
    t = read(path)
    orig = t
    tpl = tpl_cache[brand]
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = re.sub(r"\s*—\s*纳杰觅理\s*$", "", ti.group(1)).strip() if ti else slug
    cano = re.search(r'<link rel="canonical" href="([^"]*)"', t)
    url = cano.group(1) if cano else f"https://najieip.com/{brand}/blog/{slug}.html"
    notes = []

    # (1) markdown 强调 -> strong
    n_star = len(re.findall(r"\*\*[^*\n]{1,60}\*\*", t))
    if n_star:
        t = re.sub(r"\*\*([^*\n]{1,60})\*\*", r"<strong>\1</strong>", t)
        notes.append(f"strong={n_star}")

    # (2) 裸 markdown 表格 -> <table>
    def conv_table(m):
        rows = []
        for line in m.group(0).split("\n"):
            inner = re.match(r"^<p>\|(.*)\|</p>$", line.strip())
            if not inner:
                continue
            cells = [c.strip() for c in inner.group(1).split("|")]
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                continue
            rows.append(cells)
        if len(rows) < 2:
            return m.group(0)
        out = ["<table>", "<thead><tr>" + "".join(f"<th>{c}</th>" for c in rows[0]) + "</tr></thead>", "<tbody>"]
        for r in rows[1:]:
            out.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
        out.append("</tbody></table>")
        return "\n".join(out)

    n_tbl = 0
    blocks = re.findall(r"(?:^<p>\|.*\|</p>\n?)+", t, re.M)
    for blk in blocks:
        new = conv_table(re.match(r"(?s)(.*)", blk))
        if new != blk:
            t = t.replace(blk, new + "\n", 1)
            n_tbl += 1
    if n_tbl:
        notes.append(f"tables={n_tbl}")

    # (3) h1 回填 + h2 路标
    if len(re.findall(r"<h1[ >]", t)) == 0:
        am = re.search(r"<article[^>]*>", t)
        if am:
            t = t[:am.end()] + f"\n<h1>{esc_attr(title)}</h1>" + t[am.end():]
            notes.append("h1+")
    h2n = len(re.findall(r"<h2[ >]", t))
    if h2n == 0 and mdf:
        hs = md_h2s(mdf)
        paras = md_paras(mdf)
        added = 0
        for h in hs:
            key = re.sub(r"\*\*|\s", "", h)[:18]
            for para in paras:
                pk = re.sub(r"\*\*|\s", "", para)[:18]
                if pk and pk == key:
                    tag = f"<h2>{esc_attr(re.sub(r'[*]*','',h))}</h2>"
                    # 找正文中该段对应的 <p>
                    pm = re.search(r"<p>" + re.escape(re.sub(r"\*\*", "<strong>", re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", para))[:60]), t)
                    if pm:
                        t = t[:pm.start()] + tag + "\n" + t[pm.start():]
                        added += 1
                    break
        if added:
            notes.append(f"h2+={added}")

    # (4) 元数据：og:image / twitter / description
    if "og:image" not in t:
        t = t.replace("</head>", f'<meta property="og:image" content="{tpl["ogimg"]}">\n<meta property="og:site_name" content="{tpl["site"]}">\n<meta property="og:locale" content="zh_CN">\n</head>', 1)
        notes.append("og:image+")
    if 'twitter:card" content="summary"' in t:
        t = t.replace('<meta name="twitter:card" content="summary">',
                      '<meta name="twitter:card" content="summary_large_image">\n'
                      f'<meta name="twitter:title" content="{esc_attr(title)}">\n'
                      f'<meta name="twitter:image" content="{tpl["ogimg"]}">', 1)
        notes.append("tw+")

    desc = md_desc(mdf, title) if mdf else None
    if desc:
        dq = zh_quotes(desc)
        m = re.search(r'<meta name="description" content="[^"]*">', t)
        if m:
            t = t[:m.start()] + f'<meta name="description" content="{esc_attr(dq)}">' + t[m.end():]
        m = re.search(r'<meta property="og:description" content="[^"]*">', t)
        if m:
            t = t[:m.start()] + f'<meta property="og:description" content="{esc_attr(dq)}">' + t[m.end():]
        m = re.search(r'<meta name="twitter:description" content="[^"]*">', t)
        if m:
            t = t[:m.start()] + f'<meta name="twitter:description" content="{esc_attr(dq)}">' + t[m.end():]
        elif "twitter:title" in t:
            t = t.replace('<meta name="twitter:image"', f'<meta name="twitter:description" content="{esc_attr(dq)}">\n<meta name="twitter:image"', 1)
        notes.append(f"desc={len(dq)}")

    # (5) JSON-LD
    if "application/ld+json" not in t:
        art = copy.deepcopy(tpl["article"])
        art["headline"] = title
        art["description"] = zh_quotes(desc) if desc else title
        art["image"] = tpl["ogimg"]
        art["datePublished"] = date
        art["dateModified"] = date
        art["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
        art["url"] = url
        cr = copy.deepcopy(tpl["crumb"])
        if cr:
            els = cr["itemListElement"]
            els[1]["name"] = tpl["crumb"]["itemListElement"][1]["name"]
            els[1]["item"] = f"https://najieip.com/{brand}/blog/"
            els[2]["name"] = title
            els[2]["item"] = url
        payload = [art] + ([cr] if cr else [])
        txt = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in payload)
        t = t.replace("</head>", txt + "\n</head>", 1)
        notes.append("ld+")

    if t != orig:
        if APPLY:
            shutil.copyfile(path, path + ".bak-1006")
            write(path, t)
        summary.append((f"{brand}/{slug}", ",".join(notes)))
    else:
        summary.append((f"{brand}/{slug}", "nochange"))

print("\n=== 页面修复 ===")
for s, n in summary:
    print(f"  {n:24s} {s}")

# ---------- 索引补卡 ----------
def extract_first_card(t):
    m = re.search(r'<div class="article-card">', t)
    if not m:
        return None
    i = m.start()
    depth = 0
    for tag in re.finditer(r"<div\b[^>]*>|</div>", t[i:]):
        depth += -1 if tag.group(0).startswith("</") else 1
        if depth == 0:
            return t[i:i + tag.end()]
    return None

def card_template(idx, brand):
    return extract_first_card(idx)

def make_card(tplcard, href, title, desc, date, tag):
    c = tplcard
    c = re.sub(r'(<h2><a href=")[^"]*(">)[^<]*(</a></h2>)',
               lambda m: m.group(1) + href + m.group(2) + esc_attr(zh_quotes(title)) + m.group(3), c, count=1)
    c = re.sub(r"<p>.*?</p>", f"<p>{esc_attr(zh_quotes(desc[:220]))}</p>", c, count=1, flags=re.S)
    c = re.sub(r"\d{4}-\d{2}-\d{2}", date, c, count=1)
    if tag:
        c = re.sub(r'(?:\s*<span class="tag">[^<]*</span>)+',
                   f'<span class="tag">{esc_attr(zh_quotes(tag))}</span>', c, count=1)
    return c

def insert_card(t, card, date):
    pos = None
    cards = list(re.finditer(r'<div class="article-card">', t))
    for m in cards:
        seg = t[m.start():m.start() + 1200]
        d = re.search(r"(\d{4}-\d{2}-\d{2})", seg)
        if d and d.group(1) < date:
            pos = m.start()
            break
    if pos is None:
        pos = cards[-1].start() if cards else t.find('<div class="container">') + 22
    return t[:pos] + card + "\n  " + t[pos:], pos

INDEX_WORK = []
# mili 索引
mi = f"{REPO}/mili/blog/index.html"
t = read(mi)
if "20261006-mili-gas-post-judgment-six-checklist" not in t:
    ct = card_template(t, "mili")
    d = md_desc("20261006-mili-gas-post-judgment-six-checklist.md", "赢了官司还被点名6条")
    card = make_card(ct, "./20261006-mili-gas-post-judgment-six-checklist.html",
                     "赢了官司还被点名6条：这份合规清单抄了就能用", d or "赢了官司还被点名6条：这份合规清单抄了就能用", "2026-10-06", "合规")
    t2, pos = insert_card(t, card, "2026-10-06")
    print(f"[diag] card len={len(card)} article-card_count={card.count('class=\"article-card\"')}")
    print("[diag] card head:", card[:150].replace("\n", "\\n"))
    print("[diag] card tail:", card[-160:].replace("\n", "\\n"))
    assert t2.replace(card + "\n  ", "", 1) == t, "mili idx: 插入块外被改"
    assert t2.count('class="article-card"') == t.count('class="article-card"') + 1, \
        f"mili idx: 卡片计数异常 {t2.count('class=\"article-card\"')} vs {t.count('class=\"article-card\"')}"
    assert t2.count("<div") - t2.count("</div>") == t.count("<div") - t.count("</div>"), "mili idx: div 不平"
    print(f"\n=== mili 索引插卡成功 (pos={pos}) ===")
    print(card[:400])
    if APPLY:
        shutil.copyfile(mi, mi + ".bak-1006")
        write(mi, t2)
    INDEX_WORK.append(mi)

# 主索引
bi = f"{REPO}/blog/index.html"
t = read(bi)
main_add = [
    ("/mili/blog/20261006-mili-gas-post-judgment-six-checklist.html", "赢了官司还被点名6条：这份合规清单抄了就能用", "2026-10-06", "合规", "20261006-mili-gas-post-judgment-six-checklist.md"),
    ("/mili/blog/shuju-chanquan-dengji-2026.html", None, None, None, None),
    ("/najie/blog/jishu-hetong-zhuanli-guishu-2026.html", None, None, None, None),
]
for href, title, date, tag, mdf in main_add:
    if href in t:
        print(f"skip (已存在) {href}")
        continue
    p = REPO + href
    if not os.path.exists(p):
        print(f"skip (文件不存在) {href}")
        continue
    pg = read(p)
    if title is None:
        ti2 = re.search(r"<title>(.*?)</title>", pg, re.S)
        title = re.sub(r"\s*—\s*纳杰觅理\s*$", "", ti2.group(1)).strip() if ti2 else href
    if date is None:
        m = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', pg)
        if not m:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(href))
        date = m.group(1) if m else "2026-10-01"
    if tag is None:
        m = re.search(r'<meta name="keywords" content="([^"]*)"', pg)
        tag = m.group(1).split(",")[0].strip() if m else ""
    if mdf is None:
        mdf = os.path.basename(href).replace(".html", ".md")
    d = md_desc(mdf, title)
    if not d:
        m = re.search(r'<meta name="description" content="([^"]*)"', pg)
        d = m.group(1) if m else title
        if len(d) < 25 or d.strip()[:20] in title:
            m2 = re.search(r"<p>(.*?)</p>", pg, re.S)
            d = re.sub(r"<[^>]+>", "", m2.group(1))[:220] if m2 else title
    ct = card_template(t, "main")
    card = make_card(ct, href, title, d, date, tag)
    t2, pos = insert_card(t, card, date)
    assert t2.replace(card + "\n  ", "", 1) == t, f"main idx: 插入块外被改 ({href})"
    assert t2.count('class="article-card"') == t.count('class="article-card"') + 1
    assert t2.count("<div") - t2.count("</div>") == t.count("<div") - t.count("</div>"), "main idx: div 不平"
    t = t2
    print(f"main idx +card pos={pos} date={date} {href}")
if t != read(bi):
    if APPLY:
        shutil.copyfile(bi, bi + ".bak-1006")
        write(bi, t)
    INDEX_WORK.append(bi)

print("\nAPPLY =", APPLY, "| 改动文件:", INDEX_WORK)
