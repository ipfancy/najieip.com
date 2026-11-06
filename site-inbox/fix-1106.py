#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-11-06 daily: rebuild 3 partial-bare mili pages from md + fill index cards."""
import os, re, sys, json, copy, shutil, html as H

REPO = os.path.expanduser("~/wiki/najieip-verify")
MDD = os.path.expanduser("~/wiki/digital-employees/articles")
TPL = os.path.join(REPO, "mili", "blog", "20261106-mili-appraisal-opinion-review.html")
APPLY = "--apply" in sys.argv

PAGES = [
    dict(slug="20261103-mili-guarantee-period-six-months", date="2026-11-03",
         title="只写“担保人”三个字，债主得先去告欠钱的人",
         desc=("保证合同只写「担保人」没写「连带」，法律推定为一般保证：债权人得先把债务人告到判决、强制执行还拿不到钱，才轮到你。"
               "真正卡人的是 6 个月保证期间而不是 3 年诉讼时效，「直到本息还清为止」也还是 6 个月，过了再让你签字也不算。"),
         kw="保证合同,一般保证,连带责任保证,保证期间,民法典担保制度解释,债权人主张",
         section="民商事诉讼"),
    dict(slug="20261104-mili-inventor-reward-5-percent", date="2026-11-04",
         title="专利产品挣4.8亿，发明人只拿80万：5%是底线",
         desc=("（2024）最高法知民终907号：生物制剂五个年度营业利润 48018 万元，离职发明人只拿 80 万元一次性了断。"
               "职务发明报酬是法定之债，没有约定或规章就按投产后连续 3-5 年、每年营业利润 5% 计提；产品整体亏损不是拒付理由；2024 年 1 月 20 日后标准提高。"),
         kw="职务发明,发明人报酬,专利法第十五条,营业利润5%,最高法判例,专利运营",
         section="知识产权"),
    dict(slug="20261106-mili-nda-vs-noncompete", date="2026-11-06",
         title="劳动合同法第23条和第25条：保密协议和竞业限制，签错两头空",
         desc=("保密协议和竞业限制不是一回事，差的那部分全是钱：月薪两万的研发签错一份，公司要么白付 14.4 万补偿，要么连起诉的门都进不去。"
               "第 23 条管补偿与违约金，第 25 条把可约定违约金的情形锁死，一张表看清保密、竞业、脱密期三件事该怎么签。"),
         kw="保密协议,竞业限制,劳动合同法第23条,劳动合同法第25条,违约金,劳动用工合规",
         section="劳动用工"),
]

def zh_quotes(s):
    out, inside = [], 0
    for ch in s:
        if ch == '"':
            out.append('“' if inside % 2 == 0 else '”'); inside += 1
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = H.escape(s, quote=False)
    s = re.sub(r'\*\*([^*\n]{1,300})\*\*', r'<strong>\1</strong>', s)
    return s

def build_body(slug):
    md = open(os.path.join(MDD, slug + ".md"), encoding="utf-8").read()
    md = md.split("---", 2)[2] if md.startswith("---") else md
    lines = [l.rstrip() for l in md.split("\n")]
    out, i = [], 0
    while i < len(lines):
        l = lines[i].strip()
        if not l:
            i += 1; continue
        if l.startswith("<!--"):
            i += 1; continue
        if l.startswith("# "):
            out.append("<h1>" + inline(l[2:]) + "</h1>"); i += 1; continue
        if l.startswith("## "):
            out.append("<h2>" + inline(l[3:]) + "</h2>"); i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip()); i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            hdr = cells[0]
            body = [c for c in cells[1:] if not all(re.fullmatch(r':?-{2,}:?', x or '-') for x in c)]
            t = ['<table class="data">',
                 "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in hdr) + "</tr></thead>",
                 "<tbody>"]
            for c in body:
                t.append("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in c) + "</tr>")
            t += ["</tbody>", "</table>"]
            out.append("\n".join(t)); continue
        if l.startswith(">"):
            q = l.lstrip("> ").strip()
            out.append("<blockquote><p>" + inline(q) + "</p></blockquote>"); i += 1; continue
        if re.fullmatch(r'\*[^*].*\*', l):
            out.append("<p><em>" + inline(l.strip("*")) + "</em></p>"); i += 1; continue
        out.append("<p>" + inline(l) + "</p>"); i += 1
    return "\n".join(out)

# ---- house template ----
tpl = open(TPL, encoding="utf-8").read()
nav = re.search(r'<nav>.*?</nav>', tpl, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', tpl, re.S).group(0)
objs = [json.loads(b) for b in re.findall(r'application/ld\+json[^>]*>(.*?)</script>', tpl, re.S)]
print("template ld types:", [o.get("@type") for o in objs])
art_t = next(o for o in objs if o.get("@type") in ("Article", "BlogPosting"))
brd_t = next(o for o in objs if o.get("@type") == "BreadcrumbList")

def norm(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = H.unescape(s)
    for ch in '“”"\'’*|#>\u3000`:':
        s = s.replace(ch, ' ')
    s = re.sub(r"-{2,}", " ", s)
    return re.sub(r'\s+', '', s)

results = []
for P in PAGES:
    slug, brand, date = P["slug"], "mili", P["date"]
    PAGE = os.path.join(REPO, brand, "blog", slug + ".html")
    URL = f"https://najieip.com/{brand}/blog/{slug}.html"
    IMG = f"https://najieip.com/img/{slug}.png"
    TITLE, DESC, KW = P["title"], P["desc"], P["kw"]

    art = copy.deepcopy(art_t); brd = copy.deepcopy(brd_t)
    art["headline"] = TITLE; art["description"] = DESC; art["image"] = IMG
    art["datePublished"] = date; art["dateModified"] = date
    art["url"] = URL; art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
    art["keywords"] = KW.split(",")
    art["inLanguage"] = "zh-CN"
    if "articleSection" in art: art["articleSection"] = P["section"]
    il = brd.get("itemListElement", [])
    if len(il) >= 3:
        il[1]["name"] = "觅理博客"; il[1]["item"] = "https://najieip.com/mili/blog/"
        il[2]["name"] = TITLE; il[2]["item"] = URL

    head = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KW}">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:site_name" content="纳杰知产">
<meta property="og:locale" content="zh_CN">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{IMG}">
<link rel="canonical" href="{URL}">
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">
{json.dumps(art, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(brd, ensure_ascii=False, indent=2)}
</script>
</head>'''
    body = build_body(slug)
    newpage = head + "\n<body>\n" + nav + "\n<article>\n" + body + "\n</article>\n" + footer + "\n</body>\n</html>\n"

    b = newpage[newpage.find("<body"):]
    chk = {
        "h1": len(re.findall(r'<h1[ >]', newpage)) == 1,
        "h2": len(re.findall(r'<h2[ >]', newpage)),
        "ld": len(re.findall(r'application/ld\+json', newpage)) == 2,
        "og_image": 'property="og:image"' in newpage,
        "desc_real": len(DESC) > 80 and TITLE[:10] not in DESC,
        "bare_table": len(re.findall(r'<p>\s*\|', b)),
        "stars": b.count("**"),
        "schema": newpage.count("https://schema.org"),
        "triple": newpage.count("https://***"),
        "json_ok": True,
    }
    for blk in re.findall(r'application/ld\+json[^>]*>(.*?)</script>', newpage, re.S):
        try: json.loads(blk)
        except Exception as e: chk["json_ok"] = str(e)[:70]
    mdn = norm(open(os.path.join(MDD, slug + ".md"), encoding="utf-8").read().split("---", 2)[2])
    bn = norm(newpage[newpage.find("<article>"):newpage.find("</article>")])
    chk["md_contains"] = mdn in bn
    if not chk["md_contains"]:
        k = 0
        while k < min(len(mdn), len(bn)) and mdn[k] == bn[k]: k += 1
        chk["diff_at"] = (k, mdn[max(0, k-30):k+30], bn[max(0, k-30):k+30])
    print(slug, "| old", os.path.getsize(PAGE), "-> new", len(newpage.encode()), "|", json.dumps(chk, ensure_ascii=False))
    results.append((PAGE, newpage, slug))
    if APPLY:
        open(PAGE, "w", encoding="utf-8").write(newpage)
        cov = os.path.join(MDD, f"cover-{slug}.png")
        if os.path.exists(cov):
            shutil.copy(cov, os.path.join(REPO, "img", slug + ".png"))
            print("   cover copied", os.path.getsize(cov))

# ---- index cards ----
def cards(t):
    res = []
    for m in re.finditer(r'<div class="article-card">', t):
        start = m.start(); d = 0; i = start
        while i < len(t):
            nx = t.find("<div", i); nc = t.find("</div>", i)
            if nc == -1: break
            if nx != -1 and nx < nc:
                d += 1; i = nx + 4
            else:
                d -= 1; i = nc + 6
                if d == 0: break
        blk = t[start:i]
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
        res.append([start, i, dm.group(1) if dm else "", blk])
    return res

CARDS = [(p["slug"], p["date"], p["title"], p["desc"], p["kw"]) for p in PAGES]
CARDS.append(("20261106-mili-appraisal-opinion-review", "2026-11-06",
              "鉴定意见怎么写才算合格：五项审查",
              "伤残等级、三期、护理依赖，三组数字一出来赔偿金额就定了。本文把鉴定意见拆成五项审查——形式、程序、伤残等级、三期、护理依赖，给出当庭质证的四步顺序与三个最常见瑕疵。",
              "交通事故,司法鉴定,质证"))

def make_card(slug, date, title, desc, kw, is_main, tmpl_card):
    c = tmpl_card
    old_href = re.search(r'<h2><a href="([^"]+)"', c).group(1)
    if is_main:
        href = f"/mili/blog/{slug}.html"
    else:
        href = f"./{slug}.html"
    c = c.replace(old_href, href)
    c = re.sub(r'(<h2><a href="[^"]+">).*?(</a></h2>)', lambda m: m.group(1) + H.escape(title, quote=False) + m.group(2), c, count=1, flags=re.S)
    tags = "".join(f'<span class="tag">{k}</span>' for k in kw.split(",")[:3])
    c = re.sub(r'(?:<span class="tag">[^<]*</span>)+', tags, c, count=1)
    c = re.sub(r'\d{4}-\d{2}-\d{2}', date, c, count=1)
    c = re.sub(r'<p>.*?</p>', lambda m: '<p>' + H.escape(desc, quote=False) + '</p>', c, count=1, flags=re.S)
    return c

TARGETS = [(os.path.join(REPO, "mili", "blog", "index.html"), False),
           (os.path.join(REPO, "blog", "index.html"), True)]

for path, is_main in TARGETS:
    t = open(path, encoding="utf-8").read()
    cw = cards(t)
    tmpl_card = next((c[3] for c in cw if "20261106-mili-appraisal-opinion-review" in c[3]), None)
    if tmpl_card is None:
        tmpl_card = next((c[3] for c in cw if "20261104-mili-anti-involution-low-price" in c[3]), cw[0][3])
    if is_main:
        tmpl_card = next((c[3] for c in cw if "20261105-mili-non-compete-all-staff" in c[3]), tmpl_card)
    for slug, date, title, desc, kw in CARDS:
        has = re.search(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), t)
        if has:
            print(("MAIN " if is_main else "MILI ") + "card exists, skip:", slug); continue
        card = make_card(slug, date, title, desc, kw, is_main, tmpl_card)
        cw = cards(t)
        ins = next((c[0] for c in cw if c[2] and c[2] <= date), None)
        if ins is None:
            print("NO INSERT POINT", slug, path); continue
        t2 = t[:ins] + card + "\n  " + t[ins:]
        assert t2.replace(card + "\n  ", "", 1) == t, "outside-card change!"
        t = t2
        print(("MAIN " if is_main else "MILI ") + f"card added: {slug} at {ins}")
    print(path, "cards:", len(cards(t)), "| delta bytes", len(t.encode()) - os.path.getsize(path))
    if APPLY:
        open(path, "w", encoding="utf-8").write(t)
