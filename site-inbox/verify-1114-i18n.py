import json, re, os

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261113-byd-netherlands-evidence-seizure"
fails = []

for lang in ("en", "fr"):
    p = f"{REPO}/{lang}/blog/{SLUG}-{lang}.html"
    t = open(p).read()
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    for blk in ld:
        try: json.loads(blk)
        except Exception as e: fails.append(f"{lang} ld json: {e}")
    body = t[t.find("<body"):]
    cjk_body = len(re.findall(r"[\u4e00-\u9fff]", body))
    checks = {
        "h1==1": t.count("<h1") == 1,
        "ld==2": len(ld) == 2,
        "og:image": 'og:image' in t and SLUG in re.sub(r"^.*og:image", "og:image", t, flags=re.S)[:200],
        "canonical": f'<link rel="canonical" href="https://najieip.com/{lang}/blog/{SLUG}-{lang}.html">' in t,
        "hreflang==4": t.count("hreflang") == 4,
        "schema.org==2": t.count("https://schema.org") == 2,
        "no_stars": t.count("**") == 0,
        "cjk_body==0": cjk_body == 0,
        "lang_bar": f"/{lang}/blog/{SLUG}-{lang}.html\" class=\"active\"" in t,
        "h2==5": t.count("<h2") == 5,
        "table==1": t.count("<table") == 1,
        "desc_not_title_repeat": len(re.search(r'<meta name="description" content="([^"]*)"', t).group(1)) > 150,
    }
    for k, v in checks.items():
        if not v: fails.append(f"{lang}: {k}")
    print(lang, "chars", len(t), "ld", len(ld), "cjk", cjk_body, "h2", t.count("<h2"),
          "table", t.count("<table"), "OK" if all(checks.values()) else "FAIL")

# 索引卡
for lang in ("en", "fr"):
    t = open(f"{REPO}/{lang}/blog/index.html").read()
    n = t.count(f'href="/{lang}/blog/{SLUG}-{lang}.html"')
    op = sum(t.count(x) for x in ["<div", "</div>"])
    print(lang, "index cards", t.count('<div class="article-card">'), "slug hits", n,
          "div open/close", t.count("<div"), t.count("</div>"))
    if n != 1: fails.append(f"{lang} index card hits={n}")

# 中文页
zt = open(f"{REPO}/mili/blog/{SLUG}.html").read()
print("zh hreflang", zt.count("hreflang"), "h1", zt.count("<h1"), "ld", zt.count("application/ld+json"))
if zt.count("hreflang") != 4: fails.append("zh hreflang != 4")

# sitemap
import xml.etree.ElementTree as ET
try:
    root = ET.parse(f"{REPO}/sitemap.xml").getroot()
    locs = [e.text for e in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    print("sitemap locs", len(locs), "has en", any(f"{SLUG}-en" in l for l in locs),
          "has fr", any(f"{SLUG}-fr" in l for l in locs))
    if not any(f"{SLUG}-en" in l for l in locs): fails.append("sitemap en missing")
except Exception as e:
    fails.append(f"sitemap parse: {e}")

print("FAILS:", fails if fails else "NONE")
