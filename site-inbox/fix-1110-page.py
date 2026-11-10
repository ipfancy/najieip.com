#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-1110-page.py — 精修 2026-11-10 mili 遗嘱部分无效「裸发布畸形页」
判据: h1=0 / ld=0 / 无 og:image / desc 复读标题 / ** 未转
做法: md 源整页重建，套 11-09 mili 精修房屋（外链 style.css + Article/BreadcrumbList）
用法: python3 site-inbox/fix-1110-page.py [--apply]
"""
import os, re, sys, json, copy, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261110-mili-will-partial-invalid"
BRAND = "mili"
PAGE = os.path.join(REPO, BRAND, "blog", SLUG + ".html")
HOUSE = os.path.join(REPO, BRAND, "blog", "20261109-mili-prepaid-card-refund.html")
MD = os.path.expanduser("~/wiki/digital-employees/articles/%s.md" % SLUG)
COVER_SRC = os.path.expanduser("~/wiki/digital-employees/articles/cover-%s.png" % SLUG)
COVER_DST = os.path.join(REPO, "img", SLUG + ".png")
APPLY = "--apply" in sys.argv

TITLE = "6亿遗产全给再婚妻子，遗嘱里一块不算数"
DESC = ("东莞6亿遗产案：一份公证遗嘱把全部财产留给再婚妻子，前妻三个子女只主张5734万，占6亿的9.56%。"
        "《民法典》第1133条只允许处分个人合法财产，《继承编的解释（一）》第26条规定越界部分无效——"
        "遗嘱整体还在，越界那块不作数，公证只担保形式、担保不了内容。"
        "另拆解遗嘱能力的时间点难题：诊断在遗嘱之后6个月零4天，以及普通家庭动笔前该做的三件事。")
KWS = ["遗嘱部分无效", "民法典第1133条", "继承编解释一第26条", "公证遗嘱", "未分割夫妻共同财产"]
DATE = "2026-11-10"
URL = "https://najieip.com/%s/blog/%s.html" % (BRAND, SLUG)
IMG = "https://najieip.com/img/%s.png" % SLUG


def zh_quotes(s):
    """只在文本节点上转 ASCII 直引号为中文引号（成对）"""
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("\u201c" if open_q else "\u201d")
            open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)


def inline(s):
    s = zh_quotes(s)
    s = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", s)
    return s


def parse_md():
    raw = open(MD, encoding="utf-8").read()
    body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
    blocks = []
    for para in [p.strip() for p in body.split("\n\n")]:
        if not para:
            continue
        if para.startswith("<!--"):
            continue  # 上集合集注释块，不落正文
        if re.match(r"^[一二三四五六七八九十]、", para) or para == "今天就能做的三件事":
            blocks.append(("h2", para))
        else:
            blocks.append(("p", inline(para.replace("\n", " "))))
    return blocks


def build_body(blocks):
    parts = ["<h1>%s</h1>" % TITLE]
    for kind, txt in blocks:
        if kind == "h2":
            parts.append("<h2>%s</h2>" % zh_quotes(txt))
        else:
            parts.append("<p>%s</p>" % txt)
    return "\n<br>\n".join(parts)


def build_head(house_head):
    h = house_head
    h = re.sub(r"<title>.*?</title>", "<title>%s — 纳杰觅理</title>" % TITLE, h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="%s">' % DESC, h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">',
               '<meta property="og:title" content="%s">' % TITLE, h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">',
               '<meta property="og:description" content="%s">' % DESC, h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">',
               '<meta property="og:url" content="%s">' % URL, h)
    h = re.sub(r'<meta property="og:image" content="[^"]*">',
               '<meta property="og:image" content="%s">' % IMG, h)
    h = re.sub(r'<meta name="twitter:title" content="[^"]*">',
               '<meta name="twitter:title" content="%s">' % TITLE, h)
    h = re.sub(r'<meta name="twitter:description" content="[^"]*">',
               '<meta name="twitter:description" content="%s">' % DESC, h)
    h = re.sub(r'<meta name="twitter:image" content="[^"]*">',
               '<meta name="twitter:image" content="%s">' % IMG, h)
    h = re.sub(r'<meta name="keywords" content="[^"]*">',
               '<meta name="keywords" content="%s">' % ",".join(KWS), h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">',
               '<link rel="canonical" href="%s">' % URL, h)
    h = re.sub(r'<link rel="alternate" hreflang="([^"]+)" href="[^"]*">',
               lambda m: '<link rel="alternate" hreflang="%s" href="%s">' % (m.group(1), URL), h)

    # JSON-LD: 取 house 两块（Article + BreadcrumbList），deepcopy 后覆写
    lds = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', h, re.S)
    assert len(lds) == 2, "house ld count=%d" % len(lds)
    arts = [json.loads(x) for x in lds]
    article, crumb = arts[0], arts[1]
    article.update({
        "headline": TITLE, "description": DESC, "image": IMG,
        "datePublished": DATE, "dateModified": DATE, "url": URL,
        "keywords": KWS,
    })
    article["mainEntityOfPage"]["@id"] = URL
    crumb["itemListElement"][2]["name"] = "觅理博客 · " + TITLE[:12]
    crumb["itemListElement"][2]["item"] = URL
    new_ld = ""
    for obj in (article, crumb):
        new_ld += '<script type="application/ld+json">\n%s\n</script>\n' % json.dumps(obj, ensure_ascii=False, indent=2)
    # 用新块替换 head 内原有的两块
    old_blocks = re.findall(r'<script type="application/ld\+json">.*?</script>\n?', h, re.S)
    assert len(old_blocks) == 2
    first = old_blocks[0]
    h = h.replace(first, "@@LD@@", 1)
    h = h.replace(old_blocks[1], "", 1)
    h = h.replace("@@LD@@", new_ld.rstrip("\n"))
    return h


def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<h1>.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2>.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'")
    s = re.sub(r"[*\"\u201c\u201d'|:\-\s>]", "", s)
    return s


def main():
    blocks = parse_md()
    body_html = build_body(blocks)
    house = open(HOUSE, encoding="utf-8").read()
    head_end = house.find("</head>") + 7
    head = build_head(house[:head_end])

    # nav/footer 从 house 取（body 内除 article 之外的部分）
    hb = house[head_end:]
    art_start = hb.find("<article>")
    art_end = hb.find("</article>") + len("</article>")
    pre, post = hb[:art_start], hb[art_end:]
    page = head + pre + "<article>\n" + body_html + "\n</article>" + post

    # ---- 断言 ----
    errs = []
    if len(re.findall(r"<h1", page)) != 1: errs.append("h1 count")
    if page.count("application/ld+json") != 2: errs.append("ld count")
    if "og:image" not in page: errs.append("og:image missing")
    if page.count("https://***") != 0: errs.append("schema.org masked")
    if page.count("**") != 0: errs.append("markdown stars")
    if re.search(r"<p>\|", page): errs.append("raw table")
    for blk in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', page, re.S):
        try:
            json.loads(blk)
        except Exception as e:
            errs.append("ld parse: %s" % e)

    md_raw = "".join(txt for kind, txt in blocks if kind == "p")
    md_norm = textify(md_raw)
    page_body = page[page.find("<article>"):page.find("</article>")]
    pg_norm = textify(page_body)
    # 落款差异两侧各自剔除
    for s in (md_norm, pg_norm):
        pass
    BYLINE = textify("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰")
    md_norm2 = md_norm.replace(BYLINE, "")
    pg_norm2 = pg_norm.replace(BYLINE, "").replace(textify("北京觅理律师事务所 何自刚"), "")
    contained = md_norm2 in pg_norm2
    if not contained:
        errs.append("md not contained: md=%d pg=%d" % (len(md_norm2), len(pg_norm2)))

    print("blocks=%d h2=%d p=%d bytes=%d" % (len(blocks), sum(1 for k, _ in blocks if k == "h2"),
                                            sum(1 for k, _ in blocks if k == "p"), len(page)))
    print("md_contained=%s md_norm=%d pg_norm=%d" % (contained, len(md_norm2), len(pg_norm2)))
    print("errors=%s" % (errs or "NONE"))
    if errs and not (len(errs) == 1 and errs[0].startswith("md not contained")):
        print("ABORT on fatal errors")
        return 1
    if errs:
        # 打印差异定位
        for i, (a, b) in enumerate(zip(md_norm2, pg_norm2)):
            if a != b:
                print("diff_at=%d md=%r pg=%r" % (i, md_norm2[max(0, i - 30):i + 30], pg_norm2[max(0, i - 30):i + 30]))
                break
        print("ABORT: content mismatch")
        return 1

    if APPLY:
        open(PAGE, "w", encoding="utf-8").write(page)
        os.makedirs(os.path.dirname(COVER_DST), exist_ok=True)
        shutil.copyfile(COVER_SRC, COVER_DST)
        print("WROTE %s (%d bytes) + cover %d bytes" % (PAGE, os.path.getsize(PAGE), os.path.getsize(COVER_DST)))
    else:
        print("DRY-RUN ok (use --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
