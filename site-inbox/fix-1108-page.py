#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-08 夜检：精修 mili 家事盗窃文「部分裸发布」页
缺陷：h1=1 有外链 style.css，但 ld=0 / 无 og:image / 无 og:site_name / 无 keywords
      / description 复读标题(23字) / ** ×2 / 裸 markdown 表 20 行
做法：按 md 源整页重建套同日 mili 房屋（20261107-mili-unpaid-trial-shigang）
"""
import re, json, copy, os, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
SLUG = "20261108-mili-family-theft-leniency"
BRAND = "mili"
TITLE = "偷拿家里的东西不算偷？第8条只认「谅解」两个字"
DESC = ("偷拿家庭成员或近亲属财物，法释〔2013〕8号第八条只给「获得谅解」留出罪口子，"
        "没谅解就按普通盗窃办。本文算清1000至3000元、3万至10万、30万至50万元三档数额，"
        "说清刑事程序里「近亲属」只有六种人、保管与侵占和盗窃的一字之差，"
        "以及家里真出这种事该按什么顺序固定证据、什么时候签谅解书。")
KW = "家庭成员盗窃,法释2013-8号第八条,近亲属谅解,盗窃罪数额标准,侵占罪自诉"
IMG = f"https://najieip.com/img/{SLUG}.png"
URL = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
DATE = "2026-11-08"
TPL = os.path.join(REPO, "mili/blog/20261107-mili-unpaid-trial-shigang.html")
OUT = os.path.join(REPO, f"{BRAND}/blog/{SLUG}.html")
MD = os.path.join(ART, SLUG + ".md")

def zh_quotes(s):
    """只对文本节点做直引号→中文引号，绝不碰标签内部"""
    parts = re.split(r'(<[^>]+>)', s)
    out = []
    for p in parts:
        if p.startswith('<'):
            out.append(p); continue
        p = re.sub(r'"([^"<]*)"', r'“\1”', p)
        p = re.sub(r"'([^'<]*)'", r'‘\1’', p)
        out.append(p)
    return ''.join(out)

def inline(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*([^*\n]{1,240})\*\*', r'<strong>\1</strong>', s)
    return zh_quotes(s)

# ---------- 1. 解析 md ----------
raw = open(MD, encoding='utf-8').read()
# 去 frontmatter
lines = raw.split('\n')
if lines[0].strip() == '---':
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            lines = lines[i+1:]; break
blocks = []
i = 0
is_sep = lambda cells: all(re.fullmatch(r':?-{2,}:?', c.strip()) for c in cells if c.strip() != '')
while i < len(lines):
    ln = lines[i].rstrip()
    st = ln.strip()
    if not st:
        i += 1; continue
    if st.startswith('<!--'):          # 合集注释块，按既有口径排除
        i += 1; continue
    if st.startswith('# '):            # h1 单独处理
        i += 1; continue
    if st.startswith('## '):
        blocks.append(('h2', st[3:].strip())); i += 1; continue
    if st.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells = [c for c in lines[i].strip().strip('|').split('|')]
            if not is_sep(cells):
                rows.append([c.strip() for c in cells])
            i += 1
        blocks.append(('table', rows)); continue
    if st.startswith('>'):
        q = []
        while i < len(lines) and lines[i].strip().startswith('>'):
            q.append(lines[i].strip().lstrip('>').strip()); i += 1
        blocks.append(('quote', ' '.join(q))); continue
    para = []
    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('## ', '|', '>', '<!--')):
        para.append(lines[i].strip()); i += 1
    blocks.append(('p', ''.join(para)))

# ---------- 2. 渲染 body ----------
chunks = [f'<h1>{inline(TITLE)}</h1>']
tables = 0
h2s = 0
for kind, val in blocks:
    if kind == 'h2':
        h2s += 1
        chunks.append(f'<h2>{inline(val)}</h2>')
    elif kind == 'table':
        tables += 1
        head = val[0]; body = val[1:]
        th = ''.join(f'<th>{inline(c)}</th>' for c in head)
        trs = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body)
        chunks.append(f'<table class="data"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>')
    elif kind == 'quote':
        chunks.append(f'<blockquote><p>{inline(val)}</p></blockquote>')
    else:
        # 免责/落款行保留字面星号（房屋口径）
        chunks.append(f'<p>{inline(val)}</p>')
body_inner = '\n<br>\n'.join(chunks)

# ---------- 3. head / JSON-LD 用模板 deepcopy ----------
tpl = open(TPL, encoding='utf-8').read()
lds = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', tpl, re.S)
art_obj = bread_obj = None
for blk in lds:
    o = json.loads(blk)
    if o.get('@type') == 'Article': art_obj = copy.deepcopy(o)
    elif o.get('@type') == 'BreadcrumbList': bread_obj = copy.deepcopy(o)
assert art_obj and bread_obj, "模板缺 JSON-LD"

art_obj['headline'] = TITLE
art_obj['description'] = DESC
art_obj['image'] = IMG
art_obj['datePublished'] = DATE
art_obj['dateModified'] = DATE
art_obj['mainEntityOfPage']['@id'] = URL
art_obj['url'] = URL
art_obj['keywords'] = KW
bread_obj['itemListElement'][2]['name'] = TITLE
bread_obj['itemListElement'][2]['item'] = URL

def esc_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

head = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc_attr(TITLE)} — 纳杰觅理</title>
<meta name="description" content="{esc_attr(DESC)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc_attr(TITLE)}">
<meta property="og:description" content="{esc_attr(DESC)}">
<meta property="og:url" content="{URL}">
<meta property="og:site_name" content="北京觅理律师事务所">
<meta property="og:locale" content="zh_CN">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc_attr(TITLE)}">
<meta name="twitter:description" content="{esc_attr(DESC)}">
<meta name="twitter:image" content="{IMG}">
<meta name="keywords" content="{KW}">
<link rel="canonical" href="{URL}">
<link rel="alternate" hreflang="zh-CN" href="{URL}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">
{json.dumps(art_obj, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(bread_obj, ensure_ascii=False, indent=2)}
</script>
</head>'''

# nav/footer 从模板现取（避免手抄）
nav = re.search(r'<nav>.*?</nav>', tpl, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', tpl, re.S).group(0)
page = f'''{head}
<body>
{nav}
<article>
{body_inner}
</article>
{footer}
</body>
</html>
'''

# ---------- 4. 自检 ----------
b = page[page.find('<body'):]
chk = {}
chk['h1'] = len(re.findall(r'<h1[ >]', b))
chk['ld'] = page.count('application/ld+json')
chk['stars'] = len(re.findall(r'\*\*', b))
chk['bare_table'] = len(re.findall(r'<p>\s*\|', b))
chk['tables'] = page.count('<table class="data">')
chk['h2'] = len(re.findall(r'<h2[ >]', b))
chk['og_image'] = 'og:image' in page
chk['desc_len'] = len(DESC)
for blk in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', page, re.S):
    json.loads(blk)
chk['schema'] = page.count('https://schema.org')
chk['bad_schema'] = page.count('https://***')

# 正文包含断言：md 全文（去 heading/表分隔/注释）⊆ 页面 article 文本
def norm(s):
    s = re.sub(r'<h[12][^>]*>.*?</h[12]>', '', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'[-:|\s*“”"\'’‘>]+', '', s)
    return s

md_clean = re.sub(r'\A---\n.*?\n---\n', '', raw, count=1, flags=re.S)
md_clean = re.sub(r'^#{1,2} .*$', '', md_clean, flags=re.M)
md_clean = re.sub(r'<!--.*?-->', '', md_clean, flags=re.S)
md_clean = '\n'.join(l for l in md_clean.split('\n') if not re.fullmatch(r'\s*\|?[\s:|-]+\|?\s*', l) or '|' not in l and l.strip() == '---')
mdn = norm(md_clean)
art_zone = page[page.find('<article>'):page.find('</article>')]
pn = norm(art_zone)
chk['md_contained'] = mdn in pn
if not chk['md_contained']:
    k = 0
    while k < min(len(mdn), len(pn)) and mdn[k] == pn[k]: k += 1
    chk['diff_at'] = k
    chk['md_at'] = mdn[max(0,k-40):k+60]
    chk['pg_at'] = pn[max(0,k-40):k+60]

print(json.dumps(chk, ensure_ascii=False, indent=1))
print("bytes", len(page.encode()))

if '--apply' in sys.argv:
    assert chk['h1'] == 1 and chk['ld'] == 2 and chk['stars'] == 0 and chk['tables'] == tables
    assert chk['md_contained'], "正文包含断言失败，拒绝写入"
    open(OUT, 'w', encoding='utf-8').write(page)
    # 封面入库
    src = os.path.join(ART, f'cover-{SLUG}.png')
    if os.path.exists(src):
        os.makedirs(os.path.join(REPO, 'img'), exist_ok=True)
        shutil.copy2(src, os.path.join(REPO, 'img', f'{SLUG}.png'))
        print("cover copied", os.path.getsize(os.path.join(REPO,'img',f'{SLUG}.png')))
    print("WRITTEN", OUT)
else:
    open('/tmp/preview-1108.html','w',encoding='utf-8').write(page)
    print("dry-run preview /tmp/preview-1108.html")
