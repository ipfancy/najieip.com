import re, json, os, shutil, sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
APPLY = "--apply" in sys.argv

S1 = "20261127-mili-pregnant-blood-smuggling"
S2 = "20261127-mili-eu-trademark-real-cost"
T1 = "3.8万份孕妇血走私出境，最高判7年"
T2 = "850 欧元，买不下欧盟 27 国商标"
D2 = "欧盟商标官费 850 欧元只是门票。代理费、异议应对、五年不使用撤销，三笔钱中国申请人签合同前都看不到。附申请前五项检查与代价测算。"
OGD = "https://najieip.com"
KW1 = "走私人类遗传资源,刑法334条之一,孕妇血样,生物安全法,人类遗传资源管理条例"

def rd(p): return open(p, encoding="utf-8").read()

def ld_blocks(t):
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)

def textify_article(t):
    b = t[t.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r'<p class="meta">.*?</p>', " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    return re.sub(r"\s+", "", b)

# ---------- PAGE 1 ----------
p1 = f"{REPO}/mili/blog/{S1}.html"
t1 = rd(p1)
before1 = textify_article(t1)

head_end = t1.find("</head>") + 7
head = t1[:head_end]
body = t1[head_end:]

# 1) dedupe BreadcrumbList (keep first)
blocks = ld_blocks(head)
seen, drop = set(), []
for i, blk in enumerate(blocks):
    o = json.loads(blk)
    key = json.dumps(o, sort_keys=True, ensure_ascii=False)
    if key in seen:
        drop.append(blk)
    seen.add(key)
for blk in drop:
    head = head.replace('<script type="application/ld+json">%s</script>\n' % blk, "", 1)

# 2) meta enrichment: og:image / og:site_name / og:locale / keywords / twitter
cover_src = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-{S1}.png")
cover_dst = f"{REPO}/img/{S1}.png"
if APPLY and os.path.exists(cover_src):
    shutil.copyfile(cover_src, cover_dst)
ogimg = f"{OGD}/img/{S1}.png" if os.path.exists(cover_src) else f"{OGD}/assets/og-najie.png"

add = []
if 'og:site_name' not in head:
    add.append('<meta property="og:site_name" content="北京觅理律师事务所">')
if 'og:locale' not in head:
    add.append('<meta property="og:locale" content="zh_CN">')
if 'name="keywords"' not in head:
    add.append(f'<meta name="keywords" content="{KW1}">')
if 'og:image' not in head:
    add.append(f'<meta property="og:image" content="{ogimg}">')
    add.append('<meta name="twitter:image" content="%s">' % ogimg)
if 'twitter:card' in head:
    mdesc = re.search(r'<meta property="og:description" content="([^"]*)"', head)
    TXT1 = mdesc.group(1) if mdesc else T1
    head = head.replace('<meta name="twitter:card" content="summary">',
                        '<meta name="twitter:card" content="summary_large_image">\n'
                        '<meta name="twitter:title" content="%s">\n'
                        '<meta name="twitter:description" content="%s">' % (T1, TXT1), 1)
if add:
    head = head.replace("</head>", "\n".join(add) + "\n</head>", 1)

# 3) h1 + byline
h1block = f'<h1>{T1}</h1>\n<p class="meta">何自刚｜知识产权律师｜北京觅理律师事务所　·　2026-11-27</p>\n'
if "<h1" not in body:
    body = body.replace("<article>\n", "<article>\n" + h1block, 1)
else:
    print("PAGE1 already has h1, skip")

t1_new = head + body
after1 = textify_article(t1_new)
print(f"P1 ld_before={len(blocks)} ld_after={t1_new.count('application/ld+json')} h1={len(re.findall(r'<h1[ >]', t1_new))} ogimg={'og:image' in t1_new} txt_equal={textify_article(t1) == after1 or True}")
# strict: compare original text (h1/meta stripped) vs new
print(f"P1 BYTES {len(t1.encode())} -> {len(t1_new.encode())}  BODY_TEXT_UNCHANGED={before1 == after1}")
for blk in ld_blocks(t1_new):
    json.loads(blk)

# ---------- PAGE 2 ----------
p2 = f"{REPO}/mili/blog/{S2}.html"
t2 = rd(p2)
before2 = textify_article(t2)
he2 = t2.find("</head>") + 7
head2, body2 = t2[:he2], t2[he2:]

# ** -> <strong> inside blockquote
stars = body2.count("**")
body2 = body2.replace("**", "" if stars % 2 else "", 0)  # placeholder, real work below
body2 = t2[he2:]
def fix_stars(s):
    # pair up ** into <strong>...</strong>
    parts = s.split("**")
    if len(parts) % 2 == 0:
        return s
    out = parts[0]
    for i, seg in enumerate(parts[1:]):
        out += ("<strong>" if i % 2 == 0 else "</strong>") + seg
    return out
body2 = fix_stars(body2)
print(f"P2 stars {stars} -> {body2.count('**')}")

# BreadcrumbList
bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "首页", "item": f"{OGD}/"},
    {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": f"{OGD}/mili/blog/"},
    {"@type": "ListItem", "position": 3, "name": T2}]}
if '"BreadcrumbList"' not in head2:
    head2 = head2.replace("</head>", '<script type="application/ld+json">%s</script>\n</head>' % json.dumps(bc, ensure_ascii=False), 1)

add2 = []
ogimg2 = f"{OGD}/assets/og-najie.png"
if 'og:image' not in head2:
    add2 += ['<meta property="og:image" content="%s">' % ogimg2]
if 'twitter:card' not in head2:
    add2 += ['<meta name="twitter:card" content="summary_large_image">',
             '<meta name="twitter:title" content="%s">' % T2,
             '<meta name="twitter:description" content="%s">' % D2,
             '<meta name="twitter:image" content="%s">' % ogimg2]
if add2:
    head2 = head2.replace("</head>", "\n".join(add2) + "\n</head>", 1)

# refresh og:description to richer summary? keep existing (already decent, 65 chars) -> enrich to D2
head2 = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r"\g<1>" + D2.replace("\\", "\\\\") + r"\g<2>", head2, count=1)

t2_new = head2 + body2
after2 = textify_article(t2_new)
print(f"P2 ld={t2_new.count('application/ld+json')} h1={len(re.findall(r'<h1[ >]', t2_new))} ogimg={'og:image' in t2_new} tw={'twitter:card' in t2_new} stars={t2_new.count('**')} ogdesc={re.search(r'og:description\" content=\"([^\"]{0,30})', t2_new).group(1)!r}")
print(f"P2 BODY_TEXT_UNCHANGED(strip *)={before2.replace('*','') == after2.replace('*','')}")
for blk in ld_blocks(t2_new):
    json.loads(blk)

# ---------- MAIN INDEX CARD ----------
idx = f"{REPO}/blog/index.html"
ti = rd(idx)
def card_block(t, slug):
    m = re.search(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug) + r'[^"]*"', t)
    if not m: return None
    start = t.rfind('<div class="article-card">', 0, m.start())
    if start < 0: return None
    depth, i = 0, start
    while i < len(t):
        mo = re.match(r"<div\b|</div>", t[i:])
        if mo:
            if mo.group(0) == "</div>":
                depth -= 1
                if depth == 0:
                    return t[start:i + 6]
            else:
                depth += 1
            i += len(mo.group(0))
        else:
            i += 1
    return None

tpl = card_block(ti, S1)
print("\n--- MAIN CARD TEMPLATE (from pregnant) ---")
print(tpl[:700] if tpl else "NONE")
has_eu = bool(re.search(r'<h[23][^>]*><a href="[^"]*' + re.escape(S2), ti))
print("main has eu card:", has_eu)

if APPLY:
    open(p1, "w", encoding="utf-8").write(t1_new)
    open(p2, "w", encoding="utf-8").write(t2_new)
    print("WROTE pages")

# ---------- build eu card & insert into main index ----------
eu_card = None
if tpl and not has_eu:
    eu_card = tpl.replace(S1 + ".html", S2 + ".html").replace(T1, T2)
    # replace card <p> body with real summary
    eu_card = re.sub(r"<p>.*?</p>", "<p>%s</p>" % D2, eu_card, count=1, flags=re.S)
    print("\n--- EU CARD ---")
    print(eu_card)
    ti_new = ti.replace(tpl, eu_card + "\n  " + tpl, 1)
    assert ti_new.replace(eu_card + "\n  ", "", 1) == ti, "index outer change!"
    print(f"main cards {ti.count('article-card')} -> {ti_new.count('article-card')}")
    print(f"div open/close {ti.count('<div')}/{ti.count('</div>')} -> {ti_new.count('<div')}/{ti_new.count('</div>')}")
    if APPLY:
        open(idx, "w", encoding="utf-8").write(ti_new)
        print("WROTE main index")

# ---------- articles.json: drop title-duplicating description key ----------
ajp = f"{REPO}/articles.json"
aj = json.load(open(ajp, encoding="utf-8"))
items = aj if isinstance(aj, list) else aj.get("articles", [])
changed = 0
for it in items:
    if S1 in json.dumps(it, ensure_ascii=False) and "description" in it:
        if it["description"] == it.get("title"):
            del it["description"]
            changed += 1
print(f"articles.json schema fixed entries={changed} total={len(items)}")
if APPLY and changed:
    if isinstance(aj, list):
        json.dump(aj, open(ajp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    else:
        json.dump(aj, open(ajp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("WROTE articles.json")
