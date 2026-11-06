#!/usr/bin/env python3
"""本地终验：EN/FR 页结构 + 索引卡 + 中文页 hreflang + sitemap"""
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261101-najie-ip-foreign-transfer-review"
fails = []


def chk(cond, msg):
    if not cond:
        fails.append(msg)
    print(("PASS " if cond else "FAIL ") + msg)


for lang in ("en", "fr"):
    p = os.path.join(REPO, f"{lang}/blog/{SLUG}-{lang}.html")
    t = open(p, encoding="utf-8").read()
    b = t.encode()
    chk(t.count("<h1") == 1, f"{lang} h1==1")
    chk(t.count("<h2>") == 4, f"{lang} h2==4")
    chk(t.count("application/ld+json") == 2, f"{lang} ld==2")
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ok = True
    for blk in blocks:
        try:
            json.loads(blk)
        except Exception as e:
            ok = False
            print("  json err", e)
    chk(ok, f"{lang} jsonld parse")
    chk('property="og:image"' in t, f"{lang} og:image")
    chk('rel="canonical"' in t, f"{lang} canonical")
    chk(t.count('hreflang="') == 4, f"{lang} hreflang==4")
    no_lb = re.sub(r'<div class="lang-bar">.*?</div>', "", t, flags=re.S)
    chk(len(re.findall(r"[\u4e00-\u9fff]", no_lb)) == 0, f"{lang} no CJK leak")
    chk(t.count("**") == 0, f"{lang} no ** leak")
    chk("https://schema.org" in t and "https://***" not in t, f"{lang} schema.org ok")
    chk(t.count('class="disclaimer"') == 1, f"{lang} disclaimer")
    # div 配平
    depth = 0
    bad = False
    for m in re.finditer(r"<(/?)div\b", t):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            bad = True
    chk(depth == 0 and not bad, f"{lang} div balance (depth={depth})")
    print(f"  {lang} bytes={len(b)}")

# 索引卡
for lang in ("en", "fr"):
    p = os.path.join(REPO, f"{lang}/blog/index.html")
    t = open(p, encoding="utf-8").read()
    chk(t.count(SLUG) >= 1, f"{lang} index has card")
    chk(f"/{lang}/blog/{SLUG}-{lang}.html" in t, f"{lang} index href")

# 中文页
p = os.path.join(REPO, f"najie/blog/{SLUG}.html")
t = open(p, encoding="utf-8").read()
chk(t.count('hreflang="') == 4, "zh hreflang==4 unique")
chk(f"https://najieip.com/img/{SLUG}.png" in t, "zh og:image self-hosted")

# sitemap
s = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
for lang in ("en", "fr"):
    chk(f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html" in s, f"sitemap {lang} loc")
chk(s.count("<loc>") == s.count("</loc>"), "sitemap loc balanced")

# 图片
chk(os.path.exists(os.path.join(REPO, f"img/{SLUG}.png")), "cover image in repo")

print("\nFAILURES =", len(fails))
for f in fails:
    print(" -", f)
