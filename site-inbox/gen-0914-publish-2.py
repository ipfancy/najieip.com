#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 SiteOps · 2026-09-14 发布队列两篇新稿上线（主体归属按三主体铁律人工判定）

来源：/mnt/j/hermes-data/publish_queue/
  · 20260914_101800_商标被驳回的6个原因_visual.html  → 纳杰（商标授权确权）
  · 20260914_101900_专利选错白等2年_visual.html      → 爱普纳杰（专利新申请/布局选型）
  （site_classifier.py 两篇均误判 mili，原因：LITIGATION_COMPOUND 正文兜底命中
    “维权/专利侵权诉讼”等词，压过标题强信号。本次按铁律人工裁定，见 deploy-log）

动作：1) 主体目录落页（自包含样式，不依赖根 /style.css——该文件线上 404，见 deploy-log）
      2) 正文 markdown/微信残留清理（内联 style、&nbsp; 空行、纯加粗段落→h2、---→hr）
      3) articles.json +2；sitemap.xml +2
      4) najie/blog/index.html 顶部卡片+JSON-LD；aipunajie/blog/index.html 顶部卡片+JSON-LD
      5) site-inbox/deploy-log.json +1
      6) articles/ 零写入
"""
import re, json, os, html

ROOT = "/mnt/c/Users/zigan/najieip-site"
QUEUE = "/mnt/j/hermes-data/publish_queue"
os.chdir(ROOT)

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>")
TODAY = "2026-09-14"

CSS = """<style>
:root{--primary:#1a5276;--primary-dark:#0e3a55;--accent:#C0A060;--text:#333;--muted:#666;}
*{box-sizing:border-box;}
body{margin:0;background:#f6f9fb;color:#333;font-size:16px;line-height:1.8;
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;}
nav{background:#fff;box-shadow:0 1px 10px rgba(0,0,0,.06);padding:14px 24px;font-size:15px;}
nav a{color:var(--primary);text-decoration:none;font-weight:600;margin-right:14px;}
nav a:hover{color:var(--accent);}
article{max-width:760px;margin:0 auto;background:#fff;padding:40px 32px 56px;
box-shadow:0 2px 16px rgba(0,0,0,.05);}
h1{font-size:26px;color:var(--primary-dark);line-height:1.45;margin:0 0 8px;}
h2{font-size:20px;color:var(--primary-dark);margin:32px 0 12px;padding-left:12px;
border-left:4px solid var(--accent);line-height:1.5;}
p{margin:0 0 16px;}
strong{color:var(--primary-dark);}
em{color:#3d5a73;}
hr{border:none;border-top:1px solid #e3e9ee;margin:28px 0;}
blockquote{margin:16px 0;padding:12px 16px;background:#f4f8fb;border-left:3px solid var(--primary);color:#44586a;}
ul,ol{padding-left:24px;}
li{margin:6px 0;}
img{max-width:100%;height:auto;}
.byline{color:#888;font-size:14px;text-align:center;margin:0 0 20px;}
.sig{color:var(--primary-dark);font-weight:600;}
@media(max-width:640px){article{padding:24px 18px 40px;}h1{font-size:22px;}h2{font-size:19px;}}
</style>"""

JOBS = [
    dict(
        site="najie",
        slug="20260914-trademark-rejection-six-reasons",
        title="商标被驳回的6个原因",
        page_title="商标被驳回的6个原因：六类驳回情形与收到驳回通知后的三步",
        date=TODAY,
        src=QUEUE + "/20260914_101800_商标被驳回的6个原因_visual.html",
        brand="纳杰知识产权",
        publisher="北京纳杰知识产权代理有限公司",
        blog_index="https://najieip.com/najie/blog/",
        desc=("商标驳回绝大多数不是运气不好，申请之前就能看出来。六类常见驳回情形逐个拆解："
              "缺显著特征（商标法11条）、与在先商标近似（30条）、碰禁用条款（10条）、损害在先权利或抢注（32条）、"
              "图样与商品项目选错、主体材料瑕疵。附收到驳回通知书后先做的三件事——算清15天复审期限（34条）、"
              "分清全部驳回与部分驳回并考虑分割申请、按使用证据/逐条论证不近似/清除障碍三条路定策略，"
              "以及复审不成向北京知识产权法院起诉的30日司法救济。"),
        keywords="商标驳回,驳回复审,15天复审期限,商标法第30条,商标分割申请,商标检索,撤三,商标撤销",
        tags=["商标驳回", "驳回复审", "商标检索"],
        og_image=("https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg"
                  "?auto=compress&cs=tinysrgb&w=1200"),
    ),
    dict(
        site="aipunajie",
        slug="20260914-patent-invention-vs-utility-model",
        title="专利选错，白等2年",
        page_title="专利选错，白等2年：发明与实用新型怎么选，一条被低估的同日双申请路",
        date=TODAY,
        src=QUEUE + "/20260914_101900_专利选错白等2年_visual.html",
        brand="爱普纳杰专利代理",
        publisher="北京爱普纳杰专利代理事务所",
        blog_index="https://najieip.com/aipunajie/blog/",
        desc=("发明与实用新型选错，是中小企业专利布局里最贵的一个决定：结构改良只报发明，两年后产品迭代两轮、"
              "手里一件授权专利都没有。六项差别（保护对象/保护期限/审查方式/创造性标准/授权速度/官费与稳定性）"
              "一次讲清，三条选型依据（技术生命周期、是不是命门、要这件专利干什么），"
              "以及同日双申请（专利法9条1款）换时间又换稳定性的打法与三个最常见的坑——先卖货再申请、"
              "把交底书当作业、授权后不管年费与外围布局。"),
        keywords="发明专利,实用新型专利,同日双申请,专利布局,专利法第9条,不丧失新颖性宽限期,专利年费",
        tags=["专利选型", "实用新型", "同日双申请"],
        og_image=("https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg"
                  "?auto=compress&cs=tinysrgb&w=1200"),
    ),
]

log = []
NEW_URLS = []


def head_block(j):
    url = "https://najieip.com/%s/blog/%s.html" % (j["site"], j["slug"])
    t_attr = html.escape(j["page_title"], quote=True)
    d_attr = html.escape(j["desc"], quote=True)
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": j["page_title"], "description": j["desc"],
        "author": {"@type": "Person", "name": "何自刚"},
        "publisher": {"@type": "Organization", "name": j["publisher"]},
        "datePublished": j["date"], "dateModified": j["date"],
        "mainEntityOfPage": url, "url": url,
    }, ensure_ascii=False)
    ld_crumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": "博客", "item": j["blog_index"]},
            {"@type": "ListItem", "position": 3, "name": j["page_title"]},
        ],
    }, ensure_ascii=False)
    return (
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>%s — 纳杰觅理</title>\n'
        '%s\n'
        '<meta name="description" content="%s">\n'
        '<meta name="keywords" content="%s">\n'
        '<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:url" content="%s">\n'
        '<meta property="og:site_name" content="%s">\n'
        '<meta property="og:image" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '%s\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
    ) % (html.escape(j["title"]), CSS, d_attr, j["keywords"], t_attr, d_attr, url,
         j["brand"], j["og_image"], t_attr, d_attr, url, BEACON, ld_article, ld_crumb)


SIG_PAT = re.compile(r"纳杰知识产权 \| 爱普纳杰|纳杰.*爱普纳杰.*觅理")


def convert_body(raw):
    body = re.search(r"<body[^>]*>(.*)</body>", raw, re.S).group(1)
    b = body
    b = re.sub(r'\s+style="[^"]*"', "", b)                 # 去内联样式
    b = re.sub(r'<p>\s*(?:&nbsp;|\s)*</p>', "", b)          # 去空行占位段
    b = re.sub(r"<p>\s*&nbsp;\s*</p>", "", b)
    b = b.replace("<p>---</p>", "<hr>")
    # 纯加粗段落 → h2（署名行除外）；段落内不跨段匹配：<strong> 内不含标签
    def prom(m):
        inner = m.group(1).strip()
        if SIG_PAT.search(inner):
            return '<p class="sig"><strong>%s</strong></p>' % inner
        return "<h2>%s</h2>" % inner
    b = re.sub(r"<p>\s*<strong>([^<]*)</strong>\s*</p>", prom, b)
    # 顶部“原创”署名行：移到 h1 之后
    m = re.search(r"<p>([^<]*原创[^<]*)</p>", b)
    if m:
        b = b.replace(m.group(0), "", 1)
        byline = '<p class="byline">%s</p>' % m.group(1)
        b = re.sub(r"(</h1>)", r"\1\n" + byline, b, count=1)
    # 单一外层容器 div：拆掉标签（标签数必须为 1/1，防误伤）
    assert b.count("<div>") == 1 and b.count("</div>") == 1, "外层 div 数量异常"
    b = b.replace("<div>", "").replace("</div>", "")
    b = re.sub(r"\n{3,}", "\n\n", b).strip()
    b = b.replace(" & ", " &amp; ")
    return b


# ---------- 1) 落页 ----------
for j in JOBS:
    raw = open(j["src"], encoding="utf-8").read()
    body = convert_body(raw)
    nav = ('<nav><a href="/">← 纳杰觅理</a>'
           '<a href="/%s/">%s</a>'
           '<a href="/%s/blog/">博客首页</a></nav>' % (j["site"], j["brand"], j["site"]))
    out = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n' + head_block(j) + '</head>\n<body>\n'
           + nav + '\n<article>\n' + body + '\n</article>\n'
           '</body>\n</html>\n')
    assert "style=" not in out.split("</head>")[1] or "style=" not in body, j["slug"]
    assert "**" not in out and "&gt;" not in body and "&nbsp;" not in body, j["slug"]
    assert out.count("canonical") == 1 and out.count("og:url") == 1
    # 标签完整性：strong 开闭配对、h2/p 不吞并后续段落
    assert out.count("<strong>") == out.count("</strong>"), "strong 标签不配对: %s" % j["slug"]
    for h in re.findall(r"<h2>(.*?)</h2>", body, re.S):
        assert "</" not in h, "h2 内混入闭合标签: %s" % h[:40]
    assert body.count("<p") == body.count("</p>"), "p 标签不配对: %s" % j["slug"]
    dst = "%s/blog/%s.html" % (j["site"], j["slug"])
    open(dst, "w", encoding="utf-8").write(out)
    NEW_URLS.append("https://najieip.com/%s/blog/%s.html" % (j["site"], j["slug"]))
    log.append("PLACED %s -> %s (%d->%d chars, h2=%d)" % (
        os.path.basename(j["src"]), dst, len(raw), len(out), out.count("<h2>")))

# ---------- 2) articles.json ----------
ap = "articles.json"
s = open(ap, encoding="utf-8").read()
assert s.startswith("[\n")
ins = ""
for j in JOBS:
    u = "/%s/blog/%s.html" % (j["site"], j["slug"])
    if '"%s"' % u in s:
        log.append("articles.json: %s 已存在，跳过" % u)
        continue
    ins += ('  {\n    "url": "%s",\n    "title": "%s",\n    "date": "%s",\n'
            '    "site": "%s"\n  },\n' % (u, j["title"], j["date"], j["site"]))
if ins:
    s = "[\n" + ins + s[2:]
    json.loads(s)
    open(ap, "w", encoding="utf-8").write(s)
log.append("articles.json: 总条目 %d" % len(json.load(open(ap, encoding="utf-8"))))

# ---------- 3) sitemap.xml ----------
sm = "sitemap.xml"
s = open(sm, encoding="utf-8").read()
assert s.count("</urlset>") == 1
extra = ""
for u in NEW_URLS:
    if "<loc>%s</loc>" % u not in s:
        extra += ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                  "    <changefreq>weekly</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
                  % (u, TODAY))
s = s.replace("</urlset>", extra + "</urlset>")
open(sm, "w", encoding="utf-8").write(s)
import xml.dom.minidom
xml.dom.minidom.parse(sm)
log.append("sitemap.xml: 总 <url> %d" % s.count("<url>"))


def prepend_ld(text, entries, label):
    """在传入的 HTML 文本中，把 entries 插到 blogPost 数组首位（不重读文件，避免覆盖同批改动）"""
    key = '"blogPost": ['
    k = text.find(key)
    if k < 0:
        log.append("%s: 未找到 blogPost 键，跳过 JSON-LD" % label)
        return text
    k += len(key)
    return text[:k] + entries + text[k:]


# ---------- 4) 索引卡片 + JSON-LD ----------
nj = "najie/blog/index.html"
s = open(nj, encoding="utf-8").read()
j0 = JOBS[0]
if j0["slug"] in s:
    log.append("%s: 卡片已存在" % nj)
else:
    card = ('  <div class="article-card">\n'
            '    <h2><a href="./%s.html">%s</a></h2>\n'
            '    <div class="meta">%s %s · %s</div>\n'
            '    <p>%s</p>\n  </div>\n' % (
                j0["slug"], html.escape(j0["page_title"]),
                "".join('<span class="tag">%s</span>' % t for t in j0["tags"]),
                j0["date"], j0["brand"], html.escape(j0["desc"])))
    marker = '<div class="container">\n'
    i = s.find(marker) + len(marker)
    s = s[:i] + card + s[i:]
    ld = json.dumps({"@type": "BlogPosting", "headline": j0["page_title"],
                     "url": NEW_URLS[0], "datePublished": j0["date"],
                     "description": j0["desc"]}, ensure_ascii=False) + ", "
    s = prepend_ld(s, ld, nj)
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(nj, "w", encoding="utf-8").write(s)
    log.append("%s: 顶部 article-card + JSON-LD blogPost 插入" % nj)

ap_idx = "aipunajie/blog/index.html"
s = open(ap_idx, encoding="utf-8").read()
j1 = JOBS[1]
if j1["slug"] in s:
    log.append("%s: 卡片已存在" % ap_idx)
else:
    card = ('<div class="article-card">\n'
            '  <div class="date">%s</div>\n'
            '  <h3><a href="./%s.html">%s</a></h3>\n'
            '  <div class="excerpt">%s</div>\n'
            '  %s\n</div>\n' % (
                j1["date"], j1["slug"], html.escape(j1["page_title"]),
                html.escape(j1["desc"]),
                "".join('<span class="tag">%s</span>' % t for t in j1["tags"])))
    marker = '<div class="articles">\n'
    i = s.find(marker) + len(marker)
    assert i > len(marker) - 1, ap_idx
    s = s[:i] + card + s[i:]
    ld = json.dumps({"@type": "BlogPosting", "headline": j1["page_title"],
                     "url": NEW_URLS[1], "datePublished": j1["date"],
                     "description": j1["desc"]}, ensure_ascii=False) + ", "
    s = prepend_ld(s, ld, ap_idx)
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(ap_idx, "w", encoding="utf-8").write(s)
    log.append("%s: 顶部 article-card + JSON-LD blogPost 插入" % ap_idx)

# ---------- 5) deploy-log ----------
dl = "site-inbox/deploy-log.json"
d = json.load(open(dl, encoding="utf-8"))
d["deploys"].append({
    "date": TODAY, "time": "10:40", "commit": "pending",
    "trigger": "门丞 SiteOps cron：publish_queue 检出 2 篇新稿（20260914_101800 / 20260914_101900）",
    "changes": [
        "publish_queue/20260914_101800_商标被驳回的6个原因_visual.html -> najie/blog/20260914-trademark-rejection-six-reasons.html（商标授权确权 → 纳杰）",
        "publish_queue/20260914_101900_专利选错白等2年_visual.html -> aipunajie/blog/20260914-patent-invention-vs-utility-model.html（专利新申请/布局选型 → 爱普纳杰）",
        "两文补站点标准 head：description/keywords/OG（og:site_name、og:image 已 curl 验证 200）/Twitter Card/canonical/JSON-LD Article+BreadcrumbList/Cloudflare beacon",
        "正文微信排版残留清理：去内联 style、去 33/27 处 &nbsp; 空行占位段、纯加粗段落 → <h2>（9/5 处）、--- → <hr>；文字内容零改动（第一稿为准）",
        "两页采用自包含 <style>（不依赖根 /style.css — 该文件线上 404，见 deviations）",
        "articles.json +2 条（site=najie / site=aipunajie）",
        "sitemap.xml +2 条主体目录 URL（lastmod 2026-09-14，只增不删，XML 校验通过）",
        "najie/blog/index.html 与 aipunajie/blog/index.html 顶部各 +1 article-card，JSON-LD blogPost 首位各插 1 条（JSON-LD 全量校验通过）",
        "articles/ 零写入（铁律：仅存历史跳转页，不新增）；mili/blog 本轮无新增",
    ],
    "deviations": [
        "主体归属人工裁定，未采纳 site_classifier.py 结果：该脚本对两文均返回 mili。原因：正文兜底规则 LITIGATION_COMPOUND 命中「维权」「专利侵权诉讼」等词且优先级高于标题强信号，把非诉文章误判为觅理。本次按三主体铁律人工判定（商标驳回→纳杰、专利选型→爱普纳杰）。建议后续给分类器加「标题强信号优先于正文兜底」的层级修正。",
        "根 /style.css 线上 404（curl 验证）：全站 najie/blog 下 41 个已发布页引用 href=\"/style.css\"，均取不到样式表。本轮两篇新页改用自包含内联 <style> 规避；该缺陷未在本轮修复（影响面涉及 41 页历史稿件外观，需单独评审），仅记录待办。",
        "发布队列两文的对应 .md 与 _visual.html 未写入 _published/：本 cron 章程以 last_site_deploy 时间戳为增量判据，不做 _published 归档（与 site_publish.py 的三层去重链路并行，互不冲突）。",
    ],
    "verification": {
        "git_fetch_synced": True,
        "og_image_curl": {"5669602": 200, "3183150": 200},
        "style_css_404": True,
        "queue_files": ["20260914_101800_商标被驳回的6个原因_visual.html",
                        "20260914_101900_专利选错白等2年_visual.html"],
    },
})
json.dump(d, open(dl, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log.append("deploy-log.json: +1 条目（共 %d）" % len(d["deploys"]))

print("\n".join(log))
print("DONE")
