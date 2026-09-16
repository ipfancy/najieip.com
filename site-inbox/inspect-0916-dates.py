#!/usr/bin/env python3
"""Inspect date sources: article JSON-LD, meta tags, brand index embedded BlogPosting list."""
import re, os, json
root = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(root)

samples = ['najie/blog/20260817-trademark-nonuse-cancellation-rescue.html',
           'mili/blog/ai-music-copyright-boundary.html',
           'aipunajie/blog/utility-model-fast-grant-20260813.html',
           'aipunajie/blog/catl-patent-moat-profit-2026.html']
for f in samples:
    t = open(f, encoding='utf-8').read()
    print("=" * 70)
    print(f, len(t), "B")
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
        print("  JSONLD:", re.sub(r'\s+', ' ', m.group(1))[:300])
    for pat in [r'<meta[^>]*"(article:published_time|datePublished|date)[^>]*>',
                r'<meta name="date"[^>]*>', r'<time[^>]*datetime="([^"]*)"']:
        for m in re.finditer(pat, t):
            print("  meta/time:", m.group(0)[:160])
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, flags=re.S)
    print("  h1:", re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h1.group(1))).strip()[:80] if h1 else None)
    ogd = re.search(r'<meta property="og:description" content="([^"]*)"', t)
    print("  og:desc:", (ogd.group(1)[:100] if ogd else None))

print("\n" + "=" * 70)
print("brand index embedded BlogPosting maps:")
for b in ['najie', 'mili', 'aipunajie']:
    idx = open(f'{b}/blog/index.html', encoding='utf-8').read()
    pairs = re.findall(r'"url"\s*:\s*"([^"]+)"\s*,\s*"datePublished"\s*:\s*"([^"]+)"', idx)
    print(f"  {b}: {len(pairs)} BlogPosting entries, sample:", pairs[:2])
    # also try reverse order
    if not pairs:
        pairs2 = re.findall(r'"@type"\s*:\s*"BlogPosting".{0,400}?', idx, flags=re.S)[:2]
        print("   raw:", [re.sub(r'\s+', ' ', p)[:200] for p in pairs2])
