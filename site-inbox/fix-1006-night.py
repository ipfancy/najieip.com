#!/usr/bin/env python3
"""Night SiteOps 1006: repair nobel article (partial bare-publish) + index cards + articles.json guard.
Usage: python3 fix-1006-night.py [--apply]
"""
import re, os, sys, json, copy, subprocess

ROOT = "/Users/ziganghe/wiki/najieip-verify"
APPLY = "--apply" in sys.argv
SLUG = "20261006-nobel-icecube-patent-four-rules"
PAGE = os.path.join(ROOT, "mili/blog", SLUG + ".html")
TPL = os.path.join(ROOT, "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html")
TITLE = "诺奖给了中微子，专利法却说“不授权”：IceCube藏着4条创新规则"
IMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
DESC = ("2026年诺贝尔物理学奖授予南极“冰立方”中微子观测站，但这项诺奖级成果在专利法上属于“不授予专利权”的客体。"
        "本文讲清科学发现与专利的分界、可申请专利的4类技术方案、论文先发表的宽限期陷阱、长周期创新的“1+N”阶梯式布局，"
        "以及几百人项目里职务发明的署名与奖酬边界。")
KEYWORDS = "科学发现不授予专利权,专利法第25条,新颖性宽限期,职务发明,专利布局"
CARD_DESC = ("2026年诺贝尔物理学奖授予IceCube中微子观测站，但诺奖级科学发现在专利法上属于“不授予专利权”的客体。"
             "发现与专利的分界在哪、可申请专利的是哪4类技术方案、论文先发表为何会毁掉自己的新颖性、"
             "以及职务发明里发明人带走的是署名和奖酬而不是专利权——4条规则，写给做长周期创新的人。")
TAGS = ["专利法", "科学发现", "职务发明"]

# ---------- 1. read page, normalize text-node quotes ----------
t = open(PAGE, encoding="utf-8").read()

def norm_text_nodes(html):
    out = []
    i = 0
    for m in re.finditer(r">([^<>]*)<", html):
        out.append(html[i:m.start() + 1])
        seg = m.group(1)
        seg = re.sub(r'"([^"]*)"', lambda x: "\u201c" + x.group(1) + "\u201d", seg)
        out.append(seg)
        i = m.end() - 1
    out.append(html[i:])
    return "".join(out)

body_start = t.find("<body")
head, body = t[:body_start], norm_text_nodes(t[body_start:])

# **x** -> <strong>x</strong>  (before anything else)
body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body, flags=re.S)
# strip literal blockquote marker left in text
body = body.replace("<strong>【本文核心结论】", "<strong>【本文核心结论】")
body = re.sub(r"<p>\s*&gt;\s*", "<p>", body)
# escaped html comments -> real comments (do not render as text)
body = re.sub(r"<p>(&lt;!--.*?--&gt;)</p>",
              lambda m: "<!--" + m.group(1).replace("&lt;!--", "").replace("--&gt;", "") + "-->", body)

# ---------- 2. rebuild head: title/social/meta/JSON-LD ----------
lod = []
# keep charset/viewport/beacon/style link, drop old title/desc/og/twitter/canonical
new_head = ['<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"<title>{TITLE} — 纳杰觅理</title>",
            f'<meta name="description" content="{DESC}">',
            f'<meta name="keywords" content="{KEYWORDS}">',
            '<meta name="author" content="何自刚">',
            '<meta property="og:type" content="article">',
            f'<meta property="og:title" content="{TITLE}">',
            f'<meta property="og:description" content="{DESC}">',
            f'<meta property="og:url" content="{URL}">',
            f'<meta property="og:image" content="{IMG}">',
            '<meta property="og:site_name" content="觅理律师事务所">',
            '<meta property="og:locale" content="zh_CN">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{TITLE}">',
            f'<meta name="twitter:description" content="{DESC}">',
            f'<meta name="twitter:image" content="{IMG}">',
            f'<link rel="canonical" href="{URL}">']

# JSON-LD: deepcopy Article + BreadcrumbList template objects
tpl = open(TPL, encoding="utf-8").read()
tpl_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S)
art = json.loads(tpl_blocks[0])
art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMG
art["datePublished"] = "2026-10-06"
art["dateModified"] = "2026-10-06"
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
art["url"] = URL
bc = json.loads(tpl_blocks[1])
bc["itemListElement"][2]["name"] = TITLE
bc["itemListElement"][2]["item"] = URL
# schema.org literal must not be a masked/placeholder value
for blk in (art, bc):
    assert blk["@context"] == "https://schema.org", blk["@context"]
new_head.append('<script type="application/ld+json">' + json.dumps(art, ensure_ascii=False) + '</script>')
new_head.append('<script type="application/ld+json">' + json.dumps(bc, ensure_ascii=False) + '</script>')

head_body = "\n".join(new_head)
new = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n' + head_body +
       '\n<script defer src=\'https://static.cloudflareinsights.com/beacon.min.js\' data-cf-beacon=\'{"token": "c80241f3caa4e708a12ed93baec1bde"}\'></script>'
       '\n<link rel="stylesheet" href="/style.css">\n</head>\n' + body)

# ---------- 3. assertions ----------
assert new.count("<h1") == 1, "h1"
assert new.count("application/ld+json") == 2, "ld"
assert "og:image" in new
assert new.count("**") == 0 and "&lt;!--" not in new
assert '<meta property="og:title" content="' + TITLE + '">' in new
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', new, re.S):
    json.loads(b)
# body text preserved: same paragraphs (ignoring quotes/markup normalization)
def paras(h):
    seg = h[h.find("<article>"):h.find("</article>")]
    ps = []
    for p in re.findall(r"<p>(.*?)</p>", seg, re.S):
        if "lt;!--" in p or p.strip().startswith("<!--"):
            continue  # 带货位/合集 markers are excluded by house convention
        ps.append(re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", p)))
    return ps
def norm(s):
    return (s.replace("**", "").replace("\u201c", '"').replace("\u201d", '"')
             .replace("&gt;", "").replace("&amp;", "&").strip())

old_p, new_p = [norm(x) for x in paras(t)], [norm(x) for x in paras(new)]
assert len(old_p) == len(new_p), (len(old_p), len(new_p))
diff = [i for i, (a, b) in enumerate(zip(old_p, new_p)) if a != b]
assert not diff, ("body text changed at paragraphs", diff)  # 不改一字正文
print(f"page: {os.path.getsize(PAGE)}B -> {len(new.encode('utf-8'))}B | paragraphs {len(old_p)} identical")

if APPLY:
    open(PAGE, "w", encoding="utf-8").write(new)
    print("PAGE WRITTEN")

# ---------- 4. index cards ----------
def card(href, title, tags, pub, desc):
    tg = "".join(f'<span class="tag">{x}</span>' for x in tags)
    return (f'<div class="article-card">\n'
            f'    <h2><a href="{href}">{title}</a></h2>\n'
            f'    <div class="meta">{tg} 2026-10-06 · {pub}</div>\n'
            f'    <p>{desc}</p>\n'
            f'  </div>')

def insert_card(html, c):
    pos = [m.start() for m in re.finditer(r'<div class="article-card">', html)]
    target = None
    for p in pos:
        mv = re.search(r'<div class="meta">.*?(\d{4}-\d{2}-\d{2})', html[p:p + 700], re.S)
        if mv and mv.group(1) < "2026-10-06":
            target = p
            break
    assert target is not None, "no insertion point"
    return html[:target] + c + "\n  " + html[target:]

def div_depth(html, pos=None):
    seg = html[html.find("<body"):] if pos is None else html
    d = 0
    bad = 0
    for m in re.finditer(r"<(/?)div", seg):
        d += -1 if m.group(1) else 1
        if d < 0:
            bad += 1
    return d, bad

for path, href, pub, desc in [
    (os.path.join(ROOT, "mili/blog/index.html"), f"./{SLUG}.html", "北京觅理律师事务所", CARD_DESC),
    (os.path.join(ROOT, "blog/index.html"), f"/mili/blog/{SLUG}.html", "北京纳杰知识产权代理有限公司", CARD_DESC),
]:
    h = open(path, encoding="utf-8").read()
    base_depth, base_bad = div_depth(h)
    if SLUG in h:
        print(f"SKIP {os.path.basename(path)} (already has card)")
        continue
    c = card(href, TITLE, TAGS, pub, desc)
    h2 = insert_card(h, c)
    assert h2.count('<div class="article-card">') == h.count('<div class="article-card">') + 1
    assert h2.replace(c + "\n  ", "", 1) == h, "insert touched content outside card"
    d, bad = div_depth(h2)
    assert d == 0 and bad == 0, (d, bad)
    print(f"{os.path.relpath(path, ROOT)}: cards {h.count('<div class=\"article-card\">')} -> {h2.count('<div class=\"article-card\">')} | depth {base_depth}->{d} bad {base_bad}->{bad} | {os.path.getsize(path)}B -> {len(h2.encode('utf-8'))}B")
    if APPLY:
        open(path, "w", encoding="utf-8").write(h2)
print("DRY-RUN" if not APPLY else "APPLIED")
