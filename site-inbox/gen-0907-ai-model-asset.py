#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ART-2026-0079 精修: site-inbox 公众号原文 → blog + mili 精修版"""
import re, html

RAW = '/Users/ziganghe/wiki/najieip-verify/site-inbox/20260907-ai-model-asset-three-track-decision.html'
TITLE = 'AI模型被抄，三条路怎么选：有人赢160万，有人输51亿'
SLUG = '20260907-ai-model-asset-three-track-decision.html'
DATE = '2026-09-07'
DESC = ('AI模型被同行抄了，走专利、商业秘密还是反不正当竞争？抖音走反法赢160万，小i机器人走专利51亿索赔落空，'
        'CTO带团队跳槽两个月做出同款产品改判赔50万。三轨决策树：专利要公开换排他、商业秘密要保密换长久、'
        '反法要投入换兜底——三问定轨＋组合打法，附立刻能做的三件事。')
KEYWORDS = 'AI模型,商业秘密,专利侵权,反不正当竞争,模型资产,抖音案,小i机器人,知识产权诉讼'
OG_DESC = ('AI模型被抄，专利、商业秘密、反不正当竞争三条路怎么选？抖音反法赢160万、小i专利51亿索赔落空、'
           '商业秘密改判赔50万——三轨决策树直接抄。')

raw = open(RAW, encoding='utf-8').read()
m = re.search(r'<article>(.*?)</article>', raw, re.S)
body = m.group(1)
body = re.sub(r'<br\s*/?>', '', body)
paras = re.findall(r'<p>(.*?)</p>', body, re.S)

def clean(t):
    t = t.strip()
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    return t

blocks = []
for p in paras:
    p = p.strip()
    if not p:
        continue
    if p.startswith('&lt;!--'):
        continue
    if p.startswith('&gt;'):
        q = clean(p[4:].strip())
        # 引用块 -> blockquote with 署名强调
        blocks.append('<blockquote><p><strong>' + q + '</strong></p></blockquote>')
        continue
    p = clean(p)
    # 免责声明 *...* -> em
    if p.startswith('*本文仅代表'):
        p = re.sub(r'^\*(.+?)\*$', r'<em>\1</em>', p)
    # 原文尾部作者行/免责段（模板统一追加，避免重复）
    if p == '何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰':
        continue
    if p.startswith('<em>本文仅代表'):
        continue
    blocks.append('<p>' + p + '</p>')

BODY = '\n'.join(blocks)
# 去掉开头纯衔接段前的空白控制, 保留原文顺序即可

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
<meta property="og:site_name" content="{SITE}">
<meta property="og:image" content="https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{OG_DESC}">
<link rel="canonical" href="{CANONICAL}">
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "Article", "headline": "{TITLE}", "description": "{DESC}", "author": {{"@type": "Person", "name": "何自刚"}}, "publisher": {{"@type": "Organization", "name": "{SITE}"}}, "datePublished": "{DATE}", "dateModified": "{DATE}", "mainEntityOfPage": "{CANONICAL}", "url": "{CANONICAL}"}}
</script>
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}}, {{"@type": "ListItem", "position": 2, "name": "博客", "item": "{BLOG_INDEX}"}}, {{"@type": "ListItem", "position": 3, "name": "{TITLE}"}}]}}
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

def render(canonical, site, blog_index):
    h = HEAD_TPL.format(TITLE=TITLE, DESC=DESC, KEYWORDS=KEYWORDS,
                        OG_DESC=OG_DESC, CANONICAL=canonical, SITE=site,
                        BLOG_INDEX=blog_index, DATE=DATE, BODY=BODY)
    return h

blog_html = render('https://najieip.com/blog/' + SLUG, '爱普纳杰专利所', 'https://najieip.com/blog/')
mili_html = render('https://najieip.com/mili/blog/' + SLUG, '觅理律师事务所', 'https://najieip.com/mili/blog/')

open('/Users/ziganghe/wiki/najieip-verify/blog/' + SLUG, 'w', encoding='utf-8').write(blog_html)
open('/Users/ziganghe/wiki/najieip-verify/mili/blog/' + SLUG, 'w', encoding='utf-8').write(mili_html)
print('blog written:', len(blog_html), 'bytes')
print('mili written:', len(mili_html), 'bytes')
# 校验 schema.org 未被脱敏
assert 'https://schema.org' in blog_html and 'https://schema.org' in mili_html, 'schema.org missing!'
assert '***' not in blog_html and '***' not in mili_html, '*** leak!'
print('schema.org OK, no *** leak')
