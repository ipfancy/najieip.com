#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
门丞 2026-10-23 补发：publish_queue 中 10-20 仅生成 .md、未生成 _visual.html 的两篇
（管道断点补发）。主体归属：商标新法 → najie；出海专利 → aipunajie。
用法: python3 site-inbox/publish-1023-menzheng.py [--apply]
"""
import json, os, re, sys, html, shutil

REPO = "/mnt/c/Users/zigan/najieip-site"
APPLY = "--apply" in sys.argv
Q = "/mnt/j/hermes-data/publish_queue"

NAJIE_ORG = "北京纳杰知识产权代理有限公司"
AIPU_ORG = "北京爱普纳杰专利代理事务所"
SITE = "https://najieip.com"

ARTICLES = [
    dict(
        src=os.path.join(Q, "20261020_132811_商标新法还剩72天.md"),
        slug="20261023-najie-trademark-law-70-days",
        cite="najie", dir="najie/blog",
        title="商标新法还剩70天",
        date="2026-10-23",
        org=NAJIE_ORG,
        byline="何自刚 | 知识产权律师 · 专利代理师 | " + NAJIE_ORG,
        tags=["商标法修订", "使用证据", "商标布局"],
        keywords="商标法修订,使用证据,撤三,商标布局,实体从旧程序从新,商标使用证据档案",
        desc=("2027年1月1日修订后的《商标法》施行，距今70天。新法主线是「使用与保护并重」，"
              "整治规范年行动已把恶意抢注、囤积商标、恶意撤三列为打击重点；配套办法确立「实体从旧、程序从新」——"
              "2027年前提交的注册申请、异议、驳回复审、续展，凡在新法施行后作出决定的都适用新法。"
              "另有一条易被忽略：以使用取得显著特征的证据须在收到通知之日起15日内提交。文末给清70天窗口该做完的三件事。"),
        crumb="纳杰博客",
        cta=dict(
            head="商标家底，值得盘一次",
            body="免费做一轮商标清单体检：注册号、类别、法律状态、续展期限、名义与地址变更，一次说清",
            entity=NAJIE_ORG + " · 商标 · 著作权",
        ),
        color="#7a1f2b",
    ),
    dict(
        src=os.path.join(Q, "20261020_132811_出海没查专利货被扣.md"),
        slug="20261023-aipunajie-overseas-patent-fto",
        cite="aipunajie", dir="aipunajie/blog",
        title="出海没查专利，货被扣",
        date="2026-10-23",
        org=AIPU_ORG,
        byline="何自刚 | 专利代理师 · 知识产权律师 | " + AIPU_ORG,
        tags=["出海FTO", "海外专利布局", "337调查"],
        keywords="出海FTO,自由实施分析,海外专利布局,337调查,专利地域性,PCT国际申请,巴黎公约优先权",
        desc=("货柜到港被海关扣、跨境店铺被平台下架、展会首日收到临时禁令——三件事的共同原因是出海前没查目的国专利。"
              "专利保护受地域限制，中国专利不覆盖境外。本文拆三种高频翻车场景（海关扣货、平台下架、展会与337调查）、"
              "出海前必做的两件事（FTO自由实施分析、海外专利布局：发明12个月优先权、外观设计6个月），"
              "以及已经被扣被诉后的三条原则与三个常见误区。"),
        crumb="爱普纳杰博客",
        cta=dict(
            head="产品要出海，先要一张雷区地图",
            body="出海前的FTO检索与海外专利布局：检索、申请、布局一条线做完；已被扣、被诉的，先做一轮快速评估",
            entity=AIPU_ORG + " · 专利代理",
        ),
        color="#1a5276",
    ),
]

CSS_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img_url}">
<meta property="og:site_name" content="{org}">
<meta property="og:locale" content="zh_CN">
<meta name="keywords" content="{keywords}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img_url}">
<link rel="canonical" href="{url}">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{ld_article}</script>
<script type="application/ld+json">{ld_crumb}</script>
</head>
<body>
<nav><a href="/">← 首页</a> · <a href="{blog_index}">{crumb}</a></nav>
<article>
"""


def smart_quotes(s):
    """ASCII 直引号 → 中文弯引号（正文规范，见 10-21 提交）"""
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("“" if open_q else "”")
            open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)


def md_to_html(md):
    """极简 md → HTML：# 标题丢弃（用页面 h1）、## → h2、**粗体**、段落。"""
    out = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            continue  # 标题由模版给出
        if line.startswith("## "):
            out.append("<h2>%s</h2>" % html.escape(smart_quotes(line[3:].strip())))
            continue
        para = html.escape(smart_quotes(line.strip()), quote=False)
        para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", para)
        out.append("<p>%s</p>" % para)
    return out


def build_body(a, md):
    md = md.replace("72天", "70天")
    assert "72天" not in md
    body = md_to_html(md)
    # 去微信专属话术 + 三主体合并署名单行（🔴规则9：正文只署发文主体）
    fixed = []
    for p in body:
        plain = re.sub(r"<[^>]+>", "", p).strip()
        if "点击下方" in p or "点击公众号菜单" in p:
            continue
        if plain.startswith("免费咨询电话："):
            continue
        if re.fullmatch(r"纳杰知识产权\s*[|｜]\s*爱普纳杰专利代理\s*[|｜]\s*觅理律师事务所", plain):
            continue
        fixed.append(p)
    fixed.insert(0, "<h1>%s</h1>" % html.escape(a["title"]))
    cta = a["cta"]
    block = (
        '<hr>\n'
        '<div style="background:{color};border-radius:10px;padding:26px 22px;margin:30px 0 8px;text-align:center;">'
        '<p style="color:#ffffff;font-size:17px;font-weight:bold;margin:0 0 12px;line-height:1.6;">{head}</p>'
        '<p style="color:rgba(255,255,255,0.92);font-size:14px;margin:0 0 14px;line-height:1.8;">{b}</p>'
        '<p style="color:#ffffff;font-size:15px;margin:0;line-height:1.8;">咨询电话：'
        '<span style="color:#c9a227;font-weight:bold;letter-spacing:1px;">13911268604（何律师）</span></p></div>'
        '<p style="text-align:center;color:{color};font-size:15px;font-weight:bold;letter-spacing:1px;margin:22px 0 6px;">{entity}</p>'
        '<p style="text-align:center;color:#5d7d93;font-size:12px;letter-spacing:3px;margin:0 0 10px;">专业 · 严谨 · 守护创新</p>'
    ).format(color=a["color"], head=cta["head"], b=cta["body"], entity=cta["entity"])
    tail = [
        "<p>%s</p>" % html.escape(a["byline"], quote=False),
        "<p>*本文由 AI 辅助生成与整理，观点与判断由作者审定。*</p>",
        "<p>*本文仅代表作者个人观点，不构成法律意见。如需具体分析，欢迎联系我们。*</p>",
        '<figure><img src="' + a["img"] + '" alt="' + a["title"] +
        '" loading="lazy" style="max-width:100%;height:auto">'
        '<figcaption>一图速览：' + a["title"] + '</figcaption></figure>',
    ]
    return "\n".join(fixed) + "\n" + block + "\n" + "\n".join(tail)


def build_page(a):
    md = open(a["src"], encoding="utf-8").read()
    url = "%s/%s/%s.html" % (SITE, a["dir"], a["slug"])
    a["img"] = "/img/%s.png" % a["slug"]
    img_url = SITE + a["img"]
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["desc"],
        "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师 · 专利代理师",
                   "worksFor": {"@type": "LegalService", "name": a["org"], "url": "%s/%s/" % (SITE, a["cite"])}},
        "publisher": {"@type": "Organization", "name": a["org"]},
        "image": img_url, "datePublished": a["date"], "dateModified": a["date"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "url": url, "keywords": a["keywords"],
    }, ensure_ascii=False)
    ld_crumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": a["crumb"], "item": "%s/%s/blog/" % (SITE, a["cite"])},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": url},
        ],
    }, ensure_ascii=False)
    head = CSS_HEAD.format(title=a["title"], desc=a["desc"], url=url, img_url=img_url, org=a["org"],
                           keywords=a["keywords"], ld_article=ld_article, ld_crumb=ld_crumb,
                           blog_index="/%s/blog/" % a["cite"], crumb=a["crumb"])
    body = build_body(a, md)
    footer = ('</article>\n<footer>\n<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>\n'
              '<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>\n</footer>\n</body>\n</html>\n')
    return head + body + "\n" + footer


NAJIE_CARD = """  <div class="article-card">
    <h2><a href="./{slug}.html">{title}</a></h2>
    <div class="meta">{tags} {date} · {org}</div>
    <p>{desc}</p>
  </div>
"""

AIPU_CARD = """<div class="article-card">
  <div class="date">{date}</div>
  <h3><a href="./{slug}.html">{title}</a></h3>
  <div class="excerpt">{desc}</div>
  {tags}
</div>
"""


def main():
    print("=== 1. 生成文章页 ===")
    pages = {}
    for a in ARTICLES:
        p = build_page(a)
        path = os.path.join(REPO, a["dir"], a["slug"] + ".html")
        pages[a["slug"]] = p
        print("  %s  (%d bytes)" % (path.replace(REPO + "/", ""), len(p.encode())))
        if APPLY:
            assert not os.path.exists(path), "已存在，拒绝覆盖: " + path
            open(path, "w", encoding="utf-8").write(p)

    print("=== 2. 更新三处索引 ===")
    idx_edits = [
        ("najie/blog/index.html", [ARTICLES[0]], "najie"),
        ("aipunajie/blog/index.html", [ARTICLES[1]], "aipu"),
        ("blog/index.html", ARTICLES, "main"),
    ]
    for rel, arts, mode in idx_edits:
        p = os.path.join(REPO, rel)
        t = open(p, encoding="utf-8").read()
        before = t.count('<div class="article-card">')
        add = ""
        for a in arts:
            if a["slug"] in t:
                print("  SKIP %s (%s 已在)" % (rel, a["slug"]))
                continue
            tagexpr = "".join('<span class="tag">%s</span>' % html.escape(x) for x in a["tags"])
            if mode == "aipu":
                add += AIPU_CARD.format(slug=a["slug"], title=html.escape(a["title"]), date=a["date"],
                                        desc=html.escape(a["desc"]), tags=tagexpr)
            else:
                href = "./%s.html" % a["slug"] if mode == "najie" else "/%s/blog/%s.html" % (a["cite"], a["slug"])
                card = NAJIE_CARD.format(slug="__HREF__", title=html.escape(a["title"]), tags=tagexpr,
                                         date=a["date"], org=a["org"], desc=html.escape(a["desc"]))
                add += card.replace('href="./__HREF__.html"', 'href="%s"' % href)
        if not add:
            continue
        anchor = '<div class="article-card">'
        pos = t.find(anchor)
        assert pos != -1, rel
        # 退到行首，保持缩进一致
        ls = t.rfind("\n", 0, pos) + 1
        t2 = t[:ls] + add + t[ls:]
        after = t2.count('<div class="article-card">')
        assert after == before + len(arts), "%s cards %d->%d" % (rel, before, after)
        assert t2.count("<div") == t2.count("</div>"), "%s div 不平衡" % rel
        print("  OK %s cards %d -> %d" % (rel, before, after))
        if APPLY:
            shutil.copyfile(p, p + ".bak-1023")
            open(p, "w", encoding="utf-8").write(t2)

    print("=== 3. articles.json ===")
    p = os.path.join(REPO, "articles.json")
    data = json.load(open(p, encoding="utf-8"))
    have = {d.get("url") for d in data}
    n0 = len(data)
    for a in ARTICLES:
        url = "/%s/%s.html" % (a["dir"], a["slug"])
        if url in have:
            print("  SKIP", url); continue
        data.insert(0, {"title": a["title"], "url": url, "date": a["date"],
                        "description": a["desc"], "tags": a["tags"], "site": a["cite"]})
    print("  entries %d -> %d" % (n0, len(data)))
    if APPLY:
        shutil.copyfile(p, p + ".bak-1023")
        json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("=== 4. sitemap.xml ===")
    p = os.path.join(REPO, "sitemap.xml")
    t = open(p, encoding="utf-8").read()
    add = ""
    for a in ARTICLES:
        url = "%s/%s/%s.html" % (SITE, a["dir"], a["slug"])
        if url in t:
            print("  SKIP", url); continue
        add += ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                "    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
                % (url, a["date"]))
    if add:
        t2 = t.replace("</urlset>", add + "</urlset>", 1)
        print("  loc %d -> %d" % (t.count("<loc>"), t2.count("<loc>")))
        if APPLY:
            shutil.copyfile(p, p + ".bak-1023")
            open(p, "w", encoding="utf-8").write(t2)


if __name__ == "__main__":
    main()
