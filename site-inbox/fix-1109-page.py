import re, os, sys, json, shutil, copy

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261109-mili-prepaid-card-refund"
TITLE = "办卡的钱能退回多少？第15条给算法，第16条管利息"
TPL_SLUG = "20261108-mili-family-theft-leniency"
BRAND = "mili"
APPLY = "--apply" in sys.argv

DESC = ("预付卡退款怎么算：法释〔2025〕4号第九条把「一经开卡、概不退卡」直接列为无效格式条款（2025年5月1日起施行）。第15条定本金算法——扣已兑付价款，员工提成与营销成本不算合理费用；第16条按关店迁店或消费者自身原因分两档计息；第25条把消费记录的举证责任压给经营者；第6条可追加商场出租方。附三种退不了的情形和当下能做的三件事。")
KEYWORDS = "预付卡退款,法释2025-4号,第15条退款算法,第16条利息,商场出租方责任"

def zh_quotes(s):
    out = []
    for seg in re.split(r"(<[^>]+>)", s):
        if seg.startswith("<"):
            out.append(seg)
        else:
            seg = re.sub(r'"([^"\n]*)"', "\u201c\\1\u201d", seg)
            seg = re.sub(r"'([^'\n]*)'", "\u2018\\1\u2019", seg)
            out.append(seg)
    return "".join(out)

def inline(s):
    s = re.sub(r"\*\*([^*\n]{1,300})\*\*", r"<strong>\1</strong>", s)
    return zh_quotes(s)

# ---------- 1. parse md -> article inner HTML ----------
mdp = "/Users/ziganghe/wiki/digital-employees/articles/" + SLUG + ".md"
raw = open(mdp, encoding="utf-8").read()
body_md = raw.split("---", 2)[2]
body_md = re.sub(r"<!--.*?-->", "", body_md, flags=re.S)
lines = [l.rstrip() for l in body_md.split("\n")]

out, ol = [], []
def flush_ol():
    global ol
    if ol:
        out.append("<ol>" + "".join("<li>" + inline(x) + "</li>" for x in ol) + "</ol>")
        ol = []

for ln in lines:
    s = ln.strip()
    if not s:
        continue
    if s.startswith("# "):
        continue
    if s.startswith("## "):
        flush_ol()
        out.append("<h2>" + inline(s[3:]) + "</h2>")
        continue
    if re.match(r"^\d+\.\s+", s):
        ol.append(re.sub(r"^\d+\.\s+", "", s))
        continue
    flush_ol()
    out.append("<p>" + inline(s) + "</p>")
flush_ol()

def textify(s):
    s = re.sub(r"<h1[^>]*>.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2[^>]*>.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[-]{3,}", "", s)
    return re.sub(r"[\s\|\*#:`\"\u201c\u201d']", "", s)

def norm_md(s):
    s = re.sub(r"^\s*#{1,2}\s+.*$", " ", s, flags=re.M)
    s = re.sub(r"^\s*\d+\.\s+", "", s, flags=re.M)
    s = re.sub(r"[-]{3,}", "", s)
    return re.sub(r"[\s\|\*#:`\"\u201c\u201d']", "", s)

mdt = norm_md(body_md)

# ---------- 2. template pieces ----------
tp = open(os.path.join(REPO, BRAND, "blog", TPL_SLUG + ".html"), encoding="utf-8").read()
head_end = tp.find("</head>") + 7
tpl_head = tp[:head_end]
tpl_nav = re.search(r"<nav>.*?</nav>", tp, re.S).group(0)
tpl_footer = re.search(r"<footer>.*?</footer>", tp, re.S).group(0)
lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl_head, re.S)
art_obj = None
bc_obj = None
for blk in lds:
    o = json.loads(blk)
    if o.get("@type") == "Article":
        art_obj = o
    elif o.get("@type") == "BreadcrumbList":
        bc_obj = o

URL = "https://najieip.com/%s/blog/%s.html" % (BRAND, SLUG)
IMG = "https://najieip.com/img/%s.png" % SLUG

# ---------- 3. rebuild head ----------
def set_meta(h, needle_re, newline):
    h2, n = re.subn(needle_re, newline, h, count=1, flags=re.S)
    assert n == 1, needle_re
    return h2

head = tpl_head
head = re.sub(r"<title>.*?</title>", "<title>%s — 纳杰觅理</title>" % TITLE, head, count=1, flags=re.S)
head = set_meta(head, r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % DESC)
head = set_meta(head, r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % TITLE)
head = set_meta(head, r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % DESC)
head = set_meta(head, r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % URL)
head = set_meta(head, r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="%s">' % IMG)
head = set_meta(head, r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="%s">' % TITLE)
head = set_meta(head, r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="%s">' % DESC)
head = set_meta(head, r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="%s">' % IMG)
head = set_meta(head, r'<meta name="keywords" content="[^"]*">', '<meta name="keywords" content="%s">' % KEYWORDS)
head = set_meta(head, r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % URL)
head = re.sub(r'<link rel="alternate" hreflang="zh-CN" href="[^"]*">', '<link rel="alternate" hreflang="zh-CN" href="%s">' % URL, head)
head = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', '<link rel="alternate" hreflang="x-default" href="%s">' % URL, head)

# JSON-LD rebuild
art = copy.deepcopy(art_obj)
art["headline"] = TITLE
art["description"] = DESC
art["datePublished"] = "2026-11-09"
art["dateModified"] = "2026-11-09"
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
art["url"] = URL
art["image"] = IMG
if "keywords" in art:
    art["keywords"] = [k for k in KEYWORDS.split(",")]
bc = copy.deepcopy(bc_obj)
bc["itemListElement"][2]["name"] = TITLE
bc["itemListElement"][2]["item"] = URL

old_ld = re.findall(r'<script type="application/ld\+json">.*?</script>', head, re.S)
assert len(old_ld) == 2, len(old_ld)
head = head.replace(old_ld[0], '<script type="application/ld+json">\n' + json.dumps(art, ensure_ascii=False, indent=2) + '\n</script>')
head = head.replace(old_ld[1], '<script type="application/ld+json">\n' + json.dumps(bc, ensure_ascii=False, indent=2) + '\n</script>')

# ---------- 4. assemble page ----------
seps = []
for blk in out:
    seps.append(blk)
inner = "\n<br>\n".join(seps)
page = (head + "\n<body>\n" + tpl_nav + "\n<article>\n<h1>" + TITLE + "</h1>\n<br>\n" + inner +
        "\n</article>\n" + tpl_footer + "\n</body>\n</html>\n")

# ---------- 5. checks ----------
btxt = page[page.find("<body"):]
art_slice = btxt[btxt.find("<article>"):btxt.find("</article>")]
pgt = textify(art_slice)
contained = mdt in pgt
print("NEW bytes", len(page.encode()), "h1", page.count("<h1"), "ld", page.count("application/ld+json"),
      "h2", page.count("<h2"), "stars", page.count("**"), "ogimage", "og:image" in page)
print("md_contained", contained, "md_len", len(mdt), "pg_len", len(pgt))
if not contained:
    for i in range(min(len(mdt), len(pgt))):
        if mdt[i] != pgt[i]:
            print("diff_at", i, "MD:", mdt[max(0, i-25):i+45], "|| PG:", pgt[max(0, i-25):i+45])
            break
    else:
        print("prefix equal, len diff", len(mdt) - len(pgt), "| md tail:", mdt[-60:], "| pg tail:", pgt[-60:])
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
    json.loads(blk)
print("ld_json_ok")
print("hreflang", len(re.findall(r'hreflang="', page)))

# ---------- 6. index cards ----------
def extract_card(text, slug):
    m = re.search(r'<h2><a href="[^"]*' + re.escape(slug), text)
    if not m:
        m = re.search(r'<h3><a href="[^"]*' + re.escape(slug), text)
    start = text.rfind('<div class="article-card">', 0, m.start())
    depth = 0
    i = start
    while i < len(text):
        nx = re.search(r"<div\b|</div>", text[i:])
        if not nx:
            break
        if nx.group(0) == "</div>":
            depth -= 1
            i += nx.end()
            if depth == 0:
                return text[start:i]
        else:
            depth += 1
            i += nx.end()
    raise RuntimeError("card end not found")

def make_card(tpl, href, title, desc, tags, date):
    c = re.sub(r'(<h2><a href=")[^"]*(")', lambda m: m.group(1) + href + m.group(2), tpl, count=1)
    c = re.sub(r'(<h2><a[^>]*>).*?(</a>)', lambda m: m.group(1) + title + m.group(2), c, count=1, flags=re.S)
    c = re.sub(r'(?:<span class="tag">[^<]*</span>)+', "".join('<span class="tag">%s</span>' % t for t in tags), c, count=1)
    c = re.sub(r"(<p>).*?(</p>)", lambda m: m.group(1) + desc + m.group(2), c, count=1, flags=re.S)
    c = re.sub(r"2026-11-08", date, c)
    return c

def insert_card(path, card, date, brand_dir):
    t = open(path, encoding="utf-8").read()
    if SLUG in t and ('href="' + ("/" + brand_dir + "/blog/" + SLUG if brand_dir else "./" + SLUG)) in t:
        print("CARD exists", path)
        return t, 0
    # find insertion point: first card whose date < our date
    pos = None
    for m in re.finditer(r'<div class="article-card">', t):
        blk = t[m.start():m.start() + 2500]
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
        if dm and dm.group(1) < date:
            pos = m.start()
            break
    if pos is None:
        pos = re.search(r'<div class="container">', t).end()
    t2 = t[:pos] + card + "\n  " + t[pos:]
    assert t2.replace(card + "\n  ", "", 1) == t
    return t2, 1

cards = []
mili_idx = os.path.join(REPO, "mili/blog/index.html")
mt = open(mili_idx, encoding="utf-8").read()
mtpl = extract_card(mt, TPL_SLUG)
mcard = make_card(mtpl, "./" + SLUG + ".html", TITLE, DESC[:120], ["预付卡", "消费者权益", "格式条款"], "2026-11-09")
main_idx = os.path.join(REPO, "blog/index.html")
nt = open(main_idx, encoding="utf-8").read()
ntpl = extract_card(nt, TPL_SLUG) if TPL_SLUG in nt else extract_card(nt, "20261107-mili-unpaid-trial-shigang")
ncard = make_card(ntpl, "/" + BRAND + "/blog/" + SLUG + ".html", TITLE, DESC[:120], ["预付卡", "消费者权益", "格式条款"], "2026-11-09")
print("MILI CARD >>>", repr(mcard[:300]))
print("MAIN CARD >>>", repr(ncard[:300]))
print("mili cards", mt.count('<div class="article-card">'), "main cards", nt.count('<div class="article-card">'))

if APPLY:
    open(os.path.join(REPO, BRAND, "blog", SLUG + ".html"), "w", encoding="utf-8").write(page)
    cover = "/Users/ziganghe/wiki/digital-employees/articles/cover-" + SLUG + ".png"
    shutil.copy(cover, os.path.join(REPO, "img", SLUG + ".png"))
    mt2, a1 = insert_card(mili_idx, mcard, "2026-11-09", "mili")
    nt2, a2 = insert_card(main_idx, ncard, "2026-11-09", "")
    if a1:
        open(mili_idx, "w", encoding="utf-8").write(mt2)
    if a2:
        open(main_idx, "w", encoding="utf-8").write(nt2)
    inbox = os.path.join(REPO, "site-inbox", SLUG + ".html")
    if os.path.exists(inbox):
        os.remove(inbox)
        print("inbox copy removed")
    print("APPLIED cards_added", a1 + a2)
    for p, lbl in ((mili_idx, "mili"), (main_idx, "main")):
        s = open(p, encoding="utf-8").read()
        s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
        print(lbl, "cards", s.count('<div class="article-card">'), "open", s.count("<div"), "close", s.count("</div>"))
