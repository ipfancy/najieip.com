#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-0917-upc-article.py — 修复 mili/blog/20260917-upc-injunction-counterattack.html

三项缺陷（2026-09-17 巡检实测）：
  1) 正文首部泄漏 markdown frontmatter：`<p>---</p> / <p>ai_smell: 14.1</p> / <p>---</p>`
  2) 免责声明残留 markdown 斜体星号 `*...*`
  3) head 缺 og:image / twitter:title/description / Article+BreadcrumbList JSON-LD

幂等：已修项自动跳过。用法：python3 fix-0917-upc-article.py [--apply]
"""
import os, re, sys, json

SITE = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.join(SITE, "mili/blog/20260917-upc-injunction-counterattack.html")
URL = "https://najieip.com/mili/blog/20260917-upc-injunction-counterattack.html"
HEADLINE = "禁令突袭反被撤销：出海企业3招反打"
DESC = ("2025年9月IFA展会现场，科沃斯以单方命令让石头科技展品被扣；UPC杜塞尔多夫地方分庭于同年12月19日"
        "认定该命令违法作出、溯及既往全额撤销，2026年3月16日上诉法院维持原判并定性为程序滥用。败因只有一条："
        "申请时未披露己方代理人已在亚马逊买到涉案产品。对照追觅诉前行为保全被最高法撤销，附保护函、限缩检查、"
        "复审三步反打要点。")
OG_IMAGE = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"

LEAK_OLD = "<article>\n<p>---</p>\n<p>ai_smell: 14.1</p>\n<p>---</p>\n<br>\n<h1>"
LEAK_NEW = "<article>\n<h1>"
AST_OLD = "<p>*本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎在评论区留言。*</p>"
AST_NEW = "<p>本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎在评论区留言。</p>"

ARTICLE_LD = json.dumps({
    "@context": "https://schema.org", "@type": "Article", "headline": HEADLINE,
    "description": DESC,
    "image": OG_IMAGE,
    "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师",
               "affiliation": {"@type": "Organization", "name": "爱普纳杰 · 觅理 · 纳杰"}},
    "publisher": {"@type": "Organization", "name": "北京觅理律师事务所",
                  "url": "https://najieip.com/mili/"},
    "mainEntityOfPage": URL, "url": URL,
    "datePublished": "2026-09-17", "dateModified": "2026-09-17", "inLanguage": "zh-CN",
    "keywords": "涉外知识产权,UPC,单方命令,临时禁令,程序滥用",
}, ensure_ascii=False)

BREADCRUMB_LD = json.dumps({
    "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
        {"@type": "ListItem", "position": 3, "name": HEADLINE}]
}, ensure_ascii=False)


def main():
    apply = "--apply" in sys.argv
    t = open(ART, encoding="utf-8").read()
    before = t
    acts = []

    if LEAK_OLD in t:
        t = t.replace(LEAK_OLD, LEAK_NEW, 1)
        acts.append("移除 frontmatter 泄漏（<p>---</p>/ai_smell）")
    if AST_OLD in t:
        t = t.replace(AST_OLD, AST_NEW, 1)
        acts.append("移除免责声明残留星号")

    if 'property="og:image"' not in t:
        old_canon = '<link rel="canonical" href="%s">' % URL
        assert old_canon in t, "canonical 行未找到"
        t = t.replace(old_canon, old_canon + '\n<meta property="og:image" content="%s">' % OG_IMAGE, 1)
        acts.append("新增 og:image")

    old_tw = '<meta name="twitter:card" content="summary">'
    if old_tw in t and "twitter:title" not in t:
        new_tw = ('<meta name="twitter:card" content="summary_large_image">\n'
                  '<meta name="twitter:title" content="%s">\n'
                  '<meta name="twitter:description" content="%s">' % (HEADLINE, DESC))
        t = t.replace(old_tw, new_tw, 1)
        acts.append("升级 twitter card + title/description")

    if "application/ld+json" not in t:
        block = ('<script type="application/ld+json">\n%s\n</script>\n'
                 '<script type="application/ld+json">\n%s\n</script>\n' % (ARTICLE_LD, BREADCRUMB_LD))
        assert "</head>" in t
        t = t.replace("</head>", block + "</head>", 1)
        acts.append("新增 Article + BreadcrumbList JSON-LD")

    if not acts:
        print("✅ 无需修复（已全部满足）")
        return

    # 自检
    assert "https://***" not in t, "脱敏污染"
    assert t.count("https://schema.org") >= 2, "schema.org 计数异常"
    assert t.count("**") == 0, "markdown 双星号泄漏"
    assert "<p>---</p>" not in t and "ai_smell" not in t, "泄漏未清除"
    lo, hi = open(ART, encoding="utf-8").read(), t
    assert lo.count("<div") == hi.count("<div"), "div 开标签数变化异常"
    assert abs(hi.count("<div") - hi.count("</div>")) == 0, "div 配平破坏"

    print("待执行：")
    for a in acts:
        print("  ·", a)
    if not apply:
        print("[dry-run] 未写入。加 --apply 执行。")
        return
    open(ART, "w", encoding="utf-8").write(t)
    print("✅ 已写入", ART)


if __name__ == "__main__":
    main()
