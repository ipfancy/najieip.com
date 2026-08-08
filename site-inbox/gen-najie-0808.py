#!/usr/bin/env python3
"""生成 08-08 两篇 najie 文章精修版 — 清理markdown残留 + SEO头"""
import re, pathlib

home = pathlib.Path.home()
base = home / "wiki/najieip-verify"

jobs = [
    {
        "src": "articles/trademark-law-countdown-20260808.html",
        "dst": "najie/blog/trademark-law-countdown-20260808.html",
        "title": "倒计时145天：新商标法生效前，企业必须完成的6件事",
        "desc": "新《商标法》2027年1月1日施行：闲置商标可被官方撤销、误导性宣传最高罚25万、防御商标布局可被任何人提无效。距生效仅145天，企业必须完成的6件事逐条拆解。",
        "keywords": "商标法,新商标法,商标撤销,防御商标,商标布局,2027,企业合规",
        "pub_date": "2026-08-08",
        "slug": "trademark-law-countdown-20260808",
    },
    {
        "src": "articles/20260804-ic-layout-design-regulations.html",
        "dst": "najie/blog/20260804-ic-layout-design-regulations.html",
        "title": "\"半导体\"从法条消失，10月15日起芯片IP新规生效",
        "desc": "《集成电路布图设计保护条例》25年来首次全面修订：54条、2026年10月15日施行，集成光子/量子芯片布图设计正式纳入保护。新条例要点与登记权利人风险提示。",
        "keywords": "集成电路,布图设计,芯片IP,集成电路布图设计保护条例,CNIPA,2026新规",
        "pub_date": "2026-08-08",
        "slug": "20260804-ic-layout-design-regulations",
    },
]

for j in jobs:
    src_html = (base / j["src"]).read_text()
    body = src_html.split("<article>")[1].split("</article>")[0]
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)
    # 去掉裸 --- 分隔线
    body = re.sub(r"<br>\n<p>---</p>", "", body)

    title, desc, keywords, pub_date, slug = j["title"], j["desc"], j["keywords"], j["pub_date"], j["slug"]
    url = f"https://najieip.com/najie/blog/{slug}.html"
    ld = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","author":{{"@type":"Person","name":"何自刚"}},"publisher":{{"@type":"Organization","name":"纳杰知识产权"}},"datePublished":"{pub_date}","dateModified":"{pub_date}","mainEntityOfPage":"{url}","url":"{url}"}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"首页","item":"https://najieip.com/"}},{{"@type":"ListItem","position":2,"name":"纳杰博客","item":"https://najieip.com/najie/blog/"}},{{"@type":"ListItem","position":3,"name":"{title}"}}]}}
</script>'''
    page = f'''<!DOCTYPE html>
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
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="纳杰知识产权">
<meta property="og:image" content="https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="canonical" href="{url}">
{ld}
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
<h1>{title}</h1>
{body}
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 & 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
'''
    out = base / j["dst"]
    out.write_text(page)
    print(f"OK {out} | {len(page)}B | **残留:{page.count('**')}")
