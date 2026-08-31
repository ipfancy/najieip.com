#!/usr/bin/env python3
"""gen-trademark-0831.py — ART-2026-0073 商标"用或死"精修版生成
从 site-inbox 原始版 → 精修版 blog/ + najie/blog/ + articles/ 跳转页
"""
import re, os

SITE = os.path.expanduser("~/wiki/najieip-verify")
SRC = os.path.join(SITE, "site-inbox/trademark-law-use-or-die-countdown-20260831.html")

TITLE = "倒计时4个月！4987万件商标迎来\u201c用或死\u201d大限"
SLUG = "trademark-law-use-or-die-countdown-20260831"
DATE = "2026-08-31"
DESC = "截至2025年底中国有效注册商标4987.7万件。新《商标法》2027年1月1日施行：依职权主动撤销、误导宣传撤销注册、异议期3个月缩到2个月。留给企业只剩4个月——9月盘点库存、10月清理囤积建证据台账、11月搭异议监控、12月布局新机会，附中小企业四个月行动表。"
KEYWORDS = "商标法修订,用或死,商标撤三,商标撤销,4987万件,异议期,商标使用证据,2027商标法"
AUTHOR = "何自刚"

raw = open(SRC, encoding="utf-8").read()

# 提取正文 <article> 内部
body = raw.split("<article>", 1)[1].split("</article>", 1)[0]

def fix_md(text):
    """把原始版 markdown 残留转成 HTML"""
    # 表格（原始版表格行被包在 <p>|...</p> 中）
    pat = re.compile(r"(?:<p>\|[^<]*\|</p>\s*)+")
    def repl_table(m):
        rows = re.findall(r"<p>\|([^<]*)\|</p>", m.group(0))
        if len(rows) < 2:
            return m.group(0)
        cells = [r.split("|") for r in rows]
        # 去掉分隔行 |------|
        cells = [r for r in cells if not all(re.fullmatch(r"[\s:\-]+", c.strip() or "-") for c in r)]
        if not cells:
            return m.group(0)
        t = "<table><thead><tr>" + "".join(f"<th>{c.strip()}</th>" for c in cells[0]) + "</tr></thead><tbody>"
        for r in cells[1:]:
            t += "<tr>" + "".join(f"<td>{c.strip()}</td>" for c in r) + "</tr>"
        t += "</tbody></table>"
        return t
    text = pat.sub(repl_table, text)
    # 引用块（&gt; 开头）
    text = re.sub(r"<p>&gt;\s*(.+?)</p>", r"<blockquote>\1</blockquote>", text, flags=re.S)
    # **bold** → <strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # 单个 *italic* → <em>（仅在成对出现时）
    text = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", text)
    # 移除 markdown 分隔线
    text = re.sub(r"<p>---</p>", "", text)
    # 移除注释
    text = re.sub(r"&lt;!--.*?--&gt;", "", text, flags=re.S)
    text = re.sub(r"<p>.*?合集:.*?</p>", "", text)
    return text

body = fix_md(body)

def page(og_site_name, canonical_url, og_url, publisher, extra_ld=None):
    return f"""<!DOCTYPE html>
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
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{og_url}">
<meta property="og:site_name" content="{og_site_name}">
<meta property="og:image" content="https://images.pexels.com/photos/48148/documents-accent-tear-48148.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<link rel="canonical" href="{canonical_url}">
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "Article", "headline": "{TITLE}", "description": "{DESC}", "author": {{"@type": "Person", "name": "{AUTHOR}"}}, "publisher": {{"@type": "Organization", "name": "{publisher}"}}, "datePublished": "{DATE}", "dateModified": "{DATE}", "mainEntityOfPage": "{og_url}", "url": "{og_url}"}}
</script>
<script type="application/ld+json">
{{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}}, {{"@type": "ListItem", "position": 2, "name": "博客", "item": "https://najieip.com/blog/"}}, {{"@type": "ListItem", "position": 3, "name": "{TITLE}"}}]}}
</script>
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
{body}
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 & 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
"""

# 主博客版（canonical = /blog/）
main = page(
    og_site_name="爱普纳杰专利所",
    canonical_url=f"https://najieip.com/blog/{SLUG}.html",
    og_url=f"https://najieip.com/blog/{SLUG}.html",
    publisher="爱普纳杰专利所",
)
open(os.path.join(SITE, f"blog/{SLUG}.html"), "w", encoding="utf-8").write(main)

# najie 品牌版（canonical 指向主博客版，og:url 指 najie 路径 — 参照 overseas-ip-insurance-toolkit 模式）
najie = page(
    og_site_name="纳杰知识产权",
    canonical_url=f"https://najieip.com/blog/{SLUG}.html",
    og_url=f"https://najieip.com/najie/blog/{SLUG}.html",
    publisher="纳杰知识产权",
)
open(os.path.join(SITE, f"najie/blog/{SLUG}.html"), "w", encoding="utf-8").write(najie)

# articles/ 跳转页
redirect = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=/blog/{SLUG}.html">
<link rel="canonical" href="https://najieip.com/blog/{SLUG}.html">
<title>{TITLE}</title>
</head>
<body>
<p>文章已迁移：<a href="/blog/{SLUG}.html">{TITLE}</a></p>
</body>
</html>
"""
open(os.path.join(SITE, f"articles/{SLUG}.html"), "w", encoding="utf-8").write(redirect)

# 验证
for p in [f"blog/{SLUG}.html", f"najie/blog/{SLUG}.html", f"articles/{SLUG}.html"]:
    c = open(os.path.join(SITE, p), encoding="utf-8").read()
    print(p, "len:", len(c), "schema:", c.count("https://schema.org"), "**残留:", c.count("**"), "og:url:", c.count("og:url"), "canonical:", c.count("canonical"))
