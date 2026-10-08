#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 部分裸发布 defect on mili labor-contract page: JSON-LD x2 + og:image + twitter + keywords + real description + h2 landmarks.
Body text preserved verbatim (asserted)."""
import re, os, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
TARGET = "mili/blog/20261008-mili-labor-contract-four-clauses.html"
P = os.path.join(REPO, TARGET)
t = open(P, encoding="utf-8").read()
orig = t

URL = "https://najieip.com/mili/blog/20261008-mili-labor-contract-four-clauses.html"
TITLE = "一份能经得起仲裁的劳动合同，这4个条款别写错"
IMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"

DESC = ("人社部2025年统计公报显示，全国劳动人事争议全年办理454.3万件、结案金额994.7亿元，平均一案2.25万元。"
        "本文拆解劳动合同最容易写错的四个条款：工作内容与地点（写“全国”“服从公司安排”属约定不明，"
        "依《劳动争议调解仲裁法》第六条举证不利后果归单位）、劳动报酬（“工资面议”按《劳动合同法》第十八条同工同酬处理）、"
        "试用期（第十九条的期限上限，以及“录用条件”必须书面化才能据以解除）、"
        "社保与竞业限制（《劳动争议解释（二）》第十九条约定自愿放弃社保一律无效、第十三条竞业限制范围与涉密事项脱节部分无效），"
        "每条给出一个真实反例和一句可直接抄进合同的写法。")

KW = "劳动合同,劳动争议,试用期,竞业限制,劳动报酬,社保缴纳,劳动争议调解仲裁法,劳动合同法"

# ---------- 1. body text preservation baseline ----------
def paras(html):
    body = html[html.find("<body>"):]
    ps = re.findall(r"<h1[^>]*>(.*?)</h1>|<p[^>]*>(.*?)</p>", body, re.S)
    out = []
    for a, b in ps:
        s = a if a else b
        if "lt;!--" in s or s.strip().startswith("<!--"):
            continue
        out.append(s.strip())
    return out

before_paras = paras(t)
h1_before = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)
assert len(h1_before) == 1, h1_before

# ---------- 2. insert h2 landmarks by paragraph prefix ----------
LANDMARKS = [
    ("第一个，工作内容和工作地点。", "一、工作内容和工作地点：写“全国”等于没写"),
    ("第二个，劳动报酬。", "二、劳动报酬：“工资面议”按同工同酬处理"),
    ("第三个，试用期。", "三、试用期：期限有上限，“录用条件”要有书面"),
    ("第四个，社保和竞业限制。", "四、社保与竞业限制：自愿放弃社保的约定无效"),
]
for anchor, h2 in LANDMARKS:
    needle = "<p>" + anchor
    assert t.count(needle) == 1, (anchor, t.count(needle))
    t = t.replace(needle, "<h2>" + h2 + "</h2>\n<br>\n" + needle, 1)

# ---------- 3. rebuild head ----------
head_new = f"""<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KW}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:site_name" content="觅理律师事务所">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<link rel="canonical" href="{URL}">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": TITLE, "description": DESC, "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师", "worksFor": {"@type": "LegalService", "name": "北京觅理律师事务所", "url": "https://najieip.com/mili/"}}, "publisher": {"@type": "Organization", "name": "北京觅理律师事务所"}, "image": IMG, "datePublished": "2026-10-08", "dateModified": "2026-10-08", "mainEntityOfPage": URL, "url": URL}, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}, {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"}, {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL}]}, ensure_ascii=False)}</script>
</head>"""

t = re.sub(r"<head>.*?</head>", lambda m: head_new, t, count=1, flags=re.S)
# align nav to house style (brand page link)
t = t.replace('<nav><a href="/">← 首页</a></nav>', '<nav><a href="/mili/">← 首页</a></nav>', 1)

# ---------- 4. validate ----------
after_paras = paras(t)
if len(before_paras) != len(after_paras):
    print("PARA COUNT DIFF", len(before_paras), len(after_paras)); sys.exit(1)
diff = [(i, a, b) for i, (a, b) in enumerate(zip(before_paras, after_paras)) if a != b]
print("paragraphs:", len(before_paras), "diffs:", len(diff))
for d in diff[:3]:
    print("  DIFF", d[0], d[1][:60], "||", d[2][:60])
assert not diff, "body text changed"

blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
assert len(blocks) == 2, len(blocks)
for i, b in enumerate(blocks):
    json.loads(b)
print("ld+json blocks ok:", len(blocks))
assert t.count("https://schema.org") == 2
assert t.count("https://***") == 0
assert "**" not in t, t.count("**")
assert len(re.findall(r"<h1", t)) == 1
assert len(re.findall(r"<h2", t)) == 4
assert t.count("beacon.min.js") == 1

if "--apply" in sys.argv:
    open(P, "w", encoding="utf-8").write(t)
    print("WROTE", len(t.encode()), "bytes (was", len(orig.encode()), ")")
else:
    print("dry-run ok, would write", len(t.encode()), "bytes (was", len(orig.encode()), ")")
