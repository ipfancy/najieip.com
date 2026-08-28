#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-28: 保险咨询会活动稿 + 出海IP保险工具箱 补上线
articles/ 旧路径 -> 跳转页; 生成 blog/ + mili/blog/ + najie/blog/ 精修版; 更新索引 + sitemap + articles.json
"""
import json, re, os, sys

BASE = os.path.expanduser("~/wiki/najieip-verify")

# ============ 文章1: 保险咨询会活动稿 (觅理) ============
INS_SRC = os.path.join(BASE, "articles/20260911-mili-insurance-consultation.html")
INS_MILI = os.path.join(BASE, "mili/blog/20260911-mili-insurance-consultation.html")
INS_TITLE = "保险买对，家才安心：退税、医疗、储蓄，9月11日一次理清"
INS_DESC = ("9月11日，觅理律所「理享会」联合中国人寿举办家庭保障·保险咨询会。用\\u201c律师+理财师\\u201d双视角讲透三件事："
            "个人养老金每年12000元税前扣除怎么省；《保险法》第16条健康告知\\u201c问什么答什么\\u201d、两年不可抗辩期；"
            "《保险法》第42条指定受益人定向传承vs《民法典》第1136条打印遗嘱要件。保险的\\u201c坑\\u201d大多不在产品，而在法律。")
INS_KEYWORDS = "保险咨询会,个人养老金,税优,健康告知,不可抗辩期,遗嘱,觅理律所"
INS_URL = "https://najieip.com/mili/blog/20260911-mili-insurance-consultation.html"
INS_DATE = "2026-08-28"
INS_IMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"

# ============ 文章2: 出海IP保险工具箱 (纳杰 + 主博客) ============
TK_SRC = os.path.join(BASE, "articles/overseas-ip-insurance-toolkit-20260828.html")
TK_BLOG = os.path.join(BASE, "blog/overseas-ip-insurance-toolkit-20260828.html")
TK_NAJIE = os.path.join(BASE, "najie/blog/overseas-ip-insurance-toolkit-20260828.html")
TK_TITLE = "出海IP\\u201c三大新武器\\u201d：2026下半年到2027年，企业维权成本要重算"
TK_DESC = ("瑞幸泰国案只记赢了9500万泰铢不够——50R反诉索赔100亿泰铢才是警钟。2027年1月1日起新《商标法》第69条"
           "官方\\u201c驰名确认\\u201d通道开放；四部门科技保险通知+浙江统保+深圳联共体+国务院令837号；"
           "出海IP维权从\\u201c自己扛\\u201d升级为\\u201c国家+保险+服务体系\\u201d三层保护。附今天就能做的三件事。")
TK_KEYWORDS = "驰名确认,海外IP保险,统保,商标法69条,出海维权,知识产权保险,科技保险"
TK_URL = "https://najieip.com/blog/overseas-ip-insurance-toolkit-20260828.html"
TK_NAJIE_URL = "https://najieip.com/najie/blog/overseas-ip-insurance-toolkit-20260828.html"
TK_DATE = "2026-08-28"
TK_IMG = "https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200"


def json_ld_article(url, site_name, title, desc, date):
    return ('''<script type="application/ld+json">\n{"@context": "https://schema.org", "@type": "Article", '''
            f'''"headline": "{title}", "description": "{desc}", "author": {{"@type": "Person", "name": "何自刚"}}, '''
            f'''"publisher": {{"@type": "Organization", "name": "{site_name}"}}, "datePublished": "{date}", '''
            f'''"dateModified": "{date}", "mainEntityOfPage": "{url}", "url": "{url}"}}\n</script>''')


def json_ld_breadcrumb(title, blog_url, blog_name):
    return ('''<script type="application/ld+json">\n{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['''
            '''{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}, '''
            f'''{{"@type": "ListItem", "position": 2, "name": "{blog_name}", "item": "{blog_url}"}}, '''
            f'''{{"@type": "ListItem", "position": 3, "name": "{title}"}}]}}\n</script>''')


def build_head(url, site_name, title, desc, keywords, date, img, blog_url, blog_name):
    beacon = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
              "data-cf-beacon='{\\\"token\\\": \\\"c80241f3caa4e708a12ed93baec1bde\\\"}'></script>")
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
{beacon}
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{site_name}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="canonical" href="{url}">
{json_ld_article(url, site_name, title, desc, date)}
{json_ld_breadcrumb(title, blog_url, blog_name)}
</head>
'''


def fix_strong(body):
    """markdown **bold** -> <strong>bold</strong> (不触碰已存在的 <strong>)"""
    def repl(m):
        return '<strong>' + m.group(1) + '</strong>'
    return re.sub(r'\*\*(.+?)\*\*', repl, body, flags=re.S)


def fix_table(body):
    """markdown 表格 <p>| a | b |</p> -> HTML table"""
    table_re = re.compile(
        r'(<p>\|[^<]*\|</p>\s*)+', re.S)
    def table_replace(m):
        block = m.group(0)
        rows = re.findall(r'<p>\|([^<]*)\|</p>', block)
        data = []
        for r in rows:
            cells = [c.strip() for c in r.split('|')]
            if all(re.fullmatch(r'-{1,}', c) for c in cells):
                continue
            data.append(cells)
        if len(data) < 2:
            return block
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
    return table_re.sub(table_replace, body)


def fix_blockquote(body):
    """&gt; 引用 -> blockquote"""
    def repl(m):
        inner = m.group(1).strip()
        inner = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', inner)
        return f'<blockquote>{inner}</blockquote>'
    body = re.sub(r'<p>&gt;\s*(.+?)</p>', repl, body, flags=re.S)
    return body


def fix_em(body):
    """*斜体* -> <em>斜体</em>"""
    return re.sub(r'\*(.+?)\*', r'<em>\1</em>', body)


def fix_hr(body):
    """单独 --- -> <hr>"""
    return re.sub(r'<p>---</p>', '<hr>', body)


def fix_body(body):
    body = fix_strong(body)
    body = fix_blockquote(body)
    body = fix_table(body)
    body = fix_hr(body)
    body = fix_em(body)
    return body


def extract_article(path):
    raw = open(path, encoding='utf-8').read()
    m = re.search(r'<article>(.*?)</article>', raw, re.S)
    if not m:
        # 无 article 标签的纯正文（微信导出风格）
        m2 = re.search(r'<body>(.*?)</body>', raw, re.S)
        if m2:
            return m2.group(1)
        print(f"ERROR: no <article> in {path}"); sys.exit(1)
    return m.group(1)


FOOTER = '''<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 & 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
'''


def write_redirect(src, canon_url, title):
    redirect = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta http-equiv="refresh" content="0; url={canon_url}">
<link rel="canonical" href="{canon_url}">
</head>
<body>
<p>本文由纳杰觅理发布，跳转中… <a href="{canon_url}">点击直达</a></p>
</body>
</html>
'''
    open(src, 'w', encoding='utf-8').write(redirect)
    print("REDIRECT:", src)


def insert_card(idx_path, card, marker):
    html = open(idx_path, encoding='utf-8').read()
    if marker in html:
        print(f"SKIP {idx_path} (already has {marker})")
        return
    html = html.replace('<div class="container">\n', '<div class="container">\n' + card, 1)
    open(idx_path, 'w', encoding='utf-8').write(html)
    print("CARD ->", idx_path)


def upsert_sitemap(entries):
    sm = os.path.join(BASE, "sitemap.xml")
    sxml = open(sm, encoding='utf-8').read()
    added = 0
    for loc, date in entries:
        if loc in sxml:
            print("SKIP sitemap", loc)
            continue
        entry = f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
'''
        sxml = sxml.replace('</urlset>', entry + '</urlset>')
        added += 1
    if added:
        open(sm, 'w', encoding='utf-8').write(sxml)
        print("SITEMAP +%d URLs" % added)


def upsert_articles_json(entries):
    aj = os.path.join(BASE, "articles.json")
    data = json.load(open(aj, encoding='utf-8'))
    changed = 0
    for e in entries:
        exists = any(a.get('url') == e['url'] for a in data)
        if not exists:
            data.insert(0, e)
            changed += 1
            print("ARTICLES.JSON +", e['url'])
        else:
            print("SKIP articles.json", e['url'])
    if changed:
        json.dump(data, open(aj, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def main():
    # ===== 文章1: 保险咨询会 -> mili/blog =====
    ins_article = extract_article(INS_SRC)
    ins_article = fix_body(ins_article)
    ins_html = (build_head(INS_URL, "觅理律所", INS_TITLE, INS_DESC, INS_KEYWORDS, INS_DATE, INS_IMG,
                           "https://najieip.com/mili/blog/", "觅理博客")
                + '<body>\n<nav><a href="/mili/">← 觅理律所</a></nav>\n<article>' + ins_article + '</article>\n' + FOOTER)
    open(INS_MILI, 'w', encoding='utf-8').write(ins_html)
    print("WROTE:", INS_MILI, len(ins_html), "bytes")

    # ===== 文章2: 出海IP工具箱 -> blog + najie/blog =====
    tk_article = extract_article(TK_SRC)
    tk_article = fix_body(tk_article)
    tk_blog_html = (build_head(TK_URL, "爱普纳杰专利所", TK_TITLE, TK_DESC, TK_KEYWORDS, TK_DATE, TK_IMG,
                               "https://najieip.com/blog/", "爱普纳杰博客")
                    + '<body>\n<nav><a href="/">← 首页</a></nav>\n<article>' + tk_article + '</article>\n' + FOOTER)
    open(TK_BLOG, 'w', encoding='utf-8').write(tk_blog_html)
    print("WROTE:", TK_BLOG, len(tk_blog_html), "bytes")
    tk_najie_html = (build_head(TK_NAJIE_URL, "纳杰知识产权", TK_TITLE, TK_DESC, TK_KEYWORDS, TK_DATE, TK_IMG,
                                "https://najieip.com/najie/blog/", "纳杰博客")
                     + '<body>\n<nav><a href="/najie/">← 纳杰知识产权</a></nav>\n<article>' + tk_article + '</article>\n' + FOOTER)
    open(TK_NAJIE, 'w', encoding='utf-8').write(tk_najie_html)
    print("WROTE:", TK_NAJIE, len(tk_najie_html), "bytes")

    # ===== articles/ 旧路径 -> 跳转页 =====
    write_redirect(INS_SRC, INS_URL, INS_TITLE)
    write_redirect(TK_SRC, TK_URL, TK_TITLE)

    # ===== 索引卡片 =====
    ins_card = f'''  <div class="article-card">
    <h2><a href="./20260911-mili-insurance-consultation.html">{INS_TITLE}</a></h2>
    <div class="meta"><span class="tag">保险</span><span class="tag">税务</span><span class="tag">活动</span> {INS_DATE} · 觅理律师事务所</div>
    <p>9月11日，觅理律所「理享会」联合中国人寿办家庭保障·保险咨询会。个税优惠×父母医疗×储蓄传承，律师+理财师双视角。健康告知怎么填、受益人怎么指定、打印遗嘱为什么容易无效——保险的坑大多不在产品，而在法律。</p>
  </div>

'''
    insert_card(os.path.join(BASE, "mili/blog/index.html"), ins_card, "20260911-mili-insurance-consultation")

    tk_card = f'''  <div class="article-card">
    <h2><a href="/blog/overseas-ip-insurance-toolkit-20260828.html">{TK_TITLE}</a></h2>
    <div class="meta"><span class="tag">海外IP</span><span class="tag">驰名确认</span><span class="tag">保险</span> {TK_DATE} · 纳杰知识产权</div>
    <p>瑞幸泰国案赢9500万泰铢，反诉却是100亿泰铢。2027年1月1日起新《商标法》第69条官方\\u201c驰名确认\\u201d通道开放；四部门科技保险通知+浙江统保+深圳联共体+国务院令837号。出海IP维权从\\u201c自己扛\\u201d升级为三层保护，附今天就能做的三件事。</p>
  </div>

'''
    insert_card(os.path.join(BASE, "blog/index.html"), tk_card, "overseas-ip-insurance-toolkit")
    tk_najie_card = f'''  <div class="article-card">
    <h2><a href="./overseas-ip-insurance-toolkit-20260828.html">{TK_TITLE}</a></h2>
    <div class="meta"><span class="tag">海外IP</span><span class="tag">驰名确认</span><span class="tag">保险</span> {TK_DATE} · 纳杰知识产权</div>
    <p>瑞幸泰国案赢9500万泰铢，反诉却是100亿泰铢。2027年1月1日起新《商标法》第69条官方\\u201c驰名确认\\u201d通道开放；四部门科技保险通知+浙江统保+深圳联共体+国务院令837号。出海IP维权从\\u201c自己扛\\u201d升级为三层保护，附今天就能做的三件事。</p>
  </div>

'''
    insert_card(os.path.join(BASE, "najie/blog/index.html"), tk_najie_card, "overseas-ip-insurance-toolkit")

    # ===== sitemap =====
    upsert_sitemap([
        (INS_URL, INS_DATE),
        (TK_URL, TK_DATE),
        (TK_NAJIE_URL, TK_DATE),
    ])

    # ===== articles.json =====
    upsert_articles_json([
        {"url": "/mili/blog/20260911-mili-insurance-consultation.html", "title": INS_TITLE, "date": INS_DATE, "site": "mili"},
        {"url": "/blog/overseas-ip-insurance-toolkit-20260828.html", "title": TK_TITLE, "date": TK_DATE, "site": "najie"},
        {"url": "/najie/blog/overseas-ip-insurance-toolkit-20260828.html", "title": TK_TITLE, "date": TK_DATE, "site": "najie"},
    ])

    print("DONE")


if __name__ == '__main__':
    main()
