#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-29: 补建「已发布但站点无页」文章 mili/blog/20261029-mili-ai-seeding-notes-case.html
数据源: ~/wiki/digital-employees/articles/20261029-mili-ai-seeding-notes-case.md
用法: python3 gen-1029-page.py [--apply]
"""
import os, re, sys, json, copy, shutil

APPLY = '--apply' in sys.argv
REPO = os.path.expanduser('~/wiki/najieip-verify')
SLUG = '20261029-mili-ai-seeding-notes-case'
BRAND = 'mili'
BRAND_NAME = '北京觅理律师事务所'
DATE = '2026-10-29'
DESC = ('全国首例 AI 代写「种草笔记」不正当竞争案：杭州互联网法院一审、杭州中院二审认定构成不正当竞争。'
        '本文拆解法院为何不走著作权而走反不正当竞争法第二条、二审后的四层审查框架、2025 年新反法第九条的落点，'
        '以及企业用 AI 做营销的三条安全边界与留痕要求。')
OGDESC = ('AI 写的文案本身不是问题，专门为某个平台定制、批量生产伪装成真人体验的推荐内容才是。'
          '四层审查 + 2025 新法第九条 + 三条可用边界。')
TAGS = ['AI代写种草笔记', '不正当竞争', 'AI营销合规']
KW = 'AI代写种草笔记,不正当竞争,反不正当竞争法第二条,帮助虚假宣传,生成式人工智能,AI营销合规,杭州互联网法院,网络反不正当竞争暂行规定'

TEMPLATE = os.path.join(REPO, 'mili/blog/20261028-mili-pregnancy-disguised-dismissal-evidence.html')
MD = os.path.expanduser('~/wiki/digital-employees/articles/%s.md' % SLUG)
OUT = os.path.join(REPO, 'mili/blog/%s.html' % SLUG)
COVER_SRC = os.path.expanduser('~/wiki/digital-employees/articles/cover-%s.png' % SLUG)
COVER_DST = os.path.join(REPO, 'img/%s.png' % SLUG)

def zh(s):
    # 只处理文本节点：ASCII 双引号 -> 中文引号（成对）
    if '"' not in s:
        return s
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append('“' if open_q else '”')
            open_q = not open_q
        else:
            out.append(ch)
    return ''.join(out)

def inline(s):
    s = zh(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return s.strip()

def md_to_article(md):
    lines = md.split('\n')
    title = None
    # 正文截止到分隔线 '---'
    cut = len(lines)
    for i, ln in enumerate(lines):
        if ln.strip() == '---' and i > 5:
            cut = i
            break
    body = lines[:cut]
    paras = []           # list of (kind, payload)
    i = 0
    while i < len(body):
        ln = body[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith('# ') and title is None:
            title = ln[2:].strip()
            i += 1
            continue
        if ln.startswith('## '):
            paras.append(('h2', ln[3:].strip()))
            i += 1
            continue
        if ln.startswith('|'):
            tbl = []
            while i < len(body) and body[i].lstrip().startswith('|'):
                tbl.append(body[i].strip())
                i += 1
            paras.append(('table', tbl))
            continue
        if ln.startswith('>'):
            q = []
            while i < len(body) and body[i].lstrip().startswith('>'):
                q.append(body[i].lstrip()[1:].strip())
                i += 1
            paras.append(('quote', ' '.join(q)))
            continue
        paras.append(('p', ln.strip()))
        i += 1
    return title, paras

def render(paras):
    out = []
    for kind, payload in paras:
        if kind == 'h2':
            out.append('<h2>%s</h2>' % inline(payload))
        elif kind == 'p':
            out.append('<p>%s</p>' % inline(payload))
        elif kind == 'quote':
            out.append('<blockquote><p>%s</p></blockquote>' % inline(payload))
        elif kind == 'table':
            rows = [r for r in payload if not re.match(r'^\|[\s:|-]+\|$', r)]
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
            h = cells[0]
            tb = ['<table class="data">', '<thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in h) + '</tr></thead>', '<tbody>']
            for r in cells[1:]:
                tb.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            tb.append('</tbody></table>')
            out.append('\n'.join(tb))
    return out

def build():
    md = open(MD, encoding='utf-8').read()
    raw_title, paras = md_to_article(md)
    title = zh(raw_title).replace('“', '“').replace('”', '”')
    blocks = render(paras)
    parts = ['<h1>%s</h1>' % title]
    for b in blocks:
        parts.append(b)
        if not b.startswith('<table') and not b.startswith('<h2'):
            parts.append('<br>')
    tail = [
        '<p>何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰</p>', '<br>',
        '<p>*本文由 AI 辅助整理，法律观点与判断由作者核校。案件事实引自杭州互联网法院一审、杭州市中级人民法院二审公开披露信息，裁判框架引自《法律适用》2026 年第 11 期唐学兵文。具体个案请就具体事实咨询。*</p>', '<br>',
        '<p>*本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎联系我们。*</p>', '<br>',
    ]
    article = '<article>\n' + '\n'.join(parts + tail) + '\n</article>'

    tpl = open(TEMPLATE, encoding='utf-8').read()
    head_end = tpl.find('<body')
    head = tpl[:head_end]
    body_tail = tpl[tpl.find('</article>'):]

    # JSON-LD 块：deepcopy 后覆写
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
    assert len(lds) == 2, 'template ld count %d' % len(lds)
    objs = [json.loads(x) for x in lds]
    new_lds = []
    for o in objs:
        o = copy.deepcopy(o)
        if o.get('@type') == 'Article':
            o['headline'] = title
            o['description'] = DESC
            o['image'] = 'https://najieip.com/img/%s.png' % SLUG
            o['datePublished'] = DATE
            o['dateModified'] = DATE
            o['mainEntityOfPage'] = {'@type': 'WebPage', '@id': 'https://najieip.com/mili/blog/%s.html' % SLUG}
            o['url'] = 'https://najieip.com/mili/blog/%s.html' % SLUG
            o['inLanguage'] = 'zh-CN'
            if 'author' in o:
                o['author'] = {'@type': 'Person', 'name': '何自刚'}
            if 'publisher' in o:
                o['publisher'] = {'@type': 'Organization', 'name': BRAND_NAME}
        elif o.get('@type') == 'BreadcrumbList':
            els = o.get('itemListElement', [])
            if len(els) >= 3:
                els[-1]['name'] = title
                els[-1]['item'] = 'https://najieip.com/mili/blog/%s.html' % SLUG
        new_lds.append(json.dumps(o, ensure_ascii=False))

    url = 'https://najieip.com/mili/blog/%s.html' % SLUG
    img = 'https://najieip.com/img/%s.png' % SLUG
    # head 逐字段替换
    head = re.sub(r'<title>.*?</title>', '<title>%s — 纳杰觅理</title>' % title, head, count=1, flags=re.S)
    def setmeta(h, pat, val):
        return re.sub(pat, lambda m: m.group(1) + val + m.group(3), h, count=1)
    head = setmeta(head, r'(<meta name="description" content=")([^"]*)(")', DESC)
    head = setmeta(head, r'(<meta property="og:title" content=")([^"]*)(")', title)
    head = setmeta(head, r'(<meta property="og:description" content=")([^"]*)(")', OGDESC)
    head = setmeta(head, r'(<meta property="og:url" content=")([^"]*)(")', url)
    head = setmeta(head, r'(<meta property="og:image" content=")([^"]*)(")', img)
    head = setmeta(head, r'(<meta name="twitter:title" content=")([^"]*)(")', title)
    head = setmeta(head, r'(<meta name="twitter:description" content=")([^"]*)(")', OGDESC)
    head = setmeta(head, r'(<meta name="twitter:image" content=")([^"]*)(")', img)
    head = setmeta(head, r'(<meta name="keywords" content=")([^"]*)(")', KW)
    head = setmeta(head, r'(<link rel="canonical" href=")([^"]*)(")', url)
    # 去掉模板里重复的 twitter:card short
    head = head.replace('<meta name="twitter:card" content="summary">\n', '', 1)
    for old, new in zip(lds, new_lds):
        head = head.replace(old, new, 1)

    page = head + '<body>\n<nav><a href="/">← 首页</a> · <a href="https://najieip.com/mili/blog/">觅理博客</a></nav>\n' + article + body_tail
    # 修正模板 body 尾巴里可能残留的旧 url（footer 无 url，安全）
    assert '20261028-mili-pregnancy' not in page, 'template slug leaked'
    return title, page

def card_block(title, href, desc):
    tags = ''.join('<span class="tag">%s</span>' % t for t in TAGS)
    return ('<div class="article-card">\n    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · %s</div>\n    <p>%s</p>\n  </div>') % (href, title, tags, DATE, BRAND_NAME, desc)

def insert_card(path, href):
    t = open(path, encoding='utf-8').read()
    if href in t:
        print('SKIP already indexed:', path)
        return 0
    card = card_block(TITLE, href, DESC)
    pos = [m.start() for m in re.finditer(r'<div class="article-card">', t)]
    target = None
    for p in pos:
        seg = t[p:p + 1500]
        m = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
        if m and m.group(1) < DATE:
            target = p
            break
    if target is None:
        target = pos[-1] if pos else t.find('<div class="container">')
    t2 = t[:target] + card + '\n  ' + t[target:]
    assert t2.replace(card + '\n  ', '', 1) == t, 'outside-block modification in %s' % path
    # div 配平
    depth = 0
    bad = 0
    for m in re.finditer(r'<(/?)div\b', t2):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            bad += 1
            depth = 0
    assert depth == 0 and bad == 0, 'div imbalance %s (%d,%d)' % (path, depth, bad)
    print('CARD +1 %s (cards %d -> %d)' % (path, t.count('<div class="article-card">'), t2.count('<div class="article-card">')))
    if APPLY:
        open(path, 'w', encoding='utf-8').write(t2)
    return 1

def update_articles_json():
    p = os.path.join(REPO, 'articles.json')
    arr = json.load(open(p, encoding='utf-8'))
    url = '/mili/blog/%s.html' % SLUG
    if any(x.get('url') == url for x in arr):
        print('SKIP articles.json already has entry')
        return
    arr.insert(0, {'url': url, 'title': TITLE, 'date': DATE, 'site': BRAND, 'description': DESC})
    print('articles.json 264 -> %d' % len(arr))
    if APPLY:
        json.dump(arr, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

TITLE, PAGE = build()
print('TITLE:', TITLE)
print('page chars:', len(PAGE), 'h1:', PAGE.count('<h1'), 'h2:', PAGE.count('<h2'),
      'ld:', PAGE.count('application/ld+json'), 'tables:', PAGE.count('<table'),
      'stars:', PAGE.count('**'), 'schema:', PAGE.count('https://schema.org'), 'badschema:', PAGE.count('https://***'))
assert PAGE.count('<h1') == 1
assert PAGE.count('application/ld+json') == 2
assert PAGE.count('**') == 0
assert PAGE.count('https://schema.org') >= 2
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', PAGE, re.S):
    json.loads(blk)

if APPLY:
    open(OUT, 'w', encoding='utf-8').write(PAGE)
    print('WROTE', OUT)
    if os.path.exists(COVER_SRC):
        shutil.copy2(COVER_SRC, COVER_DST)
        print('COVER ->', COVER_DST, os.path.getsize(COVER_DST))
    else:
        print('WARN no cover', COVER_SRC)

insert_card(os.path.join(REPO, 'mili/blog/index.html'), './%s.html' % SLUG)
insert_card(os.path.join(REPO, 'blog/index.html'), '/mili/blog/%s.html' % SLUG)
update_articles_json()
print('APPLY' if APPLY else 'DRY-RUN')
