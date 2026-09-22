#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 0922 诊断：索引缺口 + 房屋样式四件 + articles.json 守卫 + 落款核验"""
import os, re, json, subprocess, collections

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

INDEXES = {
    "main": "blog/index.html",
    "mili": "mili/blog/index.html",
    "najie": "najie/blog/index.html",
    "aipunajie": "aipunajie/blog/index.html",
}

# ---- 1. 收集品牌索引卡片 href（相对路径），归一为绝对路径 ----
brand_cards = {}   # norm_path -> (brand, raw_href, title, date)
for brand, idx in INDEXES.items():
    if brand == "main" or not os.path.exists(idx):
        continue
    t = rd(idx)
    base = "/%s/blog" % brand
    for m in re.finditer(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', t):
        href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        p = href if href.startswith("/") else base + "/" + href.lstrip("./")
        brand_cards[p] = (brand, href, title)

print("=== 品牌索引卡片总数:", len(brand_cards))

# ---- 2. 主索引 href 集合 ----
main_t = rd(INDEXES["main"])
main_hrefs = set(re.findall(r'<h2><a href="([^"]+)"', main_t))
print("=== 主索引卡片总数:", len(main_hrefs))

# ---- 3. 真缺口：品牌索引有、主索引没有（href 归一后精确比对）----
missing = []
for p, (brand, href, title) in sorted(brand_cards.items()):
    if p not in main_hrefs:
        missing.append((p, brand, title))
print("\n=== 主索引缺口 (%d) ===" % len(missing))
for p, b, ti in missing:
    print("  [%s] %-30s %s" % (b, p.split("/")[-1], ti[:44]))

# ---- 4. 品牌索引重复卡（同 href >1）----
print("\n=== 品牌索引重复卡检查 ===")
for brand, idx in INDEXES.items():
    if not os.path.exists(idx):
        continue
    t = rd(idx)
    c = collections.Counter(re.findall(r'<h2><a href="([^"]+)"', t))
    dups = {k: v for k, v in c.items() if v > 1}
    print("  %-10s cards=%d dupes=%s" % (brand, sum(c.values()), dups if dups else "none"))

# ---- 5. 主索引同样重复检查 ----
c = collections.Counter(re.findall(r'<h2><a href="([^"]+)"', main_t))
print("  main       cards=%d dupes=%s" % (sum(c.values()), {k: v for k, v in c.items() if v > 1} or "none"))

# ---- 6. 近3天文章页「房屋样式四件」核验 ----
print("\n=== 近3天文章页房屋样式核验 ===")
recent = [
    "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html",
    "mili/blog/20260922-criminal-non-filing-civil-claim.html",
    "najie/blog/20260921-us-trademark-sanction-defense-window.html",
    "najie/blog/20260921-trademark-renewal-lapse-ten-years.html",
    "najie/blog/20260921-trademark-address-change-cancellation.html",
    "mili/blog/20260920-family-wealth-isolation-three-firewalls.html",
]
for f in recent:
    if not os.path.exists(f):
        print("  MISSING FILE: %s" % f)
        continue
    t = rd(f)
    md = re.search(r'<meta name="description" content="([^"]*)"', t)
    dlen = len(md.group(1)) if md else 0
    flg = []
    if "<style>" not in t: flg.append("NO-STYLE")
    if t.count("<h1") != 1: flg.append("H1=%d" % t.count("<h1"))
    if t.count("application/ld+json") < 2: flg.append("LD=%d" % t.count("application/ld+json"))
    if dlen <= 80: flg.append("DESC=%d" % dlen)
    if t.count("**") > 0: flg.append("MD-LEAK=%d" % t.count("**"))
    if "og:image" not in t: flg.append("NO-OGIMG")
    if "canonical" not in t: flg.append("NO-CANON")
    print("  %-62s %s" % (f.split("/")[-1][:60], ("OK" if not flg else " | ".join(flg))))

# ---- 7. articles.json 守卫 ----
print("\n=== articles.json ===")
if os.path.exists("articles.json"):
    a = json.loads(rd("articles.json"))
    print("  entries:", len(a))
    bad = []
    for e in a:
        u = e.get("url") or e.get("link") or ""
        if u.startswith("/"):
            fp = u.lstrip("/")
            if not os.path.exists(fp):
                bad.append(u)
    print("  首页 top6:", [ (e.get("url") or "")[:56] for e in a[:6] ])
    print("  违例(无本地文件)条数:", len(bad))
    for u in bad[:8]:
        print("    -", u)
    # 曝光位次
    for i, e in enumerate(a[:12], 1):
        u = e.get("url") or ""
        fp = u.lstrip("/")
        print("   rank%-2d %s  存在=%s" % (i, u[:62], os.path.exists(fp)))

# ---- 8. 索引结构终验 ----
print("\n=== 主索引结构 ===")
body = main_t[main_t.find("<body"):]
print("  article-card 计数:", main_t.count('<div class="article-card">'))
depth = 0; maxd = 0; underflow = 0
for m in re.finditer(r'<(/?)div[^>]*>', body):
    if m.group(1):
        depth -= 1
        if depth < 0: underflow += 1; depth = 0
    else:
        depth += 1
        maxd = max(maxd, depth)
print("  最终深度:", depth, " 最大深度:", maxd, " 栈空闭合异常:", underflow)
depth = 0; d2cards = 0
for m in re.finditer(r'<(/?)div[^>]*>', body):
    if m.group(1):
        depth -= 1
    else:
        depth += 1
        if depth == 2 and m.group(0).startswith('<div class="article-card"'):
            d2cards += 1
print("  depth==2 卡片数:", d2cards)
mal = 0
for blk in re.findall(r'<div class="article-card">(.*?)(?=<div class="article-card">|</div>\s*</div>\s*<footer)', body, re.S):
    if not blk.lstrip().startswith("<h2><a href="):
        mal += 1
print("  malformed 卡片:", mal)
print("  '**' 泄漏:", main_t.count("**"))
