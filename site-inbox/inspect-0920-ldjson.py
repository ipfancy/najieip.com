import re, json
t = open('blog/index.html', encoding='utf-8').read()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
print("ld_json_blocks =", len(blocks))
for i, b in enumerate(blocks):
    try:
        d = json.loads(b)
        print(f"  [{i}] keys={list(d.keys())[:8]} @type={d.get('@type')}")
        if 'blogPost' in d:
            bp = d['blogPost']
            print(f"      blogPost len={len(bp)}  first={json.dumps(bp[0], ensure_ascii=False)[:200]}")
            print(f"      last={json.dumps(bp[-1], ensure_ascii=False)[:200]}")
            print(f"      has_0920={any('family-wealth' in json.dumps(x) for x in bp)}")
    except Exception as e:
        print(f"  [{i}] NOT JSON: {e}")
print()
# sitemap lastmod for new page
s = open('sitemap.xml', encoding='utf-8').read()
for blk in re.findall(r'<url>(.*?)</url>', s, re.S):
    if 'family-wealth' in blk:
        print("sitemap block:", blk.strip())
nolm = [re.search(r'<loc>(.*?)</loc>', b).group(1) for b in re.findall(r'<url>(.*?)</url>', s, re.S) if '<lastmod>' not in b]
print(f"\nsitemap total={len(re.findall(r'<url>', s))}  no_lastmod={len(nolm)}")
for u in nolm[:10]:
    print("   ", u)
