#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞/SiteOps 2026-09-12 主体归属纠偏
何律 Mac 端 commit a165a25 (07:21) 将《注册证不是挡箭牌！包装一句话，最高罚5倍》
直推 articles/20260912-trademark-certificate-not-shield.html（违反主体归属铁律：
articles/ 仅存历史跳转页，禁新增）→ 归位 najie/blog/（商标使用合规 → 纳杰）

处理：去 <br>/---/公众号CTA/带货位注释；markdown 表格转 HTML table；&gt; 转 blockquote；
     补 OG 五件套/ canonical / JSON-LD Article+Breadcrumb / 联系方式。
模板复刻 gen-0911-horizmono.py + commit d55681f（上一轮 09-11 归位）。
"""
import re, json
import html as html_mod

REPO = '/mnt/c/Users/zigan/najieip-site'
SLUG = '20260912-trademark-certificate-not-shield.html'
TITLE = '注册证不是挡箭牌！包装一句话，最高罚5倍'
DATE = '2026-09-12'
CANON = f'https://najieip.com/najie/blog/{SLUG}'
SITE = '纳杰知识产权'
BLOG_INDEX = 'https://najieip.com/najie/blog/'
OG_IMAGE = 'https://images.pexels.com/photos/48148/documents-accent-tear-48148.jpeg?auto=compress&cs=tinysrgb&w=1200'
DESC = ('新《商标法》2027年1月1日生效，监管重心从"注册"搬到"使用"：第56条之下，包装装潢、电商详情页、'
        '直播话术里加一句"手打""零添加""源自某地"，都可能被责令改正并处经营额5倍以下或25万以下罚款，'
        '逾期不改直接撤销注册商标。近三年127.3万件"心机商标"被驳回、3351件被官方依职权宣告无效。'
        '今麦郎主动注销10件 vs 壹号土猪复审抗辩，两条路怎么选；闲置商标清点四问＋今天就能做的三件事。')
OG_DESC = ('同一件注册商标，印在包装上合规、写进详情页可能被责令改正。新《商标法》第56条管的是"怎么用"：'
           '经营额100万，最高罚500万，逾期不改直接撤销。今麦郎断臂注销 vs 壹号土猪死撑复审，判断只有一条。')
KEYWORDS = '商标使用合规,新商标法第56条,心机商标,零添加禁用,撤销注册商标,闲置商标清理,商标撤三'
TAGS = ['商标使用合规', '新商标法第56条', '闲置商标清理']
CARD_DESC = ('新《商标法》第56条把监管重心从"注册"搬到"使用"：包装、详情页、直播话术里的一句话，'
             '最高罚经营额5倍或25万，逾期不改直接撤销商标。今麦郎主动注销10件 vs 壹号土猪复审抗辩——'
             '两条路怎么选，附闲置商标清点四问与今天就能做的三件事。')

REWRITE = {
    '<p>商标使用合规体检、僵尸商标台账代建、被举报后的陈述申辩和复审，纳杰和觅理一直在做。关注公众号「纳杰觅理」，评论区说说你手上有几个三年没用的商标。</p>':
        '<p>商标使用合规体检、僵尸商标台账代建、被举报后的陈述申辩和复审，纳杰和觅理一直在做。</p>',
}
DROP_PREFIX = ('<p>何自刚 | 知识产权律师', '<p>*本文仅代表作者个人观点', '<p><em>本文仅代表作者个人观点')
DROP_SUBSTR = ('&lt;!--', '带货位', '合集:')
CONTACT = '<p>座机：010-65150974 | 手机：15321374076 / 13911268604</p>'

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
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{site}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{og_desc}">
<link rel="canonical" href="{canon}">
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "Article", "headline": {title_json}, "description": {desc_json}, "author": {{"@type": "Person", "name": "何自刚"}}, "publisher": {{"@type": "Organization", "name": "{site}"}}, "datePublished": "{date}", "dateModified": "{date}", "mainEntityOfPage": {canon_json}, "url": {canon_json}}}
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
{contact}
<p><em>本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎联系我们。</em></p>
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
'''

STUB_TPL = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=/najie/blog/{slug}">
<link rel="canonical" href="https://najieip.com/najie/blog/{slug}">
<title>{title}</title>
</head>
<body>
<p>文章已迁移：<a href="/najie/blog/{slug}">{title}</a></p>
</body>
</html>
'''


def build_body(src_path):
    t = open(src_path, encoding='utf-8').read()
    inner = re.search(r'<article>(.*?)</article>', t, re.S).group(1)
    lines = [ln.strip() for ln in inner.split('\n')]
    blocks, tbl, dropped = [], [], []
    for ln in lines:
        if not ln or ln == '<br>' or ln.startswith('<h1>'):
            continue
        if any(s in ln for s in DROP_SUBSTR) or ln.startswith(DROP_PREFIX) or ln == '<p>---</p>':
            dropped.append(ln)
            continue
        if ln.startswith('<p>|') and ln.endswith('|</p>'):
            tbl.append(ln[3:-4])
            continue
        if tbl:
            blocks.append(render_table(tbl)); tbl = []
        if ln.startswith('<p>&gt;'):
            txt = ln[3:-4].replace('&gt;', '', 1).strip()
            blocks.append(f'<blockquote>{txt}</blockquote>')
            continue
        if ln in REWRITE:
            ln = REWRITE[ln]
        if ln.startswith('<h2>') or ln.startswith('<p>'):
            blocks.append(ln)
            continue
        raise SystemExit(f'未识别行: {ln[:80]}')
    if tbl:
        blocks.append(render_table(tbl))
    body = '\n'.join(blocks)
    assert '**' not in body and '<br>' not in body, 'markdown/<br> 残留'
    assert '<table>' in body and '<blockquote>' in body, '表格/引用转换失败'
    return body, dropped


def render_table(rows):
    cells = []
    for r in rows:
        parts = [c.strip() for c in r.strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in parts):
            continue
        cells.append(parts)
    head, rest = cells[0], cells[1:]
    th = ''.join(f'<th>{c}</th>' for c in head)
    tb = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rest)
    return f'<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>'


def main():
    src = f'{REPO}/articles/{SLUG}'
    body, dropped = build_body(src)
    out = HEAD_TPL.format(
        title=TITLE, desc=html_mod.escape(DESC), keywords=KEYWORDS, og_desc=html_mod.escape(OG_DESC),
        canon=CANON, site=SITE, blog_index=BLOG_INDEX, og_image=OG_IMAGE, date=DATE,
        body=body, contact=CONTACT,
        title_json=json.dumps(TITLE, ensure_ascii=False),
        desc_json=json.dumps(DESC, ensure_ascii=False),
        canon_json=json.dumps(CANON, ensure_ascii=False),
    )
    assert f'<h1>{TITLE}</h1>' in out
    open(f'{REPO}/najie/blog/{SLUG}', 'w', encoding='utf-8').write(out)
    print(f'✅ 写入 najie/blog/{SLUG} ({len(out)}B)；丢弃 {len(dropped)} 行（<br>/注释/分隔线已在解析层处理）')

    # ---- 2) articles/ 原路径 → 跳转页 ----
    open(src, 'w', encoding='utf-8').write(STUB_TPL.format(slug=SLUG, title=TITLE))
    print(f'✅ articles/{SLUG} → 跳转页')

    # ---- 3) najie/blog/index.html：卡片 + JSON-LD BlogPosting（幂等）----
    p = f'{REPO}/najie/blog/index.html'
    idx = open(p, encoding='utf-8').read()
    tags = ''.join(f'<span class="tag">{t}</span>' for t in TAGS)
    card = ('  <div class="article-card">\n'
            f'    <h2><a href="./{SLUG}">{TITLE}</a></h2>\n'
            f'    <div class="meta">{tags} {DATE} · 纳杰知识产权</div>\n'
            f'    <p>{CARD_DESC}</p>\n'
            '  </div>\n\n')
    if f'./{SLUG}' in idx:
        print('⏭  index 卡片已存在，跳过')
    else:
        anchor = '<div class="container">\n  <div class="article-card">'
        assert idx.count(anchor) == 1, 'index container anchor missing'
        idx = idx.replace(anchor, '<div class="container">\n' + card + '  <div class="article-card">', 1)
        print('✅ najie/blog/index.html 插入顶部卡片')

    post = json.dumps({'@type': 'BlogPosting', 'headline': TITLE, 'url': CANON,
                       'datePublished': DATE, 'description': DESC}, ensure_ascii=False)
    if f'/najie/blog/{SLUG}' in idx.split('"blogPost": [')[-1].split('</script>')[0]:
        print('⏭  index JSON-LD 已存在，跳过')
    else:
        a3 = '"blogPost": ['
        assert idx.count(a3) == 1, 'blogPost anchor missing'
        idx = idx.replace(a3, a3 + post + ',', 1)
        print('✅ najie/blog/index.html 插入 JSON-LD BlogPosting')
    open(p, 'w', encoding='utf-8').write(idx)

    # ---- 4) sitemap.xml（幂等）----
    sp = f'{REPO}/sitemap.xml'
    sm = open(sp, encoding='utf-8').read()
    n_before = sm.count('<url>')
    if f'najie/blog/{SLUG}' in sm:
        print('⏭  sitemap 已存在，跳过')
    else:
        a4 = 'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        assert sm.count(a4) == 1, 'sitemap anchor missing'
        sm = sm.replace(a4, a4 + f'''  <url>
    <loc>{CANON}</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
''', 1)
        open(sp, 'w', encoding='utf-8').write(sm)
        print(f'✅ sitemap.xml +1 url（{n_before} → {n_before + 1}）')

    # ---- 5) articles.json（幂等）----
    ap = f'{REPO}/articles.json'
    aj = json.load(open(ap, encoding='utf-8'))
    url = f'/najie/blog/{SLUG}'
    if any(x.get('url') == url for x in aj):
        print('⏭  articles.json 已存在，跳过')
    else:
        aj.insert(0, {'url': url, 'title': TITLE, 'date': DATE, 'site': 'najie'})
        json.dump(aj, open(ap, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'✅ articles.json 首位插入 /najie/blog 条目（{len(aj)} 条）')

    print('ALL DONE')


if __name__ == '__main__':
    main()
