#!/usr/bin/env python3
# 结构终验 — 索引卡深度/计数 + i18n 页面字段
import os, re, sys, json

R = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260928-german-utility-model-offense"
BAD = []

def depth_check(path):
    t = open(path, encoding="utf-8").read()
    body = t[t.find("<body"):]
    depth = 0
    cards = []
    malformed = 0
    for m in re.finditer(r"<(/?)(div|article|table|tr|ul|ol)\b[^>]*>", body):
        tag = m.group(2)
        if m.group(1):
            depth -= 1
            if depth < 0:
                BAD.append(f"{path}: stack underflow")
        else:
            if tag == "div" and 'class="article-card"' in m.group(0):
                cards.append(depth)
            depth += 1
    return t.count('class="article-card"'), depth, cards, t.count("**")

for p in ("en/blog/index.html", "fr/blog/index.html"):
    fp = os.path.join(R, p)
    n, d, cards, star = depth_check(fp)
    print(f"{p}: cards={n} depth_end={d} depth_hist={sorted(set(cards))} '**'={star}")
    if d != 0 or star != 0 or len(cards) != n:
        BAD.append(f"{p}: structure fail")

for lang in ("en", "fr"):
    fp = os.path.join(R, lang, "blog", f"{SLUG}-{lang}.html")
    t = open(fp, encoding="utf-8").read()
    checks = {
        "h1": t.count("<h1"),
        "ld": t.count("application/ld+json"),
        "og:image": t.count("og:image") > 0,
        "canonical": 'rel="canonical"' in t,
        "hreflang": t.count("hreflang"),
        "schema.org": t.count("https://schema.org"),
        "masked": t.count("https://***"),
        "star": t.count("**"),
        "table": t.count("<table"),
    }
    print(f"{lang} page: {checks}")
    if not (checks["h1"] == 1 and checks["ld"] == 1 and checks["og:image"] and checks["canonical"]
            and checks["hreflang"] == 4 and checks["masked"] == 0 and checks["star"] == 0
            and checks["table"] == 2):
        BAD.append(f"{lang} page field fail")

# JSON-LD 可解析性
for fp in [os.path.join(R, lang, "blog", f"{SLUG}-{lang}.html") for lang in ("en", "fr")] + \
          [os.path.join(R, x) for x in ("mili/blog/20260928-german-utility-model-offense.html",
                                        "mili/blog/20261001-ai-voice-clone-shanghai-first-case-evidence-shift.html",
                                        "najie/blog/20261002-ai-patent-reply-evidence.html")]:
    t = open(fp, encoding="utf-8").read()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    for i, b in enumerate(blocks):
        try:
            json.loads(b)
        except Exception as e:
            BAD.append(f"{fp} ld[{i}] invalid: {e}")
    print(f"{os.path.basename(fp)}: ld_blocks={len(blocks)} all_parse={not any(fp in b for b in BAD)}")

# sitemap
s = open(os.path.join(R, "sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>(.*?)</loc>", s)
print("sitemap locs:", len(locs), "unique:", len(set(locs)),
      "| new EN:", f"https://najieip.com/en/blog/{SLUG}-en.html" in s,
      "| new FR:", f"https://najieip.com/fr/blog/{SLUG}-fr.html" in s)

print("RESULT:", "PASS" if not BAD else "FAIL " + str(BAD))
