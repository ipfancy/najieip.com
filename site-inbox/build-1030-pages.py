#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1030: 补建 3 篇「已发布但站点无页」+ 重建 1 篇裸发布畸形页 + 双索引补卡 + articles.json 条目。
用法: python3 site-inbox/build-1030-pages.py [--apply]
"""
import os, re, sys, json, html, copy, shutil

SITE = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
APPLY = "--apply" in sys.argv
BASE = "https://najieip.com"

HOUSE = {
    "mili": os.path.join(SITE, "mili/blog/20261030-mili-ai-harm-outpaces-law.html"),
    "najie": os.path.join(SITE, "najie/blog/20261030-najie-training-data-provenance.html"),
}
BLOG_ZH = {"mili": "觅理博客", "najie": "纳杰博客"}
BRAND_NAME = {"mili": "北京觅理律师事务所", "najie": "纳杰知识产权"}

JOBS = [
    dict(stem="20261028-mili-social-insurance-subsidy", brand="mili", date="2026-10-28",
         date_mod="2026-10-30",
         title="工资里那笔“社保补贴”，最后成了员工手里的一张牌",
         tags=["劳动用工", "社保合规"],
         kw="社保补贴,法释2025第12号,第19条,补缴,经济补偿",
         desc="法释〔2025〕12号第19条把“约定不缴社保”写死为无效：员工签字的补贴表格在仲裁里几乎没有抗辩力。但多数人只读到第一款——第三款给了企业唯一的反手：依法补缴后，可请求员工返还已支付的社保补贴。本文讲清三笔钱怎么算、为什么“改工资单再签一次”是最贵的一步，以及现在能做的三件事。"),
    dict(stem="20261021-mili-ai-creation-cost-evidence", brand="mili", date="2026-10-21",
         date_mod="2026-10-30",
         title="AI 创作烧的算力钱，是维权时最值钱的证据",
         tags=["AI版权", "证据留存"],
         kw="AI短剧,视听作品,算力成本,Token,酌定赔偿,证据链",
         desc="武汉市江岸区法院在 AI 短剧侵权案里，把 Token 消耗带来的算力成本与商用工具授权成本纳入酌定赔偿的考量——不是把成本直接当赔偿额，而是法院酌定时认它是投入。本文拆解认定构成作品的“实质控制力”标准、两条缺一不可的证据链（权利链与成本链），以及今天就能开始留的三样东西。"),
    dict(stem="20261030-mili-trademark-renewal", brand="mili", date="2026-10-30",
         date_mod="2026-10-30",
         title="商标到期忘了续展，2027 年起连“一年缓冲”都没有了",
         tags=["商标", "续展"],
         kw="商标续展,宽展期,2027新商标法,第四十四条,商标注销",
         desc="商标十年一续：现行《商标法》第四十条的窗口是十八个月，期满前十二个月续展、宽展期六个月，宽展期满未办理即注销。2026年6月26日修订通过的新法把规则挪到第四十四条，内容基本一致，变的是“注销之后会发生什么”——2027年1月1日起，那层兜底的一年缓冲被收窄。本文讲清窗口怎么算、断在哪一步、现在该做哪些自检。"),
    dict(stem="20261030-najie-foreign-filing-confidentiality-review", brand="najie",
         date="2026-10-30", date_mod="2026-10-30", rebuild=True,
         title="专利法第19条：等4个月没通知就出海，这条旧路没了",
         tags=["海外申请", "保密审查"],
         kw="保密审查,专利法第19条,向外国申请专利,实施细则第九条,无效理由",
         desc="向外国申请专利前的保密审查不收一分钱、通常两到四周出意见，但只要顺序错了，在中国的专利申请能被一句“不授予专利权”直接作废，且没有补救程序。2024年1月20日新细则施行后，旧版“等4个月没通知就出海”的默示许可已被删除；国知局办事指南页至今仍挂2020年旧口径。本文讲三种请求方式、四类结论、三层代价，以及（2022）最高法知行终255号刚给的三层判断标准。"),
]

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def wr(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def zh_quotes(s):
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("“" if open_q else "”"); open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    # only text nodes: quotes outside tags
    parts = re.split(r"(<[^>]+>)", s)
    return "".join(p if p.startswith("<") else zh_quotes(p) for p in parts)

def md_to_html(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    if md.lstrip().startswith("---"):
        parts = md.lstrip().split("---", 2)
        if len(parts) >= 3:
            md = parts[2]
    title = ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", md) if b.strip()]
    out = []
    for b in blocks:
        lines = b.split("\n")
        if lines[0].startswith("# "):
            title = lines[0][2:].strip()
            rest = [l for l in lines[1:] if l.strip()]
            if rest:
                out.append("<p>%s</p>" % inline(" ".join(rest)))
            continue
        if all(l.strip().startswith("|") for l in lines if l.strip()):
            rows = [l.strip() for l in lines if l.strip()]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            sep = lambda r: all(re.fullmatch(r":?-{2,}:?", c or "") for c in r)
            body_rows = [r for r in cells if not sep(r)]
            if not body_rows:
                continue
            head, *rest_rows = body_rows
            tb = ["<table class=\"data\">", "<thead><tr>"]
            tb += ["<th>%s</th>" % inline(c) for c in head]
            tb.append("</tr></thead><tbody>")
            for r in rest_rows:
                tb.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            tb.append("</tbody></table>")
            out.append("\n".join(tb))
            continue
        if lines[0].startswith("## "):
            out.append("<h2>%s</h2>" % inline(lines[0][3:].strip()))
            rest = [l for l in lines[1:] if l.strip()]
            if rest:
                out.append("<p>%s</p>" % inline(" ".join(rest)))
            continue
        if lines[0].startswith("> "):
            q = " ".join(l[2:].strip() for l in lines if l.strip())
            out.append("<blockquote><p>%s</p></blockquote>" % inline(q))
            continue
        out.append("<p>%s</p>" % inline(" ".join(l.strip() for l in lines if l.strip())))
    return title, "\n".join(out)

def textify(t):
    t = re.sub(r"<h1>.*?</h1>", " ", t, flags=re.S)
    t = re.sub(r"<figure.*?</figure>", " ", t, flags=re.S)
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[\s\*\"“”'’>\-]+", "", t)
    return t

def build_page(job):
    house = rd(HOUSE[job["brand"]])
    head_end = house.find("</head>") + 7
    head = house[:head_end]
    body = house[head_end:]
    nav = re.search(r"<nav>.*?</nav>", body, re.S).group(0)
    foot = body[body.rfind("<footer"):]
    slug = job["stem"]
    url = f"{BASE}/{job['brand']}/blog/{slug}.html"
    img = f"{BASE}/img/{slug}.png"
    md = rd(os.path.join(ART, slug + ".md"))
    _, article_html = md_to_html(md)
    # --- head rebuild ---
    head = re.sub(r"<title>.*?</title>", "<title>%s — 纳杰觅理</title>" % html.escape(job["title"]), head, flags=re.S)
    def set_meta(h, pat, val):
        return re.sub(pat, val, h, count=1)
    head = set_meta(head, r'<meta name="description" content="[^"]*">',
                    '<meta name="description" content="%s">' % html.escape(job["desc"]))
    head = set_meta(head, r'<meta property="og:title" content="[^"]*">',
                    '<meta property="og:title" content="%s">' % html.escape(job["title"]))
    head = set_meta(head, r'<meta property="og:description" content="[^"]*">',
                    '<meta property="og:description" content="%s">' % html.escape(job["desc"]))
    head = set_meta(head, r'<meta property="og:site_name" content="[^"]*">',
                    '<meta property="og:site_name" content="%s">' % BRAND_NAME[job["brand"]])
    head = set_meta(head, r'<meta name="keywords" content="[^"]*">',
                    '<meta name="keywords" content="%s">' % job["kw"])
    head = set_meta(head, r'<meta property="og:url" content="[^"]*">',
                    '<meta property="og:url" content="%s">' % url)
    head = set_meta(head, r'<meta property="og:image" content="[^"]*">',
                    '<meta property="og:image" content="%s">' % img)
    head = set_meta(head, r'<meta name="twitter:title" content="[^"]*">',
                    '<meta name="twitter:title" content="%s">' % html.escape(job["title"]))
    head = set_meta(head, r'<meta name="twitter:description" content="[^"]*">',
                    '<meta name="twitter:description" content="%s">' % html.escape(job["desc"][:150]))
    head = set_meta(head, r'<meta name="twitter:image" content="[^"]*">',
                    '<meta name="twitter:image" content="%s">' % img)
    head = set_meta(head, r'<link rel="canonical" href="[^"]*">',
                    '<link rel="canonical" href="%s">' % url)
    # --- JSON-LD from house objects ---
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
    assert len(lds) == 2, f"house ld count {len(lds)}"
    art = json.loads(lds[0]); bc = json.loads(lds[1])
    art["headline"] = job["title"]; art["description"] = job["desc"]
    art["image"] = img; art["datePublished"] = job["date"]; art["dateModified"] = job["date_mod"]
    art["mainEntityOfPage"]["@id"] = url; art["url"] = url; art["keywords"] = job["kw"]
    bc["itemListElement"][1]["name"] = BLOG_ZH[job["brand"]]
    bc["itemListElement"][1]["item"] = f"{BASE}/{job['brand']}/blog/"
    bc["itemListElement"][2]["name"] = job["title"]; bc["itemListElement"][2]["item"] = url
    new_ld = ('<script type="application/ld+json">%s</script>\n<script type="application/ld+json">%s</script>'
              % (json.dumps(art, ensure_ascii=False), json.dumps(bc, ensure_ascii=False)))
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*<script type="application/ld\+json">.*?</script>',
                  new_ld, head, count=1, flags=re.S)
    page = head + "\n<body>\n" + nav + "\n<article>\n<h1>%s</h1>\n%s\n</article>\n%s" % (
        html.escape(job["title"]), article_html, foot)
    return page, article_html

def depth_hist(t):
    hist = {}
    depth = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", t):
        if m.group(1):
            depth -= 1
        else:
            hist[depth] = hist.get(depth, 0) + 1
            depth += 1
    return hist, depth

def card_end(t, s):
    i, depth = s, 0
    while i < len(t):
        o = t.find("<div", i); c = t.find("</div>", i)
        if c == -1:
            return len(t)
        if o != -1 and o < c:
            depth += 1; i = o + 4
        else:
            depth -= 1; i = c + 6
            if depth == 0:
                return i
    return len(t)

def cards(t):
    res = []
    for m in re.finditer(r'<div class="article-card">', t):
        s = m.start(); e = card_end(t, s)
        blk = t[s:e]
        d = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
        res.append(dict(s=s, e=e, blk=blk, date=d.group(1) if d else ""))
    return res

def comp(tpl, job, abs_href):
    """按模板卡重建新卡：换 slug/标题/日期/标签/摘要，href 转目标形式。"""
    blk = tpl.replace("/%s.html" % job.get("old_slug", ""), "/%s.html" % job["stem"])
    blk = re.sub(r'(<h[23][^>]*>\s*<a [^>]*href=")([^"]*)(">)', lambda m: m.group(1) + abs_href + m.group(3), blk, count=1)
    blk = re.sub(r'(<h[23][^>]*>\s*<a [^>]*>)(.*?)(</a>)',
                 lambda m: m.group(1) + html.escape(job["title"]) + m.group(3), blk, count=1, flags=re.S)
    blk = re.sub(r"\d{4}-\d{2}-\d{2}", job["date"], blk)
    tags = "".join('<span class="tag">%s</span>' % t for t in job["tags"])
    if re.search(r'(?:<span class="tag">[^<]*</span>)+', blk):
        blk = re.sub(r'(?:<span class="tag">[^<]*</span>)+', tags, blk, count=1)
    ps = list(re.finditer(r"<p>(.*?)</p>", blk, re.S))
    if ps:
        m = ps[-1]
        blk = blk[:m.start()] + "<p>%s</p>" % html.escape(job["desc"]) + blk[m.end():]
    return blk


def insert_card(t, blk, date):
    cs = cards(t)
    assert cs, "no cards found"
    for c in cs:
        if c["date"] and c["date"] < date:
            return t[:c["s"]] + blk + "\n  " + t[c["s"]:]
    last = cs[-1]
    return t[:last["e"]] + "\n  " + blk + t[last["e"]:]


def main():
    done = []
    for job in JOBS:
        brand = job["brand"]
        slug = job["stem"]
        page, article_html = build_page(job)
        # --- self checks ---
        assert page.count("<h1") == 1, slug
        assert page.count("application/ld+json") == 2, slug
        for ld in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            json.loads(ld)
        assert page.count("**") == 0, f"{slug} stars"
        assert "https://***" not in page and page.count("https://schema.org") >= 2
        assert "<p>|" not in page
        want = textify(article_html)
        got = textify(page[page.find("<body"):])
        assert want in got or got.endswith(want) or want.replace(" ", "") in got.replace(" ", ""), f"{slug} body diff"
        out = os.path.join(SITE, brand, "blog", slug + ".html")
        old_size = os.path.getsize(out) if os.path.exists(out) else 0
        if APPLY:
            wr(out, page)
            cov = os.path.join(ART, "cover-%s.png" % slug)
            if os.path.exists(cov):
                shutil.copy2(cov, os.path.join(SITE, "img", slug + ".png"))
        done.append((slug, brand, old_size, len(page), os.path.exists(os.path.join(ART, "cover-%s.png" % slug))))
        print(f"[page] {brand}/{slug}: {old_size}B -> {len(page.encode())}B cover={done[-1][4]}")
    return done


if __name__ == "__main__":
    main()

