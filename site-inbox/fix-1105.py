#!/usr/bin/env python3
"""SiteOps 2026-11-05: rebuild mili partial-bare page + add missing main-index card."""
import os, re, sys, json, copy, shutil, html as H

REPO = os.path.expanduser("~/wiki/najieip-verify")
MDD = os.path.expanduser("~/wiki/digital-employees/articles")
SLUG = "20261105-mili-non-compete-all-staff"
BRAND = "mili"
PAGE = os.path.join(REPO, BRAND, "blog", SLUG + ".html")
TPL = os.path.join(REPO, BRAND, "blog", "20261104-mili-anti-involution-low-price.html")
URL = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
APPLY = "--apply" in sys.argv

TITLE = "全员签竞业限制：条款可能不生效，补偿金照付"
DESC = ("2025年9月1日起，法释〔2025〕12号第十三条第一款明确：没接触过商业秘密的员工，竞业限制条款不生效。"
        "本文算清两年×30%的补偿账（一个岗位7.2个月工资），给出岗位分级写法——研发可全国、销售按区域、行政后勤不宜约定，"
        "并附离职当天的三个月退出窗口与现在就能做的三件事。")
KW = "竞业限制,商业秘密,法释2025-12号,竞业限制补偿金,离职竞业限制,劳动用工合规"

def zh_quotes(s):
    out, inside = [], 0
    for ch in s:
        if ch == '"':
            out.append('“' if inside % 2 == 0 else '”'); inside += 1
        else:
            out.append(ch)
    return "".join(out)

def esc(s):
    return H.escape(s, quote=False).replace('"', '“', 1) if False else H.escape(s, quote=False)

def inline(s):
    s = H.escape(s, quote=False)
    s = re.sub(r'\*\*([^*\n]{1,300})\*\*', r'<strong>\1</strong>', s)
    return s

def build_body():
    md = open(os.path.join(MDD, SLUG + ".md"), encoding="utf-8").read()
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
            t = ['<table class="data">', "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in hdr) + "</tr></thead>", "<tbody>"]
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
    body = "\n".join(out)
    return body

tpl = open(TPL, encoding="utf-8").read()
td = re.search(r'<!DOCTYPE html>.*?<body>', tpl, re.S).group(0)
nav = re.search(r'<nav>.*?</nav>', tpl, re.S).group(0)
footer = re.search(r'<footer>.*?</footer>', tpl, re.S).group(0)

objs = [json.loads(b) for b in re.findall(r'application/ld\+json[^>]*>(.*?)</script>', tpl, re.S)]
art = copy.deepcopy(next(o for o in objs if o.get("@type") == "Article"))
brd = copy.deepcopy(next(o for o in objs if o.get("@type") == "BreadcrumbList"))
art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMG
art["datePublished"] = "2026-11-05"
art["dateModified"] = "2026-11-05"
art["url"] = URL
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
art["keywords"] = KW.split(",")
art["inLanguage"] = "zh-CN"
if "articleSection" in art: art["articleSection"] = "劳动用工"
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
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:site_name" content="纳杰知产">
<meta property="og:locale" content="zh_CN">
<meta name="keywords" content="{KW}">
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

newpage = head + "\n<body>\n" + nav + "\n<article>\n" + build_body() + "\n</article>\n" + footer + "\n</body>\n</html>\n"

# ---- validate ----
b = newpage[newpage.find("<body"):]
checks = {
    "h1": len(re.findall(r'<h1[ >]', b)) == 1,
    "ld": len(re.findall(r'application/ld\+json', newpage)) == 2,
    "json_ok": all(_ok == True for _ok in [True]) ,
    "og_image": 'property="og:image"' in newpage,
    "desc_real": len(DESC) > 80 and TITLE[:12] not in DESC,
    "tables": len(re.findall(r'<table', b)),
    "bare_table": len(re.findall(r'<p>\s*\|', b)),
    "stars": b.count("**"),
    "schema": newpage.count("https://schema.org"),
    "triple_star": newpage.count("https://***"),
}
for blk in re.findall(r'application/ld\+json[^>]*>(.*?)</script>', newpage, re.S):
    try: json.loads(blk)
    except Exception as e: checks["json_ok"] = str(e)[:80]

def norm(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = H.unescape(s)
    for ch in '“”"\'’*|#>-\u3000`:':
        s = s.replace(ch, ' ')
    return re.sub(r'\s+', '', s)

mdn = norm(open(os.path.join(MDD, SLUG + ".md"), encoding="utf-8").read().split("---", 2)[2])
bn = norm(b[b.find("<article>"):b.find("</article>")])
checks["md_contains"] = mdn in bn
if not checks["md_contains"]:
    # locate first divergence
    k = 0
    while k < min(len(mdn), len(bn)) and mdn[k] == bn[k]: k += 1
    checks["diff_at"] = (k, mdn[max(0,k-25):k+25], bn[max(0,k-25):k+25])

print("PAGE CHECKS:", json.dumps(checks, ensure_ascii=False))
print("new bytes:", len(newpage.encode()), "old bytes:", os.path.getsize(PAGE))

# ---- main index card for najie newsletter (missing) ----
NI = os.path.join(REPO, "blog", "index.html")
it = open(NI, encoding="utf-8").read()
NS = "20261105-najie-examination-15plan-foreign-filers"
has = re.search(r'<h2[^>]*><a href="[^"]*' + re.escape(NS), it)
print("newsletter main card present:", bool(has))

def cards_with_date(t):
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
        res.append((start, i, dm.group(1) if dm else "", blk))
    return res

if APPLY:
    open(PAGE, "w", encoding="utf-8").write(newpage)
    cov = os.path.join(MDD, f"cover-{SLUG}.png")
    if os.path.exists(cov):
        shutil.copy(cov, os.path.join(REPO, "img", SLUG + ".png"))
    if not has:
        cw = cards_with_date(it)
        tplcard = next(c[3] for c in cw if "20261105-mili-non-compete-all-staff" in c[3])
        card = tplcard
        card = card.replace('/mili/blog/20261105-mili-non-compete-all-staff.html', f'/najie/blog/{NS}.html')
        card = card.replace(TITLE, "专利商标审查「十五五」规划发布：涉外申请人该盯的6处变化")
        card = re.sub(r'\d{4}-\d{2}-\d{2}', '2026-11-05', card, count=1)
        card = re.sub(r'(?:\s*<span class="tag">[^<]*</span>)+',
                      '<span class="tag">涉外申请</span><span class="tag">审查规划</span><span class="tag">十五五规划</span>', card, count=1)
        card = card.replace("北京觅理律师事务所", "北京纳杰知识产权代理有限公司")
        card = re.sub(r'<p>.*?</p>', '<p>2026年11月3日国知局公布《专利和商标审查「十五五」规划》：四方面任务、7个专项工程，2030年建成世界水平审查机构。优先权仍12个月、宽限期仍6个月，但按需审查、AI使用声明、SEP审查、商标依职权撤销等6处变化直接影响涉外申请人的排期与材料。</p>', card, count=1, flags=re.S)
        ins = next((c[0] for c in cw if c[2] and c[2] <= "2026-11-05"), None)
        if ins is not None:
            it2 = it[:ins] + card + "\n  " + it[ins:]
            open(NI, "w", encoding="utf-8").write(it2)
            print("CARD INSERTED at", ins, "delta", len(it2) - len(it))
            print("card preview:", card[:200].replace("\n", " "))
        else:
            print("NO INSERT POINT FOUND")
    else:
        print("skip card, already present")
