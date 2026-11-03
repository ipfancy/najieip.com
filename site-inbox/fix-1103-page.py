import re, os, json, copy, shutil
REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261103-mili-unfair-competition-data-scraping"
PAGE = os.path.join(REPO, "mili/blog", SLUG + ".html")
HOUSE = os.path.join(REPO, "mili/blog", "20261103-mili-patrol-robot-four-questions.html")
URL = f"https://najieip.com/mili/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
TITLE = "抓一次数据：罚53万，再赔500万"
DESC = ("江苏镇江一家公司卖「一键搬家」软件抓取平台商品数据，被市场监管罚 53 万元，随后被淘宝、天猫起诉，"
        "江苏高院二审判赔 500 万元；江西九江同类案件只罚 12 万元——同一套手法差 4.4 倍。本文拆解 2025 年修订的"
        "反不正当竞争法第 13 条第 3 款与第 29 条罚则、最高法第 47 批指导性案例第 262 号的「实质性替代」标准，"
        "并给出企业四步自检：看来源、看方式、看结果、留痕止损。")
KW = "数据抓取,反不正当竞争法,实质性替代,网络不正当竞争,数据权益,技术管理措施"

t = open(PAGE, encoding="utf-8").read()
house = open(HOUSE, encoding="utf-8").read()

# --- 1. text-node quote normalization (never touch tags) ---
def zh_quotes(seg):
    # convert ASCII double quotes in text nodes to Chinese quotes, paired
    out, open_q = [], True
    for ch in seg:
        if ch == '"':
            out.append("“" if open_q else "”"); open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)

body_start = t.find("<body")
head_end = t.find("</head>") + 7
head, body = t[:head_end], t[body_start:]
parts = re.split(r"(<[^>]+>)", body)
for i in range(0, len(parts), 2):  # even indices = text nodes
    if '"' in parts[i]:
        parts[i] = zh_quotes(parts[i])
body2 = "".join(parts)

def textify(s):
    b = s[s.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<figure.*?</figure>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", "", b)
    for ch in ['"', "“", "”", "*", "&nbsp;", " "]:
        b = b.replace(ch, "")
    return b

assert textify(body2) == textify(body), "body text changed beyond quote normalization"

# --- 2. rebuild head from house template ---
h = house[:house.find("</head>") + 7]
def sub1(pat, repl, s):
    s2, n = re.subn(pat, repl, s, count=1, flags=re.S)
    assert n == 1, f"pattern not found: {pat[:50]}"
    return s2

h = sub1(r"<title>.*?</title>", f"<title>{TITLE} — 纳杰觅理</title>", h)
h = sub1(r'<meta name="description" content=".*?">', f'<meta name="description" content="{DESC}">', h)
h = sub1(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{TITLE}">', h)
h = sub1(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{DESC}">', h)
h = sub1(r'<meta name="keywords" content=".*?">', f'<meta name="keywords" content="{KW}">', h)
h = sub1(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{URL}">', h)
h = sub1(r'<meta property="og:image" content=".*?">', f'<meta property="og:image" content="{IMG}">', h)
h = sub1(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{TITLE}">', h)
h = sub1(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{DESC}">', h)
h = sub1(r'<meta name="twitter:image" content=".*?">', f'<meta name="twitter:image" content="{IMG}">', h)
h = sub1(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{URL}">', h)
h = sub1(r'<link rel="alternate" hreflang="zh-CN" href=".*?">', f'<link rel="alternate" hreflang="zh-CN" href="{URL}">', h)
h = sub1(r'<link rel="alternate" hreflang="x-default" href=".*?">', f'<link rel="alternate" hreflang="x-default" href="{URL}">', h)

# JSON-LD: deepcopy house blocks, overwrite fields
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
assert len(blocks) == 2, f"house ld blocks={len(blocks)}"
objs = [json.loads(b) for b in blocks]
assert [o.get("@type") for o in objs] == ["Article", "BreadcrumbList"], [o.get("@type") for o in objs]
art, bc = copy.deepcopy(objs[0]), copy.deepcopy(objs[1])
art.update({"headline": TITLE, "description": DESC, "image": IMG, "datePublished": "2026-11-03",
            "dateModified": "2026-11-03", "keywords": KW, "url": URL})
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
bc["itemListElement"][2].update({"name": TITLE, "item": URL})
new_ld = ['<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>" for o in (art, bc)]
old_ld = ['<script type="application/ld+json">' + b + "</script>" for b in blocks]
for o, n in zip(old_ld, new_ld):
    h = h.replace(o, n, 1)

# hreflang for en/fr not present; keep zh + x-default only
newt = h + body2
# --- 3. cover image into repo ---
src = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-{SLUG}.png")
dst = os.path.join(REPO, "img", SLUG + ".png")
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copy2(src, dst)

open(PAGE, "w", encoding="utf-8").write(newt)

# --- 4. self-checks ---
chk = open(PAGE, encoding="utf-8").read()
lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', chk, re.S)
for b in lds: json.loads(b)
bt = chk[chk.find("<body"):]
print("SIZE", os.path.getsize(PAGE))
print("h1", re.findall(r"<h1[^>]*>(.*?)</h1>", chk)[:1], "h2", chk.count("<h2"))
print("ld", len(lds), "og:image", "og:image" in chk, "twitter:title", "twitter:title" in chk,
      "kw", 'name="keywords"' in chk, "site_name", "og:site_name" in chk)
print("stars", len(re.findall(r"[0-9*]\*\*", bt)), "baretable", len(re.findall(r"<p>\s*\|", bt)))
print("schema.org", chk.count("https://schema.org"), "| ***", chk.count("https://***"))
print("desc_len", len(DESC), "desc_ne_title", DESC.strip() != TITLE)
print("body_text_same", textify(bt) == textify(body))
print("img", os.path.getsize(dst))
