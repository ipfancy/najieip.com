#!/usr/bin/env python3
# Fix 1020: 第8例「部分裸发布」— 补 h1 + Article/BreadcrumbList JSON-LD + og:image/site_name + twitter + keywords + 真摘要
import os, re, json, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

SLUG = "customs-ip-detention-30-day-timeline-20261018"
PAGE = f"mili/blog/{SLUG}.html"
TPL = "mili/blog/customs-ip-post-filing-steps-20261017.html"
COVER_SRC = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-20261018-customs-ip-detention-30-day-timeline.png")
COVER_DST = f"img/{SLUG}.png"
URL = f"https://najieip.com/{PAGE}"
TITLE = "货被海关扣了，20天还是50天？3天内定生死"
DATE = "2026-10-18"

DESC = ("海关扣留货物后头顶挂着两条时钟：依申请扣留20个工作日，依职权扣留50个工作日，到点未收到法院协助执行通知即依法放行。"
        "而扣留通知送达后只有3个工作日提交申请并交担保，逾期海关不得扣留、货直接放行。本文按T+0、T+3、T+20、T+30、T+50逐格对表，"
        "讲清10万元担保上限怎么算、总担保只对已备案商标开放、反担保放行只认专利，以及认定侵权后的四条处置路与费用主张。")

def zh_quotes_text_nodes(s):
    """只在文本节点（> ... <）内把 ASCII 直引号换中文引号，绝不碰标签属性"""
    parts = re.split(r"(<[^>]+>)", s)
    out = []
    for p in parts:
        if p.startswith("<"):
            out.append(p); continue
        # 成对替换
        cnt = [0]
        def rep(m):
            cnt[0] += 1
            return "“" if cnt[0] % 2 == 1 else "”"
        p = re.sub(r'"', rep, p)
        out.append(p)
    return "".join(out)

t = open(PAGE, encoding="utf-8").read()
orig = t
head_end = t.find("</head>") + 7
head = t[:head_end]
body = t[head_end:]

# ---------- 1. cover image ----------
os.makedirs("img", exist_ok=True)
if not os.path.exists(COVER_DST):
    shutil.copy2(COVER_SRC, COVER_DST)
print("cover:", os.path.getsize(COVER_DST), "bytes ->", COVER_DST)

# ---------- 2. JSON-LD from template (deepcopy + overwrite) ----------
tt = open(TPL, encoding="utf-8").read()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tt, re.S)
assert len(blocks) == 2, f"template ld blocks={len(blocks)}"
art = json.loads(blocks[0])
brd = json.loads(blocks[1])
art["headline"] = TITLE
art["description"] = DESC
art["image"] = f"https://najieip.com/img/{SLUG}.png"
art["datePublished"] = DATE
art["dateModified"] = DATE
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
art["url"] = URL
brd["itemListElement"][2]["name"] = TITLE
brd["itemListElement"][2]["item"] = URL
ld_html = "\n".join(
    '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>"
    for o in (art, brd))

# ---------- 3. rebuild head ----------
new_head = head
# description
new_head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{DESC}">', new_head, count=1)
# og:description
new_head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  f'<meta property="og:description" content="{DESC}">', new_head, count=1)
# og extras + keywords + twitter, insert before canonical
inject = (
    f'<meta property="og:image" content="https://najieip.com/img/{SLUG}.png">\n'
    '<meta property="og:site_name" content="北京觅理律师事务所">\n'
    '<meta property="og:locale" content="zh_CN">\n'
    f'<meta name="keywords" content="海关扣留,知识产权海关保护,扣留时限,担保,依职权扣留">\n'
    '<meta name="twitter:title" content="' + TITLE + '">\n'
    f'<meta name="twitter:description" content="{DESC}">\n'
    f'<meta name="twitter:image" content="https://najieip.com/img/{SLUG}.png">\n'
)
new_head = new_head.replace('<meta name="twitter:card" content="summary">',
                            '<meta name="twitter:card" content="summary_large_image">')
new_head = new_head.replace('<link rel="canonical"', inject + '<link rel="canonical"', 1)
# JSON-LD before </head>
new_head = new_head.replace("</head>", ld_html + "\n</head>", 1)

# ---------- 4. body: h1 after <article>, quote normalization ----------
new_body = zh_quotes_text_nodes(body)
if "<h1" not in new_body:
    new_body = new_body.replace("<article>", f"<article>\n<h1>{TITLE}</h1>", 1)

t2 = new_head + new_body
open(PAGE, "w", encoding="utf-8").write(t2)
print("bytes:", os.path.getsize(PAGE), "(was", len(orig.encode()), ")")

# ---------- 5. assertions ----------
def textify(b):
    b = b[b.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    b = re.sub(r'["“”\'’&]', "", b)
    return re.sub(r"\s+", " ", b).strip()

print("h1:", t2.count("<h1"), "ld:", t2.count("application/ld+json"),
      "og:image:", t2.count('property="og:image"'), "stars:", t2.count("**"),
      "desc_len:", len(DESC))
for i, b in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S)):
    json.loads(b)
print("ld json.loads: OK x", t2.count("application/ld+json"))
o_b = re.search(r"<body.*", orig, re.S).group(0)
eq = textify(o_b) == textify(t2[t2.find("<body"):])
print("body text equal:", eq)
if not eq:
    import difflib
    a = textify(o_b).split(); bb = textify(t2[t2.find("<body"):]).split()
    d = list(difflib.unified_diff(a, bb, lineterm="", n=1))
    print("DIFF:", d[:12])
print("div balance:", t2.count("<div") - t2.count("</div>"))
