#!/usr/bin/env python3
"""Diagnose defective pages: head tags, ld blocks, markdown leakage, table candidates."""
import os, re, glob, json

REPO = "/Users/ziganghe/wiki/najieip-verify"
os.chdir(REPO)

TARGETS = [
    "mili/blog/20261007-trademark-judicial-interpretation-opinion.html",
    "mili/blog/geely-wm-trade-secret-20260814.html",
    "najie/blog/20260901-copyright-jp18-compliance-checklist.html",
]


def rd(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


print("=== FULL-SITE DEFECT SWEEP (all */blog/*.html except index) ===")
bad = []
for f in sorted(glob.glob("*/blog/*.html")):
    if f.endswith("index.html"):
        continue
    t = rd(f)
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    ttl = re.search(r"<title>(.*?)</title>", t, re.S)
    desc = (m.group(1) if m else "").strip()
    title = re.sub(r"\s*—\s*纳杰觅理\s*$", "", (ttl.group(1).strip() if ttl else ""))
    d = dict(
        h1=len(re.findall(r"<h1[\s>]", t)),
        ld=len(re.findall(r"application/ld\+json", t)),
        ogimg=len(re.findall(r'property="og:image"', t)),
        rep=int(desc == title),
        stars=t.count("**"),
        tbl=len(re.findall(r"<p>\|.*\|</p>", t)),
    )
    ok = d["h1"] == 1 and d["ld"] >= 1 and d["ogimg"] >= 1 and not d["rep"] and d["stars"] == 0 and d["tbl"] == 0
    if not ok:
        bad.append((f, d))
print(f"total pages: {len([f for f in glob.glob('*/blog/*.html') if not f.endswith('index.html')])}, defective: {len(bad)}")
for f, d in bad:
    print("  BAD", f, d)
print()
print("=== TARGET DETAIL ===")
for p in TARGETS:
    t = rd(p)
    print("---", p, len(t), "chars")
    head = t[: t.find("</head>")]
    print("  head meta tags:")
    for mm in re.findall(r'<meta [^>]*>', head)[:24]:
        print("   ", mm[:160])
    print("  link tags:", [x[:110] for x in re.findall(r'<link [^>]*>', head)])
    print("  ld blocks:", len(re.findall(r'application/ld\+json', t)))
    print("  h1:", re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)[:1])
    body = t[t.find("<body"):]
    print("  stars:", t.count("**"), "rawtable:", len(re.findall(r"<p>\|.*\|</p>", t)))
    for x in re.findall(r"<p>\|[^\n]{0,120}", t)[:7]:
        print("   TBL:", x[:130])
    for x in re.findall(r"[^>]{0,60}\*\*[^<]{0,60}", t)[:8]:
        print("   STR:", x.replace("\n", " ")[:130])
    ps = re.findall(r"<p>(.*?)</p>", body, re.S)
    print("  first 3 <p>:", [re.sub(r"\s+", " ", x)[:110] for x in ps[:3]])
    print("  last 2 <p>:", [re.sub(r"\s+", " ", x)[:110] for x in ps[-2:]])
