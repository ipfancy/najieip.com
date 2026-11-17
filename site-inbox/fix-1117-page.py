#!/usr/bin/env python3
"""11-17 夜班：精修「德芙广告法罚角色」裸发布页（md 源整页重建 + 房屋取 11-16 mili 精修页）"""
import re, os, json, copy, sys, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261117-mili-dove-ad-role"
BRAND = "mili"
TITLE = "德芙被罚80万，罚单上却不是德芙：广告法罚的是角色，不是商标"
DESC = ("德芙被罚80万，罚单当事人却是第三方代运营上海宗正食品。广告法第2条按行为认定「广告主」，"
        "第9条第7项定性、第57条罚20万至100万；今年前三季度全国广告违法案均值4888元，本案是均值的164倍。"
        "代运营合同要写负面清单、终审留痕与全额追偿，但改不了对外的行政当事人认定。")
KW = ["广告法第9条第7项", "广告法第57条", "广告主认定", "代运营", "品牌方责任", "上海宗正食品"]
MD = os.path.expanduser("~/wiki/digital-employees/articles/%s.md" % SLUG)
TPL = os.path.join(REPO, "mili/blog/20261116-mili-protection-order-72hours.html")
OUT = os.path.join(REPO, BRAND, "blog", SLUG + ".html")
URL = "https://najieip.com/%s/blog/%s.html" % (BRAND, SLUG)
IMG = "https://najieip.com/img/%s.png" % SLUG
COVER_SRC = os.path.expanduser("~/wiki/digital-employees/articles/cover-%s.png" % SLUG)

ZH = {'"': '“', "'": "‘", "「": "「"}

def zh_quotes(s):
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("“" if open_q else "”"); open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = re.sub(r"\*\*([^*\n]{1,220})\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]{1,220})\*(?!\*)", r"<em>\1</em>", s)
    s = zhang = s.replace("&", "&amp;")
    return zhang

def textify(s):
    s = re.sub(r"<h1>.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2>.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    for ch in "“”\"'「」『』【】:：·・*|—–-…、，。！？；（）()《》<>/":
        s = s.replace(ch, "")
    return re.sub(r"\s+", "", s)

# ---------- md -> blocks ----------
raw = open(MD, encoding="utf-8").read()
raw = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
blocks = [b.strip() for b in re.split(r"\n\s*\n", raw) if b.strip()]
parts, h2s = [], []
for b in blocks:
    b = " ".join(b.split("\n")) if not b.startswith("|") else b
    m = re.fullmatch(r"\*\*(.{1,40})\*\*", b)
    if m:
        h2s.append(m.group(1)); parts.append("H2::" + m.group(1)); continue
    parts.append(b)

html_parts = []
for p in parts:
    if p.startswith("H2::"):
        html_parts.append("<h2>%s</h2>" % zh_quotes(p[4:]))
        continue
    t = p
    italic_only = re.fullmatch(r"\*(.+)\*", t) if not t.startswith("**") else None
    if italic_only:
        html_parts.append("<p><em>%s</em></p>" % zh_quotes(italic_only.group(1)))
        continue
    if t.startswith("何自刚 |"):
        html_parts.append("<p>%s</p>" % t)
        continue
    html_parts.append("<p>%s</p>" % zh_quotes(inline(t)))

article_body = "\n<br>\n".join(html_parts)

# ---------- house ----------
tpl = open(TPL, encoding="utf-8").read()
head_end = tpl.find("</head>") + 7
head = tpl[:head_end]
tail = tpl[tpl.find("</article>"):]  # </article> + footer + </html>

def sub1(pat, rep, s):
    new, n = re.subn(pat, rep, s, count=1, flags=re.S)
    assert n == 1, "no-match: " + pat
    return new

head = sub1(r'<meta name="keywords" content="[^"]*">', '<meta name="keywords" content="%s">' % ",".join(KW), head)
head = sub1(r"<title>.*?</title>", "<title>%s — 纳杰觅理</title>" % TITLE, head)
D = DESC.replace('"', "“")
for pat in [r'(<meta name="description" content=")[^"]*(">)',
            r'(<meta property="og:description" content=")[^"]*(">)',
            r'(<meta name="twitter:description" content=")[^"]*(">)']:
    head = re.sub(pat, lambda m: m.group(1) + D + m.group(2), head, count=1)
for pat in [r'(<meta property="og:title" content=")[^"]*(">)', r'(<meta property="twitter:title" content=")[^"]*(">)']:
    head = re.sub(pat, lambda m: m.group(1) + TITLE + m.group(2), head, count=1)
head = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + URL + m.group(2), head, count=1)
head = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + URL + m.group(2), head, count=1)
head = head.replace("https://najieip.com/img/20261116-mili-protection-order-72hours.png", IMG)

# JSON-LD
blocks_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
assert len(blocks_ld) == 2, blocks_ld
new_lds = []
for b in blocks_ld:
    o = json.loads(b)
    o = {"@context": "https://schema.org", **o}
    if o.get("@type") == "Article":
        o.update({"headline": TITLE, "datePublished": "2026-11-17", "dateModified": "2026-11-17",
                  "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "image": IMG,
                  "description": DESC, "keywords": KW, "url": URL})
    elif o.get("@type") == "BreadcrumbList":
        o["itemListElement"][2]["name"] = TITLE
        o["itemListElement"][2]["item"] = URL
    new_lds.append(json.dumps(o, ensure_ascii=False))
it = iter(new_lds)
head = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',
              lambda m: m.group(1) + next(it) + m.group(3), head, flags=re.S)

page = head + "<body>\n<nav><a href=\"/\">← 首页</a></nav>\n<article>\n<h1>%s</h1>\n%s\n<br>\n" % (TITLE, article_body) + tail

# ---------- assertions ----------
assert page.count("<h1") == 1 and page.count("<h2") == len(h2s) == 3, (page.count("<h1"), page.count("<h2"), h2s)
ldc = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
assert len(ldc) == 2 and all(json.loads(x) for x in ldc)
assert page.count('"@context": "https://schema.org"') == 2
assert 'property="og:image"' in page and 'summary_large_image' in page
body_txt = re.sub(r"<[^>]+>", "", re.sub(r"<script.*?</script>", " ", page[page.find("<body"):], flags=re.S))
assert body_txt.count("**") == 0, body_txt.count("**")
assert '"' not in body_txt, "ascii quote left"
# md 全文包含
art = page[page.find("<article>"):page.find("</article>")]
BYLINE = textify("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰")
_md_raw = re.sub(r"^---\n.*?\n---\n", "", open(MD, encoding="utf-8").read(), flags=re.S)
_md_lines = [ln for ln in _md_raw.split("\n") if not re.fullmatch(r"\*\*.{1,40}\*\*", ln.strip())]
md_norm = textify("\n".join(_md_lines)).replace(BYLINE, "")
pg_norm = textify(art).replace(BYLINE, "")
assert md_norm in pg_norm, (len(md_norm), len(pg_norm))
print("md_contained=True", len(md_norm), len(pg_norm), "h2s=", h2s)

if "--apply" in sys.argv:
    open(OUT, "w", encoding="utf-8").write(page)
    os.makedirs(os.path.join(REPO, "img"), exist_ok=True)
    shutil.copyfile(COVER_SRC, os.path.join(REPO, "img", SLUG + ".png"))
    print("WROTE", OUT, os.path.getsize(OUT), "cover", os.path.getsize(os.path.join(REPO, 'img', SLUG + '.png')))
else:
    print("DRY-RUN size", len(page.encode()))
