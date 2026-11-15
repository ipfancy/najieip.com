#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-11-15 精修：mili 背靠背条款页（部分裸发布 → 房屋重建）"""
import os, re, json, copy, shutil, sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"
SLUG = "20261115-mili-payment-60days-b2b"
PAGE = os.path.join(REPO, "mili", "blog", SLUG + ".html")
TPL = os.path.join(REPO, "mili", "blog", "20261114-mili-face-recognition-compliance.html")
MD = os.path.join(ART, SLUG + ".md")
COVER_SRC = os.path.join(ART, SLUG + "-cover.png")
COVER_DST = os.path.join(REPO, "img", SLUG + ".png")
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
TITLE = "「收到上家款再付」无效：国务院令第802号，逾期按日万分之五"
DESC = ("国务院令第802号把大型企业付款期限压到60日内，逾期未约定利率的按日万分之五计息；"
        "最高法法释〔2024〕11号批复明确「收到第三方款项再付」条款无效。"
        "文中给出中小企业划型自测法、条例口径与裁判口径的利息差异，以及不起诉也能施压的三条路。")
KW = ["中小企业账款", "背靠背条款", "国务院令802号", "付款期限60日", "逾期利息", "法释2024-11号"]

def zh_quotes(s):
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("“" if open_q else "”"); open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = zh_quotes(s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", s)
    return s

# ---- md 解析 ----
raw = open(MD, encoding="utf-8").read()
raw = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
blocks, buf, ol = [], [], []

def flush_p():
    global buf
    if buf:
        txt = " ".join(x.strip() for x in buf).strip()
        if txt:
            blocks.append(("p", txt))
        buf = []

def flush_ol():
    global ol
    if ol:
        blocks.append(("ol", [re.sub(r"^\d+\.\s*", "", x) for x in ol]))
        ol = []

for ln in raw.split("\n"):
    s = ln.strip()
    if not s:
        flush_p(); flush_ol(); continue
    if s.startswith("## "):
        flush_p(); flush_ol(); blocks.append(("h2", s[3:].strip())); continue
    if re.match(r"^\d+\.\s", s):
        flush_p(); ol.append(s); continue
    flush_ol(); buf.append(s)
flush_p(); flush_ol()

body_parts = []
for kind, val in blocks:
    if kind == "h2":
        body_parts.append(f"<h2>{inline(val)}</h2>")
    elif kind == "p":
        body_parts.append(f"<p>{inline(val)}</p>")
    elif kind == "ol":
        body_parts.append("<ol>\n" + "\n".join(f"<li>{inline(v)}</li>" for v in val) + "\n</ol>")
article_body = "<h1>" + inline(TITLE) + "</h1>\n" + "\n".join(body_parts)

# ---- head 模板 ----
tpl = open(TPL, encoding="utf-8").read()
head_end = tpl.find("</head>") + 7
head = tpl[:head_end]
lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
assert len(lds) == 2, f"模板 ld 数 {len(lds)}"
art_obj = json.loads(lds[0]); bc_obj = json.loads(lds[1])
art_obj = {"@context": "https://schema.org", **art_obj}
bc_obj = {"@context": "https://schema.org", **bc_obj}
art_obj.update(headline=TITLE, datePublished="2026-11-15", dateModified="2026-11-15",
               description=DESC, image=IMG, keywords=KW,
               mainEntityOfPage={"@type": "WebPage", "@id": URL}, url=URL)
bc_obj["itemListElement"][2] = {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL}

newhead = head
newhead = re.sub(r"<title>.*?</title>", f"<title>{TITLE} — 觅理律师事务所</title>", newhead, count=1, flags=re.S)
newhead = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', newhead, count=1)
newhead = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{",".join(KW)}">', newhead, count=1)
for prop, val in [("og:title", TITLE), ("og:description", DESC), ("og:url", URL), ("og:image", IMG)]:
    newhead = re.sub(rf'<meta property="{prop}" content="[^"]*">', f'<meta property="{prop}" content="{val}">', newhead, count=1)
newhead = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', newhead, count=1)
newhead = newhead.replace('content="summary_large_image"', 'content="summary_large_image"')
# 替换两块 ld+json（按顺序）
parts = re.split(r'(<script type="application/ld\+json">.*?</script>)', newhead, flags=re.S)
ld_i = 0
for i, seg in enumerate(parts):
    if seg.startswith('<script type="application/ld+json">'):
        obj = art_obj if ld_i == 0 else bc_obj
        parts[i] = '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'
        ld_i += 1
newhead = "".join(parts)

page = (newhead + "\n<body>\n"
        '<nav><a href="/">← 首页</a> · <a href="https://najieip.com/mili/blog/">觅理观察</a></nav>\n'
        "<article>\n" + article_body + "\n</article>\n"
        "<footer>\n<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>\n"
        '<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>\n</footer>\n</body>\n</html>\n')

# ---- 校验 ----
errs = []
if len(re.findall(r"<h1[ >]", page)) != 1: errs.append("h1")
ldn = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
if len(ldn) != 2: errs.append(f"ld={len(ldn)}")
for b in ldn: json.loads(b)
if page.count("https://schema.org") != 2: errs.append("ctx")
if 'property="og:image"' not in page: errs.append("og:image")
if "**" in page: errs.append("star")
if re.search(r"<p>\s*\|", page): errs.append("baretable")
if len(DESC) < 80 or DESC == TITLE: errs.append("desc")

def norm(s):
    s = s.replace("“","").replace("”","").replace('"',"").replace("'","").replace("’","")
    s = s.replace("「","").replace("」","").replace("『","").replace("』","").replace("【","").replace("】","")
    s = s.replace("|","").replace(":","").replace("-","").replace("*","")
    return re.sub(r"\s+", "", s)

def strip_tags(s):
    s = re.sub(r"<h1>.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2>.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return s

mdtxt = []
for ln in re.sub(r"^---\n.*?\n---\n", "", open(MD, encoding="utf-8").read(), flags=re.S).split("\n"):
    s = ln.strip()
    if not s or s.startswith("#"): continue
    if re.match(r"^\*\*[^*\n]{1,30}\*\*$", s) and not re.search(r"[。！？]$", s): continue
    s = re.sub(r"^\d+\.\s*", "", s).replace("*", "")
    s = s.replace("何自刚｜知识产权律师｜爱普纳杰 · 觅理 · 纳杰", "")
    mdtxt.append(s)
mdn = norm("".join(mdtxt))
art = page[page.find("<article"):page.find("</article>")]
pgn = norm(strip_tags(art))
for by in ("何自刚｜知识产权律师｜爱普纳杰 · 觅理 · 纳杰", "北京纳杰知识产权代理有限公司 何自刚"):
    nb = norm(by)
    mdn = mdn.replace(nb, ""); pgn = pgn.replace(nb, "")
contained = mdn in pgn
if not contained:
    d = next((i for i in range(min(len(mdn), len(pgn))) if mdn[i] != pgn[i]), -1)
    errs.append(f"md_not_contained diff_at={d} md={len(mdn)} pg={len(pgn)} || {mdn[d:d+40]!r} vs {pgn[d:d+40]!r}")

print("errs:", errs)
print("blocks:", [(k, (v if k != 'ol' else len(v))) for k, v in blocks])
print("size:", len(page.encode()), "mdn:", len(mdn), "pgn:", len(pgn), "contained:", contained)
if errs:
    sys.exit(1)

if "--apply" in sys.argv:
    shutil.copyfile(COVER_SRC, COVER_DST)
    open(PAGE, "w", encoding="utf-8").write(page)
    print("APPLIED", PAGE, os.path.getsize(PAGE), "cover", os.path.getsize(COVER_DST))
else:
    print("DRY-RUN ok")
