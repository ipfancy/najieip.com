#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-22 内容同步: 社保×2 + 美国TRO×1 精修上线"""
import re, json, html, os

BASE = '/Users/ziganghe/wiki/najieip-verify'

ARTICLES = [
    {
        "slug": "20260821-beijing-shebao-2026",
        "inbox": "20260821-beijing-shebao-2026.html",
        "title": "北京社保基数涨了：下限7270元，企业多掏多少？",
        "date": "2026-08-22",
        "desc": "2026年7月起北京社保缴费基数调整：上限36348元/月、下限7270元/月。三档算账（单位月缴1941.09~9704.92元）、工伤保险行业差别费率（0.4% vs 1.9%差1308.6元/年）、公积金同步调、员工到手变化、企业申报五步实操清单。",
        "keywords": "北京社保基数,社保缴费基数,五险一金,社保调整,用工成本,社保申报",
        "tags": ["社保", "劳动用工", "社保基数"],
        "card": "2026年7月起北京社保缴费基数调整：上限36348元、下限7270元。三档算账拆解单位每人每月1941.09元的真实成本，工伤行业费率差、公积金同步调、员工到手变化，附企业申报五步实操清单。",
    },
    {
        "slug": "20260821-beijing-shebao-tax",
        "inbox": "20260821-beijing-shebao-tax.html",
        "title": "社保基数涨了，企业反而能少缴税？7月补差这笔账怎么算",
        "date": "2026-08-22",
        "desc": "社保基数上调，多缴的社保费是企业所得税与个税的税前扣除项——100人企业一年约省8600元企业所得税。7月补差明细（单位28.83元/人/月）、滞纳金年化18.25%、未申报按110%核定、金税四期三条比对线、三数对齐自查清单。",
        "keywords": "社保税前扣除,企业所得税,个税专项扣除,社保补差,金税四期,社保滞纳金",
        "tags": ["社保", "税务", "劳动用工"],
        "card": "多缴的社保费是企业所得税与个税的税前扣除项——100人企业一年约省8600元企业所得税。7月补差明细、滞纳金年化18.25%与110%核定风险、金税四期三条比对线、三数对齐自查清单。",
    },
    {
        "slug": "20260822-us-tro-72hour-checklist",
        "inbox": "20260822-us-tro-72hour-checklist.html",
        "title": "货款被美国法院冻结，72小时做对这5件事",
        "date": "2026-08-22",
        "desc": "2026年25天210件TRO案、1674家中国店铺被冻结。第七巡回法院Yinnv Liu案后管辖抗辩窗口打开，《海牙送达公约》禁止电邮送达。72小时五件事清单：停售/留证据/找律师，和解30%-60% vs 应诉 vs 弃店对比表。",
        "keywords": "TRO,临时限制令,跨境电商,美国法院冻结,海牙送达公约,知识产权诉讼",
        "tags": ["TRO", "跨境电商", "涉外维权"],
        "card": "2026年25天210件TRO案、1674家中国店铺被冻结。第七巡回法院新判例撕开管辖权抗辩窗口，《海牙送达公约》禁止电邮送达。72小时五件事清单+和解/应诉/弃店对比。",
    },
]

def extract_article(inbox_path):
    """从 site-inbox 原始 HTML 提取 <article> 内容, 转精修 HTML"""
    with open(inbox_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    m = re.search(r'<article>(.*?)</article>', raw, re.S)
    if not m:
        raise RuntimeError(f"no <article> in {inbox_path}")
    body = m.group(1)
    body = re.sub(r'<h1>.*?</h1>\s*<br>\s*', '', body, flags=re.S)  # 原文h1移除(模板统一生成)

    # --- markdown 表格块 → <table> ---
    def table_repl(mt):
        rows = []
        for line in mt.group(0).split('\n'):
            line = line.strip().replace('<p>', '').replace('</p>', '').strip()
            if not line:
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cells and all(re.match(r'^:?-{2,}:?$', c) for c in cells):
                continue  # 分隔行
            rows.append(cells)
        if not rows:
            return ''
        thead = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in rows[0]) + '</tr></thead>'
        tbody = '<tbody>' + ''.join(
            '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows[1:]
        ) + '</tbody>'
        return f'<table>{thead}{tbody}</table>'

    # 合并连续的 <p>| ... |</p> 表格行
    body = re.sub(r'(?:<p>\|[^\n]*?</p>\n?)+', lambda mt: table_repl(mt) + '\n<br>\n', body)
    body = re.sub(r'<p>\|.*?</p>', lambda mt: table_repl(mt) + '\n<br>\n', body)

    # --- blockquote: <p>&gt; ...</p> ---
    def bq_repl(mt):
        inner = mt.group(1)
        inner = re.sub(r'^&gt;\s*', '', inner)
        inner = inner.replace('**', '').replace('"', '\u201c', 1)
        return f'<blockquote>{inner}</blockquote>\n<br>\n'
    body = re.sub(r'<p>(&gt;.*?)</p>', bq_repl, body, flags=re.S)

    # --- 分隔线 ---
    body = re.sub(r'<p>---</p>', '<hr>', body)

    # --- **bold** → <strong> ---
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)

    # --- *italic* → <em> ---
    body = re.sub(r'\*(?!\*)([^*]+?)\*', r'<em>\1</em>', body)

    # --- 残留 markdown 清理 ---
    body = body.replace('**', '').replace('```', '')

    # --- <br> 规范化 ---
    body = re.sub(r'<br\s*/?>', '<br>', body)
    return body.strip()

def build_head(a, publisher, site_name, url, breadcrumb_name, breadcrumb_url):
    desc = html.escape(a['desc'], quote=True)
    title_esc = html.escape(a['title'], quote=True)
    ld_article = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a['title'],
        "description": a['desc'],
        "author": {"@type": "Person", "name": "何自刚"},
        "publisher": {"@type": "Organization", "name": publisher},
        "datePublished": a['date'],
        "dateModified": a['date'],
        "mainEntityOfPage": url,
        "url": url,
    }, ensure_ascii=False)
    ld_bread = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": breadcrumb_name, "item": breadcrumb_url},
            {"@type": "ListItem", "position": 3, "name": a['title']},
        ]
    }, ensure_ascii=False)
    return f'''<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{a['title']} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<meta name="description" content="{desc}">
<meta name="keywords" content="{a['keywords']}">
<meta property="og:title" content="{title_esc}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{site_name}">
<meta property="og:image" content="https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_esc}">
<meta name="twitter:description" content="{desc}">
<link rel="canonical" href="{url}">
<script type="application/ld+json">
{ld_article}
</script>
<script type="application/ld+json">
{ld_bread}
</script>
</head>'''

def build_article_html(a, publisher, site_name, url, breadcrumb_name, breadcrumb_url, nav_href):
    body = extract_article(os.path.join(BASE, 'site-inbox', a['inbox']))
    head = build_head(a, publisher, site_name, url, breadcrumb_name, breadcrumb_url)
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
{head}
<body>
<nav><a href="{nav_href}">← 首页</a></nav>
<article>
<h1>{a['title']}</h1>
{body}
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 & 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>'''

def build_stub(a):
    url = f"https://najieip.com/blog/{a['slug']}.html"
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{a['title']}</title>
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
</head>
<body>
<p>本文由纳杰觅理发布，跳转中… <a href="{url}">点击直达</a></p>
</body>
</html>'''

def card_html(a):
    tags = ''.join(f'<span class="tag">{t}</span>' for t in a['tags'])
    return f'''  <div class="article-card">
    <h2><a href="./{a['slug']}.html">{a['title']}</a></h2>
    <div class="meta">{tags} {a['date']} · 纳杰知识产权</div>
    <p>{a['card']}</p>
  </div>'''

def card_html_main(a):
    tags = ''.join(f'<span class="tag">{t}</span>' for t in a['tags'])
    return f'''  <div class="article-card">
    <h2><a href="/blog/{a['slug']}.html">{a['title']}</a></h2>
    <div class="meta">{tags} {a['date']} · 纳杰知识产权</div>
    <p>{a['card']}</p>
  </div>'''

def main():
    written = []
    for a in ARTICLES:
        # 1) blog/ 主版本
        blog_path = os.path.join(BASE, 'blog', f"{a['slug']}.html")
        content = build_article_html(
            a, '爱普纳杰专利所', '爱普纳杰专利所',
            f"https://najieip.com/blog/{a['slug']}.html",
            '博客', 'https://najieip.com/blog/', '/')
        with open(blog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        written.append(blog_path)

        # 2) najie/blog/ 品牌版本
        najie_path = os.path.join(BASE, 'najie', 'blog', f"{a['slug']}.html")
        content_n = build_article_html(
            a, '纳杰知识产权', '纳杰知识产权',
            f"https://najieip.com/najie/blog/{a['slug']}.html",
            '纳杰博客', 'https://najieip.com/najie/blog/', '/najie/')
        with open(najie_path, 'w', encoding='utf-8') as f:
            f.write(content_n)
        written.append(najie_path)

        # 3) articles/ 跳转 stub → blog/ (铁律: 旧路径改跳转页)
        stub_path = os.path.join(BASE, 'articles', f"{a['slug']}.html")
        with open(stub_path, 'w', encoding='utf-8') as f:
            f.write(build_stub(a))
        written.append(stub_path)

        print(f"OK {a['slug']}")

    # 4) blog/index.html 卡片插入
    idx_path = os.path.join(BASE, 'blog', 'index.html')
    with open(idx_path, encoding='utf-8') as f:
        idx = f.read()
    cards = '\n\n'.join(card_html_main(a) for a in ARTICLES)
    marker = '<div class="container">'
    if marker in idx:
        # 防止重复插入
        if all(f"/blog/{a['slug']}.html" in idx for a in ARTICLES):
            print("blog/index.html 已含全部卡片, 跳过")
        else:
            insert_at = idx.index(marker) + len(marker)
            idx = idx[:insert_at] + '\n\n' + cards + '\n' + idx[insert_at:]
            with open(idx_path, 'w', encoding='utf-8') as f:
                f.write(idx)
            print("blog/index.html +3 卡片")
    else:
        print("!! blog/index.html 找不到 container 标记")

    # 5) najie/blog/index.html 卡片插入
    nidx_path = os.path.join(BASE, 'najie', 'blog', 'index.html')
    with open(nidx_path, encoding='utf-8') as f:
        nidx = f.read()
    if all(f"./{a['slug']}.html" in nidx for a in ARTICLES):
        print("najie/blog/index.html 已含全部卡片, 跳过")
    else:
        # 插到第一个 article-card 前
        m = re.search(r'<div class="article-card">', nidx)
        if m:
            cards_n = '\n\n'.join(card_html(a) for a in ARTICLES)
            nidx = nidx[:m.start()] + cards_n + '\n\n' + nidx[m.start():]
            with open(nidx_path, 'w', encoding='utf-8') as f:
                f.write(nidx)
            print("najie/blog/index.html +3 卡片")
        else:
            print("!! najie/blog/index.html 找不到 article-card 标记")

    # 6) sitemap.xml +6 URL
    sm_path = os.path.join(BASE, 'sitemap.xml')
    with open(sm_path, encoding='utf-8') as f:
        sm = f.read()
    new_urls = []
    for a in ARTICLES:
        for prefix in ('blog', 'najie/blog'):
            new_urls.append(f'''  <url>
    <loc>https://najieip.com/{prefix}/{a['slug']}.html</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')
    block = '\n'.join(new_urls)
    if all(f"{a['slug']}.html" in sm for a in ARTICLES):
        print("sitemap 已含全部条目, 跳过")
    else:
        sm = sm.replace('</urlset>', block + '\n</urlset>')
        with open(sm_path, 'w', encoding='utf-8') as f:
            f.write(sm)
        print("sitemap.xml +6 URL")

    # 7) articles.json 路径 /articles/ → /blog/
    aj_path = os.path.join(BASE, 'articles.json')
    with open(aj_path, encoding='utf-8') as f:
        aj = json.load(f)
    arts = aj if isinstance(aj, list) else aj.get('articles', aj)
    changed = 0
    for item in arts:
        u = item.get('url', '')
        for a in ARTICLES:
            if a['slug'] in u and u.startswith('/articles/'):
                item['url'] = f"/blog/{a['slug']}.html"
                changed += 1
    with open(aj_path, 'w', encoding='utf-8') as f:
        json.dump(aj, f, ensure_ascii=False, indent=2)
    print(f"articles.json 路径更新 {changed} 条")

    print(f"\n写入文件 {len(written)} 个")

if __name__ == '__main__':
    main()
