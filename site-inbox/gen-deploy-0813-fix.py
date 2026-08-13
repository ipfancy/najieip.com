#!/usr/bin/env python3
"""SiteOps 2026-08-13 修复部署:
A) 瑞幸清单 (出海商标6件事) → 主博客 blog/ + 纳杰 najie/blog/
B) 结构性卡位 (AI时代法律人护城河) → 主博客 blog/ + 觅理 mili/blog/
清理 markdown 残留 + 补 SEO 头 (OG/JSON-LD/canonical)
"""
import re, pathlib

home = pathlib.Path.home()
base = home / "wiki/najieip-verify"

def clean_body(body: str) -> str:
    body = re.sub(r"<br>\s*", "", body)
    # 表格转换
    def tbl(text):
        rows = []
        for l in re.findall(r"<p>([^<]*)</p>", text):
            l = l.strip()
            if l.startswith("|"):
                rows.append([c.strip() for c in l.strip("|").split("|")])
        rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
        if not rows:
            return ""
        thead, tbody = rows[0], rows[1:]
        h = "".join(f"<th>{c}</th>" for c in thead)
        b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in tbody)
        return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"
    body = re.sub(r"(?:<p>\|[^<]*?</p>\s*)+", lambda m: tbl(m.group(0)), body)
    body = re.sub(r"<p>&gt;\s*(.*?)</p>", lambda m: f"<blockquote><p>{m.group(1)}</p></blockquote>", body)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", body)
    body = re.sub(r"<p>-{3,}</p>", "", body)
    body = re.sub(r"^\s*<h1>.*?</h1>\s*", "", body, flags=re.S)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()

def build_page(title, desc, keywords, pub_date, slug, body, section, home_link, style_href):
    url = f"https://najieip.com/{section.rstrip('/')}/{slug}.html"
    ld = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","author":{{"@type":"Person","name":"何自刚"}},"publisher":{{"@type":"Organization","name":"纳杰知识产权"}},"datePublished":"{pub_date}","dateModified":"{pub_date}","mainEntityOfPage":"{url}","url":"{url}"}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"首页","item":"https://najieip.com/"}},{{"@type":"ListItem","position":2,"name":"博客","item":"https://najieip.com/{section.rstrip('/')}/"}},{{"@type":"ListItem","position":3,"name":"{title}"}}]}}
</script>'''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
<link rel="stylesheet" href="{style_href}">
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

def extract_body(path):
    html = path.read_text()
    return html.split("<article>")[1].split("</article>")[0]

# ================= A: 瑞幸清单 =================
j1 = {
    "src": base / "articles/20260813-luckin-thailand-trademark-checklist.html",
    "title": "瑞幸胜诉9500万泰铢，出海商标这6件事现在就该做",
    "desc": "瑞幸在泰国赢了——赔偿总额逾9500万泰铢，创泰国知识产权案件史上最高赔偿纪录。但这场官司打了5年、中间还败诉过一次。瑞幸案最大的价值不是坏人被惩罚，而是把商标布局滞后的真实成本一笔一笔算给你看：6件出海企业现在就该做的事。",
    "keywords": "瑞幸,泰国商标,商标抢注,出海商标,商标布局,涉外商标,海外IP",
    "pub_date": "2026-08-13",
    "slug": "20260813-luckin-thailand-trademark-checklist",
    "dest": ["blog", "najie/blog"],
}
# ================= B: 结构性卡位 =================
j2 = {
    "src": base / "articles/结构性卡位-AI时代法律人唯一的护城河-20260807.html",
    "title": "结构性卡位：AI时代法律人唯一的护城河",
    "desc": "护城河不是把你的能力做到极致——而是让极致的能力也无法绕过你。AI能写文章、能做检索、能出方案，但永远做不到在人类社会的法律架构中占据结构性的位置：出庭资格、律师见证、律师函签名、律师调解——这些不是AI做不到的事，而是AI没有资格做的事。",
    "keywords": "AI法律人,律师,结构性卡位,法律服务,AI替代,职业护城河",
    "pub_date": "2026-08-07",
    "slug": "结构性卡位-AI时代法律人唯一的护城河-20260807",
    "dest": ["blog", "mili/blog"],
}

jobs = [j1, j2]
style_map = {"blog": "/style.css", "najie/blog": "/style.css", "mili/blog": "/mili/style.css"}
home_map = {"blog": "/", "najie/blog": "/najie/", "mili/blog": "/mili/"}

for j in jobs:
    body = clean_body(extract_body(j["src"]))
    for section in j["dest"]:
        page = build_page(j["title"], j["desc"], j["keywords"], j["pub_date"],
                          j["slug"], body, section, home_map[section], style_map[section])
        out = base / section / f"{j['slug']}.html"
        out.write_text(page)
        schema = page.count("https://schema.org")
        print(f"OK {out.relative_to(base)} | {len(page)}B | bold残留:{page.count('**')} | schema.org:{schema}")
        assert schema >= 2, f"JSON-LD schema.org 缺失! {out}"
        assert page.count("https://***") == 0, f"JSON-LD 脱敏污染! {out}"

print("\n--- 部署完成 ---")
