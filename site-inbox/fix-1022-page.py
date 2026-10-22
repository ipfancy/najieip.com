#!/usr/bin/env python3
"""Rebuild najie 20261022 gaoqi page (naked publish -> house style).
Usage: python3 site-inbox/fix-1022-page.py [--apply]
Body is rebuilt from md source; asserts text equality with md.
"""
import re, os, sys, json, shutil

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261022-najie-gaoqi-ip-30points"
PAGE = os.path.join(REPO, f"najie/blog/{SLUG}.html")
TPL = os.path.join(REPO, "najie/blog/20261021-goods-names-acceptable-list-q4.html")
MD = f"/Users/ziganghe/wiki/digital-employees/articles/{SLUG}.md"
COVER = f"/Users/ziganghe/wiki/digital-employees/articles/cover-{SLUG}.png"
APPLY = "--apply" in sys.argv
DATE = "2026-10-22"
TITLE = "高企那30分，纯买专利这一格天花板只有3分"
DESC = ("高企评分里知识产权占 30 分，但纯买专利这一格的天花板只有 3 分——官方口径是「仅有受让、受赠和并购 1–3 分」，下限 1 分而非 3 分。"
        "本文拆官方评价表四格加一个加分项、三类凑数逐格对账、算清另外三块要凑多少分，并提示Ⅱ类知识产权仅限使用一次、北京 2026 年度三批已截止。")
KEYWORDS = "高新技术企业认定,知识产权评分,高企申报专利布局"
IMG_URL = f"https://najieip.com/img/{SLUG}.png"
URL = f"https://najieip.com/najie/blog/{SLUG}.html"

def zh_quotes(s):
    out, flip = [], True
    for ch in s:
        if ch == '"':
            out.append("“" if flip else "”")
            flip = not flip
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = s.strip()
    s = re.sub(r"(?<!\*)\*\*([^*\n]{1,220})\*\*(?!\*)", r"<strong>\1</strong>", s)
    s = zh_quotes(s)
    return s

# ---------- 1. md -> body blocks ----------
raw = open(MD, encoding="utf-8").read()
raw = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S).strip()
lines = raw.split("\n")
blocks, i = [], 0
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln.strip():
        i += 1
        continue
    if ln.startswith("## "):
        blocks.append(("h2", ln[3:].strip()))
        i += 1
    elif ln.strip().startswith("|"):
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            rows.append(lines[i].strip())
            i += 1
        cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
        body = [c for c in cells if not all(re.fullmatch(r":?-{2,}:?", x or "-") for x in c)]
        blocks.append(("table", body))
    elif re.match(r"^\d+\.\s+", ln.strip()):
        items = []
        while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
            items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
            i += 1
        blocks.append(("ol", items))
    else:
        blocks.append(("p", ln.strip()))
        i += 1

html_parts = [f"<h1>{TITLE}</h1>"]
text_probe = [TITLE]
for kind, val in blocks:
    if kind == "h2":
        html_parts.append(f"<h2>{val}</h2>")
        text_probe.append(val)
    elif kind == "p":
        html_parts.append(f"<p>{inline(val)}</p>")
        text_probe.append(re.sub(r"<[^>]+>", "", inline(val)))
    elif kind == "ol":
        html_parts.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in val) + "</ol>")
        text_probe.extend(inline(x) for x in val)
    elif kind == "table":
        head = "".join(f"<th>{inline(c)}</th>" for c in val[0])
        body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in val[1:])
        html_parts.append(f'<table class="data">\n<thead><tr>{head}</tr></thead>\n<tbody>{body}</tbody>\n</table>')
        for r in val:
            text_probe.extend(inline(c) for c in r)

html_parts.append(f'<figure><img src="/img/{SLUG}.png" alt="{TITLE}" loading="lazy" style="max-width:100%;height:auto">'
                  f"<figcaption>一图速览：{TITLE}</figcaption></figure>")
article_body = "\n".join(html_parts)

# ---------- 2. head from template ----------
tpl = open(TPL, encoding="utf-8").read()
head = tpl[:tpl.find("</head>") + 7]
T_OLD_TITLE = "商品名称写错，商标申请白等一轮：Q4 清单已更新"
T_OLD_DESC = re.search(r'<meta name="description" content="([^"]*)"', tpl).group(1)
T_OLD_SLUG = "20261021-goods-names-acceptable-list-q4"
T_OLD_IMG = "https://najieip.com/img/20261021-goods-names-q4.png"
T_OLD_KW = "商标注册,商品和服务区分表,商标申请补正"

head = head.replace(T_OLD_TITLE, TITLE).replace(T_OLD_SLUG, SLUG)
head = head.replace(T_OLD_DESC, DESC).replace(T_OLD_IMG, IMG_URL).replace(T_OLD_KW, KEYWORDS)
head = head.replace('"datePublished": "2026-10-21"', f'"datePublished": "{DATE}"')
head = head.replace('"dateModified": "2026-10-21"', f'"dateModified": "{DATE}"')
# label for breadcrumb position 2 stays 纳杰博客 (same brand) -> ok

# drop template FAQPage block (its Q&A belongs to the template article, not this one)
head = re.sub(r'<script type="application/ld\+json">\s*\{[^<]*?"@type": "FAQPage".*?</script>', "", head, flags=re.S)

# template residue check before saving
if T_OLD_SLUG in head or T_OLD_TITLE in head:
    print("WARN template residue in head")

# ---------- 3. shell from template ----------
nav = re.search(r"<nav>.*?</nav>", tpl, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", tpl, re.S).group(0)
new = (head + "\n<body>\n" + nav + "\n<article>\n" + article_body + "\n</article>\n" + footer + "\n</body>\n</html>\n")

# ---------- 4. assertions ----------
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', new, re.S):
    json.loads(m)
assert new.count("<h1") == 1, new.count("<h1")
assert new.count("application/ld+json") == 2
assert "og:image" in new and "twitter:image" in new
assert T_OLD_SLUG not in new and T_OLD_TITLE not in new, "template residue"
assert new.count("**") == 0
assert not re.search(r"<p>\s*\|", new), "bare table left"
assert new.count("https://***") == 0 and new.count("https://schema.org") >= 2

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<figure.*?</figure>", " ", s, flags=re.S)
    s = re.sub(r"<h1>.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    s = re.sub(r"\*+", "", s)
    return re.sub(r"\s+", "", s)

def md_text():
    body = []
    for kind, val in blocks:
        if kind in ("p", "h2"):
            body.append(val)
        elif kind == "ol":
            body.extend(val)
        elif kind == "table":
            for r in val:
                body.extend(r)
    s = "".join(body)
    s = re.sub(r"\*+", "", s)
    return re.sub(r"\s+", "", zh_quotes(s))

page_txt = textify(new[new.find("<article"):new.find("</article>")])
md_txt = md_text()
same = page_txt == md_txt
print("md chars", len(md_txt), "page chars", len(page_txt), "EQUAL" if same else "DIFF")
if not same:
    import difflib
    a, b = md_txt, page_txt
    for k in range(min(len(a), len(b))):
        if a[k] != b[k]:
            print("first diff at", k, "| md:", a[max(0,k-40):k+40], "| page:", b[max(0,k-40):k+40])
            break
    print("len delta", len(b) - len(a))

if APPLY:
    shutil.copyfile(PAGE, PAGE + ".bak-1022")
    open(PAGE, "w", encoding="utf-8").write(new)
    os.makedirs(os.path.join(REPO, "img"), exist_ok=True)
    shutil.copyfile(COVER, os.path.join(REPO, f"img/{SLUG}.png"))
    print("APPLIED size", len(new), "cover bytes", os.path.getsize(os.path.join(REPO, f'img/{SLUG}.png')))
else:
    print("DRY-RUN size", len(new))
