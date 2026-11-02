#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-02: 按 md 源 + 同日同品牌房屋重建 20261102-najie-tech-export-catalog-48 页
（上游裸发布档：ld=0/无og:image/无keywords/无h2/**未转/正文截断）"""
import os, re, json, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles/20261102-najie-tech-export-catalog-48.md")
HOUSE = os.path.join(REPO, "najie/blog/20261102-najie-ai-search-summary-pay.html")
TARGET = os.path.join(REPO, "najie/blog/20261102-najie-tech-export-catalog-48.html")
SLUG = "20261102-najie-tech-export-catalog-48"
BRAND = "najie"
URL_BASE = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
IMG_URL = f"https://najieip.com/img/{SLUG}.png"
TITLE = "48号公告：40项技术出口先登记，判断错了没人替你兜底"
DESC = ("商务部、科技部第48号公告拟增列40项技术（人工智能23项、生物医药5项、光伏12项），拟禁止14项、拟限制26项，"
        "11月15日是征求意见截止日；但临时出口前登记自2026年10月16日公告发布当天就已生效。登记义务由出口经营者自行判断，"
        "判断错了没有官方替你兜底。本文拆四类登记情形、六种出海形态对号入座、最易漏的控制权变更，以及条例第39条前置材料"
        "与第43、44条真正罚则的口径差别。")
KEYWORDS = "技术出口,48号公告,技术进出口管理条例,自动许可,控制权变更,涉外知识产权"
DATE = "2026-11-02"

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def zh_quotes(s):
    out = []
    # 只在文本片段上转换成对直引号
    for part in re.split(r"(<[^>]+>)", s):
        if part.startswith("<"):
            out.append(part)
        else:
            n = part.count('"')
            for i in range(n):
                part = part.replace('"', "“" if i % 2 == 0 else "”", 1)
            out.append(part)
    return "".join(out)

# ---------- 1. 解析 md ----------
raw = rd(MD)
raw = re.sub(r"^---.*?---\s*", "", raw, count=1, flags=re.S)
raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
paras = [p.strip() for p in raw.split("\n") if p.strip()]

html_paras = []
h2_count = 0
for p in paras:
    if p.startswith("# "):
        continue  # 标题单独用 TITLE
    m = re.fullmatch(r"\*\*(.+?)\*\*", p)
    if m:
        html_paras.append("<h2>" + zh_quotes(m.group(1)).replace('"', "“", 1) + "</h2>")
        h2_count += 1
        continue
    # 落款 / 免责
    if p.startswith("何自刚 |"):
        html_paras.append('<p class="byline">北京纳杰知识产权代理有限公司 何自刚</p>')
        continue
    if p.startswith("本文仅代表作者个人观点"):
        html_paras.append('<p class="disclaimer">' + p + "</p>")
        continue
    if p.startswith("*本文由 AI 辅助生成"):
        html_paras.append('<p class="disclaimer">' + p.strip("*") + "</p>")
        continue
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
    s = zh_quotes(s)
    html_paras.append("<p>" + s + "</p>")

print(f"paras={len(paras)} html={len(html_paras)} h2={h2_count}")

# ---------- 2. 房屋（head + nav + footer） ----------
hs = rd(HOUSE)
head_end_h = hs.find("</head>") + 7
head_t = hs[:head_end_h]
body_t = hs[head_end_h:]
nav = re.search(r"<nav>.*?</nav>", body_t, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", body_t, re.S).group(0)

# head 替换
head = head_t
head = head.replace("<title>AI 搜索按千次卖，被摘要的网页按什么收钱 — 纳杰觅理</title>", f"<title>{TITLE} — 纳杰觅理</title>")
old_desc = re.search(r'<meta name="description" content="[^"]*">', head).group(0)
head = head.replace(old_desc, f'<meta name="description" content="{DESC}">')
head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{TITLE}">', head)
head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', head)
head = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{KEYWORDS}">', head)
head = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL_BASE}">', head)
head = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG_URL}">', head)
head = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{TITLE}">', head)
head = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{DESC}">', head)
head = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG_URL}">', head)
head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL_BASE}">', head)
head = re.sub(r'<link rel="alternate" hreflang="zh-CN" href="[^"]*">', f'<link rel="alternate" hreflang="zh-CN" href="{URL_BASE}">', head)
head = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{URL_BASE}">', head)

# JSON-LD：deepcopy 模板对象后覆写
lod = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
assert len(lod) == 2, f"house ld count {len(lod)}"
art = json.loads(lod[0]); bc = json.loads(lod[1])
art = copy.deepcopy(art)
art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMG_URL
art["datePublished"] = DATE
art["dateModified"] = DATE
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL_BASE}
art["url"] = URL_BASE
art["keywords"] = KEYWORDS
bc = copy.deepcopy(bc)
bc["itemListElement"][2]["name"] = TITLE
bc["itemListElement"][2]["item"] = URL_BASE
new_ld = ('<script type="application/ld+json">' + json.dumps(art, ensure_ascii=False) + '</script>\n'
          '<script type="application/ld+json">' + json.dumps(bc, ensure_ascii=False) + '</script>')
# 用两块 ld 整体替换（从第一块起至第二块止）
i1 = head.find('<script type="application/ld+json">')
i2 = head.find("</script>", head.find("</script>", i1) + 9) + 9
head = head[:i1] + new_ld + head[i2:]

body = body_t
body = body.replace(nav, nav, 1)
article = "<article>\n<h1>" + TITLE + "</h1>\n" + "\n".join(html_paras) + "\n</article>"
body = re.sub(r"<article>.*?</article>", lambda _: article, body, count=1, flags=re.S)

new_html = head + body

# ---------- 3. 断言 ----------
assert len(re.findall(r"<h1[\s>]", new_html)) == 1
assert len(re.findall(r'application/ld\+json', new_html)) == 2
assert "<meta property=\"og:image\"" in new_html
assert "**" not in re.sub(r'<script.*?</script>', " ", new_html, flags=re.S)
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', new_html, re.S):
    json.loads(blk)
# 正文与 md 逐段比对（文本归一）
def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in [("&nbsp;", " "), ("&amp;", "&"), ("&gt;", ">"), ("&lt;", "<"), ("&quot;", '"')]:
        s = s.replace(a, b)
    s = s.replace("“", "").replace("”", "").replace('"', "")
    return re.sub(r"\s+", "", s)
mtxt = textify(raw.replace("#", " ").replace("*", " "))
mtxt = mtxt.replace("何自刚|知识产权律师|爱普纳杰·觅理·纳杰", "")
b = new_html[new_html.find("<body"):]
ab = re.search(r"<article>.*?</article>", b, re.S).group(0)
btxt = textify(ab).replace("北京纳杰知识产权代理有限公司何自刚", "")
print(f"md_len={len(mtxt)} art_len={len(btxt)} contained={mtxt in btxt}")
if mtxt not in btxt:
    # 定位差异
    import difflib
    print("DIFF:", list(difflib.unified_diff([mtxt[i:i+40] for i in range(0, len(mtxt), 40)],
                                             [btxt[i:i+40] for i in range(0, len(btxt), 40)], lineterm=""))[:12])
    sys.exit("正文包含断言失败")

if "--apply" in sys.argv:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"WROTE {TARGET} {os.path.getsize(TARGET)}B")
else:
    print("DRY-RUN ok, size would be", len(new_html.encode()))
