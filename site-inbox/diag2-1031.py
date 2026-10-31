#!/usr/bin/env python3
# SiteOps daily diagnostic part 2 — page existence + six checks + gaps
import os, re, json, subprocess, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")

def rd(p):
    return open(p, encoding="utf-8", errors="ignore").read()

main_i = rd(os.path.join(REPO, "blog/index.html"))

# candidate slugs from today/yesterday
cands = [
    "najie/blog/20261031-najie-specialized-sme-patent-screen.html",
    "najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html",
    "mili/blog/20261031-mili-mofcom-trade-secret-sanctions.html",
    "najie/blog/20261030-najie-foreign-filing-confidentiality-review.html",
    "mili/blog/20261030-mili-ai-harm-outpaces-law.html",
    "najie/blog/20261030-najie-training-data-provenance.html",
]
# plus the two content.db articles: search files by keyword
for kw in ("孕期", "yunjia", "pregnancy", "gongju-zhongli", "shua-haoping", "刷好评", "工具中立"):
    hits = [p for p in glob.glob(os.path.join(REPO, "*/blog/*.html")) if kw in os.path.basename(p)]
    if hits:
        for h in hits:
            rel = os.path.relpath(h, REPO)
            if rel not in cands:
                cands.append(rel)

print("=== CANDIDATES ===")
for c in cands:
    p = os.path.join(REPO, c)
    print(("EXIST " if os.path.exists(p) else "MISSING ") + c, (os.path.getsize(p) if os.path.exists(p) else ""))
print("\n=== SIX-CHECK ===")
for c in cands:
    p = os.path.join(REPO, c)
    if not os.path.exists(p):
        continue
    t = rd(p)
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = t.count('application/ld+json')
    ogimg = 'property="og:image"' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    title = tm.group(1).strip() if tm else ""
    star = len(re.findall(r"(?<![0-9*])\*\*(?![0-9*])", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    baretbl = len(re.findall(r"<p>\s*\|", t))
    print(f"{c}\n  h1={h1} ld={ld} ogimage={ogimg} stars={star} baretable={baretbl}")
    print(f"  desc[{len(desc)}]={desc[:90]}")
    print(f"  title={title[:80]}")
    # json-ld validity
    for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)):
        try:
            json.loads(blk)
        except Exception as e:
            print(f"  LD[{i}] INVALID: {e}")
    mainhit = os.path.basename(c) in main_i
    brand = c.split("/")[0]
    bi = rd(os.path.join(REPO, brand, "blog/index.html"))
    print(f"  main_index={mainhit} brand_index={os.path.basename(c) in bi}")
    print(f"  schema.org={t.count('https://schema.org')} stars_any={t.count('**')}")

print("\n=== aipunajie gap disambiguation ===")
missing = ['20260723-weituo-chuangzuo-banquan-xieyi-bi-keng.html', 'ai-ip-compliance-redline-20260726.html',
           'wipo-ai-ip-dialogue-20260725.html', 'wipo-free-databases-20260726.html', '觅理加盟-创始合伙人亲述-20260719.html']
for mb in missing:
    p = os.path.join(REPO, "aipunajie/blog", mb)
    exists = os.path.exists(p)
    size = os.path.getsize(p) if exists else 0
    title = ""
    if exists:
        t = rd(p)
        tm = re.search(r"<title>(.*?)</title>", t, re.S)
        title = tm.group(1).strip() if tm else ""
        shell = 'http-equiv="refresh"' in t
    else:
        shell = None
    print(f"{mb} exists={exists} size={size} shell={shell} title={title[:70]}")
    # look for the title stem in main index to detect rehost
    if title:
        stem = re.split(r"[，,：:|—\-]", title)[0][:12]
        print("   stem_in_main:", stem in main_i, "|", stem)
