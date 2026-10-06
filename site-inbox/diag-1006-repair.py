#!/usr/bin/env python3
"""1006 修复前取证：房屋模板 + 目标页结构 + md 源摘要"""
import re, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles")

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def strip_fm(s):
    if s.startswith("---"):
        e = s.find("\n---", 3)
        if e > 0:
            return s[e+4:].lstrip()
    return s

print("=== 模板 A: mili 精修页 ===")
ta = read(f"{REPO}/mili/blog/20261005-trade-secret-confidentiality-measures.html")
for m in re.finditer(r'<meta (?:property|name)="(og:[^"]+|twitter:[^"]+)" content="([^"]*)"', ta):
    if m.group(1) in ("og:image", "og:site_name", "og:locale", "og:type", "twitter:card", "twitter:title", "twitter:image", "twitter:description"):
        print(f"  {m.group(1)} = {m.group(2)[:120]}")
print(f"  hreflang count = {len(re.findall(r'rel=\"alternate\"', ta))}")
print("  --- ld+json blocks ---")
for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', ta, re.S)):
    print(f"  [block {i}] {blk.strip()[:800]}")
    print("  ---")

print("\n=== 目标页结构汇总 ===")
TARGETS = [
    ("mili", "20261006-mili-gas-post-judgment-six-checklist", "20261006-mili-gas-post-judgment-six-checklist.md"),
    ("mili", "20261005-mili-gas-supply-cutoff-justification", "20261005-mili-gas-supply-cutoff-justification.md"),
    ("mili", "20261004-mili-gas-deviation-settlement-account", "20261004-mili-gas-deviation-settlement-account.md"),
    ("mili", "bambu-stratasys-fto-decision-tree-20261004", "bambu-stratasys-fto-decision-tree-20261004.md"),
    ("najie", "20261005-patent-annual-fee-ledger-5-signals", "20261005-patent-annual-fee-ledger-5-signals.md"),
    ("najie", "20261005-trademark-law-2027-implementing-rules", "20261005-trademark-law-2027-implementing-rules.md"),
    ("najie", "20261003-trademark-invalidated-500w", "20261003-trademark-invalidated-500w.md"),
]
for brand, slug, mdf in TARGETS:
    p = f"{REPO}/{brand}/blog/{slug}.html"
    if not os.path.exists(p):
        print(f"\n-- {brand}/{slug}: FILE MISSING")
        continue
    t = read(p)
    print(f"\n-- {brand}/{slug} ({os.path.getsize(p)}B)")
    print(f"   h1={len(re.findall(r'<h1[ >]', t))} h2={len(re.findall(r'<h2[ >]', t))}")
    print(f"   h2 texts: {re.findall(r'<h2[^>]*>(.*?)</h2>', t, re.S)[:8]}")
    stars = re.findall(r'\*\*[^*]{1,30}\*\*', t)
    print(f"   ** samples: {stars[:6]}")
    tbl = re.findall(r'<p>\|[^\n]{0,70}</p>', t)
    print(f"   裸表行数={len(re.findall(r'<p>\|.*\|</p>', t))} samples: {tbl[:3]}")
    mdp = f"{MD}/{mdf}"
    if os.path.exists(mdp):
        body = strip_fm(read(mdp))
        paras = [x.strip() for x in body.split("\n\n") if x.strip() and not x.strip().startswith("#") and not x.strip().startswith("<!--")]
        print(f"   md exists | 首段: {paras[0][:160] if paras else 'NONE'}")
    else:
        print("   md MISSING")
    print(f"   article tag: {'<article' in t} | nav: {'<nav' in t} | footer: {'<footer' in t}")
