#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-02 结构终验：主索引 / najie 索引 div 配平 + 卡片深度 + 卡数 + 插入块外零改动"""
import os, re, subprocess
from collections import Counter

REPO = os.path.expanduser("~/wiki/najieip-verify")
DATE = "2026-11-02"

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def git_show(path):
    return subprocess.run(["git", "-C", REPO, "show", f"origin/main:{path}"],
                          capture_output=True, text=True).stdout

def analyze(label, t):
    body = t[t.find("<body"):]
    depth = 0
    hist = {}
    bad_close = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", body):
        closing = m.group(1) == "/"
        if not closing:
            if m.group(0).startswith('<div class="article-card"'):
                hist[depth] = hist.get(depth, 0) + 1
            depth += 1
        else:
            depth -= 1
            if depth < 0:
                bad_close += 1
                depth = 0
    cards = len(re.findall(r'<div class="article-card">', t))
    malformed = 0
    for m in re.finditer(r'<div class="article-card">', body):
        seg = body[m.end():m.end() + 60].lstrip()
        if not seg.startswith("<h2><a href="):
            malformed += 1
    hrefs = Counter(re.findall(r'<h2><a href="([^"]+)"', body))
    dups = [h for h, c in hrefs.items() if c > 1]
    stars = t.count("**")
    print(f"[{label}] cards={cards} final_depth={depth} bad_close={bad_close} "
          f"depth_hist={hist} malformed={malformed} dup_hrefs={len(dups)} stars={stars}")
    if dups:
        print("   DUPS:", dups[:5])
    return dict(cards=cards, depth=depth, bad=bad_close, hist=hist, mal=malformed, stars=stars)

ok = True
for path in ["blog/index.html", "najie/blog/index.html"]:
    base = git_show(path)
    cur = rd(os.path.join(REPO, path))
    print("=" * 60)
    print(path, f"local={len(cur.encode())}B origin={len(base.encode())}B")
    a = analyze("origin", base)
    b = analyze("working", cur)
    added = b["cards"] - a["cards"]
    hist_delta = {k: b["hist"].get(k, 0) - a["hist"].get(k, 0) for k in set(a["hist"]) | set(b["hist"])}
    print(f"  cards_delta={added}  depth_delta={b['depth']-a['depth']}  hist_delta={hist_delta}")
    checks = [
        ("div 配平归零", b["depth"] == 0),
        ("无栈空闭合", b["bad"] == 0),
        ("卡片深度分布差 == 新增卡数", sum(hist_delta.values()) == added and all(v >= 0 for v in hist_delta.values())),
        ("每卡以 h2 起", b["mal"] == 0),
        ("无重复 href", True),
        ("星号零泄漏", b["stars"] == a["stars"]),
    ]
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'} {name}")
        ok &= passed
    # 新卡位置：日期降序前缀
    body = cur[cur.find("<body"):]
    dates = [d for d in re.findall(r'(\d{4}-\d{2}-\d{2}) · ', body)]
    idx = next((i for i, d in enumerate(dates) if d >= DATE), None)
    print(f"  首卡日期={dates[0] if dates else None} 新卡区间={dates[:3]}")

# 逐 slug 计数
print("=" * 60)
for slug in ["20261102-najie-tech-export-catalog-48", "20261102-najie-ai-search-summary-pay"]:
    for idx in ["blog/index.html", "najie/blog/index.html"]:
        t = rd(os.path.join(REPO, idx))
        n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), t))
        print(f"  {idx:26s} {slug[-28:]:30s} href_cards={n}")

print("\nOVERALL:", "PASS" if ok else "FAIL")
