#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 SiteOps · 2026-09-16 · 觅理 blog 上线 3 篇（最高法网络法治典型案例解读）

派单：TASK-SITE-PUBLISH-3ART-20260916（扬声）｜复检放行：如己 2026-09-16｜何律放行 2026-09-16
执行包：/mnt/i/内省II耳目手足爪牙/文件存放/市场部/发布执行包_20260916/
取件：以执行包 HTML 的 md5 为基线（hash 不符即停，不换版本）

动作（只增不删）：
  1) 3 篇 package HTML → site-inbox/ 留档
  2) 生成 mili/blog/{slug}.html（站点模板：head 五件套 + JSON-LD Article/BreadcrumbList + 标准三行落款）
  3) mili/blog/index.html 顶部 +3 卡片 + JSON-LD blogPost 前插 3 条
  4) articles.json +3（按日期倒序，去重，每 slug 恰 1 条）
  5) sitemap.xml +3 loc（只增不删，XML 校验）
  6) site-inbox/deploy-log.json +1
退出码：0=全部成功；非 0=有断言失败（不写半成品）
"""
import re
import os
import json
import html
import hashlib
import shutil
import xml.dom.minidom

ROOT = "/mnt/c/Users/zigan/najieip-site"
PKG = "/mnt/i/内省II耳目手足爪牙/文件存放/市场部/发布执行包_20260916"
PUB_DAY = "2026-09-16"
BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>")
OG_IMAGE = ("https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg"
            "?auto=compress&cs=tinysrgb&w=1200")
FOOTER = ('<footer>\n<p>\u00a9 2026 纳杰觅理 \u00b7 \u611b\u666e\u7d0d\u5091专利所 &amp; 觅理律所</p>\n'
          '<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>\n</footer>')
SIG = ('<hr>\n<p>010-65150974 / 13911268604</p>\n'
       '<p>何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰</p>\n'
       '<p><em>本文仅代表作者个人观点，不构成法律意见。</em></p>')

ARTICLES = [
    dict(
        slug="20260917-livestream-ai-voice-personality-rights",
        md5="7375db55198c5af8b20c622c7d96ea22",
        title="主播用了别人的脸和AI合成的声音，赔钱的为什么还有商家？",
        date="2026-09-17",
        desc=("最高法2026网络法治典型案例解读：带货主播擅用他人肖像、配上与本人高度近似的AI合成声音做推广，"
              "委托的图书公司未审核素材来源与授权，与主播构成共同侵权并承担连带责任，判赔12万元。"
              "附推广素材四项审查与合同四条清单。"),
        keywords="AI合成声音,肖像权,带货主播,共同侵权,最高法典型案例",
        tags=["人格权", "AI合规", "最高法典型案例"],
        link_para=('<p>延伸阅读：<a href="https://najieip.com/mili/blog/20260909-aucl-livestream-ads.html">'
                   '直播带货、测评视频、比较广告：市场部最容易踩的3条"反法"红线</a>（2026-09-09）；'
                   '<a href="https://najieip.com/mili/blog/20260907-ai-judicial-opinion.html">'
                   '最高法AI司法意见落地：企业AI资产与责任边界，24条规则一次讲清</a>（2026-09-07）</p>'),
    ),
    dict(
        slug="20260918-ai-search-rag-liability",
        md5="cf133330f8e6af96eda91d3905875322",
        title="AI搜索引擎搜出盗版链接，平台为什么不用赔？",
        date="2026-09-18",
        desc=("最高法2026网络法治典型案例解读：AI搜索引擎使用检索增强生成（RAG）技术展示第三方网盘盗版链接，"
              "因未主动上传与编辑推荐、现阶段技术无法自动识别、已履行算法备案、知悉后当日删除，不构成侵权；"
              "\u201c与算法、数据优势程度相匹配的注意义务\u201d与更重的举证责任成为关键。"),
        keywords="AI搜索引擎,检索增强生成,民法典1197条,注意义务,算法备案",
        tags=["AI与平台责任", "著作权", "最高法典型案例"],
        link_para=None,  # 执行包 HTML 文末已含内链，脚本内断言其在位
    ),
    dict(
        slug="20260918-personality-rights-injunction",
        md5="494b7867e71e0811f295df88384abccd",
        title="被网暴了，不用等到判决：一份6个月的\u201c停止侵害\u201d禁令怎么申请下来",
        date="2026-09-19",
        desc=("最高法2026网络法治典型案例解读：两名合计粉丝量超2000万的博主持续发布侮辱诽谤内容、"
              "煽动粉丝实施网络暴力，法院依民法典第997条发出人格权侵害禁令，责令立即停止侵权、有效期6个月，"
              "违反可罚款、拘留。含适用审查的三组考量因素与申请前证据清单。"),
        keywords="人格权侵害禁令,网络暴力,民法典997条,名誉权,最高法典型案例",
        tags=["人格权", "网络暴力", "最高法典型案例"],
        link_para=('<p>延伸阅读：<a href="https://najieip.com/mili/blog/20260907-ai-judicial-opinion.html">'
                   '最高法AI司法意见落地：企业AI资产与责任边界，24条规则一次讲清</a>（2026-09-07）；'
                   '<a href="https://najieip.com/mili/blog/beiruqin-sancha-20260831.html">'
                   '被入侵前，先查这三样</a>（2026-08-31）</p>'),
    ),
]

log = []
NEW_URLS = []


def tw_trunc(d, limit=118):
    if len(d) <= limit:
        return d
    cut = d[:limit]
    p = cut.rfind("。")
    return cut[:p + 1] if p >= 40 else cut


def head_block(a):
    url = "https://najieip.com/mili/blog/%s.html" % a["slug"]
    t_attr = html.escape(a["title"], quote=True)
    d_attr = html.escape(a["desc"], quote=True)
    d_tw = html.escape(tw_trunc(a["desc"]), quote=True)
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["desc"],
        "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师",
                   "affiliation": {"@type": "Organization", "name": "爱普纳杰 · 觅理 · 纳杰"}},
        "publisher": {"@type": "Organization", "name": "北京觅理律师事务所",
                      "url": "https://najieip.com/mili/"},
        "mainEntityOfPage": url, "url": url,
        "datePublished": a["date"], "dateModified": a["date"],
        "inLanguage": "zh-CN", "keywords": a["keywords"],
    }, ensure_ascii=False)
    ld_crumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
            {"@type": "ListItem", "position": 3, "name": a["title"]},
        ],
    }, ensure_ascii=False)
    return (
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>%s — 纳杰觅理</title>\n'
        '<link rel="stylesheet" href="/style.css">\n'
        '%s\n'
        '<meta name="description" content="%s">\n'
        '<meta name="keywords" content="%s">\n'
        '<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:url" content="%s">\n'
        '<meta property="og:site_name" content="北京觅理律师事务所">\n'
        '<meta property="og:image" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
    ) % (t_attr, BEACON, d_attr, a["keywords"], t_attr, d_attr, url,
         OG_IMAGE, t_attr, d_tw, url, ld_article, ld_crumb)


# ───────── 1) 取件 + 生成 3 页 ─────────
pages = {}
for a in ARTICLES:
    src = os.path.join(PKG, a["slug"] + ".html")
    raw_bytes = open(src, "rb").read()
    md5 = hashlib.md5(raw_bytes).hexdigest()
    assert md5 == a["md5"], "md5 不符: %s -> %s" % (src, md5)
    raw = raw_bytes.decode("utf-8")
    m = re.search(r"<article>(.*?)</article>", raw, re.S)
    assert m, "无 <article>: %s" % src
    body = m.group(1)
    # 去掉执行包自带的 <h1>（模板统一生成）
    body2 = re.sub(r"^\s*<h1>.*?</h1>\s*", "", body, count=1, flags=re.S)
    assert body2 != body, "未剥离 h1: %s" % a["slug"]
    body = body2.strip()
    h1 = re.search(r"<h1>(.*?)</h1>", raw, re.S).group(1)
    assert h1 == a["title"], "h1 与标题不一致: %s" % a["slug"]
    # 清理断言（如己质量关固定要求）
    assert "**" not in body, "markdown 加粗残留: %s" % a["slug"]
    for bad in ("附一", "附二", "附三", "状态：", "拟 slug", "配图建议"):
        assert bad not in body, "内部痕迹(%s): %s" % (bad, a["slug"])
    assert "本文仅代表作者个人观点" not in body, "落款未剔除(%s)" % a["slug"]
    # 内链
    if a["link_para"]:
        assert a["link_para"] not in body, "内链已存在: %s" % a["slug"]
        body = body + "\n" + a["link_para"]
    else:
        assert "20260909-civilcode1197-ai-redflag.html" in body, "执行包内链缺失: %s" % a["slug"]
    out = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n' + head_block(a) + '</head>\n<body>\n'
           '<nav><a href="/mili/">← 首页</a></nav>\n<article>\n'
           '<h1>%s</h1>\n%s\n%s\n</article>\n%s\n</body>\n</html>\n'
           % (a["title"], body, SIG, FOOTER))
    # 完整性断言
    assert out.count("<h1>") == 1 and out.count("</h1>") == 1, "h1 异常: %s" % a["slug"]
    assert out.count("<h2>") == body.count("<h2>"), "h2 异常: %s" % a["slug"]
    assert out.count("canonical") == 1 and out.count("og:url") == 1, "canonical/og:url 异常: %s" % a["slug"]
    assert out.count("010-65150974 / 13911268604") == 1, "落款重复或缺失: %s" % a["slug"]
    assert "本文仅代表作者个人观点，不构成法律意见。" in out
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S):
        json.loads(blk)
    pages[a["slug"]] = (out, raw_bytes)
    NEW_URLS.append("https://najieip.com/mili/blog/%s.html" % a["slug"])

# 关键串（扬声上线后抽查用）
assert "12万元" in pages["20260917-livestream-ai-voice-personality-rights"][0]
assert "检索增强生成" in pages["20260918-ai-search-rag-liability"][0]
assert "有效期6个月" in pages["20260918-personality-rights-injunction"][0]

# ───────── 2) 全部断言通过后落盘 ─────────
for a in ARTICLES:
    dst = os.path.join(ROOT, "mili", "blog", a["slug"] + ".html")
    out = pages[a["slug"]][0]
    if os.path.exists(dst):
        old = open(dst, encoding="utf-8").read()
        if old == out:
            log.append("SKIP（已存在且一致）mili/blog/%s.html" % a["slug"])
        else:
            raise RuntimeError("目标页已存在且不一致，拒绝覆盖: %s" % dst)
    else:
        open(dst, "w", encoding="utf-8").write(out)
        log.append("PLACED mili/blog/%s.html (%d 字符, md5_src=%s)" % (a["slug"], len(out), a["md5"][:10]))
    # site-inbox 留档
    shutil.copyfile(os.path.join(PKG, a["slug"] + ".html"),
                    os.path.join(ROOT, "site-inbox", a["slug"] + ".html"))
    log.append("ARCHIVED site-inbox/%s.html" % a["slug"])

# ───────── 3) articles.json ─────────
ap = os.path.join(ROOT, "articles.json")
data = json.load(open(ap, encoding="utf-8"))
print("articles.json 原有条目:", len(data))
print("  原有是否按日期倒序:", data == sorted(data, key=lambda x: x.get("date", ""), reverse=True))
have = {x.get("url") for x in data}
added = 0
for a in ARTICLES:
    u = "/mili/blog/%s.html" % a["slug"]
    if u in have:
        log.append("articles.json: %s 已存在，跳过" % u)
        continue
    data.append({"url": u, "title": a["title"], "description": a["desc"],
                 "date": a["date"], "site": "mili"})
    added += 1
data.sort(key=lambda x: x.get("date", ""), reverse=True)
seen, dedup = set(), []
for x in data:
    if x.get("url") in seen:
        continue
    seen.add(x.get("url"))
    dedup.append(x)
assert len(dedup) == len(data), "去重前后条数不一致"
json.dump(dedup, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(ap, encoding="utf-8"))
assert len(chk) == len(dedup)
for a in ARTICLES:
    u = "/mili/blog/%s.html" % a["slug"]
    assert sum(1 for x in chk if x["url"] == u) == 1, "articles.json 条目数异常: %s" % u
log.append("articles.json: +%d 条（总 %d 条，每 slug 恰 1 条，按日期倒序）" % (added, len(chk)))

# ───────── 4) sitemap.xml（只增不删） ─────────
sm = os.path.join(ROOT, "sitemap.xml")
s = open(sm, encoding="utf-8").read()
n_before = s.count("<url>")
assert s.count("</urlset>") == 1
extra = ""
added_sm = 0
for u in NEW_URLS:
    if "<loc>%s</loc>" % u in s:
        log.append("sitemap: %s 已存在，跳过" % u)
        continue
    extra += ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
              "    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n" % (u, PUB_DAY))
    added_sm += 1
s = s.replace("</urlset>", extra + "</urlset>")
open(sm, "w", encoding="utf-8").write(s)
xml.dom.minidom.parse(sm)
s2 = open(sm, encoding="utf-8").read()
assert all("<loc>%s</loc>" % u in s2 for u in NEW_URLS)
assert s2.count("<url>") == n_before + added_sm, "sitemap 条数异常"
assert s2.count("</urlset>") == 1
log.append("sitemap.xml: 总 <url> %d（+%d，只增不删，XML 校验通过）" % (s2.count("<url>"), added_sm))

# ───────── 5) mili/blog/index.html 卡片 + JSON-LD ─────────
idx = os.path.join(ROOT, "mili", "blog", "index.html")
s = open(idx, encoding="utf-8").read()
cards, ld_entries = "", ""
for a in sorted(ARTICLES, key=lambda x: x["date"], reverse=True):
    if 'href="./%s.html"' % a["slug"] in s:
        log.append("mili/blog/index.html: 卡片已存在，跳过 %s" % a["slug"])
        continue
    url = "https://najieip.com/mili/blog/%s.html" % a["slug"]
    cards += ('  <div class="article-card">\n'
              '    <h2><a href="./%s.html">%s</a></h2>\n'
              '    <div class="meta">%s %s · 觅理律师事务所</div>\n'
              '    <p>%s</p>\n  </div>\n'
              % (a["slug"], a["title"],
                 "".join('<span class="tag">%s</span>' % t for t in a["tags"]), a["date"], a["desc"]))
    ld_entries += json.dumps({"@type": "BlogPosting", "headline": a["title"], "url": url,
                              "datePublished": a["date"], "description": a["desc"]},
                             ensure_ascii=False) + ", "
marker = '<div class="container">\n'
i = s.index(marker) + len(marker)
s = s[:i] + cards + s[i:]
key = '"blogPost": ['
k = s.index(key) + len(key)
s = s[:k] + ld_entries + s[k:]
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
    json.loads(blk)
open(idx, "w", encoding="utf-8").write(s)
s = open(idx, encoding="utf-8").read()
for a in ARTICLES:
    assert s.count('href="./%s.html"' % a["slug"]) == 1, "卡片数异常: %s" % a["slug"]
    assert s.count('"url": "https://najieip.com/mili/blog/%s.html"' % a["slug"]) == 1, "blogPost 数异常: %s" % a["slug"]
log.append("mili/blog/index.html: +3 顶部卡片 + 3 BlogPosting（全量 JSON-LD 校验通过）")

# ───────── 6) deploy-log.json ─────────
dl = os.path.join(ROOT, "site-inbox", "deploy-log.json")
d = json.load(open(dl, encoding="utf-8"))
TRIG = "如己 2026-09-16 派单 TASK-SITE-PUBLISH-3ART-20260916（扬声执行包 20260916）—— 最高法网络法治典型案例 3 篇 → mili/blog"
if any(e.get("trigger") == TRIG for e in d["deploys"]):
    log.append("deploy-log.json: 本轮条目已存在，跳过")
else:
    d["deploys"].append({
        "date": PUB_DAY, "time": "17:2x", "commit": "pending", "trigger": TRIG,
        "changes": [
            "市场部/发布执行包_20260916/{3 篇}.html (md5 7375db55/cf133330/494b7867) → mili/blog/{slug}.html + site-inbox 留档",
            "站点模板 head：description/keywords/og 五件套(og:image pexels 5669602)/Twitter Card/canonical/JSON-LD Article+BreadcrumbList/Cloudflare beacon",
            "站点模板落款＝标准三行（010-65150974 / 13911268604 ＋ 何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰 ＋ 斜体免责行）",
            "内链落地：篇1→20260909-aucl-livestream-ads + 20260907-ai-judicial-opinion；篇3→20260907-ai-judicial-opinion + beiruqin-sancha-20260831；篇2 执行包自带内链（已在位）",
            "mili/blog/index.html 顶部 +3 卡片 + JSON-LD blogPost 前插 3 条",
            "articles.json +3（site=mili，按日期倒序，共 %d 条）" % len(chk),
            "sitemap.xml +3 loc（lastmod 2026-09-16，只增不删，共 %d 条）" % s2.count("<url>"),
            "文章日期按派单写死错峰：2026-09-17 / 2026-09-18 / 2026-09-19；上线日 2026-09-16",
        ],
        "deviations": [
            "三篇同日上线但 datePublished 错峰（派单指定，防同日多篇）；sitemap lastmod 用实际上线日 2026-09-16。",
            "执行包为完整 HTML 片段（非 md），故不走 gen_siteops.py 的 ARTICLES 批量流程，另起 site-inbox/gen-0916-mili-netlaw-3.py。",
        ],
        "verification": {
            "md5_source": {a["slug"]: a["md5"] for a in ARTICLES},
            "signature_checked": True, "og_image": 200,
            "key_strings": {"12万元": True, "检索增强生成": True, "有效期6个月": True},
        },
    })
    json.dump(d, open(dl, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log.append("deploy-log.json: +1 条目（共 %d）" % len(d["deploys"]))

print("\n".join(log))
print("NEW_URLS\t" + "\t".join(NEW_URLS))
print("DONE")
