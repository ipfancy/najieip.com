#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 · 主体归属纠偏（第二批 · 2026-09-07 直推 articles/ 遗漏件）
两篇 2026-09-07 20:07 由 Mac 端发布脚本直推 articles/（无主体目录）的推广文章，
未走「精修归位」流程，属铁律违规（articles/ 仅存历史跳转页，不新增文章）：
  articles/20260907-ai-judicial-opinion.html  -> mili/blog/  (涉AI纠纷/AI侵权/责任边界 → 觅理)
  articles/20260907-trademark-law-2026.html   -> najie/blog/ (商标法2026/第56条/商标合规 → 纳杰)
动作：充实 head（description/keywords/OG/Twitter/canonical/JSON-LD/beacon），
      旧路径留跳转页，articles.json + sitemap + 两个主体索引（卡片 + JSON-LD blogPost 首位），
      en/fr 翻译页中文回链改主体路径。
"""
import re, json, os, html

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)

BEACON = "<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>"

JOBS = [
    dict(
        src="articles/20260907-ai-judicial-opinion.html",
        dst="mili/blog/20260907-ai-judicial-opinion.html",
        old_url="https://najieip.com/articles/20260907-ai-judicial-opinion.html",
        new_url="https://najieip.com/mili/blog/20260907-ai-judicial-opinion.html",
        title="最高法AI司法意见落地：企业AI资产与责任边界，24条规则一次讲清",
        desc="最高法《关于依法审理涉人工智能纠纷案件的意见》（法发〔2026〕10号）24条逐条拆解：过错责任为默认、责任按控制力分层；AI换脸拟声、网络开盒、大数据杀熟、辅助驾驶四大踩雷场景；训练数据合理使用、生成式AI避风港、AI生成内容侵权、开源豁免与AI发明人认定；数据权益双轨保护、证据妨碍推定与AI文书当庭核实义务。附企业现在就做的三件事。",
        keywords="涉AI纠纷,最高法24条,AI侵权,训练数据合规,AI发明人,过错责任",
        site_name="觅理律师事务所",
        publisher="北京觅理律师事务所",
        date="2026-09-07",
        tags=["人工智能", "涉AI纠纷", "诉讼合规"],
        brand="觅理律师事务所",
        blog_index=("https://najieip.com/mili/blog/", "觅理律师事务所 · 法律观察"),
    ),
    dict(
        src="articles/20260907-trademark-law-2026.html",
        dst="najie/blog/20260907-trademark-law-2026.html",
        old_url="https://najieip.com/articles/20260907-trademark-law-2026.html",
        new_url="https://najieip.com/najie/blog/20260907-trademark-law-2026.html",
        title="商标不是注册完就安全：新商标法56条开始管“怎么用”",
        desc="新《商标法》2026年6月26日通过、2027年1月1日施行（9章87条），新增第56条把“以误导公众的方式使用注册商标”单列罚则：最高罚经营额5倍或25万元，逾期不改撤销注册商标。另六大变化：异议期3个月缩至2个月、“在先合法权益”取代“在先权利”、依职权撤三恢复、许可质量条款升级、代理监管扩至从业人员。附企业现在该做的五件事。",
        keywords="商标法2026,第56条,误导性使用,依职权撤三,异议期2个月,商标合规",
        site_name="纳杰知识产权",
        publisher="北京纳杰知识产权代理有限公司",
        date="2026-09-07",
        tags=["商标法2026", "误导性使用", "商标合规"],
        brand="纳杰知识产权",
        blog_index=("https://najieip.com/najie/blog/", "纳杰知识产权 · 商标版权观察"),
    ),
]

log = []


def head_block(j, body_head):
    """用站点统一标准重写 head（保留 charset/viewport/title）"""
    t_attr = html.escape(j["title"], quote=True)
    d_attr = html.escape(j["desc"], quote=True)
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": j["title"], "description": j["desc"],
        "author": {"@type": "Person", "name": "何自刚"},
        "publisher": {"@type": "Organization", "name": j["publisher"]},
        "datePublished": j["date"], "dateModified": "2026-09-12",
        "mainEntityOfPage": j["new_url"], "url": j["new_url"],
    }, ensure_ascii=False)
    ld_crumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": "博客", "item": j["blog_index"][0]},
            {"@type": "ListItem", "position": 3, "name": j["title"]},
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
        '<meta property="og:site_name" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
    ) % (j["title"], BEACON, d_attr, j["keywords"], t_attr, d_attr, j["new_url"],
         j["site_name"], t_attr, d_attr, j["new_url"], ld_article, ld_crumb)


# ---------- 1. 主体目录落盘（精修 head + 内链纠正） ----------
for j in JOBS:
    src = open(j["src"], encoding="utf-8").read()
    # body 起始位置
    bi = src.find("<body>")
    assert bi > 0, j["src"]
    body = src[bi:]
    # 内链：同类文章旧 articles/ 路径 -> 主体路径（仅本批涉及的旧路径按镜像规则）
    for other in JOBS:
        body = body.replace(other["old_url"], other["new_url"])
    body = body.replace("/articles/20260907-ai-model-asset-three-track-decision.html",
                        "/mili/blog/20260907-ai-model-asset-three-track-decision.html")
    # 延伸阅读内链回本主体博客索引（旧文无此项，保持原状即可）
    out = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n' + head_block(j, body)
           + '</head>\n' + body)
    open(j["dst"], "w", encoding="utf-8").write(out)
    log.append("MOVED %s -> %s (%d->%d chars)" % (j["src"], j["dst"], len(src), len(out)))

# ---------- 2. 旧路径留跳转页 ----------
for j in JOBS:
    stub = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        '<meta http-equiv="refresh" content="0; url=/%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<meta name="robots" content="noindex, follow">\n'
        '<title>%s</title>\n</head>\n<body>\n'
        '<p>文章已迁移：<a href="%s">%s</a></p>\n</body>\n</html>\n'
    ) % (j["dst"], j["new_url"], j["title"], "/" + j["dst"], j["title"])
    open(j["src"], "w", encoding="utf-8").write(stub)
    log.append("STUB %s -> /%s" % (j["src"], j["dst"]))

# ---------- 3. articles.json ----------
ap = "articles.json"
s = open(ap, encoding="utf-8").read()
before = s
for j in JOBS:
    s = s.replace('"url": "/%s"' % j["src"], '"url": "/%s"' % j["dst"])
json.loads(s)
open(ap, "w", encoding="utf-8").write(s)
log.append("articles.json: url 修正 = %s" % (before != s))

# ---------- 4. sitemap.xml（只增不删） ----------
sm = "sitemap.xml"
s = open(sm, encoding="utf-8").read()
assert s.count("</urlset>") == 1
extra = ""
for j in JOBS:
    if "<loc>%s</loc>" % j["new_url"] not in s:
        extra += ("  <url>\n    <loc>%s</loc>\n    <lastmod>2026-09-12</lastmod>\n"
                  "    <changefreq>weekly</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
                  % j["new_url"])
s = s.replace("</urlset>", extra + "</urlset>")
open(sm, "w", encoding="utf-8").write(s)
import xml.dom.minidom
xml.dom.minidom.parse(sm)
log.append("sitemap.xml: +%d 主体 URL，总 URL 数 %d"
           % (len(JOBS), s.count("<url>")))

# ---------- 5. en/fr 翻译页中文回链 ----------
for p in ("en/blog/20260907-ai-judicial-opinion-en.html",
          "fr/blog/20260907-ai-judicial-opinion-fr.html"):
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        n = t.replace('href="/articles/20260907-ai-judicial-opinion.html"',
                      'href="/mili/blog/20260907-ai-judicial-opinion.html"')
        if n != t:
            open(p, "w", encoding="utf-8").write(n)
            log.append("%s: 中文回链 → mili/blog" % p)

# ---------- 6. 主体索引：顶部 article-card + JSON-LD blogPost 首位 ----------
for j in JOBS:
    idxp = j["dst"].split("/")[0] + "/blog/index.html"
    s = open(idxp, encoding="utf-8").read()
    if j["dst"].split("/")[-1] in s:
        log.append("%s: 卡片/条目已存在，跳过" % idxp)
        continue
    card = ('  <div class="article-card">\n'
            '    <h2><a href="./%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>\n'
            % (j["dst"].split("/")[-1], html.escape(j["title"]),
               "".join('<span class="tag">%s</span>' % t for t in j["tags"]),
               j["date"], j["brand"], html.escape(j["desc"])))
    marker = '<div class="container">\n'
    i = s.find(marker)
    assert i > 0, idxp
    i += len(marker)
    s = s[:i] + card + s[i:]
    entry = json.dumps({
        "@type": "BlogPosting", "headline": j["title"], "url": j["new_url"],
        "datePublished": j["date"], "description": j["desc"],
    }, ensure_ascii=False)
    key = '"blogPost": ['
    k = s.find(key)
    assert k > 0, idxp
    k += len(key)
    s = s[:k] + entry + ", " + s[k:]
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(idxp, "w", encoding="utf-8").write(s)
    log.append("%s: 顶部 article-card + JSON-LD 首位插入" % idxp)

# ---------- 7. deploy-log ----------
dl = "site-inbox/deploy-log.json"
d = json.load(open(dl, encoding="utf-8"))
d["deploys"].append({
    "date": "2026-09-12", "time": "23:40", "commit": "pending",
    "trigger": "门丞 SiteOps cron 例行巡检（发布队列空 → 转主体归属专项）",
    "changes": [
        "发布队列无新稿（最新 visual.html 2026-08-25，早于 last_site_deploy 2026-09-12 10:35）",
        "专项排查发现 2026-09-07 20:07 Mac 端直推 articles/ 的两篇推广文章未走精修归位流程（铁律：articles/ 禁新增文章）",
        "articles/20260907-ai-judicial-opinion.html -> mili/blog/20260907-ai-judicial-opinion.html（涉AI纠纷/AI侵权/责任边界 → 觅理；系 20260908《AI生成内容被告》文中预告的“24条逐条拆解”续篇）",
        "articles/20260907-trademark-law-2026.html -> najie/blog/20260907-trademark-law-2026.html（商标法2026/第56条/商标合规 → 纳杰）",
        "两文 head 补齐站点标准：description/keywords/OG(含 og:site_name 主体)/Twitter/canonical/JSON-LD Article+BreadcrumbList/Cloudflare beacon",
        "旧 articles/ 路径改跳转页（meta refresh + canonical + noindex, follow），保留已收录 URL",
        "articles.json url 两条改主体路径；sitemap.xml +2 主体 URL（只增不删）",
        "mili/blog/index.html、najie/blog/index.html 顶部 article-card + JSON-LD blogPost 首位插入",
        "en/blog、fr/blog 两篇翻译页中文回链改指 mili/blog",
        "未办事项（专项批次）：articles/ 仍存 20 篇完整文章未归位（其中 10 篇主体目录已有同名件可直接转跳转，10 篇需按标题重新归类）",
    ],
    "verification": {
        "queue_empty": True,
        "git_fetch_synced": True,
        "articles_full_remaining": 20,
    },
    "systemic_note": "同类违规累计 4 起（0907×2 + 0912×2），根因同前：Mac 端发布脚本落盘目录写死为 articles/ 与 blog/ 根。建议尽快把脚本落盘目录改为 najie/blog、aipunajie/blog、mili/blog；另建议一次性清理 articles/ 遗留 20 篇完整页。",
})
json.dump(d, open(dl, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log.append("deploy-log.json: +1 条目")

print("\n".join(log))
print("DONE")
