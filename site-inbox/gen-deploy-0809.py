#!/usr/bin/env python3
"""SiteOps 2026-08-09 部署：ART-2026-0041 (AI员工成本→主博客+najie) + ART-2026-0042 (AI责任链→主博客+mili)
清理 markdown 残留 + 补 SEO 头 + 更新索引/sitemap/articles.json"""
import re, json, pathlib, datetime

home = pathlib.Path.home()
base = home / "wiki/najieip-verify"
TODAY = "2026-08-09"

# ---------- 通用清理 ----------
def clean_body(body: str) -> str:
    # 去掉模板自带的 <br> 空行（保留段落结构）
    body = re.sub(r"<br>\s*", "", body)
    # markdown 表格 -> HTML table（责任链自查表）
    def tbl(text):
        rows = []
        for l in re.findall(r"<p>([^<]*)</p>", text):
            l = l.strip()
            if l.startswith("|"):
                rows.append([c.strip() for c in l.strip("|").split("|")])
        # 去掉分隔行 |---|
        rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
        if not rows:
            return ""
        thead = rows[0]
        tbody = rows[1:]
        h = "".join(f"<th>{c}</th>" for c in thead)
        b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in tbody)
        return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"
    # 先移除 <br>（表格行粘连为连续 <p>|...|</p>）
    body = re.sub(r"<br>\s*", "", body)
    body = re.sub(r"(?:<p>\|[^<]*?</p>\s*)+", lambda m: tbl(m.group(0)), body)
    # 块引用 &gt; -> blockquote
    body = re.sub(r"<p>&gt;\s*(.*?)</p>", lambda m: f"<blockquote><p>{m.group(1)}</p></blockquote>", body)
    # **bold** -> <strong> （先处理粗体，避免被斜体规则吃掉）
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    # *italic* -> <em> （安全规则：非**开头、无嵌套星号）
    body = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", body)
    # 裸 --- 分隔线
    body = re.sub(r"<p>-{3,}</p>", "", body)
    # 去掉正文中重复的 h1（模板会输出一次）
    body = re.sub(r"^\s*<h1>.*?</h1>\s*", "", body, flags=re.S)
    # 压缩连续空行
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

# ================= ART-2026-0041: AI员工 vs 人类员工 =================
j1 = {
    "src": base / "articles/20260809-ai-vs-employee-综合对比.html",
    "title": "AI员工 vs 人类员工：一场算不清账的战争？——经济学/管理学/税收财务/心理学/哲学五维对比，给创业者和传统老板的最终答案",
    "desc": "AI员工 vs 人类员工：一场算不清账的战争？从经济学、管理学、税收财务、心理学、哲学五个维度彻底算透AI原生与人力用工的真实成本，给创业者和传统老板一套按阶段切换的组合打法——不是二选一，是分阶段切换。",
    "keywords": "AI员工,数字员工,AI原生,用工成本,一人公司,降本增效,AI创业,人力资源,何自刚",
    "pub_date": TODAY,
    "slug": "20260809-ai-vs-employee",
    "dest": ["blog", "najie/blog"],
    "brand": "najie",
}
# ================= ART-2026-0042: AI数字员工责任链 =================
j2 = {
    "src": base / "site-inbox/ai-agent-liability-chain-20260809.html",
    "title": "AI数字员工闯祸谁赔？从\"养龙虾\"暴雷到首案裁判，企业必看的责任链清单",
    "desc": "AI数字员工闯祸谁赔？从OpenClaw\"养龙虾\"暴雷到杭州AI幻觉首案、广州双重授权裁定，拆解部署前、运行中、出事后三层责任链，附10项企业AI智能体部署合规自查表。",
    "keywords": "AI智能体,数字员工,侵权责任,双重授权,民法典,AI合规,责任链,智能体规范",
    "pub_date": TODAY,
    "slug": "ai-agent-liability-chain-20260809",
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
        print(f"OK {out.relative_to(base)} | {len(page)}B | **残留:{page.count('**')}")

print("\n--- 文件写入完成 ---")
for w in written:
    print(" ", w[0])
