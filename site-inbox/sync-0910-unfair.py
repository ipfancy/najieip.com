#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""索引/站点地图/文章清单 同步：mili/blog 新文章 20260910-unfair-competition-nine-red-lines.html
   - mili/blog/index.html : 顶部卡片 + JSON-LD blogPost 追加
   - sitemap.xml          : 增量插入 mili/blog URL
   - articles.json        : /articles/ → /mili/blog/，site najie → mili
"""
import json, re, io

REPO = '/mnt/c/Users/zigan/najieip-site'
SLUG = '20260910-unfair-competition-nine-red-lines.html'
TITLE = '最高法连发9案：AI写点评也违法，你公司踩了几条红线？'
CANON = 'https://najieip.com/mili/blog/' + SLUG
DATE = '2026-09-10'
CARD_DESC = ('最高法9月9日连发9件反不正当竞争典型案例：AI批量生成数万篇“XX软件怎么样”测评文被判不正当竞争——'
             '“AI技术中立”不再是挡箭牌；技术秘密案4458万基数上叠加2倍惩罚性赔偿，蹭“六福”字号、拿《狂飙》剧名卖酒一律重罚。'
             '九案三条线＋企业今天就能做的三件事。')
JSONLD_DESC = ('最高法2026年9月9日发布9件反不正当竞争典型案例：AI批量生成数万篇测评文被判不正当竞争，技术中立不免责；'
               '技术秘密案4458万基数叠加2倍惩罚性赔偿。附九案三条线与合规动作清单。觅理律师事务所出品。')

# ── 1. mili/blog/index.html ──
p = REPO + '/mili/blog/index.html'
h = open(p, encoding='utf-8').read()

anchor = '<div class="container">\n  <div class="article-card">'
assert h.count(anchor) == 1, 'container/anchor count=%d' % h.count(anchor)
card = ('<div class="container">\n'
        '  <div class="article-card">\n'
        '    <h2><a href="./%s">%s</a></h2>\n'
        '    <div class="meta"><span class="tag">反不正当竞争</span><span class="tag">AI合规</span><span class="tag">内容营销</span> %s · 觅理律师事务所</div>\n'
        '    <p>%s</p>\n'
        '  </div>\n') % (SLUG, TITLE, DATE, CARD_DESC)
h = h.replace(anchor, card.rstrip('\n'), 1)

ja = '"blogPost": ['
assert h.count(ja) == 1, 'blogPost anchor count=%d' % h.count(ja)
obj = {"@type": "BlogPosting", "headline": TITLE, "url": CANON, "datePublished": DATE,
       "description": JSONLD_DESC}
h = h.replace(ja, ja + json.dumps(obj, ensure_ascii=False) + ',', 1)
open(p, 'w', encoding='utf-8').write(h)

# ── 2. sitemap.xml ──
p = REPO + '/sitemap.xml'
s = open(p, encoding='utf-8').read()
assert CANON not in s, 'sitemap 已含该 URL'
ins = ('  <url>\n'
       '    <loc>%s</loc>\n'
       '    <lastmod>%s</lastmod>\n'
       '    <changefreq>monthly</changefreq>\n'
       '    <priority>0.8</priority>\n'
       '  </url>\n') % (CANON, DATE)
marker = '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
assert s.count(marker) == 1
s = s.replace(marker, marker + ins, 1)
open(p, 'w', encoding='utf-8').write(s)

# ── 3. articles.json ──
p = REPO + '/articles.json'
arr = json.load(open(p, encoding='utf-8'))
hit = 0
for a in arr:
    if a.get('url') == '/articles/' + SLUG:
        a['url'] = '/mili/blog/' + SLUG
        a['site'] = 'mili'
        hit += 1
assert hit == 1, 'articles.json 命中 %d 条' % hit
open(p, 'w', encoding='utf-8').write(json.dumps(arr, ensure_ascii=False, indent=2) + '\n')

print('index.html: card + jsonld inserted')
print('sitemap.xml: +1 url')
print('articles.json: url/site updated (%d entries total)' % len(arr))
