#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-27: ART-2026-0068 503面馆商标案 补上线
articles/ 旧路径 -> 跳转页; 生成 blog/ + mili/blog/ 精修版; 更新双索引 + sitemap + articles.json
"""
import json, re, shutil, sys, os

BASE = os.path.expanduser("~/wiki/najieip-verify")
SRC = os.path.join(BASE, "articles/trademark-enforcement-3-gates-20260827.html")
BLOG = os.path.join(BASE, "blog/trademark-enforcement-3-gates-20260827.html")
MILI = os.path.join(BASE, "mili/blog/trademark-enforcement-3-gates-20260827.html")

TITLE = "503家门店告一家面馆，最后把商标白送：维权前先过3关"
DESC = ("上市公司503家门店起诉夫妻面馆索赔七八千，四天后公开道歉还白送商标——2026年6月\u201c遇见小面\u201d维权翻车案。"
        "商标维权先过三关：能不能告看权利（稳定性、使用证据、混淆可能性）、该不该告看体量（侵权分级评估表）、"
        "怎么告看舆情（先礼后兵、诉求排序、叙事锚定、留痕、舆情先于法律）。新商标法从\u201c重注册\u201d转向\u201c重使用\u201d，"
        "第81条恶意诉讼反噬风险必须留痕。")
KEYWORDS = "商标维权,商标法修订,恶意诉讼,遇见小面,商标侵权,商标抢注"
CANON_SLUG = "https://najieip.com/blog/trademark-enforcement-3-gates-20260827.html"
MILI_URL = "https://najieip.com/mili/blog/trademark-enforcement-3-gates-20260827.html"
DATE = "2026-08-27"
IMG = "https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200"

def json_ld_article(url, site_name):
    return ('''<script type="application/ld+json">\n{"@context": "https://schema.org", "@type": "Article", '''
            f'''"headline": "{TITLE}", "description": "{DESC}", "author": {{"@type": "Person", "name": "何自刚"}}, '''
            f'''"publisher": {{"@type": "Organization", "name": "{site_name}"}}, "datePublished": "{DATE}", '''
            f'''"dateModified": "{DATE}", "mainEntityOfPage": "{url}", "url": "{url}"}}\n</script>''')

def json_ld_breadcrumb():
    return ('''<script type="application/ld+json">\n{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['''
            '''{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}, '''
            '''{"@type": "ListItem", "position": 2, "name": "博客", "item": "https://najieip.com/blog/"}, '''
            f'''{{"@type": "ListItem", "position": 3, "name": "{TITLE}"}}]}}\n</script>''')

def build_head(url, site_name):
    beacon = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
              "data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>")
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
{beacon}
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KEYWORDS}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{site_name}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<link rel="canonical" href="{url}">
{json_ld_article(url, site_name)}
{json_ld_breadcrumb()}
</head>
'''

def fix_body(body):
    """精修正文: markdown 表格 -> HTML table, &gt; 引用 -> blockquote, *斜体* -> em"""
    # 表格
    table_re = re.compile(
        r'<p>\| 评估指标 \| 恶意攀附（值得告） \| 无意撞名（慎告） \|</p>\s*'
        r'<p>\| --- \| --- \| --- \|</p>\s*'
        r'(<p>\|[^<]+\|</p>\s*)+', re.S)
    def table_replace(m):
        rows = re.findall(r'<p>\|([^<]+)\|</p>', m.group(0))
        data = []
        for r in rows:
            cells = [c.strip() for c in r.split('|')]
            if all(re.fullmatch(r'-{1,}', c) for c in cells):
                continue  # 分隔行 | --- | --- |
            data.append(cells)
        html = '<table>\n<thead><tr>'
        for c in data[0]:
            html += f'<th>{c}</th>'
        html += '</tr></thead>\n<tbody>\n'
        for r in data[1:]:
            html += '<tr>'
            for c in r:
                html += f'<td>{c}</td>'
            html += '</tr>\n'
        html += '</tbody>\n</table>\n'
        return html
    body = table_re.sub(table_replace, body)
    # blockquote
    body = re.sub(
        r'<p>&gt; ("商标维权[^<]+") —— 何自刚 \| 知识产权律师 \| 爱普纳杰 · 觅理 · 纳杰</p>',
        r'<blockquote>\1 —— 何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰</blockquote>',
        body)
    # 结尾斜体免责声明
    body = body.replace(
        '<p>*本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎关注公众号「纳杰觅理」留言。*</p>',
        '<p><em>本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎关注公众号「纳杰觅理」留言。</em></p>')
    return body

def main():
    raw = open(SRC, encoding='utf-8').read()
    # 正文: <article> 到 </article>
    m = re.search(r'<article>(.*?)</article>', raw, re.S)
    if not m:
        print("ERROR: no <article> in source"); sys.exit(1)
    article = m.group(1)
    article = fix_body(article)

    footer = '''<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 & 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
'''

    blog_html = build_head(CANON_SLUG, "爱普纳杰专利所") + '<body>\n<nav><a href="/">← 首页</a></nav>\n<article>' + article + '</article>\n' + footer
    mili_html = build_head(MILI_URL, "觅理律所") + '<body>\n<nav><a href="/mili/">← 觅理律所</a></nav>\n<article>' + article + '</article>\n' + footer

    open(BLOG, 'w', encoding='utf-8').write(blog_html)
    open(MILI, 'w', encoding='utf-8').write(mili_html)
    print("WROTE:", BLOG, len(blog_html), "bytes")
    print("WROTE:", MILI, len(mili_html), "bytes")

    # 1. articles/ 旧路径 -> 跳转页
    redirect = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{TITLE}</title>
<meta http-equiv="refresh" content="0; url={CANON_SLUG}">
<link rel="canonical" href="{CANON_SLUG}">
</head>
<body>
<p>本文由纳杰觅理发布，跳转中… <a href="{CANON_SLUG}">点击直达</a></p>
</body>
</html>
'''
    open(SRC, 'w', encoding='utf-8').write(redirect)
    print("REDIRECT:", SRC)

    # 2. blog/index.html 插入卡片(container 后第一位)
    card = f'''  <div class="article-card">
    <h2><a href="/blog/trademark-enforcement-3-gates-20260827.html">{TITLE}</a></h2>
    <div class="meta"><span class="tag">商标维权</span><span class="tag">商标法修订</span><span class="tag">恶意诉讼</span> {DATE} · 纳杰知识产权</div>
    <p>上市公司503家门店起诉夫妻面馆索赔七八千，四天后道歉还白送商标——2026年6月\u201c遇见小面\u201d维权翻车案。维权前先过三关：能不能告看权利（稳定性/使用证据/混淆可能），该不该告看体量（侵权分级评估表），怎么告看舆情（先礼后兵/诉求排序/叙事锚定/留痕）。</p>
  </div>

'''
    idx = os.path.join(BASE, "blog/index.html")
    html = open(idx, encoding='utf-8').read()
    if 'trademark-enforcement-3-gates' not in html:
        html = html.replace('<div class="container">\n', '<div class="container">\n' + card, 1)
        open(idx, 'w', encoding='utf-8').write(html)
        print("CARD -> blog/index.html")
    else:
        print("SKIP blog/index.html (already has card)")

    # 3. mili/blog/index.html 插入卡片
    mili_card = f'''  <div class="article-card">
    <h2><a href="./trademark-enforcement-3-gates-20260827.html">{TITLE}</a></h2>
    <div class="meta"><span class="tag">商标维权</span><span class="tag">商标法修订</span><span class="tag">恶意诉讼</span> {DATE} · 觅理律师事务所</div>
    <p>上市公司503家门店起诉夫妻面馆索赔七八千，四天后道歉还白送商标——2026年6月\u201c遇见小面\u201d维权翻车案。维权前先过三关：能不能告看权利（稳定性/使用证据/混淆可能），该不该告看体量（侵权分级评估表），怎么告看舆情（先礼后兵/诉求排序/叙事锚定/留痕）。</p>
  </div>

'''
    midx = os.path.join(BASE, "mili/blog/index.html")
    mhtml = open(midx, encoding='utf-8').read()
    if 'trademark-enforcement-3-gates' not in mhtml:
        mhtml = mhtml.replace('<div class="container">\n', '<div class="container">\n' + mili_card, 1)
        open(midx, 'w', encoding='utf-8').write(mhtml)
        print("CARD -> mili/blog/index.html")
    else:
        print("SKIP mili/blog/index.html (already has card)")

    # 4. sitemap.xml 插入两条
    sm = os.path.join(BASE, "sitemap.xml")
    sxml = open(sm, encoding='utf-8').read()
    entry_blog = f'''  <url>
    <loc>{CANON_SLUG}</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
'''
    entry_mili = f'''  <url>
    <loc>{MILI_URL}</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
'''
    if 'trademark-enforcement-3-gates' not in sxml:
        sxml = sxml.replace('</urlset>', entry_blog + entry_mili + '</urlset>')
        open(sm, 'w', encoding='utf-8').write(sxml)
        print("SITEMAP +2 URLs")
    else:
        print("SKIP sitemap (already has entry)")

    # 5. articles.json 顶部插入 mili 精修版
    aj = os.path.join(BASE, "articles.json")
    data = json.load(open(aj, encoding='utf-8'))
    if not any(a.get('url', '').startswith('/mili/blog/trademark-enforcement') for a in data):
        data.insert(0, {
            "url": "/mili/blog/trademark-enforcement-3-gates-20260827.html",
            "title": TITLE,
            "description": DESC,
            "date": DATE,
            "site": "mili"
        })
        json.dump(data, open(aj, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print("ARTICLES.JSON +1 (mili version)")
    else:
        print("SKIP articles.json (already has mili entry)")

    print("DONE")

if __name__ == '__main__':
    main()
