#!/usr/bin/env python3
"""verify-1009.py — 结构终验（depth 对 origin 基线校准）"""
import os, re, subprocess, json

BASE = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261009-mili-ai-short-drama-token-evidence"

def load(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def origin(path):
    r = subprocess.run(["git", "-C", BASE, "show", "origin/main:" + path],
                       capture_output=True, text=True)
    return r.stdout

def analyze(t):
    """返回 (卡片数, depth 直方图, 非<h2起卡数, div配平)"""
    depth = 0
    cards = 0
    hist = {}
    malformed = 0
    # 逐 card 起始，判断其所在 depth
    card_positions = [m.start() for m in re.finditer(r'<div class="article-card">', t)]
    for cp in card_positions:
        d = 0
        for m in re.finditer(r'<(/?)div[ >]', t[:cp]):
            d += -1 if m.group(1) == "/" else 1
        hist[d] = hist.get(d, 0) + 1
        cards += 1
    # 每卡必须以 <h2><a href= 起
    for m in re.finditer(r'<div class="article-card">\s*(.{0,25})', t):
        if not m.group(1).startswith("<h2><a href="):
            malformed += 1
    # div 配平
    opens = len(re.findall(r"<div[ >]", t))
    closes = len(re.findall(r"</div>", t))
    return cards, hist, malformed, (opens - closes)

def page_report(p):
    t = load(p)
    return {
        "ld": t.count("application/ld+json"),
        "ogimg": t.count('property="og:image"'),
        "h1": len(re.findall(r"<h1[ >]", t)),
        "stars": t.count("**"),
        "ogurl": t.count('property="og:url"'),
        "canon": t.count('rel="canonical"'),
        "schema": t.count("https://schema.org"),
        "bad": t.count("https://***"),
    }

print("=== PAGE ===")
pr = page_report(os.path.join(BASE, "mili/blog/%s.html" % SLUG))
print(pr)
assert pr["ld"] >= 2 and pr["ogimg"] == 1 and pr["h1"] == 1 and pr["stars"] == 0
assert pr["schema"] >= 2 and pr["bad"] == 0

print("\n=== INDEXES ===")
for rel in ["mili/blog/index.html", "blog/index.html"]:
    cur = load(os.path.join(BASE, rel))
    org = origin(rel)
    c1, h1, m1, b1 = analyze(cur)
    c0, h0, m0, b0 = analyze(org)
    print("%s: cards %d -> %d | depth %s -> %s | malformed %d->%d | divΔ %d->%d"
          % (rel, c0, c1, h0, h1, m0, m1, b0, b1))
    assert c1 == c0 + 1, "card count not +1"
    assert m1 == 0, "malformed cards"
    assert b1 == 0, "div not balanced"
    # 新卡是首卡（body 内）
    body = cur[cur.find("<body"):]
    first = re.search(r'<div class="article-card">.*?<h2><a href="([^"]+)"', body, re.S)
    assert first and SLUG in first.group(1), "new card not first"
    # 插入点前缀日期降序（新卡之前的卡日期 >= 新卡日期）
    dates = re.findall(r'<div class="article-card">.*?<div class="meta">.*?(\d{4}-\d{2}-\d{2})',
                       cur, re.S)
    print("   first 4 card dates:", dates[:4])
    assert dates[0] == "2026-10-09"
    assert all(d <= dates[0] for d in dates[1:4]), "date order broken"

print("\n=== ALL STRUCTURE CHECKS PASSED ===")
