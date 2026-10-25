#!/usr/bin/env python3
"""SiteOps 2026-10-25: build 2 missing mili pages from md + fix defendant og:image.
Usage: python3 site-inbox/gen-1025-pages.py [--apply]
"""
import os, re, sys, json, copy, shutil, glob

ROOT = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"
APPLY = "--apply" in sys.argv
KEEP_MD_TAIL = True  # 保留 md 原文落款（含联系电话），不替换为统一三行
TPL = os.path.join(ROOT, "mili/blog/20261024-mili-personal-safety-protection-order.html")

TASKS = [
    dict(stem="20261025-mili-ai-label-service", date="2026-10-25",
         cover=os.path.join(ART, "cover-20261025-ai-label.png"),
         tags=["AI生成内容标识", "生成合成内容标识办法", "平台责任"],
         desc="《人工智能生成合成内容标识办法》2025年9月1日施行，同日实施强制性国标GB 45438—2025。办法第六条要求平台三层核查：元数据有隐式标识就加显著提示、用户自行声明就提示可能为生成合成内容、元数据与声明都没有但检测到生成痕迹则按疑似处理——不标不等于不算。本文拆隐式标识必含的三项信息、删标识为什么是最贵的动作、标识之外哪两层更容易翻车。",
         desc_short="平台按第六条三层核查（元数据隐式标识／用户声明／检测痕迹）自动加提示，删水印不等于干净；本文拆隐式标识三项必填、删标识的后果与三层自查动作。"),
    dict(stem="20261024-mili-yetan-will", date="2026-10-24",
         cover=os.path.join(ART, "cover-20261024-yetan-will.png"),
         tags=["遗嘱形式", "意定监护", "慈善信托"],
         desc="叶檀10月20日公开表示已办遗嘱，媒体报道其组合为生前预嘱、意定监护、遗嘱、慈善信托四份文件。本文按《民法典》第1134至1139条讲六种遗嘱形式的形式要件——打印遗嘱须两个以上见证人在场、遗嘱人与见证人在每一页签名并注明年月日；第1140条列明见证人排除范围；公证遗嘱不再优先。另解意定监护解决失能后谁签字、慈善信托解决钱怎么走。",
         desc_short="据《民法典》第1134—1139条拆六种遗嘱形式的形式要件与见证人排除规则，公证遗嘱不再优先；再讲意定监护与慈善信托各解决什么。"),
]

STD_TAIL = ["何自刚 | 北京觅理律师事务所",
            "*本文由 AI 辅助生成与整理，观点与判断由作者审定。*",
            "*本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎联系我们。*"]

def zh_quotes(s):
    out = []
    open_q = True
    for ch in s:
        if ch == '"':
            out.append('“' if open_q else '”')
            open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return zh_quotes(s)

def md_to_html(md):
    lines = md.split("\n")
    # strip markdown html comments
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    lines = md.split("\n")
    title = None
    blocks = []
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        st = ln.strip()
        if not st:
            i += 1; continue
        if st.startswith("# ") and title is None:
            title = st[2:].strip(); i += 1; continue
        if st.startswith("## "):
            blocks.append("<h2>%s</h2>" % inline(st[3:].strip())); i += 1; continue
        if re.match(r"^-{3,}$", st) or re.match(r"^\*{3,}$", st):
            i += 1; continue  # markdown horizontal rule: drop
        if st.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip()); i += 1
            def cells(r):
                return [c.strip() for c in r.strip("|").split("|")]
            head = cells(rows[0])
            body = []
            for r in rows[1:]:
                cs = cells(r)
                if all(re.match(r"^:?-{2,}:?$", c) for c in cs if c != ""):
                    continue
                body.append(cs)
            h = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            blocks.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (h, tb))
            continue
        if st.startswith("> "):
            blocks.append("<p><em>%s</em></p>" % inline(st[2:].strip())); i += 1; continue
        if re.match(r"^[-*] ", st):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i].strip()):
                items.append("<li>%s</li>" % inline(lines[i].strip()[2:].strip())); i += 1
            blocks.append("<ul>%s</ul>" % "".join(items)); continue
        blocks.append("<p>%s</p>" % inline(st)); i += 1
    return title, blocks

def strip_std_tail(title, blocks):
    blocks = [b for b in blocks if not re.match(r"^<p>(<em>)?\s*(何自刚|本文仅代表|本文由 AI)", b)]
    return blocks

# ---------- og image for defendant page (no cover existed) ----------
def make_title_card(title, out_path):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (31, 78, 121))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=(192, 160, 96))
    fp = None
    for cand in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Supplemental/Songti.ttc",
                 "/System/Library/Fonts/Hiragino Sans GB.ttc"]:
        if os.path.exists(cand):
            fp = cand; break
    f_big = ImageFont.truetype(fp, 62) if fp else ImageFont.load_default()
    f_small = ImageFont.truetype(fp, 30) if fp else ImageFont.load_default()
    # wrap by chars
    maxc = 15
    lines = [title[i:i+maxc] for i in range(0, len(title), maxc)]
    y = 190
    for ln in lines[:4]:
        d.text((90, y), ln, font=f_big, fill=(255, 255, 255)); y += 88
    d.text((90, H - 110), "北京觅理律师事务所  ·  najieip.com", font=f_small, fill=(192, 160, 96))
    img.save(out_path)

# ---------- main ----------
tpl = open(TPL, encoding="utf-8").read()
head_end = tpl.find("</head>") + 7
tpl_head, tpl_body = tpl[:head_end], tpl[head_end:]
HEAD_ART = re.search(r'<script type="application/ld\+json">(.*?)</script>', tpl_head, re.S)

def set_meta(head, prop_or_name, value, kind):
    pat = re.compile(r'(<%s %s="%s" content=")[^"]*(")' % ("meta", kind, re.escape(prop_or_name)))
    if pat.search(head):
        return pat.sub(lambda m: m.group(1) + value + m.group(2), head, count=1)
    return head

def build_head(old_head, title, desc, desc_short, url, img_url, tags, date):
    h = old_head
    h = re.sub(r"<title>[^<]*</title>", "<title>%s — 纳杰觅理</title>" % title, h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), h, count=1)
    h = set_meta(h, "og:title", title, "property")
    h = set_meta(h, "og:description", desc_short, "property")
    h = set_meta(h, "og:url", url, "property")
    h = set_meta(h, "og:image", img_url, "property")
    h = set_meta(h, "twitter:image", img_url, "name")
    h = set_meta(h, "twitter:title", title, "name")
    h = set_meta(h, "twitter:description", desc_short, "name")
    h = re.sub(r'(<meta name="keywords" content=")[^"]*(")', lambda m: m.group(1) + ",".join(tags) + m.group(2), h, count=1)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), h, count=1)
    # JSON-LD blocks
    def fix_ld(m):
        raw = m.group(1)
        try:
            obj = json.loads(raw)
        except Exception:
            return m.group(0)
        t = obj.get("@type")
        if t == "Article":
            obj["headline"] = title
            obj["description"] = desc
            if "datePublished" in obj: obj["datePublished"] = date
            if "dateModified" in obj: obj["dateModified"] = date
            if "image" in obj and isinstance(obj["image"], str): obj["image"] = img_url
            if "mainEntityOfPage" in obj:
                mp = obj["mainEntityOfPage"]
                if isinstance(mp, dict) and "@id" in mp: mp["@id"] = url
                elif isinstance(mp, str): obj["mainEntityOfPage"] = url
            if "url" in obj: obj["url"] = url
            if "keywords" in obj: obj["keywords"] = tags
        elif t == "BreadcrumbList":
            it = obj.get("itemListElement", [])
            if len(it) >= 3:
                it[2]["name"] = title
                it[2]["item"] = url
        elif t == "WebPage":
            if "url" in obj: obj["url"] = url
            if "name" in obj: obj["name"] = title
        return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, indent=2) + "</script>"
    h = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, h, flags=re.S)
    return h

def build_page(task):
    stem = task["stem"]
    md = open(os.path.join(ART, stem + ".md"), encoding="utf-8").read()
    title, blocks = md_to_html(md)
    blocks = strip_std_tail(title, blocks) if KEEP_MD_TAIL == False else blocks
    url = "https://najieip.com/mili/blog/%s.html" % stem
    img_url = "https://najieip.com/img/%s.png" % stem
    h1 = zh_quotes(title)
    body_parts = ["<h1>%s</h1>" % h1.replace("&", "&amp;").replace("<", "&lt;")] + blocks
    if not KEEP_MD_TAIL:
        body_parts += ["<p>%s</p>" % inline(x) for x in STD_TAIL]
    article = "<article>\n" + "\n".join(body_parts) + "\n</article>"
    head = build_head(tpl_head, h1, task["desc"], task["desc_short"], url, img_url, task["tags"], task["date"])
    # body surgery: replace template article
    m = re.search(r"<article>.*?</article>", tpl_body, re.S)
    new_body = tpl_body[:m.start()] + article + tpl_body[m.end():]
    page = head + new_body
    return page, title, blocks

def card_tpl(index_path, needle):
    t = open(index_path, encoding="utf-8").read()
    m = re.search(r'<h2><a href="[^"]*%s"' % re.escape(needle), t)
    if not m:
        raise SystemExit("card anchor not found in %s for %s" % (index_path, needle))
    start = t.rfind('<div class="article-card">', 0, m.start())
    d = 0; j = start
    while j < len(t):
        mm = re.match(r'<div\b', t[j:])
        if mm:
            d += 1; j += mm.end(); continue
        mm = re.match(r'</div>', t[j:])
        if mm:
            d -= 1; j += mm.end()
            if d == 0: break
            continue
        j += 1
    return t[start:j]

def make_card(tpl_card, href, title, tags, date, desc, site_label="北京觅理律师事务所"):
    c = tpl_card
    c = re.sub(r'<h2><a href="[^"]*">.*?</a></h2>',
               lambda m: '<h2><a href="%s">%s</a></h2>' % (href, escape_all(title)), c, count=1, flags=re.S)
    c = re.sub(r"(?:<span class=\"tag\">[^<]*</span>)+", "".join('<span class="tag">%s</span>' % escape_all(x) for x in tags), c, count=1)
    c = re.sub(r"\d{4}-\d{2}-\d{2} · [^<]*", "%s · %s" % (date, site_label), c, count=1)
    c = re.sub(r"<p>.*?</p>", "<p>%s</p>" % escape_all(desc), c, count=1, flags=re.S)
    # remove the doubled title text produced by the h2 substitution above
    return c

def escape_all(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def insert_card(index_path, card, date):
    t = open(index_path, encoding="utf-8").read()
    # find all card starts with their date
    positions = []
    for m in re.finditer(r'<div class="article-card">', t):
        seg = t[m.start():m.start() + 1200]
        dm = re.search(r"(\d{4}-\d{2}-\d{2}) ·", seg)
        positions.append((m.start(), dm.group(1) if dm else "0000-00-00"))
    pos = None
    for s, d in positions:
        if d < date:
            pos = s; break
    if pos is None:
        pos = positions[-1][0]
    t2 = t[:pos] + card + "\n  " + t[pos:]
    assert t2.replace(card + "\n  ", "", 1) == t, "outer-edit guard failed"
    return t2

report = {}
pages = {}
for task in TASKS:
    page, title, blocks = build_page(task)
    pages[task["stem"]] = (page, title, task)
    print("[page]", task["stem"], "chars", len(page), "h1", len(re.findall(r"<h1[ >]", page)),
          "ld", len(re.findall(r"application/ld\+json", page)), "h2", len(re.findall(r"<h2[ >]", page)),
          "table", len(re.findall(r"<table", page)), "stars", page.count("**"))
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        json.loads(b)
print("ld json parses OK")

# defendant og image
defendant_img = os.path.join(ROOT, "img/20261025-defendant-info-query-beijing.png")
if not os.path.exists(defendant_img):
    make_title_card("立案卡在「查不到被告」？北京律师现在能查人口信息了", defendant_img)
    print("[img] created", defendant_img, os.path.getsize(defendant_img))

if APPLY:
    # 1. write pages
    for stem, (page, title, task) in pages.items():
        open(os.path.join(ROOT, "mili/blog/%s.html" % stem), "w", encoding="utf-8").write(page)
    # 2. covers
    for task in TASKS:
        dst = os.path.join(ROOT, "img/%s.png" % task["stem"])
        if task["cover"] and os.path.exists(task["cover"]):
            shutil.copy2(task["cover"], dst)
            print("[cover]", task["stem"], os.path.getsize(dst))
        else:
            raise SystemExit("cover missing for " + task["stem"])
    # 3. defendant page og:image + twitter
    dpath = os.path.join(ROOT, "mili/blog/20261025-defendant-info-query-beijing.html")
    d = open(dpath, encoding="utf-8").read()
    if "og:image" not in d:
        img_url = "https://najieip.com/img/20261025-defendant-info-query-beijing.png"
        og_url = re.search(r'<meta property="og:url" content="([^"]+)"', d).group(1)
        anchor = re.search(r'<meta property="og:url" content="[^"]+">\n', d)
        add = ('<meta property="og:image" content="%s">\n'
               '<meta name="twitter:card" content="summary_large_image">\n'
               '<meta name="twitter:image" content="%s">\n'
               '<meta name="twitter:title" content="%s">\n') % (
            img_url, img_url,
            re.search(r'<meta property="og:title" content="([^"]+)"', d).group(1))
        d2 = d[:anchor.end()] + add + d[anchor.end():]
        open(dpath, "w", encoding="utf-8").write(d2)
        print("[fix] defendant og:image added; chars", len(d), "->", len(d2))
    # 4. index cards
    mili_index = os.path.join(ROOT, "mili/blog/index.html")
    main_index = os.path.join(ROOT, "blog/index.html")
    tpl_mili_card = card_tpl(mili_index, "20261024-mili-personal-safety-protection-order.html")
    tpl_main_card = card_tpl(main_index, "20261024-mili-personal-safety-protection-order.html")
    for stem in ["20261025-mili-ai-label-service", "20261024-mili-yetan-will"]:
        page, title, task = pages[stem]
        if "./%s.html" % stem in open(mili_index, encoding="utf-8").read():
            print("[card]", stem, "already present, skip"); continue
        mi = make_card(tpl_mili_card, "./%s.html" % stem, title, task["tags"], task["date"], task["desc_short"])
        t = insert_card(mili_index, mi, task["date"])
        open(mili_index, "w", encoding="utf-8").write(t)
        mn = make_card(tpl_main_card, "/mili/blog/%s.html" % stem, title, task["tags"], task["date"], task["desc_short"])
        t2 = insert_card(main_index, mn, task["date"])
        open(main_index, "w", encoding="utf-8").write(t2)
        print("[card]", stem, "mili+main inserted")
    # 5. articles.json
    aj_path = os.path.join(ROOT, "articles.json")
    aj = json.load(open(aj_path, encoding="utf-8"))
    have = {a["url"] for a in aj}
    for stem in ["20261025-mili-ai-label-service", "20261024-mili-yetan-will"]:
        page, title, task = pages[stem]
        u = "/mili/blog/%s.html" % stem
        if u in have:
            continue
        entry = {"url": u, "title": title, "date": task["date"], "site": "mili",
                 "description": task["desc_short"], "tags": task["tags"]}
        idx = len(aj)
        for k, a in enumerate(aj):
            if a.get("date", "9999") < task["date"]:
                idx = k; break
        aj.insert(idx, entry)
        print("[articles.json]", stem, "inserted at", idx)
    open(aj_path, "w", encoding="utf-8").write(json.dumps(aj, ensure_ascii=False, indent=2) + "\n")
    print("DONE apply")
else:
    print("DRY RUN — pass --apply to write")
