#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ART-2026-0081 精修归位: /articles/ 原始版(含markdown表格) → blog + mili/blog 精修版
   复刻 gen-0908-siteops.py / c7748bb(ART-0080) 模式: JSON-LD/OG补全, markdown表格→HTML表格,
   **→strong, 去公众号CTA/带货注释/重复签名, /articles/ 后续改跳转页(由归位后手动替换)"""
import re, html

RAW = '/Users/ziganghe/wiki/najieip-verify/articles/20260909-ai-image-copyright-four-cases.html'
TITLE = 'AI生图算不算作品？4个法院2胜2负，输赢只差一件事'
SLUG = '20260909-ai-image-copyright-four-cases.html'
DATE = '2026-09-09'
DESC = ('同一个问题：AI画的图算不算作品。过去三年，四个法院给出了两胜两负的答案——春风案、武汉案认构成作品，'
        '丰某案、崔某案一键生图被驳，连《作品登记证书》都没能翻盘。输赢只差一件事：人的独创性智力投入有没有留痕。'
        '拆四个案子＋苏州中院裁判原则，附五条现在就能做的留痕动作。')
KEYWORDS = 'AI生图,著作权,独创性,AI版权,作品登记,春风案'
OG_DESC = ('AI生图算不算作品？四个法院两胜两负：赢的靠人的投入和留痕，输的连《作品登记证书》都救不了。'
           '著作权法只认“人的独创性智力投入”，附五条留痕动作。')

raw = open(RAW, encoding='utf-8').read()
m = re.search(r'<article>(.*?)</article>', raw, re.S)
body = m.group(1)
body = re.sub(r'<br\s*/?>', '', body)

lines = [l.strip() for l in body.splitlines()]
out = []
i = 0
while i < len(lines):
    l = lines[i]
    if not l:
        i += 1
        continue
    if l.startswith('<h2>'):
        out.append(l)
        i += 1
        continue
    if not (l.startswith('<p>') and l.endswith('</p>')):
        i += 1
        continue
    inner = l[3:-4]
    # markdown 表格行分组（连续以 | 开头的 <p>）
    if inner.startswith('|'):
        rows = []
        while i < len(lines):
            li = lines[i]
            if li.startswith('<p>') and li.endswith('</p>') and li[3:-4].strip().startswith('|'):
                rows.append(li[3:-4].strip())
                i += 1
            else:
                break
        data = [r for r in rows if not re.match(r'^\|[\s:|\-]+\|$', r)]
        header = [c.strip() for c in data[0].strip('|').split('|')]
        out.append('<table>\n<thead>\n<tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in header) + '</tr>\n</thead>\n<tbody>')
        for r in data[1:]:
            cells = [c.strip() for c in r.strip('|').split('|')]
            out.append('<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in cells) + '</tr>')
        out.append('</tbody>\n</table>')
        continue
    i += 1
    # 带货位注释
    if '&lt;!--' in inner:
        continue
    # 引用块 &gt;
    if inner.startswith('&gt;'):
        q = inner[4:].strip()
        q = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', q)
        q = q.replace('爱普纳杰·觅理·纳杰', '爱普纳杰 · 觅理 · 纳杰')
        out.append('<blockquote><p>' + q + '</p></blockquote>')
        continue
    if inner == '---':
        continue
    if inner.startswith('*本文仅代表'):   # 模板footer自带免责声明，去重
        continue
    if inner.startswith('下一篇聊'):      # 公众号 CTA
        continue
    if inner.startswith('何自刚 | 知识产权律师'):  # 模板footer自带署名
        continue
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', inner)
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

# 质量断言
for name, h in (('blog', blog_html), ('mili', mili_html)):
    assert 'https://schema.org' in h, name + ': schema.org missing!'
    assert '***' not in h, name + ': *** leak!'
    assert '**' not in h, name + ': 残留 ** markdown 加粗'
    assert '<br' not in h, name + ': 残留 <br>'
    body_clean = h.split('<article>')[1].split('</article>')[0]
    assert '<p>|' not in body_clean and '|:--' not in body_clean, name + ': 残留 markdown 表格行'
    assert '&lt;!--' not in body_clean, name + ': 残留注释'
    assert '留言区聊聊' not in h and '下一篇聊' not in h, name + ': 公众号 CTA 未清'
    n_table = body_clean.count('<table>')
    print(name, 'OK — 表格数:', n_table, '| blockquote:', body_clean.count('<blockquote>'))
