#!/usr/bin/env python3
"""0925 第4例裸发布畸形页修复：mili/blog/20260925-policy-cash-value-execution-2024-instance.html
- 房屋模板取自同日同品牌精修页（09-24）
- 正文一字不改（与 md 源逐段 0 差异断言）
- 补 h1 / 8 条描述性 h2 路标 / Article+BreadcrumbList JSON-LD / og 全套 / keywords / canonical
用法：python3 fix-0925-page.py [--apply]
"""
import json
import os
import re
import sys
import shutil

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20260925-policy-cash-value-execution-2024-instance"
PAGE = f"{REPO}/mili/blog/{SLUG}.html"
HOUSE = f"{REPO}/mili/blog/20260924-malicious-litigation-supervision.html"
MD = f"/Users/ziganghe/wiki/digital-employees/articles/{SLUG}.md"
APPLY = "--apply" in sys.argv

TITLE = "保单现金价值被划走28.5万！最少的一笔只有2970元"
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
DATE = "2026-09-25"
DESC = ("2024年8月14日内蒙古海拉尔区法院对5人名下的保单逐笔扣划现金价值，最少的一笔只有2970元。"
        "本文拆清股权之外的这层财产：现金价值为何归投保人、按身份与按险种的双轴划分、"
        "江苏/北京/广东三地口径这几年的变化，以及收到冻结通知后的四个自救动作和三个最容易踩的误区。")
KEYWORDS = "保单现金价值,法院强制执行,保险避债,投保人,被保险人,受益人,赎买介入,执行异议"
OGIMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"

# h2 路标：锚点 = 该段开头前缀（不改一字正文，只在其前插入描述性路标）
LANDMARKS = [
    ("先说一句早就定下的老话", "现金价值归投保人：法院为什么能查、能冻、能划"),
    ("真正值得讲清楚的，是哪些保单能划", "按身份 × 按险种：哪些保单会被划走"),
    ("顺带说一句，卖保险时拿", "「保险能避债」本身就是违规宣传"),
    ("再说一件很多人没注意的事：各地口径", "各地口径这几年在往「更能划」变：江苏、北京、广东"),
    ("还有两份新东西，比老的更细", "两份更细的新文件：四川工作指引与广州会议纪要"),
    ("好，到关键了。如果哪天你或者你家里人收到了法院的冻结通知", "收到冻结通知之后：四个动作"),
    ("还有三个坑，是实务里最容易踩的", "三个最容易踩的坑"),
    ("收个尾。保单从来不是藏钱的地方", "一句话收尾"),
]


def strip_frontmatter(md_text: str) -> str:
    lines = md_text.split("\n")
    if not lines or lines[0].strip() != "---":
        return md_text
    for i in range(1, min(len(lines), 40)):
        if lines[i].strip() in ("---", "..."):
            return "\n".join(lines[i + 1:]).lstrip("\n")
    return md_text


def norm(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    return s.strip("*")


page = open(PAGE, encoding="utf-8").read()
art_html = re.search(r"<article>(.*?)</article>", page, re.S).group(1)
page_paras = [p.strip() for p in re.findall(r"<p[^>]*>(.*?)</p>", art_html, re.S) if p.strip()]
md_body = strip_frontmatter(open(MD, encoding="utf-8").read())
md_paras_raw = [p.strip() for p in re.split(r"\n\s*\n", md_body) if p.strip()]
# 排除 md 尾部运营注释块（合集/检索词块）——按站内既有口径不入正文
excluded = [p for p in md_paras_raw if p.lstrip().startswith("<!--")]
md_paras = [p for p in md_paras_raw if not p.lstrip().startswith("<!--")]
if excluded:
    print(f"已排除 md 运营注释块 {len(excluded)} 处：{[e.splitlines()[0][:60] for e in excluded]}")

print(f"页面段落 {len(page_paras)} | md 源段落 {len(md_paras)}")
diff = 0
for i in range(max(len(page_paras), len(md_paras))):
    a = norm(page_paras[i]) if i < len(page_paras) else "<缺>"
    b = norm(md_paras[i]) if i < len(md_paras) else "<缺>"
    if a != b:
        diff += 1
        print(f"  ⚠️ 段 {i+1} 差异:\n     页面: {page_paras[i][:90] if i < len(page_paras) else '-'}\n     md  : {md_paras[i][:90] if i < len(md_paras) else '-'}")
print(f"正文差异段数: {diff}  {'✅ 0 差异，可重建' if diff == 0 else '❌ 需人工核对，停止'}")

# 路标锚点校验
missing = [a for a, _ in LANDMARKS if not any(p.startswith(a) for p in page_paras)]
print("路标锚点未命中:", missing if missing else "无（全部命中）")
if diff or missing:
    if APPLY:
        print("❌ 断言未过，拒绝写入")
        sys.exit(1)

# 组装正文：原段落 + 在锚点前插 h2
body_lines = []
for p in page_paras:
    for anchor, h2 in LANDMARKS:
        if p.startswith(anchor):
            body_lines.append(f"<h2>{h2}</h2>")
    body_lines.append(f"<p>{p}</p>")
body = "\n".join(body_lines)

house = open(HOUSE, encoding="utf-8").read()
h_head = house[: house.find("</head>")]
css_link = re.search(r'<link rel="stylesheet"[^>]*>', h_head).group(0)
beacon = re.search(r"<script defer src='https://static\.cloudflareinsights\.com[^>]*></script>", h_head).group(0)
footer = house[house.rfind("<footer>"):]

ld_article = {
    "@context": "https://schema.org", "@type": "Article", "headline": TITLE,
    "description": DESC, "author": {"@type": "Person", "name": "何自刚"},
    "publisher": {"@type": "Organization", "name": "北京觅理律师事务所"},
    "datePublished": DATE, "dateModified": DATE, "mainEntityOfPage": URL, "url": URL,
}
ld_crumb = {
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
        {"@type": "ListItem", "position": 3, "name": TITLE},
    ],
}
new_head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
{css_link}
{beacon}
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KEYWORDS}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:site_name" content="觅理律所">
<meta property="og:image" content="{OGIMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<link rel="canonical" href="{URL}">
<script type="application/ld+json">
{json.dumps(ld_article, ensure_ascii=False)}
</script>
<script type="application/ld+json">
{json.dumps(ld_crumb, ensure_ascii=False)}
</script>
</head>
<body>
<nav><a href="/mili/">← 首页</a></nav>
<article>
<h1>{TITLE}</h1>
{body}
</article>
{footer}"""

out = new_head

# ---- 终验 ----
checks = []
checks.append(("<h1> 计数 == 1", len(re.findall(r"<h1", out)) == 1, len(re.findall(r"<h1", out))))
checks.append((f"<h2> 计数 == {len(LANDMARKS)}", len(re.findall(r"<h2", out)) == len(LANDMARKS), len(re.findall(r"<h2", out))))
checks.append(("ld+json 块 == 2", len(re.findall(r"application/ld\+json", out)) == 2, len(re.findall(r"application/ld\+json", out))))
checks.append(("og:image 存在", "og:image" in out, "og:image" in out))
checks.append(("keywords 存在", 'name="keywords"' in out, 'name="keywords"' in out))
checks.append(("description 长度 > 80", len(DESC) > 80, len(DESC)))
checks.append(("<p> 计数不变", len(re.findall(r"<p[ >]", out)) == len(page_paras) + 2 + 0, len(re.findall(r"<p[ >]", out))))
checks.append(("schema.org 未脱敏", out.count("https://schema.org") == 2 and out.count("https://***") == 0, out.count("https://schema.org")))
checks.append(("markdown 星号未泄漏", out.count("**") == 0, out.count("**")))
checks.append(("<br> 已归位房屋样式(无裸 br 分隔)", out.count("<br>") == 0, out.count("<br>")))
# 每个原段落仍在
body_out = re.search(r"<article>(.*?)</article>", out, re.S).group(1)
out_paras = [p.strip() for p in re.findall(r"<p[^>]*>(.*?)</p>", body_out, re.S) if p.strip()]
checks.append((f"段落数 == {len(page_paras)}", len(out_paras) == len(page_paras), len(out_paras)))
checks.append(("段落内容逐段一致", all(norm(a) == norm(b) for a, b in zip(out_paras, page_paras)), "逐段比对"))

print("\n--- 终验 ---")
allok = True
for name, ok, val in checks:
    allok &= ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  (实测 {val})")
print("字节:", len(page.encode()), "->", len(out.encode()))

if not allok:
    print("\n❌ 终验未过，拒绝写入")
    sys.exit(1)
if not APPLY:
    print("\n(dry-run，未写入；加 --apply 生效)")
    sys.exit(0)

shutil.copy(PAGE, PAGE + ".bak-20260925")
open(PAGE, "w", encoding="utf-8").write(out)
print("\n✅ 已写入", PAGE)
