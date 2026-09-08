#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-08: ART-0080 AI生成内容24条 + 版权十五五规划v2
site-inbox/articles 原文 → blog + mili/blog 精修版 (复刻 gen-0907 模式)
+ articles/ 旧路径改跳转 + 主blog/mili索引卡片 + mili JSON-LD blogPost + sitemap + articles.json
"""
import re, html as html_mod, json, os, shutil

REPO = '/Users/ziganghe/wiki/najieip-verify'

ARTICLES = [
    {
        'raw': f'{REPO}/articles/20260908-ai-content-liability-24-rules.html',
        'slug': '20260908-ai-content-liability-24-rules.html',
        'title': 'AI生成内容被告，最高法24条新规：别甩锅给AI',
        'date': '2026-09-08',
        'desc': ('9月7日最高法发布《关于涉人工智能纠纷案件适用法律若干问题的意见》，5部分24条——全国首部AI裁判规则。'
                 '拆解三大要点："AI生成"不是免死金牌，提示词、生成、传播的实际控制人照赔不误；生成式AI算"服务"不算"产品"，'
                 '侵权走一般过错责任；作品归属与训练数据两问最高法暂未定，现在就该留痕。附三条今天就能落地的合规动作。'),
        'og_desc': ('最高法24条涉AI裁判规则："AI生成"不是免死金牌，实际控制人照赔；AI服务走一般过错责任。'
                    '两条没定的事现在就要留痕，附三条今天就做的合规动作。'),
        'keywords': 'AI生成内容,涉AI纠纷,最高法24条,AI侵权,过错责任,AIGC合规',
        'tags': ['AI生成内容', '最高法24条', '知识产权诉讼'],
    },
    {
        'raw': f'{REPO}/articles/20260907-copyright-15plan-opportunities-v2-生命力润色版.html',
        'slug': '20260907-copyright-15plan-opportunities-v2-生命力润色版.html',
        'title': '版权质押冲120亿：国家版权"十五五"规划里的4个新机会',
        'date': '2026-09-08',
        'desc': ('《版权工作"十五五"规划》2026年8月发布：作品登记749万→950万件、软著318万→400万、版权质押融资84亿→120亿。'
                 '版权正从"防侵权的证书"变成"能融资的资产"——质押融资、AI训练数据付费、登记服务放量、版权资产化，'
                 '这5年藏着4个新机会，附未来5年吃香的5种能力清单。'),
        'og_desc': ('版权"十五五"规划：作品登记749万→950万、质押融资84亿→120亿。版权从证书变资产，'
                    '质押融资/AI训练数据付费/登记放量4个新机会一次翻出来。'),
        'keywords': '版权质押,版权登记,十五五规划,版权融资,AI训练数据,版权资产化',
        'tags': ['版权质押', '版权登记', '政策解读', '版权融资'],
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

ATTR = html_mod.escape  # quotes -> &quot; for meta attributes

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
    """articles/ 原文 <article> 内文 → 精修 blocks html（复刻 gen-0907 清洗逻辑）"""
    t = open(raw_path, encoding='utf-8').read()
    m = re.search(r'<article>(.*?)</article>', t, re.S)
    assert m, f'no <article> in {raw_path}'
    inner = m.group(1)
    inner = re.sub(r'<h1>.*?</h1>', '', inner, flags=re.S)      # 标题去重
    inner = inner.replace('<br>', '').replace('<br/>', '').replace('<br />', '')
    inner = html_mod.unescape(inner)
    # 去掉内部注释（带货位/合集等）
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)

    tokens = re.findall(r'<h2>(.*?)</h2>|<li>(.*?)</li>|<p>(.*?)</p>', inner, re.S)
    blocks = []
    ul_buf = []
    def flush_ul():
        nonlocal ul_buf
        if ul_buf:
            blocks.append('<ul>\n' + '\n'.join(f'<li>{x}</li>' for x in ul_buf) + '\n</ul>')
            ul_buf = []
    for h2, li, p in tokens:
        # findall 未匹配组返回 '' 而非 None —— 必须用 truthiness 判断
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
            # 块引用（&gt; 引出的署名式结论行）→ 去 ** 后整行 strong（避免双重嵌套）
            if c.startswith('>'):
                c = c.lstrip('>').strip()
                c = c.replace('**', '')
                blocks.append(f'<blockquote><p><strong>{c}</strong></p></blockquote>')
                continue
            # 免责声明/作者行/公众号CTA/小店带货/发布器尾部签名块 → 模板统一追加，跳过
            if c == '何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰':
                continue
            if c == '何自刚 | 知识产权律师 | 北京纳杰知识产权':
                continue
            if c == '---':
                continue
            if c.startswith('*本文仅代表'):
                continue
            if c.startswith('关注公众号'):
                continue
            if c.startswith('想先要一份'):
                continue
            if c.startswith('座机：010-65150974 | 电话：'):
                continue
            if c.startswith('邮箱：collection@najieip.com'):
                continue
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
            c = re.sub(r'\*(.+?)\*', r'<em>\1</em>', c)
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

# ---------- 1. 生成 blog + mili/blog 精修版 ----------
for a in ARTICLES:
    body = extract_body(a['raw'])
    assert '**' not in body, f'** remnant in {a["slug"]}'
    blog_html = render(a, body, f'https://najieip.com/blog/{a["slug"]}',
                       '爱普纳杰专利所', 'https://najieip.com/blog/')
    mili_html = render(a, body, f'https://najieip.com/mili/blog/{a["slug"]}',
                       '觅理律师事务所', 'https://najieip.com/mili/blog/')
    for h in (blog_html, mili_html):
        assert 'https://schema.org' in h and '***' not in h, 'schema/leak check failed'
    open(f'{REPO}/blog/{a["slug"]}', 'w', encoding='utf-8').write(blog_html)
    open(f'{REPO}/mili/blog/{a["slug"]}', 'w', encoding='utf-8').write(mili_html)
    print('written', a['slug'], len(blog_html), 'bytes (blog)', len(mili_html), '(mili)')

# ---------- 2. articles/ 旧路径改跳转页 ----------
REDIR_TPL = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="0; url=/blog/{slug}">
<link rel="canonical" href="https://najieip.com/blog/{slug}">
<title>{title}</title>
</head>
<body>
<p>文章已迁移：<a href="/blog/{slug}">{title}</a></p>
</body>
</html>
'''
for a in ARTICLES:
    open(a['raw'], 'w', encoding='utf-8').write(
        REDIR_TPL.format(slug=a['slug'], title=a['title']))
    print('redirected', a['raw'].split('/')[-1])

# ---------- 3. 索引卡片 ----------
main_cards = ''.join(card_html(a, '/blog/', '纳杰知识产权') for a in ARTICLES)
mili_cards = ''.join(card_html(a, './', '觅理律师事务所') for a in ARTICLES)

blog_idx = open(f'{REPO}/blog/index.html', encoding='utf-8').read()
anchor = '<div class="container">\n'
assert blog_idx.count(anchor) == 1
blog_idx = blog_idx.replace(anchor, anchor + main_cards, 1)
open(f'{REPO}/blog/index.html', 'w', encoding='utf-8').write(blog_idx)

mili_idx = open(f'{REPO}/mili/blog/index.html', encoding='utf-8').read()
anchor2 = '<div class="container">\n'
assert mili_idx.count(anchor2) == 1
mili_idx = mili_idx.replace(anchor2, anchor2 + mili_cards, 1)

# mili JSON-LD blogPost 数组头部插入
anchor3 = '"blogPost": ['
assert mili_idx.count(anchor3) == 1
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
print('indexes updated: blog/index.html + mili/blog/index.html')

# ---------- 4. sitemap ----------
smap = open(f'{REPO}/sitemap.xml', encoding='utf-8').read()
anchor4 = 'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
assert smap.count(anchor4) == 1
new_urls = ''
for a in ARTICLES:
    for path in (f'blog/{a["slug"]}', f'mili/blog/{a["slug"]}'):
        new_urls += f'''  <url>
    <loc>https://najieip.com/{path}</loc>
    <lastmod>{a["date"]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
smap = smap.replace(anchor4, anchor4 + new_urls, 1)
open(f'{REPO}/sitemap.xml', 'w', encoding='utf-8').write(smap)
print('sitemap updated (+4 urls)')

# ---------- 5. articles.json ----------
aj = json.load(open(f'{REPO}/articles.json'))
assert isinstance(aj, list)
for a in ARTICLES:
    # 找该文章现有 articles/ 条目，紧随其后插入 blog + mili/blog 条目
    base_url = f'/articles/{a["slug"]}'
    idx = next((i for i, e in enumerate(aj) if e.get('url') == base_url), None)
    add = [
        {'url': f'/blog/{a["slug"]}', 'title': a['title'], 'date': a['date'], 'site': 'najie'},
        {'url': f'/mili/blog/{a["slug"]}', 'title': a['title'], 'date': a['date'], 'site': 'mili'},
    ]
    add = [e for e in add if not any(x.get('url') == e['url'] for x in aj)]
    if idx is not None:
        aj[idx + 1:idx + 1] = add
    else:
        aj.append({'url': base_url, 'title': a['title'], 'date': a['date'], 'site': 'najie'})
        aj.extend(add)
json.dump(aj, open(f'{REPO}/articles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('articles.json updated')

# ---------- 6. site-inbox 交接文件归档 ----------
inbox_file = f'{REPO}/site-inbox/20260907-copyright-15plan-opportunities-v2-生命力润色版_cms.html'
if os.path.exists(inbox_file):
    dst = f'{REPO}/site-inbox/archive/20260907-copyright-15plan-opportunities-v2-生命力润色版_cms.html'
    shutil.move(inbox_file, dst)
    print('archived:', inbox_file.split('/')[-1])
print('ALL DONE')
