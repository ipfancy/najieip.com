#!/usr/bin/env python3
"""精确体检指定页面（不依赖共享变量）"""
import re, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
FILES = [
    "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
    "mili/blog/20261005-mili-gas-supply-cutoff-justification.html",
    "mili/blog/20261004-mili-gas-deviation-settlement-account.html",
    "mili/blog/20261005-trade-secret-confidentiality-measures.html",
    "mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
    "najie/blog/20261005-patent-annual-fee-ledger-5-signals.html",
    "najie/blog/20261005-trademark-law-2027-implementing-rules.html",
    "najie/blog/20261005-trademark-squatting-3-remedies.html",
    "najie/blog/20261003-trademark-invalidated-500w.html",
    "en/blog/20261005-trademark-law-2027-implementing-rules-en.html",
    "fr/blog/20261005-trademark-law-2027-implementing-rules-fr.html",
]

for rel in FILES:
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        print(f"MISSING {rel}")
        continue
    size = os.path.getsize(p)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    h1 = len(re.findall(r"<h1[ >]", t))
    h2 = len(re.findall(r"<h2[ >]", t))
    ld = t.count("application/ld+json")
    ogimg = "og:image" in t
    twcard = "twitter:card" in t
    md = re.search(r'<meta name="description" content="([^"]*)"', t)
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    desc = md.group(1) if md else ""
    title = ti.group(1).strip() if ti else ""
    defrep = (desc.strip()[:30] in title) if desc else True
    starstar = t.count("**")
    ptable = len(re.findall(r"<p>\|.*\|</p>", t))
    style = ("<style" in t) or ("/style.css" in t)
    schema_ok = t.count("https://schema.org")
    schema_bad = t.count("https://***")
    print(f"{rel}")
    print(f"   {size}B h1={h1} h2={h2} ld={ld} og:image={ogimg} tw={twcard} style={style} desc_len={len(desc)} defrep={defrep} **={starstar} 裸表={ptable} schema={schema_ok} bad={schema_bad}")
    print(f"   title={title[:70]}")
    print(f"   desc={desc[:110]}")
