#!/usr/bin/env python3
"""11-25 索引结构终验：卡片数 / div 配平 / depth / malformed / 重复 / 星号"""
import re, subprocess, collections

REPO = "/Users/ziganghe/wiki/najieip-verify"
PATHS = ["blog/index.html", "najie/blog/index.html", "mili/blog/index.html"]


def get(rev, path):
    return subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"],
                          capture_output=True, text=True).stdout


def depth_hist(t):
    """逐 div 累计深度，统计 class=article-card 出现时的深度"""
    hist = collections.Counter()
    depth = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", t):
        tag = m.group(0)
        if m.group(1):
            depth -= 1
            if depth < 0:
                hist["NEG"] += 1
                depth = 0
        else:
            if 'class="article-card"' in tag:
                hist[depth] += 1
            depth += 1
    hist["_final_depth"] = depth
    return hist


for p in PATHS:
    base = get("HEAD~1", p)
    new = get("HEAD", p)
    if not base:
        print(f"SKIP {p} (no prev)")
        continue
    cards = new.count('<div class="article-card">')
    op = len(re.findall(r"<div\b", new)); cl = new.count("</div>")
    bop = len(re.findall(r"<div\b", base)); bcl = base.count("</div>")
    malformed = len([m for m in re.finditer(r'<div class="article-card">', new)
                     if not new[m.end():m.end() + 200].lstrip().startswith("<h2><a href=")])
    hrefs = collections.Counter(re.findall(r'<h2><a href="([^"]+)"', new))
    dups = {k: v for k, v in hrefs.items() if v > 1}
    hb = depth_hist(base); hn = depth_hist(new)
    delta = {k: hn[k] - hb.get(k, 0) for k in set(hn) | set(hb)}
    stars = new.count("**")
    print(f"{p}: cards={cards} div={op}/{cl} delta_div={op-bop}/{cl-bcl} "
          f"malformed={malformed} dups={len(dups)} stars={stars} depthdelta={dict(delta)}")
    if malformed:
        print("   MALFORMED_SAMPLES:", [new[m.start():m.start() + 90] for m in
              [x for x in re.finditer(r'<div class="article-card">', new)
               if not new[x.end():x.end() + 200].lstrip().startswith("<h2><a href=")][:2]])
    if dups:
        print("   DUP_SAMPLES:", list(dups.items())[:3])
