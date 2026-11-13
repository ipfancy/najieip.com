#!/usr/bin/env python3
# 2026-11-13 精修「荷兰突击搜查撤销」部分裸发布页：md 源重建 + 房屋(head/nav/footer/CTA) + ld=2 带 @context
import re, os, json, shutil, sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
MD = "/Users/ziganghe/wiki/digital-employees/articles/20261113-byd-netherlands-evidence-seizure.md"
SLUG = "20261113-byd-netherlands-evidence-seizure"
BRAND = "mili"
ORG = "北京觅理律师事务所"
URL = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
OUT = f"{REPO}/{BRAND}/blog/{SLUG}.html"
DATE = "2026-11-13"

DESC = ("荷兰海牙法院11月11日撤销了8月对比亚迪欧洲办公室的突击搜查令。真正决定成败的不是现场那一下，"
        "而是事后异议程序。本文拆荷兰《民事诉讼法》第1019条取证专章的三项特征、中国民诉法第84条与"
        "《知产证据规定》第11/12/17条的对应关系，以及出海企业现场、异议、成本三步应对。")
KW = "涉外知产,证据保全,荷兰民事诉讼法1019条,知产证据规定,异议解除,出海合规"

md = open(MD, encoding="utf-8").read()
md = re.sub(r'^---.*?---\s*', '', md, flags=re.S)
lines = md.split('\n')
title = None
blocks = []  # ('p'|'table', text)
raw_paras = []
buf = []
def flush():
    global buf
    if buf:
        raw_paras.append(('p', ' '.join(x.strip() for x in buf).strip()))
        buf = []

tbl = []
for ln in lines:
    s = ln.strip()
    if s.startswith('#'):
        if title is None and s.startswith('# '):
            title = s[2:].strip()
        continue
    if s.startswith('|'):
        flush()
        tbl.append(s)
        continue
    elif tbl:
        raw_paras.append(('table', list(tbl)))
        tbl = []
    if not s:
        flush()
        continue
    if s.startswith('<!--'):
        flush()
        continue
    buf.append(s)
flush()
if tbl:
    raw_paras.append(('table', tbl))

assert title, "no title"

def zh_quotes(s):
    # 成对 ASCII 直引号 -> 中文引号（仅文本节点调用）
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append('“' if open_q else '”')
            open_q = not open_q
        else:
            out.append(ch)
    return ''.join(out)

def inline(s):
    s = zh_quotes(s)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'^\*([^*]+)\*$', r'<em>\1</em>', s)
    return s

ANCHORS = [
    ("先说清楚发生了什么。", "事情本身：先批准、后撤销"),
    ("荷兰这一手，依据是荷兰", "荷兰Rv第1019条：三个特征"),
    ("这套东西，中国法里其实有一一对应的条款。", "中国法的对应条款：四因素与异议解除"),
    ("落回行动，就三步。", "落地的三步：现场、异议、成本"),
    ("最后泼一盆冷水：", "一句冷水：这只是程序性裁定"),
]

body_parts = []
h2_done = []
for kind, val in raw_paras:
    if kind == 'p':
        for pre, h2 in ANCHORS:
            if val.startswith(pre) and h2 not in h2_done:
                body_parts.append(f"<h2>{h2}</h2>")
                h2_done.append(h2)
        body_parts.append(f"<p>{inline(val)}</p>")
    else:
        rows = [r for r in val if not re.fullmatch(r'\|[\s:|-]+\|', r)]
        def cells(r):
            return [c.strip() for c in r.strip().strip('|').split('|')]
        head = cells(rows[0])
        html = ['<table class="data">', '<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead>', '<tbody>']
        for r in rows[1:]:
            html.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells(r)) + '</tr>')
        html += ['</tbody>', '</table>']
        body_parts.append('\n'.join(html))

assert len(h2_done) == len(ANCHORS), f"h2 anchors hit {h2_done}"
body = '\n'.join(body_parts)

# 封面入库
src = f"/Users/ziganghe/wiki/digital-employees/articles/cover-{SLUG}.png"
dst = f"{REPO}/img/{SLUG}.png"
assert os.path.exists(src), "cover missing"
shutil.copyfile(src, dst)

art = {"@context": "https://schema.org", "@type": "Article",
       "headline": title, "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师"},
       "publisher": {"@type": "Organization", "name": ORG},
       "datePublished": DATE, "dateModified": DATE,
       "mainEntityOfPage": URL, "url": URL, "image": IMG,
       "description": DESC, "keywords": KW, "inLanguage": "zh-CN"}
bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
    {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
    {"@type": "ListItem", "position": 3, "name": title}]}

def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} — 纳杰觅理</title>
<meta name="description" content="{esc(DESC)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(DESC)}">
<meta property="og:site_name" content="觅理律所">
<meta property="og:locale" content="zh_CN">
<meta name="keywords" content="{KW}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(DESC)}">
<meta name="twitter:image" content="{IMG}">
<link rel="canonical" href="{URL}">
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(art, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>
</head>
<body>
<nav><a href="/">← 首页</a> · <a href="https://najieip.com/mili/blog/">觅理博客</a></nav>
<article>
<h1>{inline(title)}</h1>
<figure><img src="/img/{SLUG}.png?v=20261113" alt="{esc(title)}（信息图）" width="800" height="1200" loading="lazy" style="max-width:100%;height:auto"></figure>
{body}
<footer>
<p>© 2026 纳杰觅理 · 北京纳杰知识产权代理有限公司</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
<!--CTA-STD-->
<div style="margin:36px 0;padding:18px 24px;border-left:3px solid #4A2C6E;background:#F6F3FA;border-radius:6px"><p style="margin:0 0 6px"><strong>这篇文章的场景，落到你公司身上是什么样？</strong></p><p style="margin:0;font-size:14px;color:#555">何自刚｜知识产权律师　电话 010-65150974 / 15321374076　微信同号</p></div>
<!--/CTA-STD-->
</article>
</body>
</html>
'''

if '--apply' in sys.argv:
    open(OUT, 'w', encoding='utf-8').write(html)
    print("WROTE", OUT, os.path.getsize(OUT), "B")
else:
    print("DRY len", len(html))

# 自检
t = html
print("h1:", len(re.findall(r'<h1[ >]', t)), "| h2:", len(re.findall(r'<h2[ >]', t)),
      "| ld:", len(re.findall(r'application/ld\+json', t)), "| schema.org:", t.count('https://schema.org'))
print("stars:", t.count('**'), "| naked_tbl:", len(re.findall(r'<p>\|', t)), "| table:", t.count('<table'))
for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)):
    o = json.loads(blk)
    print("  ld", i, "ok @type=", o.get('@type'), "ctx=", o.get('@context'))
print("desc len:", len(DESC), "| desc!=title:", DESC != title)
print("img exists:", os.path.exists(dst), os.path.getsize(dst))
