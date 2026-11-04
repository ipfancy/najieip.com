#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-11-04 修复：①精修 anti-involution 页 ②封面入库 ③三篇双索引补卡
用法: python3 site-inbox/fix-1104.py [--apply]
"""
import os, re, sys, json, copy, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
APPLY = "--apply" in sys.argv

ARTICLES = [
    dict(brand="mili", slug="20261104-mili-anti-involution-low-price",
         title="反法第14条：平台逼你「全网最低价」，商家先留3样证据",
         tags=["反不正当竞争法", "平台低价", "证据"],
         desc="平台强制改价把 19.8 元的套餐压到实收 2.58 元，卖一单赔一单。反法 2025 年新增第 14、15 条自 2025 年 10 月 15 日施行，本文给出两条罚则金额、管辖层级差异（第 14 条县级可接、第 15 条归省级以上），以及针对第 14 条与第 15 条各一张三样证据的取证清单。"),
    dict(brand="mili", slug="20261104-mili-provisional-protection-fee",
         title="专利还没授权就被用了：这笔使用费能要，但不能要赔偿",
         tags=["临时保护期使用费", "发明专利", "专利法第13条"],
         desc=None),
    dict(brand="najie", slug="20261104-najie-priority-right-reform-agenda",
         title="专利优先权写进修法议程：出海排期，别赌规则会变",
         tags=["专利优先权", "专利法修订", "出海布局"],
         desc=None),
]

# ---------- 1. 精修 anti-involution 页 ----------
def card_block(t, slug):
    """div 深度配对取卡片"""
    i = t.find("<h2><a href=\"" )
    # 找含 slug 的卡：定位 <div class="article-card"> 起
    for m in re.finditer(r'<div class="article-card">', t):
        start = m.start()
        depth = 0
        j = start
        while j < len(t):
            no = t.find("<div", j)
            nc = t.find("</div>", j)
            if nc == -1: break
            if no != -1 and no < nc:
                depth += 1; j = no + 4
            else:
                depth -= 1; j = nc + 6
                if depth == 0:
                    blk = t[start:j]
                    if slug in blk:
                        return blk, start, j
                    break
    return None, -1, -1

def fix_page():
    slug = "20261104-mili-anti-involution-low-price"
    path = os.path.join(REPO, "mili/blog", slug + ".html")
    tplp = os.path.join(REPO, "mili/blog/20261104-mili-provisional-protection-fee.html")
    t = open(path, encoding="utf-8").read()
    tpl = open(tplp, encoding="utf-8").read()

    # 1a. 裸 markdown 表 → <table class="data">
    def conv_tables(html):
        lines = html.split("\n")
        out, i, made = [], 0, 0
        while i < len(lines):
            if re.match(r"^<p>\|.*\|</p>$", lines[i].strip()):
                grp = []
                while i < len(lines) and re.match(r"^<p>\|.*\|</p>$", lines[i].strip()):
                    grp.append(lines[i].strip()); i += 1
                rows = []
                for g in grp:
                    inner = re.match(r"^<p>\|(.*)\|</p>$", g).group(1)
                    cells = [c.strip() for c in inner.split("|")]
                    if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                        continue
                    rows.append(cells)
                if len(rows) >= 2:
                    h = ['<table class="data">', "<thead><tr>" + "".join(f"<th>{c}</th>" for c in rows[0]) + "</tr></thead>", "<tbody>"]
                    for r in rows[1:]:
                        h.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
                    h += ["</tbody>", "</table>"]
                    out.append("\n".join(h)); made += 1; continue
                else:
                    out.extend(grp); continue
            out.append(lines[i]); i += 1
        return "\n".join(out), made

    body_html, tables = conv_tables(t)
    print("  tables converted:", tables)

    # 1b. head 重建（原始 </head> 偏移切 body）
    head_end = body_html.find("</head>") + 7
    body = body_html[head_end:]
    thead_i = tpl.find("<head>"); thead_end = tpl.find("</head>") + 7
    head = tpl[thead_i:thead_end]
    A = ARTICLES[0]
    title, desc = A["title"], A["desc"]
    url = f"https://najieip.com/{A['brand']}/blog/{slug}.html"
    img = f"https://najieip.com/img/{slug}.png"
    kw = ",".join(A["tags"] + ["反法第14条", "反法第15条", "全网最低价"])

    def setattr_(h, pat, val, count=1):
        return re.sub(pat, lambda m: m.group(1) + val + m.group(3), h, count=count, flags=re.S)

    head = re.sub(r"<title>.*?</title>", "<title>" + title + " — 纳杰觅理</title>", head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + title + m.group(2), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), head)
    head = re.sub(r'(<meta property="og:image" content=")[^"]*(")', lambda m: m.group(1) + img + m.group(2), head)
    head = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + title + m.group(2), head)
    head = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), head)
    head = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', lambda m: m.group(1) + img + m.group(2), head)
    head = re.sub(r'(<meta name="keywords" content=")[^"]*(")', lambda m: m.group(1) + kw + m.group(2), head)

    # 1c. JSON-LD：deepcopy 模板两块后覆写
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
    print("  tmpl ld blocks:", [json.loads(b).get("@type") for b in blocks])
    new_blocks = []
    for b in blocks:
        o = copy.deepcopy(json.loads(b))
        if o.get("@type") == "FAQPage":
            print("  skip FAQPage (模板自带内容，不带入新页)")
            continue
        if o.get("@type") == "Article" or o.get("@type") == "BlogPosting":
            o["headline"] = title
            o["description"] = desc
            o["image"] = img
            o["datePublished"] = "2026-11-04"
            o["dateModified"] = "2026-11-04"
            o["url"] = url
            if "mainEntityOfPage" in o:
                me = o["mainEntityOfPage"]
                if isinstance(me, dict): me["@id"] = url
                else: o["mainEntityOfPage"] = url
            o["keywords"] = kw
            if "author" in o and isinstance(o["author"], dict):
                o["author"]["name"] = "何自刚"
            if "@id" in o and str(o["@id"]).startswith("http"):
                o["@id"] = url + "#article"
        elif o.get("@type") == "BreadcrumbList":
            items = o.get("itemListElement", [])
            if len(items) >= 3:
                items[2]["item"] = {"@id": url, "name": title}
                items[2]["name"] = title
        new_blocks.append('<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=2) + "\n</script>")
    # 用新块替换旧块
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', "\u0000", head, flags=re.S)
    for nb in new_blocks:
        head = head.replace("\u0000", nb, 1)
    head = head.replace("\u0000", "")

    out = "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n" + head + body
    print(f"  page size {len(t)} -> {len(out)}")
    if APPLY:
        open(path, "w", encoding="utf-8").write(out)
        # 封面入库
        src = os.path.join(ART, "cover-" + slug + ".png")
        dst = os.path.join(REPO, "img", slug + ".png")
        if os.path.exists(src):
            shutil.copy(src, dst); print("  cover ->", dst, os.path.getsize(dst))
        else:
            print("  COVER MISSING", src)
    return out

# ---------- 2. 索引补卡 ----------
def page_desc(brand, slug):
    p = os.path.join(REPO, brand, "blog", slug + ".html")
    t = open(p, encoding="utf-8").read()
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    return m.group(1).strip() if m else ""


def build_card(brand_index_html, tmpl_slug, new_slug, title, desc, tags, brand, is_main):
    if not desc:
        desc = page_desc(brand, new_slug)
    blk, s, e = card_block(brand_index_html, tmpl_slug)
    if blk is None:
        # 退化为任一卡
        m = re.search(r'<div class="article-card">', brand_index_html)
        blk, s, e = card_block(brand_index_html, brand_index_html[m.start():m.start()+400])
    hreft = ('/' + brand + '/blog/' + new_slug + '.html') if is_main else ('./' + new_slug + '.html')
    b = re.sub(r'href="[^"]*"', 'href="' + hreft + '"', blk, count=1)
    # 标题
    b = re.sub(r'(<h2><a href="[^"]*">)(.*?)(</a></h2>)', lambda m: m.group(1) + title + m.group(3), b, flags=re.S)
    # tag span 组整段替换
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    b = re.sub(r'(?:\s*<span class="tag">[^<]*</span>)+', tags_html, b, count=1)
    # 日期
    b = re.sub(r'\d{4}-\d{2}-\d{2}', '2026-11-04', b)
    # 摘要
    b = re.sub(r'(<p>)(?!<).*?(</p>)', lambda m: m.group(1) + desc + m.group(2), b, count=1, flags=re.S)
    return b

def insert_card(index_path, card, is_main):
    t = open(index_path, encoding="utf-8").read()
    if re.search(r'<h[23][^>]*><a href="[^"]*' + re.escape(os.path.basename(index_path)), t):
        pass
    # 找第一张日期 < 2026-11-04 的卡
    pos = None
    for m in re.finditer(r'<div class="article-card">', t):
        # 取该卡日期
        seg = t[m.start():m.start()+3000]
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
        if dm and dm.group(1) < "2026-11-04":
            pos = m.start(); break
    if pos is None:
        pos = t.find('<div class="container">')
        pos = t.find('<div class="article-card">', pos)
    t2 = t[:pos] + card + "\n  " + t[pos:]
    return t, t2

if __name__ == "__main__":
    print("=== 1. 精修页 ===")
    fix_page()

    print("\n=== 2. 索引补卡（dry 预览） ===")
    idx = {}
    for b in ("mili", "najie"):
        idx[b] = open(os.path.join(REPO, b, "blog", "index.html"), encoding="utf-8").read()
    main_idx_path = os.path.join(REPO, "blog", "index.html")
    main_idx = open(main_idx_path, encoding="utf-8").read()

    for A in ARTICLES:
        b = A["brand"]; idxp = os.path.join(REPO, b, "blog", "index.html")
        t = open(idxp, encoding="utf-8").read()
        # 已有卡?
        have_b = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(A["slug"]), t))
        have_m = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(A["slug"]), main_idx))
        print(f"{b}/{A['slug']}: brand_have={have_b} main_have={have_m}")
        if have_b == 0:
            card = build_card(t, "20261103-mili-unfair-competition-data-scraping", A["slug"], A["title"], A["desc"], A["tags"], b, False)
            print("  BRAND CARD >>>", card[:400].replace("\n", "\\n"))
            if APPLY:
                o, n = insert_card(idxp, card, False)
                open(idxp, "w", encoding="utf-8").write(n)
        if have_m == 0:
            card = build_card(t, "20261103-mili-unfair-competition-data-scraping", A["slug"], A["title"], A["desc"], A["tags"], b, True)
            print("  MAIN CARD >>>", card[:400].replace("\n", "\\n"))
            if APPLY:
                o, n = insert_card(main_idx_path, card, True)
                open(main_idx_path, "w", encoding="utf-8").write(n)
                main_idx = n
    print("\nAPPLY =", APPLY)
