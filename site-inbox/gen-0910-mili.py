#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-10 发布: 觅理 blog × 2篇 (TASK-MKT-PATENT1318 / TASK-MKT-OPC)
执行包HTML(扬声产出+如己质量关+何律放行) → mili/blog 精修版(复刻 gen-0909 模式)
+ mili/blog 索引卡片 + JSON-LD blogPost + sitemap + articles.json
由如己代跑(同 9/9 应急模式); 只新增不删除
"""
import re, html as html_mod, json

REPO = '/mnt/c/Users/zigan/najieip-site'
PKG = '/mnt/i/内省II耳目手足爪牙/文件存放/市场部/发布执行包_20260909'

ARTICLES = [
    {
        'raw': f'{PKG}/20260909-patent-claim-construction-1318.html',
        'slug': '20260909-patent-claim-construction-1318.html',
        'title': '发明目的能限缩专利保护范围吗？——从一审34万改判270万说起',
        'date': '2026-09-10',
        'desc': ('最高法知产法庭（2022）最高法知民终1318号：同一专利同一批产品，一审赔34万、二审改判270万，'
                 '差在"权利要求解释"。多发明目的并存时，并非每项权利要求都须实现全部发明目的；未限定的技术特征'
                 '不得用发明目的限缩。附专利法59.1、法释〔2009〕21号第2/5/7条要旨与企业三点提示。'),
        'og_desc': '最高法1318号：同一专利同一批产品，一审赔34万、二审改判270万——差在"权利要求解释"。发明目的不能给权利要求"加锁"。',
        'keywords': '专利侵权,权利要求解释,发明目的,全面覆盖原则,专利保护范围,最高法知产法庭',
        'tags': ['专利', '侵权判定', '权利要求'],
    },
    {
        'raw': f'{PKG}/20260909-opc-one-person-company-legal.html',
        'slug': '20260909-opc-one-person-company-legal.html',
        'title': 'OPC 一人公司：AI让一个人像一支队伍，法律却问你五个问题',
        'date': '2026-09-10',
        'desc': ('《中国企业家》OPC调研：286万户注册、47%增长，但40%无付费客户、六成月入不过万。商业四关之外'
                 '还有"第五关法律关"：一人公司股东举证不能即连带（新公司法23条3款，真实判例（2023）京02民终4794号：'
                 '执行程序可直接追加股东）、委托开发成果默认归研究开发人（民法典859条）、个人IP不做商标、'
                 '熟人单不留痕。附OPC落地清单。'),
        'og_desc': '286万OPC背后那个没人提的"第五关"：一人公司股东举证不能即连带、成果归属默认归开发方、个人IP不做商标就是别人的。',
        'keywords': 'OPC,一人公司,一人公司股东责任,公司法23条,执行追加被执行人,委托开发成果归属,个人IP商标',
        'tags': ['OPC', '创业合规', '一人公司'],
    },
]

HEAD_TPL = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{site}">
<meta property="og:image" content="https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{og_desc}">
<link rel="canonical" href="{canonical}">
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "Article", "headline": {title_json}, "description": {desc_json}, "author": {{"@type": "Person", "name": "何自刚"}}, "publisher": {{"@type": "Organization", "name": "{site}"}}, "datePublished": "{date}", "dateModified": "{date}", "mainEntityOfPage": {canonical_json}, "url": {canonical_json}}}
</script>
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}}, {{"@type": "ListItem", "position": 2, "name": "博客", "item": "{blog_index}"}}, {{"@type": "ListItem", "position": 3, "name": {title_json}}}]}}
</script>
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
<h1>{title}</h1>
{body}
<p>何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰</p>
<p>座机：010-65150974 | 手机：15321374076 / 13911268604</p>
<p><em>本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎联系我们。</em></p>
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
'''

ATTR = html_mod.escape

def render(a, body, canonical, site, blog_index):
    vals = {
        'title': a['title'], 'desc': ATTR(a['desc']), 'keywords': a['keywords'],
        'og_desc': ATTR(a['og_desc']), 'canonical': canonical, 'site': site,
        'blog_index': blog_index, 'date': a['date'], 'body': body,
        'title_json': json.dumps(a['title'], ensure_ascii=False),
        'desc_json': json.dumps(a['desc'], ensure_ascii=False),
        'canonical_json': json.dumps(canonical, ensure_ascii=False),
    }
    return HEAD_TPL.format(**vals)

def extract_body(raw_path):
    t = open(raw_path, encoding='utf-8').read()
    m = re.search(r'<article>(.*?)</article>', t, re.S)
    assert m, f'no <article> in {raw_path}'
    inner = m.group(1)
    inner = re.sub(r'<h1>.*?</h1>', '', inner, flags=re.S)
    inner = inner.replace('<br>', '').replace('<br/>', '').replace('<br />', '')
    inner = re.sub(r'<hr\s*/?>', '', inner)
    inner = inner.replace('<ul>', '').replace('</ul>', '')
    inner = html_mod.unescape(inner)
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    tokens = re.findall(r'<h2>(.*?)</h2>|<li>(.*?)</li>|<p>(.*?)</p>', inner, re.S)
    blocks, ul_buf = [], []
    def flush_ul():
        nonlocal ul_buf
        if ul_buf:
            blocks.append('<ul>\n' + '\n'.join(f'<li>{x}</li>' for x in ul_buf) + '\n</ul>')
            ul_buf = []
    for h2, li, p in tokens:
        if h2:
            flush_ul()
            c = h2.strip()
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
            blocks.append(f'<h2>{c}</h2>')
        elif li:
            c = li.strip()
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
            ul_buf.append(c)
        else:
            flush_ul()
            c = p.strip()
            if not c:
                continue
            if c == '---':
                continue
            if c.startswith('>'):
                c = c.lstrip('>').strip().replace('**', '')
                blocks.append(f'<blockquote><p><strong>{c}</strong></p></blockquote>')
                continue
            if c.startswith('*本文') or c.startswith('关注公众号') or c.startswith('座机：'):
                # 免责声明由模板统一追加, 去重
                continue
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
            c = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', c)
            blocks.append(f'<p>{c}</p>')
    flush_ul()
    return '\n'.join(blocks)

def card_html(a, url_prefix, author_label):
    tags = ''.join(f'<span class="tag">{t}</span>' for t in a['tags'])
    return (
        f'  <div class="article-card">\n'
        f'    <h2><a href="{url_prefix}{a["slug"]}">{a["title"]}</a></h2>\n'
        f'    <div class="meta">{tags} {a["date"]} · {author_label}</div>\n'
        f'    <p>{a["desc"]}</p>\n'
        f'  </div>\n'
    )

# ---------- 1. 生成 mili/blog 精修版 ----------
for a in ARTICLES:
    body = extract_body(a['raw'])
    assert '**' not in body, f'** remnant in {a["slug"]}'
    assert '我们代理过' not in body, 'stale expression leaked!'
    h = render(a, body, f'https://najieip.com/mili/blog/{a["slug"]}',
               '觅理律师事务所', 'https://najieip.com/mili/blog/')
    assert 'https://schema.org' in h and '***' not in h, 'schema/leak check failed'
    assert f'<h1>{a["title"]}</h1>' in h, 'title check failed'
    open(f'{REPO}/mili/blog/{a["slug"]}', 'w', encoding='utf-8').write(h)
    print('written mili/blog/', a['slug'], len(h), 'bytes')

# ---------- 2. 索引卡片 + JSON-LD ----------
mili_cards = ''.join(card_html(a, './', '觅理律师事务所') for a in ARTICLES)
mili_idx = open(f'{REPO}/mili/blog/index.html', encoding='utf-8').read()
anchor2 = '<div class="container">\n'
assert mili_idx.count(anchor2) == 1, 'mili index container anchor missing'
mili_idx = mili_idx.replace(anchor2, anchor2 + mili_cards, 1)
anchor3 = '"blogPost": ['
assert mili_idx.count(anchor3) == 1, 'blogPost anchor missing'
posts = []
for a in ARTICLES:
    posts.append(json.dumps({
        '@type': 'BlogPosting',
        'headline': a['title'],
        'url': f'https://najieip.com/mili/blog/{a["slug"]}',
        'datePublished': a['date'],
        'description': a['desc'] + '觅理律师事务所出品。',
    }, ensure_ascii=False))
mili_idx = mili_idx.replace(anchor3, anchor3 + ','.join(posts) + ',', 1)
open(f'{REPO}/mili/blog/index.html', 'w', encoding='utf-8').write(mili_idx)
print('index updated: mili/blog/index.html')

# ---------- 3. sitemap ----------
smap = open(f'{REPO}/sitemap.xml', encoding='utf-8').read()
anchor4 = 'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
assert smap.count(anchor4) == 1
new_urls = ''
for a in ARTICLES:
    new_urls += f'''  <url>
    <loc>https://najieip.com/mili/blog/{a["slug"]}</loc>
    <lastmod>{a["date"]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
smap = smap.replace(anchor4, anchor4 + new_urls, 1)
open(f'{REPO}/sitemap.xml', 'w', encoding='utf-8').write(smap)
print('sitemap updated (+2 urls)')

# ---------- 4. articles.json ----------
aj = json.load(open(f'{REPO}/articles.json'))
assert isinstance(aj, list)
for a in ARTICLES:
    e = {'url': f'/mili/blog/{a["slug"]}', 'title': a['title'], 'date': a['date'], 'site': 'mili'}
    if not any(x.get('url') == e['url'] for x in aj):
        aj.append(e)
json.dump(aj, open(f'{REPO}/articles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('articles.json updated (+2)')

# ---------- 5. 验证 ----------
for a in ARTICLES:
    h = open(f'{REPO}/mili/blog/{a["slug"]}', encoding='utf-8').read()
    assert '**' not in h and '<strong>' in h, f'render issue in {a["slug"]}'
print('ALL DONE - local render verified')
