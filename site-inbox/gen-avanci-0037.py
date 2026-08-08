#!/usr/bin/env python3
"""生成 ART-2026-0037 (Avanci 5G SEP) 精修版 HTML — 主博客 + mili 双收录"""
import re, pathlib

home = pathlib.Path.home()
src = home / "wiki/najieip-verify/articles/20260807-avanci-uk-chinese-automakers-sep.html"
html = src.read_text()

# 提取正文
body = html.split("<article>")[1].split("</article>")[0]
# **bold** -> <strong>
body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
# *italic* -> <em>
body = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)

title = "一辆车32美元，特斯拉打了三年官司——中国车企的5G专利攻守棋局"
desc = ("英国最高法院裁定专利池FRAND承诺不因集体许可而消失——全球首次专利池费率进入司法审查。"
        "拆解判决两面与中国车企的三层意义，附入池/谈判/反垄断决策清单。")
keywords = "SEP,FRAND,专利池,Avanci,5G,标准必要专利,车企出海,涉外诉讼,特斯拉,英国最高法院"
pub_date = "2026-08-07"

def make_page(canonical_url, og_url, ld_url, home_link):
    ld = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","author":{{"@type":"Person","name":"何自刚"}},"publisher":{{"@type":"Organization","name":"纳杰知识产权"}},"datePublished":"{pub_date}","dateModified":"{pub_date}","mainEntityOfPage":"{ld_url}","url":"{ld_url}"}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"首页","item":"https://najieip.com/"}},{{"@type":"ListItem","position":2,"name":"博客","item":"https://najieip.com/blog/"}},{{"@type":"ListItem","position":3,"name":"{title}"}}]}}
</script>'''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
<link rel="stylesheet" href="{home_link}style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{og_url}">
<meta property="og:site_name" content="纳杰知识产权">
<meta property="og:image" content="https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="canonical" href="{canonical_url}">
{ld}
</head>
<body>
<nav><a href="{home_link}">← 首页</a></nav>
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

# 主博客版本
blog_page = make_page(
    "https://najieip.com/blog/20260807-avanci-uk-chinese-automakers-sep.html",
    "https://najieip.com/blog/20260807-avanci-uk-chinese-automakers-sep.html",
    "https://najieip.com/blog/20260807-avanci-uk-chinese-automakers-sep.html",
    "/",
)
# mili 版本
mili_page = make_page(
    "https://najieip.com/mili/blog/20260807-avanci-uk-chinese-automakers-sep.html",
    "https://najieip.com/mili/blog/20260807-avanci-uk-chinese-automakers-sep.html",
    "https://najieip.com/mili/blog/20260807-avanci-uk-chinese-automakers-sep.html",
    "/mili/",
)

out1 = home / "wiki/najieip-verify/blog/20260807-avanci-uk-chinese-automakers-sep.html"
out2 = home / "wiki/najieip-verify/mili/blog/20260807-avanci-uk-chinese-automakers-sep.html"
out1.write_text(blog_page)
out2.write_text(mili_page)
print("主博客版:", out1, out1.exists(), len(blog_page))
print("mili版:", out2, out2.exists(), len(mili_page))
print("残留**:", blog_page.count("**"), "残留*:", blog_page.count("*"))
