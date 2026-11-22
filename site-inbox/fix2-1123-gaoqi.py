#!/usr/bin/env python3
# site-inbox/fix2-1123-gaoqi.py — 修 20261123 高企文 + 三处补卡 + articles.json
import os, re, json, glob, copy, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
APPLY = "--apply" in sys.argv
SLUG = "20261123-mili-gaoqi-2026-no-new-standard"
PAGE = f"najie/blog/{SLUG}.html"
URL = f"https://najieip.com/najie/blog/{SLUG}.html"
TITLE = "高企“2026新规”，官方文件里查不到"

t = open(PAGE, encoding="utf-8").read()
head_end = t.find("</head>") + 7
head, body = t[:head_end], t[head_end:]

# --- 1. h1 ---
if not re.search(r"<h1[\s>]", body):
    body = re.sub(r"(<article>\s*)", r"\1\n<h1>" + TITLE + "</h1>\n", body, count=1)
    print("h1 inserted")

# --- 2. ** → strong ; 描述 ---
starb = body.count("**")
body = re.sub(r"\*\*([^*\n]{1,220})\*\*", r"<strong>\1</strong>", body)
body = re.sub(r"<p>\s*&lt;!--.*?--&gt;\s*</p>\s*", "", body, flags=re.S)
print("stars converted:", starb, "-> left", body.count("**"))

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()

paras = [textify(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)]
paras = [p for p in paras if len(p) > 40 and "lt;!--" not in p and "<!--" not in p]
DESC = paras[0][:150] if paras else TITLE
if DESC.endswith(("，", "、")): DESC = DESC[:-1] + "。"
print("DESC:", DESC)

# --- 3. 封面 ---
cands = []
for pat in (f"img/{SLUG}.png", f"img/*gaoqi-2026*.png"):
    cands += glob.glob(pat)
art_cands = glob.glob(os.path.expanduser("~/wiki/digital-employees/articles/*gaoqi-2026-no-new-standard*.png"))
print("covers repo:", cands[:3], "src:", [os.path.basename(x) for x in art_cands][:3])
IMG = ""
if cands:
    IMG = "https://najieip.com/" + cands[0]
elif art_cands:
    IMG = f"https://najieip.com/img/{SLUG}.png"
    if APPLY:
        os.makedirs("img", exist_ok=True)
        open("img/%s.png" % SLUG, "wb").write(open(art_cands[0], "rb").read())

# --- 4. JSON-LD 模板 ---
tpl = None
for p in sorted(glob.glob("najie/blog/*.html"), key=os.path.getmtime, reverse=True):
    if p.endswith("index.html") or SLUG in p: continue
    s = open(p, encoding="utf-8", errors="ignore").read()
    if s.count("application/ld+json") >= 2 and "og:image" in s:
        tpl = s; print("TEMPLATE:", os.path.basename(p)); break
objs = []
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S):
    o = json.loads(b)
    if o.get("@type") == "FAQPage": continue
    objs.append(copy.deepcopy(o))
A = next(o for o in objs if o.get("@type") == "Article")
B = next(o for o in objs if o.get("@type") == "BreadcrumbList")
A.update({"@context": "https://schema.org", "headline": TITLE, "description": DESC, "datePublished": "2026-11-23",
          "dateModified": "2026-11-23", "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "url": URL,
          "inLanguage": "zh-CN", "keywords": "高新认定,高企,2026新规,认定机构,知识产权权重"})
if IMG: A["image"] = IMG
ile = B.get("itemListElement", [])
if len(ile) >= 3:
    ile[2]["name"] = TITLE; ile[2]["item"] = URL

# --- 5. head 手术 ---
h2 = head
h2 = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', h2, count=1)
h2 = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', h2, count=1)
h2 = h2.replace('<meta name="twitter:card" content="summary">', '<meta name="twitter:card" content="summary_large_image">')
add = ('\n<meta name="keywords" content="高新认定,高企,2026新规,认定机构,知识产权权重">'
       '\n<meta property="og:site_name" content="纳杰觅理">'
       + (f'\n<meta property="og:image" content="{IMG}">\n<meta name="twitter:image" content="{IMG}">' if IMG else "")
       + f'\n<meta name="twitter:title" content="{TITLE}">'
       f'\n<meta name="twitter:description" content="{DESC}">'
       f'\n<script type="application/ld+json">{json.dumps(A, ensure_ascii=False)}</script>'
       f'\n<script type="application/ld+json">{json.dumps(B, ensure_ascii=False)}</script>\n')
h2 = h2.replace("</head>", add + "</head>", 1)
newpage = h2 + body
assert newpage.count("application/ld+json") == 2
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', newpage, re.S): json.loads(m)
assert newpage.count("https://schema.org") == 2
assert len(re.findall(r"<h1[\s>]", newpage)) == 1
assert newpage.count("**") == 0
assert newpage[newpage.find("</head>")+7:] == body, "body shifted"
print("PAGE OK size", len(newpage.encode()))

# --- 6. 卡片 ---
def build_card(href, date="2026-11-23", tag="纳杰", org="纳杰 · 高新认定"):
    return (f'<div class="article-card">\n    <h2><a href="{href}">{TITLE}</a></h2>\n'
            f'    <div class="meta"><span class="tag">{tag}</span> {date} · {org}</div>\n'
            f'    <p>{DESC}</p>\n  </div>')

def add_card(idx, href, mode):
    s = open(idx, encoding="utf-8").read()
    if len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(SLUG), s)):
        print("  card exists:", idx); return s
    card = build_card(href)
    if mode == "top":
        s2 = s.replace('<div class="container">\n  ', '<div class="container">\n  ' + card + "\n  ", 1) if '<div class="container">\n  ' in s else s.replace('<div class="container">', '<div class="container">\n  ' + card, 1)
    else:  # append after last card
        pos = [m.start() for m in re.finditer(r'<div class="article-card">', s)]
        assert pos, "no cards"
        end = pos[-1]
        depth = 0
        for m in re.finditer(r"<(/?)div\b", s[end:]):
            depth += -1 if m.group(1) else 1
            if depth == 0:
                end = end + m.end(); break
        end = s.find("</div>", end) + 6 if False else end
        s2 = s[:end] + "\n  " + card + s[end:]
    assert s2 != s
    return s2

nidx_src = add_card("najie/blog/index.html", "./" + SLUG + ".html", "append")
midx_src = add_card("blog/index.html", f"/najie/blog/{SLUG}.html", "top")

# --- 7. articles.json ---
aj = json.load(open("articles.json", encoding="utf-8"))
if not any(SLUG in x.get("url", "") for x in aj):
    aj.insert(0, {"url": f"/najie/blog/{SLUG}.html", "title": TITLE.replace("“", "\"").replace("”", "\""), "date": "2026-11-23", "site": "纳杰觅理"})
    print("articles.json +1 ->", len(aj))

if APPLY:
    open(PAGE, "w", encoding="utf-8").write(newpage)
    open("najie/blog/index.html", "w", encoding="utf-8").write(nidx_src)
    open("blog/index.html", "w", encoding="utf-8").write(midx_src)
    json.dump(aj, open("articles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("APPLIED")
else:
    print("DRY-RUN")
