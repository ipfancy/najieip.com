#!/usr/bin/env python3
"""SiteOps 修复 2026-11-24 mili 裸发布页（h1=0 / ld=0 / 无 og:image / desc 复读标题）
按 md 源整页重建，房屋取同日同品牌精修页 20261121-mili-patent-agency-revoked-34.html
用法: python3 site-inbox/fix-1124-page.py [--apply]
"""
import os, re, sys, json, copy, shutil

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261124-mili-punitive-damages-one-shot"
HOUSE = f"{REPO}/mili/blog/20261121-mili-patent-agency-revoked-34.html"
TARGET = f"{REPO}/mili/blog/{SLUG}.html"
MD = f"/Users/ziganghe/wiki/digital-employees/articles/{SLUG}.md"
COVER_SRC = f"/Users/ziganghe/wiki/digital-employees/articles/cover-{SLUG}.png"
COVER_DST = f"{REPO}/img/{SLUG}.png"
APPLY = "--apply" in sys.argv

TITLE = "漏写请求，最高五倍没了"
HEADLINE = "漏写请求，最高五倍没了：一审那句“先不主张”，把五倍赔偿永久关在门外"
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
DESC = ("法释〔2026〕7号今年5月1日施行：第12条给出最高五倍的赔偿总额，但第3条只留一个补票窗口——"
        "一审法庭辩论终结前；第4条规定经法院释明仍未请求的，判决生效后另案起诉请求惩罚性赔偿不予受理，"
        "二审才增加请求的只能调解。附一审笔录话术、起诉状三件套与第5条“反法混淆不能加倍”的雷。")
KEYWORDS = "惩罚性赔偿,法释2026-7号,知识产权诉讼,商业秘密,反不正当竞争,五倍赔偿"

def zh_quotes(s):
    out, buf = [], []
    for ch in s:
        if ch == '"':
            buf.append('“' if len(buf) % 2 == 0 else '”')
        else:
            buf.append(ch)
    # 成对处理更稳：替换外层函数
    return s

def zh_q(s):
    # 交替替换直引号为中文引号
    res, open_q = [], True
    for ch in s:
        if ch == '"':
            res.append('“' if open_q else '”')
            open_q = not open_q
        else:
            res.append(ch)
    return "".join(res)

def inline(s):
    s = zh_q(s)
    s = re.sub(r"\*\*([^*]{1,200})\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]{1,200})\*(?!\*)", r"<em>\1</em>", s)
    return s

# ---- 解析 md ----
raw = open(MD, encoding="utf-8").read()
body_md = raw.split("---", 2)[2]
lines = [l.rstrip() for l in body_md.split("\n")]
# 丢弃注释行与单独 --- 行
clean = [l for l in lines if not l.strip().startswith("<!--") and l.strip() != "---"]

blocks, cur = [], []
for l in clean:
    if not l.strip():
        if cur:
            blocks.append(cur); cur = []
    else:
        cur.append(l)
if cur: blocks.append(cur)

parts = []
h2s = []
for blk in blocks:
    if len(blk) == 1 and blk[0].startswith("## "):
        h = blk[0][3:].strip()
        h2s.append(h)
        parts.append(f"<h2>{inline(h)}</h2>")
    elif len(blk) == 1 and re.match(r"^\*[^*].*\*$", blk[0].strip()):
        parts.append(f"<p><em>{inline(blk[0].strip()[1:-1])}</em></p>")
    else:
        txt = " ".join(blk).strip()
        parts.append(f"<p>{inline(txt)}</p>")

# ---- 房屋 ----
house = open(HOUSE, encoding="utf-8").read()
nav = re.search(r"<nav>.*?</nav>", house, re.S).group(0)
after_article = house[house.find("</article>"):]

lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', house, re.S)
art_obj = bc_obj = None
for s in lds:
    o = json.loads(s)
    if o.get("@type") == "Article":
        art_obj = o
    elif o.get("@type") == "BreadcrumbList":
        bc_obj = o
assert art_obj and bc_obj, "模板缺 Article/BreadcrumbList"

a = copy.deepcopy(art_obj)
a["headline"] = HEADLINE
a["description"] = DESC
a["image"] = IMG
a["datePublished"] = "2026-11-24"
a["dateModified"] = "2026-11-24"
a["keywords"] = KEYWORDS.split(",")
if "mainEntityOfPage" in a:
    a["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
if "url" in a:
    a["url"] = URL
if "@id" in a:
    a["@id"] = URL
b = copy.deepcopy(bc_obj)
b["itemListElement"][2]["name"] = TITLE
b["itemListElement"][2]["item"] = URL

head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KEYWORDS}">
<meta property="og:type" content="article">
<meta property="og:title" content="{HEADLINE}">
<meta property="og:description" content="{DESC}">
<meta property="og:site_name" content="北京觅理律师事务所">
<meta property="og:locale" content="zh_CN">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{HEADLINE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{IMG}">
<link rel="canonical" href="{URL}">
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(a, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>
</head>
<body>
{nav}
<article>
<h1>{TITLE}</h1>
<figure><img src="/img/{SLUG}.png?v=20261124" alt="{TITLE}（信息图）" width="1080" height="1440" loading="lazy" style="max-width:100%;height:auto"></figure>
""" + "\n".join(parts) + "\n" + after_article

# ---- 断言 ----
assert head.count("<h1>") == 1, "h1 计数"
assert head.count("application/ld+json") == 2, "ld 块数"
assert head.count("https://schema.org") == 2, "schema 计数"
assert 'property="og:image"' in head
assert re.sub(r"[0-9]\*{2,}[0-9.]*", "", head).count("**") == 0, "markdown 星号残留"
assert "<p>|" not in head and not re.search(r"<p>\s*\|", head), "裸表残留"
assert not re.search(r"<p>\s*(slug|title|date|brand|style|voice|end|tags|author)\s*[:：]", head), "frontmatter 泄漏"
assert not re.search(r"<p>\s*-{3,}\s*</p>", head), "分隔行泄漏"
op, cl = head.count("<div"), head.count("</div>")
d = 0; bad = 0
for m in re.finditer(r"<(/?)div\b[^>]*>", head):
    d += -1 if m.group(1) else 1
    if d < 0: bad += 1
print(f"div open={op} close={cl} depth_end={d} bad={bad}")

# 正文包含断言：md 全文（归一）出现在页面正文（归一）
def norm(s):
    s = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = s.replace("*", "").replace("“", "").replace("”", "").replace('"', "")
    s = re.sub(r"[「」『』【】]", "", s)
    s = re.sub(r"^\s*\d+\.\s+", "", s, flags=re.M)
    s = re.sub(r"-{3,}", "", s)
    s = re.sub(r"\s+", "", s)
    return s

md_txt = norm("\n".join(l for l in clean if not l.strip().startswith("## ")))
pg_art = head[head.find("<article>"):head.find("</article>")]
pg_txt = norm(pg_art)
pg_txt = pg_txt.replace("漏写请求，最高五倍没了", "", 1)  # 剥 h1 文本
contained = md_txt in pg_txt
print(f"md_len={len(md_txt)} page_len={len(pg_txt)} contained={contained} h2={len(h2s)}")
if not contained:
    i = 0
    while i < min(len(md_txt), len(pg_txt)) and md_txt[i] == pg_txt[i]: i += 1
    print("diff_at", i, repr(md_txt[max(0,i-40):i+60]), "||", repr(pg_txt[max(0,i-40):i+60]))
    sys.exit(1)

print("size", len(head.encode()))
if APPLY:
    open(TARGET, "w", encoding="utf-8").write(head)
    if os.path.exists(COVER_SRC):
        os.makedirs(f"{REPO}/img", exist_ok=True)
        shutil.copy(COVER_SRC, COVER_DST)
        print("cover copied", os.path.getsize(COVER_DST))
    else:
        print("WARN cover missing", COVER_SRC)
    print("APPLIED", TARGET, os.path.getsize(TARGET))
