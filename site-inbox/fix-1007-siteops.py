#!/usr/bin/env python3
"""SiteOps 1007: fix defects on recently-touched brand pages.
 - mili/blog/20261007-trademark-judicial-interpretation-opinion.html : ld=0, og:image=0, desc=title repeat (at homepage exposure rank 3)
 - mili/blog/geely-wm-trade-secret-20260814.html                       : markdown ** and raw tables leaked, ld=0
 - najie/blog/20260901-copyright-jp18-compliance-checklist.html        : markdown ** leaked, ld=0
House templates = same-brand refined pages. Usage: python3 fix-1007-siteops.py [--apply]
"""
import re, os, sys, json, shutil, copy

APPLY = "--apply" in sys.argv
REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles")
os.chdir(REPO)


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
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
    out, o = [], True
    for ch in s:
        if ch == '"':
            out.append("\u201c" if o else "\u201d")
            o = not o
        else:
            out.append(ch)
    return "".join(out)


def esc_attr(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def md_desc(mdf, title):
    p = f"{MD}/{mdf}"
    if not (mdf and os.path.exists(p)):
        return None
    body = strip_fm(read(p))
    parts = []
    for para in [x.strip() for x in body.split("\n\n") if x.strip()]:
        if para.startswith("#") or para.startswith("<!--") or para.startswith("|"):
            continue
        c = re.sub(r"\*+", "", re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para))
        c = re.sub(r"\s+", " ", c).strip()
        if len(c) < 25:
            continue
        parts.append(c)
        if sum(len(x) for x in parts) >= 240:
            break
    if not parts:
        return None
    d = "".join(parts)[:300].rstrip()
    return None if d[:20] in title else d


def page_desc(t, title):
    """Fallbacks when md source is absent: longest non-title <p>, else og/twitter desc."""
    for pat in (r"<p>(.*?)</p>",):
        for x in re.findall(pat, t[t.find("<body"):], re.S):
            c = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()
            if len(c) > 60 and c[:20] not in title:
                return c[:280]
    for name in ("twitter:description", "og:description"):
        m = re.search(rf'name="{name}" content="([^"]*)"', t)
        if m and m.group(1).strip()[:20] not in title and len(m.group(1)) > 60:
            return m.group(1).strip()
    return None


# ---------- house templates ----------
HOUSE = {
    "mili": "mili/blog/technical-secret-presumed-infringement-1590-2026.html",
    "najie": "najie/blog/civil-criminal-cross-19-2026.html",
}
tpl = {}
for b, p in HOUSE.items():
    t = read(p)
    objs = []
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            objs.append(json.loads(blk))
        except Exception:
            pass
    art = next(x for x in objs if x.get("@type") in ("Article", "BlogPosting"))
    crumb = next((x for x in objs if x.get("@type") == "BreadcrumbList"), None)
    tpl[b] = {
        "art": art,
        "crumb": crumb,
        "ogimg": re.search(r'<meta property="og:image" content="([^"]*)"', t).group(1),
        "site": re.search(r'<meta property="og:site_name" content="([^"]*)"', t).group(1),
        "crumb2": crumb["itemListElement"][1]["name"] if crumb else "",
    }
    print(f"[house:{b}] {p} og:image={tpl[b]['ogimg'][:70]} crumb2={tpl[b]['crumb2']}")

# ---------- targets ----------
TARGETS = [
    ("mili", "20261007-trademark-judicial-interpretation-opinion", "20261007-trademark-judicial-interpretation-opinion.md", "2026-10-07"),
    ("mili", "geely-wm-trade-secret-20260814", "geely-wm-trade-secret-20260814.md", "2026-08-14"),
    ("najie", "20260901-copyright-jp18-compliance-checklist", "20260901-copyright-jp18-compliance-checklist.md", "2026-09-01"),
]


def textify(t):
    b = t[t.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    for a, c in (("&gt;", ">"), ("&lt;", "<"), ("&amp;", "&"), ("&quot;", '"'), ("&#8217;", "'")):
        b = b.replace(a, c)
    # strip markdown-artifact characters that the fixer intentionally converts
    return re.sub(r"[\s*|\"“”'’>\-]+", "", b)


summary = []
for brand, slug, mdf, date in TARGETS:
    path = f"{brand}/blog/{slug}.html"
    t = read(path)
    orig, before = t, len(t)
    T = tpl[brand]
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = re.sub(r"\s*—\s*纳杰觅理\s*$", "", ti.group(1)).strip() if ti else slug
    cano = re.search(r'<link rel="canonical" href="([^"]*)"', t)
    url = cano.group(1) if cano else f"https://najieip.com/{brand}/blog/{slug}.html"
    notes = []

    # (1) markdown emphasis -> <strong>
    n_star = len(re.findall(r"\*\*[^*\n]{1,60}\*\*", t)) + len(re.findall(r"\*\*[^*\n]{61,220}\*\*", t))
    if n_star:
        t = re.sub(r"\*\*([^*\n]{1,60})\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\*\*([^*\n]{1,220})\*\*", r"<strong>\1</strong>", t)
        notes.append(f"strong={n_star}")
    # leaked blockquote marker before a bold lead
    n_bq = len(re.findall(r"<p>&gt;\s*(?=<strong>)", t))
    if n_bq:
        t = re.sub(r"<p>&gt;\s*(?=<strong>)", "<p>", t)
        notes.append(f"bq={n_bq}")
    # leaked markdown horizontal rule
    n_hr = len(re.findall(r"<p>-{3,}</p>", t))
    if n_hr:
        t = re.sub(r"<p>-{3,}</p>", "<hr>", t)
        notes.append(f"hr={n_hr}")
    # ASCII quotes inside text nodes -> Chinese quotes (house style, never touch attributes)
    def zh_text_nodes(block):
        parts = re.split(r"(<[^>]+>)", block)
        return "".join(p if p.startswith("<") else zh_quotes(p) for p in parts)
    n_q = 0
    for m in list(re.finditer(r"<p>.*?</p>", t, re.S)):
        seg = m.group(0)
        if '"' in seg:
            new = zh_text_nodes(seg)
            if new != seg:
                t = t[:m.start()] + new + t[m.end():]
                n_q += 1
    if n_q:
        notes.append(f"quotes={n_q}")

    # (2) raw markdown table rows -> <table>
    def conv(block):
        rows = []
        for line in block.split("\n"):
            m = re.match(r"^<p>\|(.*)\|</p>$", line.strip())
            if not m:
                continue
            cells = [c.strip() for c in m.group(1).split("|")]
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                continue
            rows.append(cells)
        if len(rows) < 2:
            return block
        o = ["<table>", "<thead><tr>" + "".join(f"<th>{c}</th>" for c in rows[0]) + "</tr></thead>", "<tbody>"]
        o += ["<tr>" + "".join(f"<td>{c}</td>" for c in r) for r in rows[1:]]
        o.append("</tbody></table>")
        return "\n".join(o)

    n_tbl = 0
    for blk in re.findall(r"(?:^<p>\|.*\|</p>\n?)+", t, re.M):
        new = conv(blk)
        if new != blk:
            t = t.replace(blk, new + "\n", 1)
            n_tbl += 1
    if n_tbl:
        notes.append(f"tables={n_tbl}")

    # (3) description: md source -> page fallback
    d = md_desc(mdf, title)
    if not d and (re.search(r'<meta name="description" content="([^"]*)"', t) or [None])[0]:
        cur = re.search(r'<meta name="description" content="([^"]*)"', t).group(1).strip()
        if cur == title or len(cur) < 80:
            d = page_desc(t, title)
    if d:
        dq = esc_attr(zh_quotes(d))
        for pat in (r'<meta name="description" content="[^"]*">',
                    r'<meta property="og:description" content="[^"]*">',
                    r'<meta name="twitter:description" content="[^"]*">'):
            m = re.search(pat, t)
            if m:
                attr = "name" if 'name="' in pat else "property"
                key = re.search(rf'{attr}="([^"]*)"', pat).group(1)
                t = t[:m.start()] + f'<meta {attr}="{key}" content="{dq}">' + t[m.end():]
        notes.append(f"desc={len(d)}")

    # (4) og:image / twitter
    if 'property="og:image"' not in t:
        t = t.replace("</head>", f'<meta property="og:image" content="{T["ogimg"]}">\n'
                                 f'<meta property="og:site_name" content="{T["site"]}">\n'
                                 f'<meta property="og:locale" content="zh_CN">\n</head>', 1)
        notes.append("og:image+")
    if 'name="twitter:image"' not in t:
        add = (f'<meta name="twitter:title" content="{esc_attr(zh_quotes(title))}">\n'
               f'<meta name="twitter:image" content="{T["ogimg"]}">\n')
        if 'name="twitter:card"' in t:
            m = re.search(r'<meta name="twitter:card"[^>]*>', t)
            t = t[:m.end()] + "\n" + add + t[m.end():]
        else:
            t = t.replace("</head>", add + "</head>", 1)
        notes.append("twitter+")

    # (5) JSON-LD
    if "application/ld+json" not in t:
        a = copy.deepcopy(T["art"])
        a["headline"] = title
        a["description"] = zh_quotes(d) if d else title
        a["image"] = T["ogimg"]
        a["datePublished"] = date
        a["dateModified"] = date
        a["url"] = url
        a["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
        payload = [a]
        if T["crumb"]:
            c = copy.deepcopy(T["crumb"])
            els = c["itemListElement"]
            els[1]["name"] = T["crumb2"]
            els[1]["item"] = f"https://najieip.com/{brand}/blog/"
            els[2]["name"] = title
            els[2]["item"] = url
            payload.append(c)
        txt = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
                        for x in payload)
        t = t.replace("</head>", txt + "\n</head>", 1)
        notes.append("ld+")

    # ---------- self checks ----------
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = len(re.findall(r"application/ld\+json", t))
    ogi = len(re.findall(r'property="og:image"', t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    nrep = int((m.group(1).strip() if m else "") == title)
    stars, tbl = t.count("**"), len(re.findall(r"<p>\|.*\|</p>", t))
    assert h1 == 1 and ld >= 1 and ogi >= 1 and not nrep and stars == 0 and tbl == 0, \
        f"{slug}: check failed h1={h1} ld={ld} ogi={ogi} rep={nrep} stars={stars} tbl={tbl}"
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        json.loads(blk)
    assert textify(t) == textify(orig), f"{slug}: body text changed!"
    if APPLY:
        shutil.copyfile(path, path + ".bak-1007")
        write(path, t)
    summary.append((f"{brand}/{slug}", ", ".join(notes) or "nochange", before, len(t)))

print("\n=== page fixes ===")
for s, n, b, a in summary:
    print(f"  {n:32s} {s}  {b} -> {a} B   (body text identical: asserted, ld+json parses)")
print("APPLY =", APPLY)
