#!/usr/bin/env python3
"""Rebuild bare-published page from md source using same-day najie house template.
Idempotent-ish; run with --apply to write.
Target: najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html
"""
import os, re, json, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
SLUG = "20261031-mili-ai-product-image-review-tool-neutrality"
BRAND = "najie"
TARGET = os.path.join(REPO, BRAND, "blog", SLUG + ".html")
HOUSE = os.path.join(REPO, "najie/blog/20261031-najie-specialized-sme-patent-screen.html")
APPLY = "--apply" in sys.argv

TITLE = "「工具中立」还能用多久？反不正当竞争法第13条堵死了AI刷好评"
DESC = ("2025年10月15日施行的新《反不正当竞争法》把「帮别人刷」单列为违法行为（第9条第2款，罚则上限200万元），"
        "并把「数据和算法」写进第13条的手段清单（攻击同行罚则最高500万元）。本文拆解两条法条的分界、"
        "AI生成商品图「打了标也不免责」的边界、杭州AI换脸虚假宣传案（2025浙0110民初10694号），"
        "并给电商卖家与工具/代运营服务商各5条可当天执行的自查线。")
KEYWORDS = "反不正当竞争法第13条,工具中立,AI刷好评,虚假宣传,AI生成商品图标识,数据和算法不正当竞争"
DATE = "2026-10-31"

def zh_quotes(s):
    # only in text: "xxx" -> “xxx”
    out = []
    for i, ch in enumerate(s):
        if ch == '"':
            out.append("“" if (i == 0 or s[i-1] in " \n\t（(：:，,。、；;？?！!—>") else "”")
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = zh_quotes(s)
    s = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s

def md_to_blocks(md):
    lines = md.split("\n")
    # strip frontmatter
    if lines[0].strip() == "---":
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        lines = lines[end+1:]
    blocks = []
    for ln in lines:
        s = ln.rstrip()
        st = s.strip()
        if not st:
            continue
        if st.startswith("<!--"):
            continue
        if re.fullmatch(r"-{3,}", st):
            continue
        if st.startswith("# "):
            blocks.append(("h1", st[2:].strip()))
        elif st.startswith("## "):
            blocks.append(("h2", st[3:].strip()))
        elif st.startswith("### "):
            blocks.append(("h3", st[4:].strip()))
        elif re.match(r"^\d+\.\s", st):
            blocks.append(("p", st))  # keep literal numbering as paragraph (no list in source)
        else:
            blocks.append(("p", st))
    return blocks

md = open(os.path.join(ART, SLUG + ".md"), encoding="utf-8").read()
blocks = md_to_blocks(md)
h1s = [b for b in blocks if b[0] == "h1"]
body_blocks = [b for b in blocks if b[0] != "h1"]
print("md blocks:", len(blocks), "h1:", len(h1s), "h2:", sum(1 for b in blocks if b[0] == "h2"))

def textify_md(md):
    t = md
    if t.lstrip().startswith("---"):
        parts = t.split("---", 2)
        t = parts[2] if len(parts) > 2 else t
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"^\s*#{1,6}\s*", "", t, flags=re.M)
    t = re.sub(r"^\s*-{3,}\s*$", " ", t, flags=re.M)
    t = t.replace("**", "").replace("*", "")
    t = re.sub(r'[""]', '"', t)
    return re.sub(r"\s+", "", t)

new_art = ["<article>", f"<h1>{h1s[0][1]}</h1>" if h1s else f"<h1>{TITLE}</h1>"]
for kind, txt in body_blocks:
    if kind in ("h2", "h3"):
        new_art.append(f"<{kind}>{inline(txt)}</{kind}>")
    else:
        new_art.append(f"<p>{inline(txt)}</p>")
new_art.append("</article>")
new_art = "\n".join(new_art)

house = open(HOUSE, encoding="utf-8").read()
hs, he = house.find("<article"), house.find("</article>") + len("</article>")
assert hs > 0 and he > hs, "house article markers"
page = house[:hs] + new_art + house[he:]

# --- head rewrite using original </head> offset ---
head_end = page.find("</head>") + len("</head>")
head, rest = page[:head_end], page[head_end:]

def sub1(pat, rep, s, flags=0):
    new, n = re.subn(pat, rep, s, count=1, flags=flags)
    assert n == 1, f"pattern not found: {pat[:60]}"
    return new

esc = lambda x: x.replace('"', "&quot;")
head = sub1(r"<title>.*?</title>", f"<title>{esc(TITLE)} — 纳杰觅理</title>", head, re.S)
head = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(DESC)}">', head)
head = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(TITLE)}">', head)
head = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(DESC)}">', head)
head = sub1(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{KEYWORDS}">', head)
URL = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
head = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', head)
head = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', head)
IMG = f"https://najieip.com/img/{SLUG}.png"
head = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG}">', head)
head = sub1(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{esc(TITLE)}">', head)
head = sub1(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{esc(DESC)}">', head)
if 'name="twitter:image"' in head:
    head = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG}">', head)

# JSON-LD
def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)

def fixld(o):
    t = o.get("@type")
    types = t if isinstance(t, list) else [t]
    if "Article" in types:
        o["headline"] = TITLE
        o["description"] = DESC
        o["datePublished"] = DATE
        o["dateModified"] = DATE
        o["url"] = URL
        o["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
        if "image" in o:
            o["image"] = [IMG] if isinstance(o["image"], list) else IMG
    if "BreadcrumbList" in types:
        items = o.get("itemListElement", [])
        if len(items) >= 2:
            items[-1]["name"] = TITLE
            items[-1]["item"] = URL

lds = re.findall(r'(<script type="application/ld\+json">)(.*?)(</script>)', head, re.S)
print("ld blocks in house head:", len(lds))
new_head = head
for open_tag, blob, close_tag in lds:
    old = open_tag + blob + close_tag
    obj = json.loads(blob)
    fixld_root = copy.deepcopy(obj)
    walk(fixld_root, fixld)
    new_blob = json.dumps(fixld_root, ensure_ascii=False, indent=2)
    new_head = new_head.replace(old, open_tag + new_blob + close_tag, 1)
    json.loads(new_blob)

page = new_head + rest

# --- assertions ---
assert page.count("<h1") == 1, "h1 count"
assert page.count('application/ld+json') == 2, f"ld count {page.count('application/ld+json')}"
assert 'property="og:image"' in page
m = re.search(r'<link rel="canonical" href="([^"]+)"', page)
assert m and m.group(1).endswith(f"/{BRAND}/blog/{SLUG}.html"), "canonical"
assert page.count("https://schema.org") >= 2
assert "https://***" not in page

# body text vs md text
body = page[page.find("<body"):]
body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
btxt = re.sub(r"<[^>]+>", " ", body)
btxt = btxt.replace("&amp;", "&").replace("&quot;", '"').replace("&gt;", ">").replace("&lt;", "<").replace("&#x27;", "'")
btxt = re.sub(r'["“”]', '"', btxt)
btxt = re.sub(r"\s+", "", btxt)
mdtxt = textify_md(md)
# house footer/nav text present in page but not md -> check md text is a subsequence-by-chunks
missing = [c for c in re.findall(r".{1,40}", mdtxt[:200]) if c and c not in btxt]
print("md chars:", len(mdtxt), "page chars:", len(btxt))
print("md fully contained in page:", mdtxt in btxt)
if mdtxt not in btxt:
    # locate divergence
    import difflib
    for i, s in enumerate(mdtxt):
        if s not in btxt:
            print("first missing char at", i, repr(mdtxt[max(0,i-60):i+60]))
            break
    # chunk check
    step = 200
    for j in range(0, len(mdtxt), step):
        chunk = mdtxt[j:j+step]
        if chunk not in btxt:
            print("chunk FAIL at", j, repr(chunk[:120]))
            break

print("new size:", len(page))
if APPLY:
    open(TARGET, "w", encoding="utf-8").write(page)
    src = os.path.join(ART, "cover-" + SLUG + ".png")
    dst = os.path.join(REPO, "img", SLUG + ".png")
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print("cover copied:", dst, os.path.getsize(dst))
    print("WROTE", TARGET)
else:
    print("DRY RUN (use --apply)")
