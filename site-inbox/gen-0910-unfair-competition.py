#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归位: /articles/20260910-unfair-competition-nine-red-lines.html（何律 Mac 端直推 articles/，违反主体归属铁律）
   → mili/blog/20260910-unfair-competition-nine-red-lines.html（觅理：反不正当竞争/AI内容营销合规）
   复刻 gen-0909-ai-image.py / gen-0908-siteops.py 模式：JSON-LD/OG/canonical 补全，去 <br>、
   markdown 强调转 HTML、去公众号 CTA 与重复签名；/articles/ 原路径改跳转页。
   主体判定依据：反不正当竞争 + AI 合规 → 觅理；同批 9 案解读 20260909-aucl-livestream-ads.html 已在 mili/blog。
   （site_classifier.py 因 <title> 联合署名「— 纳杰觅理」误判 najie，属已知联合品牌假阳性）
"""
import re, html, os

REPO = '/mnt/c/Users/zigan/najieip-site'
RAW = os.path.join(REPO, 'articles/20260910-unfair-competition-nine-red-lines.html')
SLUG = '20260910-unfair-competition-nine-red-lines.html'
TITLE = '最高法连发9案：AI写点评也违法，你公司踩了几条红线？'
DATE = '2026-09-10'
DESC = ('最高法2026年9月9日发布9件反不正当竞争典型案例：AI批量生成数万篇“XX软件怎么样”测评文被判不正当竞争，'
        '“AI技术中立”不是免死金牌；技术秘密案在4458万基数上再叠加2倍惩罚性赔偿；企业字号蹭“六福”商标赔10万；'
        '《狂飙》剧名卖酒判500万。2025年全国法院审结不正当竞争一审案件10135件、505件适用惩罚性赔偿、判赔18亿元。'
        '附企业今天就能做的三件事。')
KEYWORDS = '反不正当竞争法,最高法典型案例,AI内容营销,技术中立,惩罚性赔偿,企业合规'
OG_DESC = ('最高法连发9件反不正当竞争典型案例：AI批量测评文被判“截流”、技术中立不再免责，技术秘密案4458万基数叠加2倍惩罚，'
           '蹭字号、蹭剧名照样重罚。九案三条线＋企业今天能做的三件事。')

raw = open(RAW, encoding='utf-8').read()
body = re.search(r'<article>(.*?)</article>', raw, re.S).group(1)
body = re.sub(r'<br\s*/?>', '', body)

lines = [l.strip() for l in body.splitlines()]
out = []
for l in lines:
    if not l:
        continue
    if l.startswith('<h1>') or l.startswith('<h2>') or l.startswith('<ul>') or l.startswith('<li>'):
        out.append(l)
        continue
    if not (l.startswith('<p>') and l.endswith('</p>')):
        continue
    inner = l[3:-4]
    if '&lt;!--' in inner:                      # 带货/注释残留
        continue
    if inner.startswith('关注公众号') or inner.startswith('公众号'):   # 公众号 CTA
        continue
    if inner.startswith('*本文仅代表'):          # 模板 footer 自带免责声明，去重
        continue
    if inner.startswith('何自刚 | 知识产权律师'):  # 模板 footer 自带署名
        continue
    if inner.startswith('>') or inner.startswith('&gt;'):
        continue
    if inner == '---':
        continue
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', inner)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    t = t.replace('爱普纳杰·觅理·纳杰', '爱普纳杰 · 觅理 · 纳杰')
    out.append('<p>' + t + '</p>')

BODY = '\n'.join(out)

HEAD_TPL = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KEYWORDS}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{CANONICAL}">
<meta property="og:site_name" content="觅理律师事务所">
<meta property="og:image" content="https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{OG_DESC}">
<link rel="canonical" href="{CANONICAL}">
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "Article", "headline": "{TITLE}", "description": "{DESC}", "author": {{"@type": "Person", "name": "何自刚"}}, "publisher": {{"@type": "Organization", "name": "觅理律师事务所"}}, "datePublished": "{DATE}", "dateModified": "{DATE}", "mainEntityOfPage": "{CANONICAL}", "url": "{CANONICAL}"}}
</script>
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}}, {{"@type": "ListItem", "position": 2, "name": "博客", "item": "https://najieip.com/mili/blog/"}}, {{"@type": "ListItem", "position": 3, "name": "{TITLE}"}}]}}
</script>
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
<h1>{TITLE}</h1>
{BODY}
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

CANONICAL = 'https://najieip.com/mili/blog/' + SLUG
mili_html = HEAD_TPL.format(TITLE=TITLE, DESC=DESC, KEYWORDS=KEYWORDS, OG_DESC=OG_DESC,
                            CANONICAL=CANONICAL, DATE=DATE, BODY=BODY)

REDIRECT = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="0; url=/mili/blog/{SLUG}">
<link rel="canonical" href="{CANONICAL}">
<title>{TITLE}</title>
</head>
<body>
<p>文章已迁移：<a href="/mili/blog/{SLUG}">{TITLE}</a></p>
</body>
</html>
'''.format(SLUG=SLUG, CANONICAL=CANONICAL, TITLE=TITLE)

open(os.path.join(REPO, 'mili/blog/' + SLUG), 'w', encoding='utf-8').write(mili_html)
open(RAW, 'w', encoding='utf-8').write(REDIRECT)

# 质量断言
h = mili_html
assert 'https://schema.org' in h and 'canonical' in h
assert '**' not in h, '残留 ** markdown 加粗'
assert '<br' not in h, '残留 <br>'
assert '关注公众号' not in h, '公众号 CTA 未清'
assert '&lt;!--' not in h, '注释残留'
b = h.split('<article>')[1].split('</article>')[0]
assert '<h1>' in b and '<h2>' in b
print('mili/blog/%s written: %d bytes' % (SLUG, len(mili_html)))
print('articles/%s → redirect: %d bytes' % (SLUG, len(REDIRECT)))
print('段落数:', b.count('<p>'), '| h2 数:', b.count('<h2>'))
