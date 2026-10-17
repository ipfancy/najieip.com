#!/usr/bin/env python3
"""2026-10-17 fix: partial bare publish page (mili customs-ip-post-filing-steps-20261017).
Adds h1 + Article/BreadcrumbList JSON-LD + og:image/og:site_name/twitter/keywords + real description.
Body text must stay byte-identical (after removing new h1 + scripts).
"""
import os, re, json, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "customs-ip-post-filing-steps-20261017"
PAGE = os.path.join(REPO, f"mili/blog/{SLUG}.html")
TPL = os.path.join(REPO, "mili/blog/20261015-ip-4-hard-deadlines-buju-revision.html")
COVER = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-20261017-customs-ip-post-filing-steps.png")
IMG = os.path.join(REPO, f"img/{SLUG}.png")

TITLE = "货被海关扣了怎么办？备案后的三步处置（10月14日新规）"
DESC = ("海关总署审核通过知识产权备案3.52万件、全国海关查扣侵权货物8642万件。备案不等于海关替你拦货："
        "依职权扣留要你在通知送达后3个工作日内申请扣留并交担保，错过即依法放行。本文讲清依申请与依职权的区别、"
        "担保怎么算，以及货被扣后按10月14日新规走的三步处置流程。")
KW = "海关备案,知识产权海关保护,海关扣货,依职权扣留,担保,三步处置,10月14日新规"
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
IMGURL = f"https://najieip.com/img/{SLUG}.png"

t = open(PAGE, encoding="utf-8").read()
orig = t
head_end = t.find("</head>") + 7
assert head_end > 7, "no </head>"
head = t[:head_end]
body = t[head_end:]

def textify(s):
    b = s[s.find("<body"):] if "<body" in s else s
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)   # new h1 is an addition
    b = re.sub(r"<nav>.*?</nav>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", "", b)
    b = b.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
    return re.sub(r"\s+", "", b)

pre_text = textify(orig)

# --- head rewrite ---
head = re.sub(r'<meta name="description" content="[^"]*">',
              f'<meta name="description" content="{DESC}">', head, count=1)
head = re.sub(r'<meta property="og:description" content="[^"]*">',
              f'<meta property="og:description" content="{DESC}">', head, count=1)
head = head.replace('<meta name="twitter:card" content="summary">',
                    '<meta name="twitter:card" content="summary_large_image">')

extra = (f'\n<meta property="og:site_name" content="北京觅理律师事务所">'
         f'\n<meta property="og:image" content="{IMGURL}">'
         f'\n<meta name="keywords" content="{KW}">'
         f'\n<meta name="twitter:title" content="{TITLE}">'
         f'\n<meta name="twitter:description" content="{DESC}">'
         f'\n<meta name="twitter:image" content="{IMGURL}">')
anchor = re.search(r'<meta property="og:url" content="[^"]*">', head)
assert anchor
head = head[:anchor.end()] + extra + head[anchor.end():]

# --- JSON-LD from template (deepcopy + override) ---
tt = open(TPL, encoding="utf-8").read()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tt, re.S)
art = json.loads(blocks[0])
bc = json.loads(blocks[1])
art = copy.deepcopy(art)
art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMGURL
art["datePublished"] = "2026-10-17"
art["dateModified"] = "2026-10-17"
art["mainEntityOfPage"] = URL
art["url"] = URL
bc = copy.deepcopy(bc)
bc["itemListElement"][2]["name"] = TITLE
bc["itemListElement"][2]["item"] = URL
ld_txt = ""
for o in (art, bc):
    ld_txt += ('<script type="application/ld+json">'
               + json.dumps(o, ensure_ascii=False) + "</script>\n")
head = head.replace("</head>", ld_txt + "</head>")

# --- body: insert h1 after <article> ---
assert "<h1" not in body
body2 = body.replace("<article>\n", f"<article>\n<h1>{TITLE}</h1>\n<br>\n", 1)
assert body2 != body

new = head + body2
new_text = textify(new)
if new_text != pre_text:
    import difflib
    print("BODY TEXT MISMATCH")
    for l in list(difflib.unified_diff([pre_text], [new_text], lineterm=""))[:6]:
        print(l[:300])
    sys.exit(1)

if "--apply" not in sys.argv:
    print("DRY-RUN ok. size %d -> %d" % (len(orig.encode()), len(new.encode())))
    print("h1=%d ld=%d og:image=%d" % (
        len(re.findall(r"<h1[\s>]", new)),
        len(re.findall(r"application/ld\+json", new)),
        len(re.findall(r'property="og:image"', new))))
    sys.exit(0)

open(PAGE, "w", encoding="utf-8").write(new)
os.makedirs(os.path.dirname(IMG), exist_ok=True)
shutil.copy2(COVER, IMG)
print("APPLIED", os.path.getsize(PAGE), "B; cover ->", IMG, os.path.getsize(IMG), "B")
print("body_text_identical:", textify(open(PAGE, encoding="utf-8").read()) == pre_text)
print("h1=%d h2=%d ld=%d" % (
    len(re.findall(r"<h1[\s>]", new)), len(re.findall(r"<h2[\s>]", new)),
    len(re.findall(r"application/ld\+json", new))))
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', new, re.S):
    json.loads(blk)
print("ld_json_parse: all OK")
print("schema_org=%d bad_redact=%d stars=%d" % (new.count("https://schema.org"), new.count("https://***"), new.count("**")))
