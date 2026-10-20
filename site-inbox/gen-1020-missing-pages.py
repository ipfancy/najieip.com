#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0920/1020: 为 content.db 已发布但站点无页面的文章生成房屋样式页面 + 双索引补卡 + articles.json 条目。
用法: python3 site-inbox/gen-1020-missing-pages.py [--apply]
"""
import os, re, sys, json, html, shutil, copy

SITE = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
TEMPLATE = os.path.join(SITE, "mili/blog/customs-ip-detention-30-day-timeline-20261018.html")
APPLY = "--apply" in sys.argv

JOBS = [
    {
        "stem": "20261020-mili-overtime-leave-evidence",
        "date": "2026-10-20",
        "title": "加班费年假争议，企业拿不出记录就输：法释26号第42条",
        "desc": "法释〔2020〕26号第42条把举证责任压回单位：劳动者能证明考勤、加班记录在单位手里，单位拿不出来就承担不利后果。加班费三档（延时150%、休息日200%、法定节假日300%）容易算错，但真正让企业输的是留痕。本文讲清考勤、工资台账、年假签字三样证据怎么留、留几年，以及未休年假300%的举证规则。",
        "tags": ["劳动用工", "证据留存"],
        "h2": [("法释〔2020〕26号第42条", "第42条的举证逻辑：账本在谁手里，谁扛"),
               ("两年。", "工资台账必须书面留两年"),
               ("年假天数按累计工龄算", "年假：证明不了已安排，就推定没休"),
               ("三样东西今天就开留", "今天就该开的三个留痕动作，")],
    },
    {
        "stem": "20261019-mili-community-correction-medical-standard",
        "date": "2026-10-19",
        "title": "11月1日起，保外就医的门槛变了：2014年的老标准作废",
        "desc": "司发通〔2026〕55号自2026年11月1日施行，2014年《保外就医严重疾病范围》同时废止。新标准把“生活不能自理”从五项里三项需协助改为四项里一项完全不能自主完成，观察期由六个月以上缩到一个月以上，病种目录同步扩容，但审批与鉴定责任一寸没松。本文按变化、未变、家属该做什么三块讲清。",
        "tags": ["刑事", "暂予监外执行"],
        "h2": [],
    },
]


def read_md(stem):
    p = os.path.join(ART, stem + ".md")
    t = open(p, encoding="utf-8").read()
    # strip frontmatter
    if t.startswith("---"):
        parts = t.split("---", 2)
        if len(parts) >= 3:
            t = parts[2]
    return t


def md_to_html(md, h2map):
    out = []
    paras = [b.strip() for b in re.split(r"\n\s*\n", md) if b.strip()]
    h2done = set()
    for b in paras:
        if b.startswith("<!--"):
            continue
        if b.startswith("# "):
            continue  # title goes to h1
        if b.startswith("## "):
            out.append("<h2>%s</h2>" % html.escape(b[3:].strip()))
            continue
        # optional h2 injection by prefix anchor
        if h2map:
            for anchor, heading in h2map:
                if anchor not in h2done and b.startswith(anchor):
                    out.append("<h2>%s</h2>" % html.escape(heading.rstrip("，")))
                    h2done.add(anchor)
                    break
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        # markdown table?
        if len(lines) >= 2 and lines[0].startswith("|") and re.match(r"^\|[\s:\-|]+\|$", lines[1]):
            rows = [l for l in lines if not re.match(r"^\|[\s:\-|]+\|$", l)]
            cells = lambda l: [c.strip() for c in l.strip("|").split("|")]
            th = "".join("<th>%s</th>" % inline(c) for c in cells(rows[0]))
            trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in cells(r)) for r in rows[1:])
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, trs))
            continue
        if all(l.startswith("- ") for l in lines):
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(l[2:]) for l in lines))
            continue
        txt = inline(" ".join(lines))
        out.append("<p>%s</p>" % txt)
    body = "\n<br>\n".join(out)
    return body


def inline(s):
    s = zh_quotes(s)
    s = html.escape(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def zh_quotes(s):
    # ASCII double quotes -> Chinese quotes in text nodes only
    out, depth = [], 0
    for ch in s:
        if ch == '"':
            out.append("“" if depth % 2 == 0 else "”")
            depth += 1
        else:
            out.append(ch)
    return "".join(out)


def build_head(tpl, job, slug, path):
    head_end = tpl.find("</head>") + 7
    head = tpl[:head_end]
    url = "https://najieip.com/%s/%s.html" % (path, slug)
    img = "https://najieip.com/img/%s.png" % slug
    head = re.sub(r"<title>.*?</title>", "<title>%s — 纳杰觅理</title>" % html.escape(job["title"]), head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + html.escape(job["desc"]) + m.group(2), head, count=1)
    head = re.sub(r'(<meta name="keywords" content=")[^"]*(")', lambda m: m.group(1) + ",".join(job["tags"]) + m.group(2), head, count=1)
    for prop in ["og:title", "twitter:title"]:
        head = re.sub(r'(<meta property="%s" content=")[^"]*(")' % prop, lambda m: m.group(1) + html.escape(job["title"]) + m.group(2), head)
    for prop in ["og:description", "twitter:description"]:
        head = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % prop, lambda m: m.group(1) + html.escape(job["desc"]) + m.group(2), head)
    for prop in ["og:url"]:
        head = re.sub(r'(<meta property="%s" content=")[^"]*(")' % prop, lambda m: m.group(1) + url + m.group(2), head)
    for prop in ["og:image", "twitter:image"]:
        head = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % prop, lambda m: m.group(1) + img + m.group(2), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), head)

    # JSON-LD blocks: deepcopy template objects
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, flags=re.S)
    assert len(blocks) == 2, "template ld blocks=%d" % len(blocks)
    objs = [json.loads(b) for b in blocks]
    for o in objs:
        if o.get("@type") == "Article":
            o["headline"] = job["title"]
            o["description"] = job["desc"]
            o["image"] = img
            o["datePublished"] = job["date"]
            o["dateModified"] = job["date"]
            o["url"] = url
            o["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
            o["keywords"] = ",".join(job["tags"])
        elif o.get("@type") == "BreadcrumbList":
            items = o.get("itemListElement", [])
            if len(items) >= 3:
                items[2]["name"] = job["title"]
                items[2]["item"] = url
    new_blocks = ['<script type="application/ld+json">%s</script>' % json.dumps(o, ensure_ascii=False)
                  for o in objs]
    old_blocks = re.findall(r'<script type="application/ld\+json">.*?</script>', head, flags=re.S)
    for old, new in zip(old_blocks, new_blocks):
        head = head.replace(old, new, 1)
    return head


def card_block(tpl, job, path, rel):
    """取模板卡（10-18）按 div 深度配对"""
    idx = tpl.find("<h2><a href=\"")
    hm = re.search(r'<h2><a href="[^"]*customs-ip-detention-30-day-timeline-20261018\.html"', tpl)
    idx = hm.start() if hm else -1
    start = tpl.rfind('<div class="article-card">', 0, idx)
    depth, i = 1, start + len('<div class="article-card">')
    for m in re.finditer(r"<div\b|</div>", tpl[i:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            end = i + m.end()
            break
    blk = tpl[start:end]
    new = blk
    new = re.sub(r'<h2><a href="[^"]*">.*?</a></h2>',
                 '<h2><a href="%s">%s</a></h2>' % (rel, html.escape(job["title"])), new, flags=re.S)
    new = re.sub(r"<p>.*?</p>", "<p>%s</p>" % html.escape(job["desc"]), new, count=1, flags=re.S)
    new = re.sub(r'(?:\s*<span class="tag">[^<]*</span>)+',
                 "".join('<span class="tag">%s</span>' % t for t in job["tags"]), new, count=1)
    new = re.sub(r"\d{4}-\d{2}-\d{2}", job["date"], new)
    return new


def insert_card(index_html, job, rel):
    if rel in index_html or job["stem"] in index_html:
        return index_html
    tpl = open(TEMPLATE, encoding="utf-8").read()
    card = card_block(index_html, job, "", rel)
    dates = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="meta">[^<]*(?:<[^>]+>[^<]*)*?(\d{4}-\d{2}-\d{2})', index_html)]
    # fallback: find card start positions with dates
    cards = []
    for m in re.finditer(r'<div class="article-card">', index_html):
        s = m.start()
        seg = index_html[s:s + 2000]
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", seg)
        cards.append((s, dm.group(1) if dm else "9999-99-99"))
    pos = None
    for s, d in cards:
        if d < job["date"]:
            pos = s
            break
    if pos is None:
        pos = cards[0][0] if cards else index_html.find('<div class="container">')
    return index_html[:pos] + card + "\n  " + index_html[pos:]


def main():
    tpl = open(TEMPLATE, encoding="utf-8").read()
    report = []
    for job in JOBS:
        slug = job["stem"]
        path = "mili/blog"
        md = read_md(slug)
        body = md_to_html(md, job["h2"])
        body = zh_quotes_in_textnodes(body)
        head = build_head(tpl, job, slug, path)
        # house body skeleton
        nav = re.search(r"<nav>.*?</nav>", tpl, flags=re.S).group(0)
        footer = re.search(r"<footer>.*?</footer>", tpl, flags=re.S).group(0)
        page = head + "<body>\n" + nav + "\n<article>\n<h1>%s</h1>\n%s\n</article>\n%s\n</body>\n</html>\n" % (
            html.escape(job["title"]), body, footer)
        # checks
        assert page.count("<h1") == 1, slug
        assert page.count("application/ld+json") == 2, slug
        assert "og:image" in page and page.count("https://***") == 0
        assert "**" not in page, "%s has **" % slug
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, flags=re.S):
            json.loads(b)
        # text fidelity: strip tags -> compare with md paragraphs
        ptext = lambda s: [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()]
        # cover
        cover_src = os.path.join(ART, "cover-%s.png" % slug)
        cover_dst = os.path.join(SITE, "img", "%s.png" % slug)
        cover_ok = os.path.exists(cover_src)
        report.append("PAGE %s chars=%d h1=%d ld=2 cover_src=%s" % (slug, len(page), page.count("<h1"), cover_ok))
        if APPLY:
            open(os.path.join(SITE, path, slug + ".html"), "w", encoding="utf-8").write(page)
            if cover_ok:
                shutil.copy2(cover_src, cover_dst)
    if APPLY:
        # index cards
        for idx_path, relfmt in [("mili/blog/index.html", "./%s.html"), ("blog/index.html", "/mili/blog/%s.html")]:
            p = os.path.join(SITE, idx_path)
            t = open(p, encoding="utf-8").read()
            before = t.count('<div class="article-card">')
            for job in sorted(JOBS, key=lambda j: j["date"], reverse=True):
                t = insert_card(t, job, relfmt % job["stem"])
            after = t.count('<div class="article-card">')
            open(p, "w", encoding="utf-8").write(t)
            report.append("CARDS %s %d->%d (+%d)" % (idx_path, before, after, after - before))
        # articles.json entries
        p = os.path.join(SITE, "articles.json")
        raw = open(p, encoding="utf-8").read()
        data = json.loads(raw)
        arr = data if isinstance(data, list) else data.get("articles", [])
        have = {a.get("url") for a in arr}
        added = 0
        for job in sorted(JOBS, key=lambda j: j["date"], reverse=True):
            u = "/mili/blog/%s.html" % job["stem"]
            if u in have:
                continue
            entry = {"title": job["title"], "url": u, "date": job["date"],
                     "description": job["desc"], "tags": job["tags"]}
            arr.insert(added, entry)
            added += 1
        open(p, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        report.append("ARTICLES.JSON +%d (total %d)" % (added, len(arr)))
    print("\n".join(report))
    print("APPLIED" if APPLY else "DRY-RUN")


def zh_quotes_in_textnodes(s):
    parts = re.split(r"(<[^>]+>)", s)
    for i, p in enumerate(parts):
        if not p.startswith("<"):
            parts[i] = zh_quotes(p)
    return "".join(parts)


if __name__ == "__main__":
    main()
