#!/usr/bin/env python3
# SiteOps 0920 日检 — 索引覆盖 + 结构 + 污染检查
import os, re, json, sqlite3, sys
from collections import Counter

REPO = os.path.expanduser("~/wiki/najieip-verify")

# 最近文章 slug 映射（brand, slug, title）
targets = [
    ("mili", "20260920-family-wealth-isolation-three-firewalls", "ART-2026-0091"),
    ("mili", "20260919-offer-to-sell-three-rules", "ART-2026-0090"),
    ("najie", "20260918-eu-digital-design-three-tables", "ART-2026-0089"),
    ("mili", "20260917-upc-injunction-counterattack", "ART-2026-0088"),
    ("najie", "nongye-pinpai-ip-buju-2026", "农业品牌(0919)"),
    ("mili", "wangluo-jishu-zhichi-kaishe-duchangzui-2026", "网络赌场(0919)"),
]

files = {
    "main": os.path.join(REPO, "blog/index.html"),
    "mili": os.path.join(REPO, "mili/blog/index.html"),
    "najie": os.path.join(REPO, "najie/blog/index.html"),
    "aipunajie": os.path.join(REPO, "aipunajie/blog/index.html"),
}

texts = {}
for k, p in files.items():
    if os.path.exists(p):
        texts[k] = open(p, encoding="utf-8").read()
    else:
        texts[k] = None

print("=== 索引卡计数 ===")
for k, t in texts.items():
    if t is None:
        print(f"  {k}: MISSING FILE")
        continue
    print(f"  {k}: article-card={t.count('article-card')}  bytes={len(t.encode())}  md_leak={t.count('**')}")

print("\n=== 文章覆盖检查 ===")
for brand, slug, aid in targets:
    hits = []
    for k, t in texts.items():
        if t is None:
            continue
        # 归一比对：/(brand)/blog/slug 或 ./slug 或任意包含 slug 的 href
        hrefs = re.findall(r'<h2><a href="([^"]+)"', t)
        norm = []
        for h in hrefs:
            if h.startswith("./"):
                norm.append("/" + k + "/blog/" + h[2:] if k != "main" else "/blog/" + h[2:])
            else:
                norm.append(h)
    # 简单包含判断
    covered = {}
    for k, t in texts.items():
        if t is None:
            covered[k] = False
            continue
        pat = re.compile(r'<h2><a href="[^"]*' + re.escape(slug) + r'[^"]*"')
        covered[k] = bool(pat.search(t))
    flag = "OK" if covered.get(brand) else "!!MISSING-BRAND"
    print(f"  {aid:16s} {slug}")
    print(f"      brand({brand})={covered.get(brand)}  main={covered.get('main')}  -> {flag}")

print("\n=== 结构校验（主索引）===")
t = texts["main"]
body = t[t.find("<body"):]
# div 深度
depth = 0; bad = 0
for m in re.finditer(r'</?div[^>]*>', body):
    if m.group(0).startswith("</"):
        depth -= 1
        if depth < 0:
            bad += 1; depth = 0
    else:
        depth += 1
print(f"  final_div_depth={depth}  stack_underflow={bad}")
# 卡片首标签
cards = re.findall(r'<div class="article-card">(.*?)(?=<div class="article-card">|</div>\s*</div>)', body, re.S)
malformed = sum(1 for c in cards if not c.lstrip().startswith("<h2><a href="))
print(f"  article-card_raw_blocks={len(cards)}  malformed={malformed}")
# 重复 href
hrefs = Counter(re.findall(r'<h2><a href="([^"]+)"', body))
dups = {h: c for h, c in hrefs.items() if c > 1}
print(f"  unique_hrefs={len(hrefs)}  duplicate_hrefs={len(dups)}")
if dups:
    for h, c in list(dups.items())[:8]:
        print(f"      DUP x{c}: {h}")
# md 泄漏
print(f"  md_leak('**')={t.count('**')}")

# 日期序列（前 20）
dates = re.findall(r'<span class="tag">[^<]*</span>\s*(\d{4}-\d{2}-\d{2})', body)
if not dates:
    dates = re.findall(r'(\d{4}-\d{2}-\d{2})', body[:200000])
print(f"  first12_dates={dates[:12]}")

print("\n=== 今日新文页面检查 ===")
page = os.path.join(REPO, "mili/blog/20260920-family-wealth-isolation-three-firewalls.html")
pt = open(page, encoding="utf-8").read()
print(f"  bytes={len(pt.encode())}")
for label, pat in [("og:url", 'og:url'), ("canonical", 'rel="canonical"'), ("ld+json", 'application/ld+json'),
                   ("og:image", 'og:image'), ("twitter:card", 'twitter:card'), ("h1", '<h1')]:
    print(f"      {label}: {pt.count(pat)}")
print(f"      schema.org: {pt.count('https://schema.org')}  broken_schema: {pt.count('https://***')}")
print(f"      md_leak: {pt.count('**')}  frontmatter_leak: {'---\\ntitle' in pt or pt.startswith('---')}")

print("\n=== articles.json 守卫（只读 --check）===")
aj = os.path.join(REPO, "articles.json")
if os.path.exists(aj):
    d = json.load(open(aj, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("articles", [])
    print(f"  entries={len(items)}")
    missing = []
    for it in items:
        u = it.get("url") or it.get("link") or ""
        p = u.split("najieip.com")[-1].split("?")[0]
        fp = os.path.join(REPO, p.lstrip("/"))
        if p and not os.path.exists(fp):
            missing.append((p, it.get("date", "")))
    print(f"  no_page_entries={len(missing)}")
    for p, dt in missing[:6]:
        print(f"      {dt}  {p}")
