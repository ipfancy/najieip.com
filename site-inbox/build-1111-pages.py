#!/usr/bin/env python3
"""2026-11-11 夜：补建「已发布无页」+ 精修「部分裸发布」+ 双索引补卡
用法: python3 build-1111-pages.py [--apply]
"""
import os, re, sys, json, copy, shutil

REPO = "/Users/ziganghe/wiki/najieip-verify"
MDS = "/Users/ziganghe/wiki/digital-employees/articles"
TPL = os.path.join(REPO, "mili/blog/20261111-mili-fake-patent-marking-line.html")
APPLY = "--apply" in sys.argv

# ---------- md -> html ----------
def zh_q(s):
    s = re.sub(r'"([^"]*)"', r'「\1」', s)
    s = re.sub(r"(?<!\w)'([^']{1,60})'(?!\w)", r'「\1」', s)
    return s

def inline(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', s)
    return zh_q(s)

def cell_is_sep(c):
    return bool(re.match(r'^:?-{2,}:?$', c.strip()))

def convert(md_text):
    md_text = re.sub(r'^---.*?\n---\n', '', md_text, count=1, flags=re.S)
    md_text = re.sub(r'<!--.*?-->', '', md_text, flags=re.S)
    lines = [l.rstrip() for l in md_text.split('\n')]
    out, i, n = [], 0, len(lines)
    while i < n:
        l = lines[i].strip()
        if not l:
            i += 1; continue
        if l.startswith('# ') and not l.startswith('## '):
            i += 1; continue
        m = re.match(r'^##\s+(.*)$', l)
        if m:
            out.append(f'<h2>{inline(m.group(1))}</h2>'); i += 1; continue
        m = re.match(r'^\*\*(.+)\*\*$', l)
        if m:
            txt = m.group(1).strip()
            if len(txt) <= 30 and not txt.endswith(('。', '！', '？')):
                out.append(f'<h2>{zh_q(txt)}</h2>')
            else:
                out.append(f'<p><strong>{zh_q(txt)}</strong></p>')
            i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            if len(rows) >= 2:
                head = rows[0]
                body = [r for r in rows[1:] if not all(cell_is_sep(c) for c in r)]
                th = ''.join(f'<th>{inline(c)}</th>' for c in head)
                trs = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data">\n<thead><tr>{th}</tr></thead>\n<tbody>{trs}</tbody>\n</table>')
            continue
        if l.startswith('> '):
            buf = []
            while i < n and lines[i].strip().startswith('> '):
                buf.append(lines[i].strip()[2:].strip()); i += 1
            out.append('<blockquote><p>' + inline(' '.join(buf)) + '</p></blockquote>')
            continue
        if re.match(r'^\d+\.\s', l):
            items = []
            while i < n and re.match(r'^\d+\.\s', lines[i].strip()):
                items.append(re.sub(r'^\d+\.\s+', '', lines[i].strip())); i += 1
            out.append('<ol>\n' + '\n'.join(f'<li>{inline(x)}</li>' for x in items) + '\n</ol>')
            continue
        if l.startswith('- '):
            items = []
            while i < n and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:].strip()); i += 1
            out.append('<ul>\n' + '\n'.join(f'<li>{inline(x)}</li>' for x in items) + '\n</ul>')
            continue
        out.append(f'<p>{inline(l)}</p>')
        i += 1
    return '\n'.join(out)

def textify(html):
    b = html
    m = re.search(r'<article.*?</article>', b, re.S)
    if m: b = m.group(0)
    for tag in ('h1', 'h2', 'h3', 'figure', 'script', 'style'):
        b = re.sub(rf'<{tag}.*?</{tag}>', ' ', b, flags=re.S)
    b = re.sub(r'<[^>]+>', '', b)
    for a, c in (('&gt;', '>'), ('&lt;', '<'), ('&amp;', '&'), ('&nbsp;', ' '), ('&quot;', '"')):
        b = b.replace(a, c)
    b = re.sub(r'[\s*|:>"“”「」\'’‘–\-]+', '', b)
    return b

BYLINES = ['何自刚|知识产权律师|爱普纳杰·觅理·纳杰', '何自刚｜知识产权律师｜010-65150974',
           '何自刚|知识产权律师|010-65150974']
DISCLAIM = ['本文由AI辅助生成与整理，观点与判断由作者审定。本文仅代表作者个人观点，不构成法律意见。',
            '本文由AI辅助生成与整理，观点与判断由作者审定。', '本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎联系我们。',
            '本文仅代表作者个人观点，不构成法律意见。']

def norm(s):
    for b in BYLINES: s = s.replace(b, '')
    for d in DISCLAIM: s = s.replace(d, '')
    return s

def md_norm_text(md):
    md = re.sub(r'^---.*?\n---\n', '', md, count=1, flags=re.S)
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    out = []
    for l in md.split('\n'):
        s = l.strip()
        if not s: continue
        if re.match(r'^#{1,2}\s', s): continue
        m = re.match(r'^\*\*(.+)\*\*$', s)
        if m and len(m.group(1).strip()) <= 30 and not m.group(1).strip().endswith(('。', '！', '？')):
            continue
        s = re.sub(r'^\d+\.\s*', '', s)
        if s.startswith('|') and all(cell_is_sep(c) for c in s.strip('|').split('|')): continue
        out.append(s)
    s = '\n'.join(out)
    for a, c in (('&gt;', '>'), ('&lt;', '<'), ('&amp;', '&'), ('&nbsp;', ' '), ('&quot;', '"')):
        s = s.replace(a, c)
    s = re.sub(r'[\s*|:>"“”「」\'’‘–\-#]+', '', s)
    return norm(s)

# ---------- house ----------
tpl = open(TPL, encoding='utf-8').read()
NAV = tpl[tpl.find('<nav'):tpl.find('</nav>') + 6]
FOOT = tpl[tpl.find('<footer'):tpl.find('</footer>') + 9]
CTA = tpl[tpl.find('<!--CTA-STD-->'):tpl.find('<!--/CTA-STD-->') + len('<!--/CTA-STD-->')]
lds = [json.loads(m.group(1)) for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S)]
ART_LD = next(d for d in lds if d.get('@type') == 'Article')
BC_LD = next(d for d in lds if d.get('@type') == 'BreadcrumbList')

def build_head(r):
    s = lambda k: (r[k].replace('"', '&#34;'))
    a = copy.deepcopy(ART_LD)
    a.update({
        'headline': r['title'], 'description': r['desc'],
        'image': r['img'], 'datePublished': r['date'], 'dateModified': r['date'],
        'mainEntityOfPage': r['url'], 'url': r['url'], 'keywords': r['kw'],
        'inLanguage': 'zh-CN',
    })
    b = copy.deepcopy(BC_LD)
    b['itemListElement'][1]['name'] = '觅理博客'
    b['itemListElement'][1]['item'] = 'https://najieip.com/mili/blog/'
    b['itemListElement'][2]['name'] = r['short']
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{r['title']} — 纳杰觅理</title>
<meta name="description" content="{s('desc')}">
<meta property="og:type" content="article">
<meta property="og:title" content="{s('title')}">
<meta property="og:description" content="{s('desc')}">
<meta property="og:site_name" content="觅理律所">
<meta property="og:locale" content="zh_CN">
<meta name="keywords" content="{s('kw')}">
<meta property="og:url" content="{r['url']}">
<meta property="og:image" content="{r['img']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{s('title')}">
<meta name="twitter:description" content="{s('desc')}">
<meta name="twitter:image" content="{r['img']}">
<link rel="canonical" href="{r['url']}">
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(a, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>
</head>'''

def build_page(r, body):
    art = f'''<article>
<h1>{r['title']}</h1>
<figure><img src="{r['imgsrc']}" alt="{r['title']}（信息图）" width="800" height="1200" loading="lazy" style="max-width:100%;height:auto"></figure>
{body}
<p>何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰</p>
<p>本文由 AI 辅助生成与整理，观点与判断由作者审定。本文仅代表作者个人观点，不构成法律意见。</p>
{FOOT}
{CTA}
</article>'''
    return build_head(r) + '\n<body>\n' + NAV + '\n' + art + '\n</body>\n</html>\n'

TARGETS = [
    {'brand': 'mili', 'slug': '20261111-mili-earnest-money-cap', 'date': '2026-11-11', 'mode': 'create',
     'title': '合同标的 500 万，定金写 150 万：多写的 50 万，双倍不了',
     'short': '合同标的 500 万，定金写 150 万',
     'desc': '定金不是写多少就锁多少。民法典第586条第二款给了一道硬上限：主合同标的额的20%，超出部分不产生定金效力，违约时只能按预付款原额退回。500万的合同写150万定金，法院只认100万，双倍返还200万，另50万照原额退。本文拆三块：20%的基数取哪个数、定金与违约金为何只能择一（第588条）、未实际交付就没有定金（第586条），附四档算例和三件今晚就能改合同的事。',
     'kw': '定金,定金20%上限,民法典第586条,定金与违约金,双倍返还,预付款,定金罚则',
     'cover': 'cover-20261111-mili-earnest-money-cap.png'},
    {'brand': 'mili', 'slug': '20261112-mili-year-end-bonus-cancel', 'date': '2026-11-12', 'mode': 'repair',
     'title': '两年的年终奖说取消就取消，能不能要回来（劳动合同法第4条）',
     'short': '年终奖被整体取消能不能要回来',
     'desc': '在职员工的年度奖金被整体取消，比「离职了还想拿年终奖」好打得多：只要有约定、制度或惯例中的任意一项，它就属劳动报酬而非红包。本文拆公司想取消要过的三道闸（内容依据／劳动合同法第4条民主程序与公示／第35条书面协商一致）、为何举证责任在公司（司法解释一第44条），以及劳动监察、在职仲裁、被迫解除三条路各自要付的代价。',
     'kw': '年终奖,劳动合同法第4条,劳动报酬,举证责任,被迫解除,指导案例183号',
     'cover': 'cover-20261112-mili-year-end-bonus-cancel.png'},
]

results = {}
for r in TARGETS:
    md = os.path.join(MDS, r['slug'] + '.md')
    body = convert(open(md, encoding='utf-8').read())
    r['url'] = f"https://najieip.com/{r['brand']}/blog/{r['slug']}.html"
    r['img'] = f"https://najieip.com/img/{r['slug']}.png"
    r['imgsrc'] = f"/img/{r['slug']}.png?v={r['date'].replace('-', '')}"
    page = build_page(r, body)
    pg = os.path.join(REPO, r['brand'], 'blog', r['slug'] + '.html')
    old = open(pg, encoding='utf-8').read() if os.path.exists(pg) else ''
    print(f"[{r['mode']}] {r['slug']}  old={len(old)}B new={len(page)}B")
    h1 = len(re.findall(r'<h1[ >]', page)); h2 = len(re.findall(r'<h2[ >]', page))
    ld = len(re.findall(r'application/ld\+json', page))
    stars = len(re.findall(r'(?<![0-9*])\*\*', page)); bt = len(re.findall(r'<p>\|', page))
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        json.loads(m.group(1))
    mt = md_norm_text(open(md, encoding='utf-8').read())
    pt = norm(textify(page))
    if mt not in pt:
        import difflib
        cut = next((k for k in range(min(len(mt), len(pt))) if mt[k] != pt[k]), min(len(mt), len(pt)))
        print(f"   DIFF at {cut}: md=...{mt[max(0,cut-25):cut+25]!r}")
        print(f"                 pg=...{pt[max(0,cut-25):cut+25]!r}")
    print(f"   h1={h1} h2={h2} ld={ld} stars={stars} baretbl={bt} md_in_page={mt in pt} ({len(mt)}/{len(pt)})")
    results[r['slug']] = (mt in pt)
    # cover
    src = os.path.join(MDS, r['cover'])
    if os.path.exists(src):
        dst = os.path.join(REPO, 'img', r['slug'] + '.png')
        print(f"   cover {os.path.getsize(src)}B -> img/")
        if APPLY: shutil.copyfile(src, dst)
    else:
        print("   !! COVER MISSING", src)
    if APPLY:
        open(pg, 'w', encoding='utf-8').write(page)

print('MD_IN_PAGE', results)
