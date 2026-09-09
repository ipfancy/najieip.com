#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-09 应急发布: 觅理 blog × 3篇 (TASK-MKT-FILING/AUCL/AI1197)
执行包HTML(扬声产出, 如己质量关+何律终审通过) → mili/blog 精修版(复刻 gen-0908 模式)
+ mili/blog 索引卡片 + JSON-LD blogPost + sitemap + articles.json
由如己代跑(门丞调度缺口应急); 只新增不删除, 避开误删事故模式
"""
import re, html as html_mod, json, os

REPO = '/mnt/c/Users/zigan/najieip-site'
PKG = '/mnt/i/内省II耳目手足爪牙/文件存放/市场部/发布执行包_20260909_三篇'

ARTICLES = [
    {
        'raw': f'{PKG}/20260909-jicheng-jiufen-li-an.html',
        'slug': '20260909-jicheng-jiufen-li-an.html',
        'title': '继承纠纷想打官司，立案先过这4关——刚替当事人立上案，把坑都踩明白了',
        'date': '2026-09-09',
        'desc': ('继承纠纷想打官司，立案先过这4关：专属管辖去哪家法院、4类材料怎么备、在线立案审核与7日期限、'
                 '立案后还有哪些程序。文末附出发前自查5项清单。结合《民事诉讼法》（2023修正）第34/122/126/16/95条'
                 '与《人民法院在线诉讼规则》（法释〔2021〕12号）。'),
        'og_desc': '继承纠纷立案4关：管辖法院、4类材料、在线立案7日期限、立案后程序——附出发前自查5项清单。',
        'keywords': '继承纠纷,立案,专属管辖,人民法院在线服务,在线立案,遗产继承,诉讼程序',
        'tags': ['民商事诉讼', '继承纠纷', '立案'],
    },
    {
        'raw': f'{PKG}/20260909-aucl-livestream-ads.html',
        'slug': '20260909-aucl-livestream-ads.html',
        'title': '直播带货、测评视频、比较广告：市场部最容易踩的3条"反法"红线',
        'date': '2026-09-09',
        'desc': ('最高法2026年反不正当竞争典型案例（案例七/八/九）解读：篡改同行直播切片=虚假宣传、恶意剪辑测评视频='
                 '商业诋毁、遮logo不实比较广告照样担责。新《反不正当竞争法》（2025修订，2025-10-15施行）第9/12条，'
                 '附市场部5条底线清单。'),
        'og_desc': '直播切片、测评视频、比较广告——市场部最容易踩的3条"反法"红线：篡改切片=虚假宣传、恶意剪辑=商业诋毁、遮logo不实比较照样担责。',
        'keywords': '直播带货合规,测评视频,商业诋毁,虚假宣传,比较广告,反不正当竞争法,典型案例',
        'tags': ['反不正当竞争', '直播电商', '合规'],
    },
    {
        'raw': f'{PKG}/20260909-civilcode1197-ai-redflag.html',
        'slug': '20260909-civilcode1197-ai-redflag.html',
        'title': '技术不是"免责牌"：民法典第1197条，什么时候会找上AI公司？',
        'date': '2026-09-09',
        'desc': ('最高法《关于依法审理涉人工智能纠纷案件的意见》（2026-09-07施行）制定思路解读：AI服务提供者有"避风港"'
                 '（《意见》第7条），但红旗原则随时可能适用——民法典第1197条"知道或应当知道却不作为"→连带责任。'
                 '企业不能只获利不担责，附AI企业三件合规动作。'),
        'og_desc': 'AI服务提供者"避风港"有红线：民法典第1197条红旗原则，什么时候会找上AI公司？附三件合规动作。',
        'keywords': '人工智能,民法典1197条,红旗原则,避风港,生成式AI,AI侵权,最高法AI意见',
        'tags': ['人工智能', '合规', '民法典'],
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
<meta property="og:image" content="https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg?auto=compress&cs=tinysrgb&w=1200">
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
    inner = inner.replace('<ul>', '').replace('</ul>', '')  # li 顺序已保证, 手动组 ul
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
            if c.startswith('*本文仅代表') or c.startswith('关注公众号') or c.startswith('座机：'):
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

# ---------- 1. 生成 mili/blog 精修版 (本批三篇均为觅理 blog 栏目) ----------
for a in ARTICLES:
    body = extract_body(a['raw'])
    assert '**' not in body, f'** remnant in {a["slug"]}'
    h = render(a, body, f'https://najieip.com/mili/blog/{a["slug"]}',
               '觅理律师事务所', 'https://najieip.com/mili/blog/')
    assert 'https://schema.org' in h and '***' not in h, 'schema/leak check failed'
    assert a['title'] in h and f'<h1>{a["title"]}</h1>' in h, 'title check failed'
    open(f'{REPO}/mili/blog/{a["slug"]}', 'w', encoding='utf-8').write(h)
    print('written mili/blog/', a['slug'], len(h), 'bytes')

# ---------- 2. 索引卡片 + JSON-LD blogPost ----------
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
print('sitemap updated (+3 urls)')

# ---------- 4. articles.json ----------
aj = json.load(open(f'{REPO}/articles.json'))
assert isinstance(aj, list)
for a in ARTICLES:
    add = [{'url': f'/mili/blog/{a["slug"]}', 'title': a['title'], 'date': a['date'], 'site': 'mili'}]
    add = [e for e in add if not any(x.get('url') == e['url'] for x in aj)]
    # 插到同日期/同主题附近: 简单追加尾部(与现有 mili 条目并列即可)
    aj.extend(add)
json.dump(aj, open(f'{REPO}/articles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('articles.json updated (+3)')

# ---------- 5. 本地验证: 渲染无残留 ----------
for a in ARTICLES:
    h = open(f'{REPO}/mili/blog/{a["slug"]}', encoding='utf-8').read()
    assert '<strong>' in h, f'no strong in {a["slug"]}'
    assert '**' not in h, f'** leak in {a["slug"]}'
print('ALL DONE - local render verified')
