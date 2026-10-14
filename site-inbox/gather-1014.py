#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补卡 dry-run：提取主索引卡模板 + 待补页元数据 + sitemap 核对"""
import re, os, json, collections
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))

def cards_with_pos(t):
    """按 div 深度配对提取每张卡（含起止位置）"""
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        i = m.start(); d = 0; j = i
        while j < len(t):
            if t.startswith("<div", j): d += 1; j += 4
            elif t.startswith("</div>", j):
                d -= 1; j += 6
                if d == 0: break
            else: j += 1
        out.append((i, j, t[i:j]))
    return out

t = open("blog/index.html", encoding="utf-8", errors="ignore").read()
cs = cards_with_pos(t)
print("主索引卡片数:", len(cs))

# 目标模板卡
def find_card(sub):
    for i, j, blk in cs:
        if sub in blk:
            return i, j, blk
    return None

for sub in ["20261014-trademark-pattern-packaging-confusion",
            "20261010-mili-aigc-trade-secret-two-leaks"]:
    r = find_card(sub)
    print("\n=== TEMPLATE (%s) pos=%s ===" % (sub, r[0] if r else None))
    print(repr(r[2]) if r else "NOT FOUND")

# 待补页元数据
print("\n=== 待补页元数据 ===")
for f, link in [("mili/blog/patent-vs-trade-secret-layering-2026.html", "/mili/blog/patent-vs-trade-secret-layering-2026.html"),
                ("najie/blog/layout-design-originality-claim-322-2026.html", "/najie/blog/layout-design-originality-claim-322-2026.html")]:
    t2 = open(f, encoding="utf-8", errors="ignore").read()
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t2, re.S)
    md = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', t2)
    kw = re.search(r'<meta\s+name="keywords"\s+content="([^"]*)"', t2)
    # 品牌索引里该文的卡片（取标题/摘要/日期，与品牌博客展示一致）
    brand = "mili" if "/mili/" in link else "najie"
    bt = open("%s/blog/index.html" % brand, encoding="utf-8", errors="ignore").read()
    bcs = cards_with_pos(bt)
    bc = next((b for i, j, b in bcs if link.replace("/%s/blog" % brand, ".") in b or os.path.basename(f) in b), None)
    print("---", link)
    print("  h1:", re.sub(r"\s+", " ", h1.group(1)).strip()[:80] if h1 else None)
    print("  desc:", (md.group(1)[:100] if md else None), "len", len(md.group(1)) if md else 0)
    print("  keywords:", kw.group(1) if kw else None)
    print("  brand card:", repr(bc)[:700] if bc else "NOT FOUND")

# sitemap 核对
sm = open("sitemap.xml", encoding="utf-8", errors="ignore").read()
print("\n=== sitemap loc 数:", sm.count("<loc>"))
for s in ["patent-vs-trade-secret-layering-2026", "layout-design-originality-claim-322-2026",
          "20261014-trademark-pattern-packaging-confusion"]:
    print("  %s -> %d" % (s, sm.count(s)))
