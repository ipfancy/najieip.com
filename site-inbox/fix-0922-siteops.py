#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0922 重建裸发布畸形页 —— 从同日同品牌精修页取房屋模板，正文与 md 源 0 差异"""
import os, re, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles/20260922-us-trademark-sanction-three-step-selfcheck.md")
REF = os.path.join(REPO, "najie/blog/20260921-us-trademark-sanction-defense-window.html")
TARGET = os.path.join(REPO, "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html")
APPLY = "--apply" in sys.argv

SLUG = "20260922-us-trademark-sanction-three-step-selfcheck"
URL = "https://najieip.com/najie/blog/%s.html" % SLUG
TITLE = "美国商标'已注册'可能是假的！10月1日前5分钟三步自查"
DESC = ("USPTO 9 月 1 日合并令（In re Trademark Emergent, et al.）脚注 7 写明：注册被重开审理期间，"
        "系统因技术限制可能继续显示「已注册」，状态绿不等于安全。申辩截止 2026 年 10 月 1 日东部时间 23:59"
        "（北京时间 10 月 2 日 11:59），商标权人须走 Petition to Director 表单并附证据。本文给出五分钟三步自查清单："
        "查制裁名单、核代理资质、走对申辩渠道，并纠正中文信息里流传的「877 件」误传（Exhibit A 实为 436 件申请序列号）。")
KEYWORDS = "美国商标制裁,USPTO制裁名单,商标显示已注册,美国商标代理资质,Petition to Director"
OGIMG = "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200"
TAGS = ["美国商标制裁", "USPTO制裁名单", "商标显示已注册"]

def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

# ---------- 1. md 源正文段落 ----------
md = rd(MD)
md_body = md.split("---", 2)[2]
md_body = re.sub(r"<!--.*?-->", "", md_body, flags=re.S)          # 去评论/检索词块
md_paras = [p.strip() for p in md_body.split("\n\n") if p.strip()]
md_paras = [re.sub(r"^\*|\*$", "", p).strip() for p in md_paras]
md_paras = [p for p in md_paras if p and not p.startswith("---")]

# ---------- 2. 畸形页现有段落（正文源） ----------
old = rd(TARGET)
old_ps = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<p[^>]*>(.*?)</p>", old, re.S)]
old_ps = [re.sub(r"&#x27;", "'", p) for p in old_ps]
content = old_ps[:13]     # 0..12 = 正文 13 段
tail_old = old_ps[13:]

# ---------- 3. 断言：正文段落与 md 源 0 差异 ----------
print("=== 正文比对（畸形页 vs md 源） ===")
diff = 0
for i, (a, b) in enumerate(zip(content, md_paras[:len(content)])):
    a2 = a.replace("&amp;", "&")
    b2 = b.replace("&amp;", "&")
    if a2 != b2:
        diff += 1
        print("  [DIFF %d]\n    page: %s\n    md  : %s" % (i, a2[:100], b2[:100]))
print("  content paras:", len(content), " md paras:", len(md_paras), " DIFF:", diff)
extra_md = md_paras[len(content):]
print("  md 尾部未用的段:", extra_md)

# ---------- 4. 从参照页取房屋模板 ----------
ref = rd(REF)
css = re.search(r"<style>.*?</style>", ref, re.S).group(0)
nav = re.search(r"<nav>.*?</nav>", ref, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", ref, re.S).group(0)
beacon = re.search(r"<script defer src='https://static\.cloudflareinsights\.com[^>]*></script>", ref).group(0)
assert "schema.org" in ref
print("\n=== 房屋模板 ===")
print("  css %d B, nav %r, footer %d B, beacon %s" % (len(css), nav[:60], len(footer), bool(beacon)))

# ---------- 5. h2 路标（只补描述性路标，不引入新论点） ----------
H2 = {
    1: "一、反直觉的一句：绿字可能早就不是你的了",
    3: "二、截止时间：10 月 1 日东部时间 23:59",
    4: "三、三步自查清单，五分钟够",
    8: "四、877 还是 436：数字要打开原文核",
    9: "五、被点名的代理画像，与免费的维权网络",
    12: "六、今晚就可以做的一件事",
}

body_parts = []
for i, p in enumerate(content):
    if i in H2:
        body_parts.append("<h2>%s</h2>" % H2[i])
    body_parts.append("<p>%s</p>" % p)
body_html = "\n".join(body_parts)

# ---------- 6. 组装 ----------
ld_article = {
    "@context": "https://schema.org", "@type": "Article",
    "headline": TITLE, "description": DESC,
    "author": {"@type": "Person", "name": "何自刚"},
    "publisher": {"@type": "Organization", "name": "北京纳杰知识产权代理有限公司"},
    "image": OGIMG, "datePublished": "2026-09-22", "dateModified": "2026-09-22",
    "inLanguage": "zh-CN", "keywords": KEYWORDS,
    "mainEntityOfPage": URL, "url": URL,
}
ld_crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
    {"@type": "ListItem", "position": 2, "name": "博客", "item": "https://najieip.com/najie/blog/"},
    {"@type": "ListItem", "position": 3, "name": TITLE}]}

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
{css}
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="纳杰知识产权">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{ogimg}">
<link rel="canonical" href="{url}">
{beacon}
<script type="application/ld+json">
{ld1}
</script>
<script type="application/ld+json">
{ld2}
</script>
</head>
<body>
{nav}
<article>
<h1>{title}</h1>
<p class="byline">纳杰知识产权 &middot; 原创</p>
{body}
<hr>
<p>010-65150974 / 13911268604</p>
<p>何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰</p>
<p><em>本文仅代表作者个人观点，不构成法律意见。</em></p>
</article>
{footer}
</body>
</html>
""".replace("{title}", TITLE).replace("{css}", css).replace("{desc}", DESC).replace("{kw}", KEYWORDS) \
   .replace("{url}", URL).replace("{ogimg}", OGIMG).replace("{beacon}", beacon).replace("{nav}", nav) \
   .replace("{body}", body_html).replace("{footer}", footer) \
   .replace("{ld1}", json.dumps(ld_article, ensure_ascii=False)).replace("{ld2}", json.dumps(ld_crumb, ensure_ascii=False))

# ---------- 7. 校验 ----------
print("\n=== 生成页校验 ===")
checks = []
checks.append(("h1 计数==1", html.count("<h1") == 1))
checks.append(("h2 计数==%d" % len(H2), html.count("<h2>") == len(H2)))
checks.append(("JSON-LD >=2", html.count("application/ld+json") >= 2))
checks.append(("schema.org >=2 且无脱敏", html.count("https://schema.org") >= 2 and "https://***" not in html))
checks.append(("og:image 有", "og:image" in html))
checks.append(("canonical 有", "canonical" in html))
checks.append(("desc > 80", len(DESC) > 80))
checks.append(("无 '**'", html.count("**") == 0))
checks.append(("无 frontmatter 泄漏", "ai_smell" not in html and "title: " not in html))
checks.append(("无 HTML 注释残留", "<!--" not in html))
checks.append(("有 style", "<style>" in html))
checks.append(("正文段落数", html.count("<p>") >= 13 + 3))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
    try:
        json.loads(b)
    except Exception as e:
        checks.append(("JSON-LD parse", False))
        print("   PARSE FAIL", e)
for n, ok in checks:
    print("   %-24s %s" % (n, "PASS" if ok else "FAIL"))
depth = 0; under = 0
for m in re.finditer(r'<(/?)div[^>]*>', html):
    depth += -1 if m.group(1) else 1
    if depth < 0:
        under += 1; depth = 0
print("   div 深度归零: %s (depth=%d under=%d)" % (depth == 0 and under == 0, depth, under))
# 正文 0 差异断言（对生成页再验一次）
new_ps = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<p>(.*?)</p>", html, re.S)]
new_content = [p for p in new_ps if p in content]
print("   生成页含原文段落:", len(new_content), "/", len(content))
print("\n   新页字节数:", len(html.encode()))

if APPLY:
    with open(TARGET + ".bak-0922", "w", encoding="utf-8") as f:
        f.write(old)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(html)
    print("\n*** APPLIED -> %s (backup .bak-0922) ***" % TARGET)
else:
    print("\n(dry-run; 加 --apply 生效)")
    print("\n---- 生成页正文预览 ----")
    print(html[html.find("<article>"):html.find("</article>")][:1500])
