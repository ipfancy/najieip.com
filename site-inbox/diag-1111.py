#!/usr/bin/env python3
"""2026-11-11 夜检诊断：页面存在/六项/正文md包含"""
import os, re, glob, json

REPO = "/Users/ziganghe/wiki/najieip-verify"
MD = "/Users/ziganghe/wiki/digital-employees/articles"

cands = [
    ("mili", "20261111-mili-fake-patent-marking-line"),
    ("najie", "20261111-najie-same-day-dual-filing-one-choice"),
    ("mili", "20261112-mili-year-end-bonus-cancel"),
    ("mili", "20261111-mili-earnest-money-cap"),
]

def textify(html):
    b = html
    m = re.search(r"<article.*?</article>", b, re.S)
    if m:
        b = m.group(0)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<h2>.*?</h2>", " ", b, flags=re.S)
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<figure.*?</figure>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", "", b)
    b = b.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&nbsp;", " ")
    b = re.sub(r"[\s*|:\"'“”‘’>–\-]+", "", b)
    return b

for brand, slug in cands:
    p = os.path.join(REPO, brand, "blog", slug + ".html")
    md = os.path.join(MD, slug + ".md")
    print("=" * 60)
    print(f"{brand}/{slug}")
    if not os.path.exists(p):
        print(f"  PAGE MISSING  (md exists={os.path.exists(md)})")
        continue
    t = open(p, encoding="utf-8", errors="replace").read()
    size = os.path.getsize(p)
    h1 = len(re.findall(r"<h1[ >]", t))
    h2 = len(re.findall(r"<h2[ >]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = 'og:image' in t
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = desc.group(1) if desc else ""
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    title = title.group(1).strip() if title else ""
    stars = len(re.findall(r"(?<![0-9*])\*\*", t))
    bare_table = len(re.findall(r"<p>\|", t))
    style = ("<style" in t) or ('/style.css' in t)
    can = re.search(r'<link rel="canonical" href="([^"]*)"', t)
    can = can.group(1) if can else "NONE"
    print(f"  size={size} h1={h1} h2={h2} ld={ld} og:image={ogimg} style={style} stars={stars} baretbl={bare_table}")
    print(f"  desc[{len(desc)}]={desc[:70]}")
    print(f"  title={title[:60]}")
    print(f"  canonical={can}")
    print(f"  canonical_ok={can.endswith('/' + brand + '/blog/' + slug + '.html')}")
    # md containment
    if os.path.exists(md):
        m = open(md, encoding="utf-8", errors="replace").read()
        m = re.sub(r"^---.*?---", "", m, count=1, flags=re.S)
        m = re.sub(r"<!--.*?-->", " ", m, flags=re.S)
        mt = textify("<article>" + m.replace("##", "") + "</article>")
        pt = textify(t)
        BY = "何自刚|知识产权律师|爱普纳杰·觅理·纳杰"
        print(f"  md_contained={mt in pt}  md_len={len(mt)} pg_len={len(pt)}")
    else:
        print("  md source missing")
