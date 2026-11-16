#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 1116 修复：mili protection-order 页补 h1 + og:image/twitter；封面入库"""
import os, re, json, shutil, sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"
SLUG = "20261116-mili-protection-order-72hours"
PAGE = os.path.join(REPO, "mili", "blog", SLUG + ".html")
IMG = os.path.join(REPO, "img", SLUG + ".png")
COVER = os.path.join(ART, "cover-" + SLUG + ".png")
BASE = "https://najieip.com"
APPLY = "--apply" in sys.argv

t = open(PAGE, encoding="utf-8").read()
orig = t
HEAD_END = t.find("</head>") + 7
head, rest = t[:HEAD_END], t[HEAD_END:]

title = re.search(r'<title>(.*?)</title>', head, re.S).group(1).split(" — ")[0].strip()
desc = re.search(r'<meta name="description" content="([^"]*)"', head, re.S).group(1)
kws = re.search(r'<meta name="keywords" content="([^"]*)"', head, re.S)
img_url = f"{BASE}/img/{SLUG}.png"

report = {}

# 1) h1
if "<h1" not in rest:
    rest = rest.replace("<article>", f"<article>\n<h1>{title}</h1>", 1)
    report["h1"] = "added"

# 2) keywords
if not kws:
    kw = "人身安全保护令,反家庭暴力法,妇女权益保障法第29条,分手后骚扰,72小时,法释2022-17号"
    head = head.replace('<meta name="viewport"',
                        f'<meta name="keywords" content="{kw}">\n<meta name="viewport"', 1)
    report["keywords"] = "added"

# 3) og:image
if 'og:image' not in head:
    head = head.replace('<meta name="twitter:card"',
                        f'<meta property="og:image" content="{img_url}">\n<meta name="twitter:card"', 1)
    report["og_image"] = "added"

# 4) twitter card upgrades
head = head.replace('<meta name="twitter:card" content="summary">',
                    '<meta name="twitter:card" content="summary_large_image">')
if 'twitter:title' not in head:
    head = head.replace('<meta property="twitter:description"',
                        f'<meta property="twitter:title" content="{title}">\n<meta property="twitter:description"', 1)
    report["twitter_title"] = "added"
if 'twitter:image' not in head:
    head = head.replace('<meta property="twitter:description"',
                        f'<meta property="twitter:image" content="{img_url}">\n<meta property="twitter:description"', 1)
    report["twitter_image"] = "added"

# 5) Article JSON-LD 补 image
def fix_ld(m):
    raw = m.group(1)
    try:
        o = json.loads(raw)
    except Exception as e:
        report.setdefault("ld_err", []).append(str(e))
        return m.group(0)
    if o.get("@type") == "Article" and "image" not in o:
        new = {}
        for k, v in o.items():
            new[k] = v
            if k == "mainEntityOfPage":
                new["image"] = img_url
        if "image" not in new:
            new["image"] = img_url
        return '<script type="application/ld+json">' + json.dumps(new, ensure_ascii=False) + '</script>'
    return m.group(0)

head = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, head, flags=re.S)
t2 = head + rest

# 6) 校验：剥 h1 后正文文本不变
def prose(s):
    b = re.search(r'<article[^>]*>(.*?)</article>', s, re.S)
    b = b.group(1) if b else ""
    b = re.sub(r'<h1>.*?</h1>', ' ', b, flags=re.S)
    b = re.sub(r'<script.*?</script>', ' ', b, flags=re.S)
    b = re.sub(r'<[^>]+>', ' ', b)
    return re.sub(r'\s+', ' ', b).strip()

assert prose(t2) == prose(orig), "正文被改动！"

# 7) ld 自检
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    json.loads(blk)

# 8) 封面入库
if not os.path.exists(IMG):
    if not os.path.exists(COVER):
        raise SystemExit("封面缺失: " + COVER)
    if APPLY:
        shutil.copy2(COVER, IMG)
    report["cover"] = os.path.getsize(COVER)

print("APPLY" if APPLY else "DRY", json.dumps(report, ensure_ascii=False))
print("size:", len(orig.encode()), "->", len(t2.encode()))
print("h1:", len(re.findall(r'<h1[\s>]', t2)), "ld:", t2.count('application/ld+json'),
      "og:image:", t2.count('og:image'), "tw_card:", 'summary_large_image' in t2)

if APPLY:
    open(PAGE, "w", encoding="utf-8").write(t2)
    print("WRITTEN")
