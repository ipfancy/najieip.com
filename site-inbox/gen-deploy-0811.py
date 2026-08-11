#!/usr/bin/env python3
"""SiteOps 2026-08-11 部署：
A) 20260810-xishuo-patent-invalid-huashan (专利无效华山论剑 → 主博客)
B) 20260811-ai-copyright-cn-us-overseas (中美AI版权出海 → 主博客 + mili)
清理 markdown 残留 + 补 SEO 头 + 更新索引/sitemap/articles.json"""
import re, json, pathlib

home = pathlib.Path.home()
base = home / "wiki/najieip-verify"
TODAY = "2026-08-11"

# ---------- 通用清理（同 0809 模式） ----------
def clean_body(body: str) -> str:
    body = re.sub(r"<br>\s*", "", body)

    def tbl(text):
        rows = []
        for l in re.findall(r"<p>([^<]*)</p>", text):
            l = l.strip()
            if l.startswith("|"):
                rows.append([c.strip() for c in l.strip("|").split("|")])
        rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
        if not rows:
            return ""
        thead = rows[0]
        tbody = rows[1:]
        h = "".join(f"<th>{c}</th>" for c in thead)
        b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in tbody)
        return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"

    body = re.sub(r"<br>\s*", "", body)
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

# ================= A: 专利无效华山论剑 =================
j1 = {
    "src": base / "site-inbox/20260810-xishuo-patent-invalid-huashan.html",
    "title": "专利无效攻防：一场没有硝烟的「华山论剑」",
    "desc": "专利无效宣告是知识产权界最刺激的\"约架\"——请求人三把刀：新颖性、创造性、公开不充分；专利权人只有一个月应战。为什么无效掉一个好专利比申请一个好专利还难？戏说IP系列用「华山论剑」拆解无效攻防全流程，附专利质量三问自检。",
    "keywords": "专利无效,无效宣告,新颖性,创造性,专利复审,专利质量,专利法,戏说IP",
    "pub_date": "2026-08-10",
    "slug": "20260810-xishuo-patent-invalid-huashan",
    "dest": ["blog"],
    "brand": "apnajie",
}
# ================= B: 中美AI版权出海 =================
j2 = {
    "src": base / "site-inbox/20260811-AI版权中美路径企业出海实操.html",
    "title": "中美AI版权\"冰火两重天\"：你的AI生成内容，出海怎么办？",
    "desc": "2026年3月2日，美国最高法院拒审Thaler案——纯AI生成在美国不受版权保护；同一天，中国法院认定AI图片可构成作品。幻之翼案输20万 vs 春风案赢500元，区别只有四个字：创作留痕。拆解中美两国\"冰火两重天\"的政策路径，附6个出海实操动作清单。",
    "keywords": "AI版权,AI生成内容,著作权,Thaler案,幻之翼案,春风案,出海合规,创作留痕",
    "pub_date": "2026-08-11",
    "slug": "20260811-ai-copyright-cn-us-overseas",
    "dest": ["blog", "mili/blog"],
    "brand": "mili",
}

jobs = [j1, j2]
style_map = {"blog": "/style.css", "najie/blog": "/style.css", "mili/blog": "/mili/style.css"}
home_map = {"blog": "/", "najie/blog": "/najie/", "mili/blog": "/mili/"}

written = []
for j in jobs:
    body = clean_body(extract_body(j["src"]))
    for section in j["dest"]:
        page = build_page(j["title"], j["desc"], j["keywords"], j["pub_date"],
                          j["slug"], body, section, home_map[section], style_map[section])
        out = base / section / f"{j['slug']}.html"
        out.write_text(page)
        written.append((str(out), len(page)))
        print(f"OK {out.relative_to(base)} | {len(page)}B | bold残留:{page.count('**')}")

print("\n--- 文件写入完成 ---")
for w in written:
    print(" ", w[0])
