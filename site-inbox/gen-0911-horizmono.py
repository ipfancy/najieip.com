#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-11 发布: 觅理 blog × 1篇
《"联营整合、共同定价"，怎么就成了垄断协议？——四家检测公司的教训》
执行包: /mnt/i/内省II耳目手足爪牙/文件存放/市场部/发布执行包_20260910/
派单: TASK-SITE-PUBLISH-1ART-HORIZMONO-20260910（扬声）| 如己质量关通过 2026-09-10 14:49
模板复刻 gen-0910-mili.py；本次加幂等保护（卡片/JSON-LD/sitemap/articles.json 已存在则跳过）
"""
import re, json, os
import html as html_mod

REPO = '/mnt/c/Users/zigan/najieip-site'
PKG = '/mnt/i/内省II耳目手足爪牙/文件存放/市场部/发布执行包_20260910'

A = {
    'raw': f'{PKG}/20260910-horizontal-monopoly-agreement.html',
    'slug': '20260910-horizontal-monopoly-agreement.html',
    'title': '"联营整合、共同定价"，怎么就成了垄断协议？——四家检测公司的教训',
    'date': '2026-09-11',
    'desc': ('最高法2026反垄断典型案例解读：四家机动车检测公司签"整合联营协议"，被认定构成横向垄断协议——'
             '协议整体无效、主张分配垄断利益的请求不予支持、违法线索还被移送市场监管部门。附企业与行业协会自查清单。'),
    'og_desc': '最高法2026反垄断典型案例：四家检测公司签"整合联营协议"，被判构成横向垄断协议。协议无效、分成拿不到、线索移送执法部门——小企业同样会踩线。',
    'keywords': '横向垄断协议,联营协议,反垄断法第十七条,最高法典型案例,企业合规',
    'tags': ['反垄断', '企业合规', '最高法典型案例'],
}

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


def extract_body(raw_path):
    t = open(raw_path, encoding='utf-8').read()
    m = re.search(r'<article>(.*?)</article>', t, re.S)
    assert m, f'no <article> in {raw_path}'
    inner = m.group(1)
    inner = re.sub(r'<h1>.*?</h1>', '', inner, flags=re.S)
    inner = re.sub(r'<br\s*/?>', '', inner)
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
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h2.strip())
            blocks.append(f'<h2>{c}</h2>')
        elif li:
            ul_buf.append(re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', li.strip()))
        else:
            flush_ul()
            c = p.strip()
            if not c or c == '---':
                continue
            if c.startswith('>'):
                blocks.append(f'<blockquote><p><strong>{c.lstrip(">").strip().replace("**", "")}</strong></p></blockquote>')
                continue
            if c.startswith('*本文') or c.startswith('关注公众号') or c.startswith('座机：'):
                continue
            c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
            c = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', c)
            blocks.append(f'<p>{c}</p>')
    flush_ul()
    return '\n'.join(blocks)


def main():
    slug = A['slug']
    canonical = f'https://najieip.com/mili/blog/{slug}'

    # ---- 1) 渲染正文 ----
    body = extract_body(A['raw'])
    assert '**' not in body, 'markdown ** remnant'
    assert '<strong>' in body and '<ul>' in body, 'render check failed'
    out = HEAD_TPL.format(
        title=A['title'], desc=ATTR(A['desc']), keywords=A['keywords'], og_desc=ATTR(A['og_desc']),
        canonical=canonical, site='觅理律师事务所', blog_index='https://najieip.com/mili/blog/',
        date=A['date'], body=body,
        title_json=json.dumps(A['title'], ensure_ascii=False),
        desc_json=json.dumps(A['desc'], ensure_ascii=False),
        canonical_json=json.dumps(canonical, ensure_ascii=False),
    )
    assert '<h1>' + A['title'] + '</h1>' in out
    open(f'{REPO}/mili/blog/{slug}', 'w', encoding='utf-8').write(out)
    print(f'✅ 写入 mili/blog/{slug} ({len(out)}B)')

    # ---- 2) mili/blog/index.html：卡片 + JSON-LD（幂等）----
    p = f'{REPO}/mili/blog/index.html'
    idx = open(p, encoding='utf-8').read()
    tags = ''.join(f'<span class="tag">{t}</span>' for t in A['tags'])
    card = (f'  <div class="article-card">\n'
            f'    <h2><a href="./{slug}">{A["title"]}</a></h2>\n'
            f'    <div class="meta">{tags} {A["date"]} · 觅理律师事务所</div>\n'
            f'    <p>{A["desc"]}</p>\n'
            f'  </div>\n')
    if f'./{slug}' in idx:
        print('⏭  index 卡片已存在，跳过')
    else:
        anchor = '<div class="container">\n'
        assert idx.count(anchor) == 1, 'index container anchor missing'
        idx = idx.replace(anchor, anchor + card, 1)
        print('✅ index.html 插入卡片')

    post = json.dumps({'@type': 'BlogPosting', 'headline': A['title'], 'url': canonical,
                       'datePublished': A['date'], 'description': A['desc'] + '觅理律师事务所出品。'},
                      ensure_ascii=False)
    if slug in idx.split('"blogPost": [')[-1].split('</script>')[0]:
        print('⏭  index JSON-LD 已存在，跳过')
    else:
        anchor3 = '"blogPost": ['
        assert idx.count(anchor3) == 1, 'blogPost anchor missing'
        idx = idx.replace(anchor3, anchor3 + post + ',', 1)
        print('✅ index.html 插入 JSON-LD BlogPosting')
    open(p, 'w', encoding='utf-8').write(idx)

    # ---- 3) sitemap.xml（幂等）----
    sp = f'{REPO}/sitemap.xml'
    sm = open(sp, encoding='utf-8').read()
    if f'mili/blog/{slug}' in sm:
        print('⏭  sitemap 已存在，跳过')
    else:
        anchor4 = 'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        assert sm.count(anchor4) == 1, 'sitemap anchor missing'
        sm = sm.replace(anchor4, anchor4 + f'''  <url>
    <loc>{canonical}</loc>
    <lastmod>{A['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
''', 1)
        open(sp, 'w', encoding='utf-8').write(sm)
        print('✅ sitemap.xml +1 url')

    # ---- 4) articles.json（幂等）----
    ap = f'{REPO}/articles.json'
    aj = json.load(open(ap, encoding='utf-8'))
    assert isinstance(aj, list)
    url = f'/mili/blog/{slug}'
    if any(x.get('url') == url for x in aj):
        print('⏭  articles.json 已存在，跳过')
    else:
        aj.append({'url': url, 'title': A['title'], 'date': A['date'], 'site': 'mili'})
        json.dump(aj, open(ap, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'✅ articles.json +1（{len(aj)} 条）')

    print('ALL DONE')


if __name__ == '__main__':
    main()
