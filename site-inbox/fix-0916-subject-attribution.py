#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 · 主体归属纠偏（第三批 · 2026-09-16 直推 articles/ 遗漏件）
两篇 2026-09-16 由 Mac 端分发脚本直推 articles/（无主体目录）的文章，
未走「精修归位」流程，属铁律违规（articles/ 仅存历史跳转页，不新增文章）：
  articles/20260916-inventor-remuneration-907.html -> mili/blog/ (职务发明报酬·最高法知民终907号判例 → 觅理)
  articles/20260916-data-asset-four-step.html      -> najie/blog/ (数据确权/登记/入表/质押 → 纳杰 非诉)
动作：修 markdown 残留（**加粗/| 表格/---/*斜体/转义注释）→ 充实 head（description/keywords/OG/Twitter/
      canonical/JSON-LD/beacon）→ 旧路径留跳转页 → articles.json + sitemap + 两个主体索引（卡片 + JSON-LD）。
"""
import re, json, os, html

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>")
NAJIE_IMG = "https://images.pexels.com/photos/48148/documents-accent-tear-48148.jpeg?auto=compress&cs=tinysrgb&w=1200"
MILI_IMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"

JOBS = [
    dict(
        src="articles/20260916-inventor-remuneration-907.html",
        dst="mili/blog/20260916-inventor-remuneration-907.html",
        old_url="https://najieip.com/articles/20260916-inventor-remuneration-907.html",
        new_url="https://najieip.com/mili/blog/20260916-inventor-remuneration-907.html",
        subject="mili",
        title="产品整体还在亏损，公司仍被判付 80 万：离职发明人的报酬怎么算",
        desc=("最高法知产法庭（2024）最高法知民终907号：产品整体亏损不是拒付理由——《促进科技成果转化法》"
              "第45条按“每年”营业利润提取不低于5%；证据在单位手里，发明人不必自掏审计费，可请求法院责令提交；"
              "80万＝48018万×5%×20%÷6人。附《专利法》15条、《专利法实施细则》92—94条，企业与发明人双向清单。"),
        ogdesc=("产品和公司都还在亏损，为什么法院仍判付发明人80万？最高法知民终907号把“以年为单位算营业利润”"
                "和举证责任两条规则说清楚了。"),
        keywords="职务发明报酬,发明人奖励与报酬,专利法第15条,专利法实施细则94条,促进科技成果转化法45条,最高法知民终907号",
        site_name="觅理律师事务所",
        publisher="北京觅理律师事务所",
        img=MILI_IMG,
        tags=["职务发明", "发明人报酬", "专利诉讼"],
        date="2026-09-16",
        index="mili/blog/index.html",
        index_href="./20260916-inventor-remuneration-907.html",
        index_brand="觅理律师事务所",
        blog_index=("https://najieip.com/mili/blog/", "觅理律师事务所 · 法律观察"),
    ),
    dict(
        src="articles/20260916-data-asset-four-step.html",
        dst="najie/blog/20260916-data-asset-four-step.html",
        old_url="https://najieip.com/articles/20260916-data-asset-four-step.html",
        new_url="https://najieip.com/najie/blog/20260916-data-asset-four-step.html",
        subject="najie",
        title="你的数据能换5000万吗？4步闭环",
        desc=("2026年9月2日上海市知识产权局为首个虚拟歌手音频数据集发出数据产品知识产权登记证书——"
              "数据从服务器里的文件变成能质押、能入表、能维权的资产。四步不能颠倒：A轨数据产权登记与B轨数据"
              "知识产权登记怎么选、数据资产质押四个真实案例（5000万/3000万/1000万/200万）、入表为何要登记凭证、"
              "证书只是初步证据不是权利。附今天就能做的3件事。"),
        ogdesc=("数据已经从服务器里的文件，变成能抵押、能入表、能打官司的资产。顺序错了，前面全白干——"
                "登记、质押、入表、维权四步拆解。"),
        keywords="数据知识产权登记,数据资产入表,数据资产质押,数据确权,AIGC版权,虚拟人",
        site_name="纳杰知识产权",
        publisher="北京纳杰知识产权代理有限公司",
        img=NAJIE_IMG,
        tags=["数据资产", "数据知识产权登记", "AIGC"],
        date="2026-09-16",
        index="najie/blog/index.html",
        index_href="./20260916-data-asset-four-step.html",
        index_brand="纳杰知识产权",
        blog_index=("https://najieip.com/najie/blog/", "纳杰知识产权 · 商标版权观察"),
    ),
]

log = []


# ---------- 0. markdown 残留清理 ----------
def fix_md(body: str) -> str:
    # 表格块：连续 <p>| ... |</p>
    def conv_table(m):
        rows = []
        for pm in re.finditer(r'<p>(\|[^<]*\|)</p>', m.group(0)):
            cells = [c.strip() for c in pm.group(1).strip().strip('|').split('|')]
            rows.append(cells)
        if not rows:
            return m.group(0)
        head, data = None, rows
        if len(rows) >= 2 and all(re.fullmatch(r':?-{2,}:?', c) for c in rows[1] if c):
            head, data = rows[0], rows[2:]
        out = '<table>'
        if head:
            out += '<thead><tr>' + ''.join('<th>%s</th>' % c for c in head) + '</tr></thead>'
        out += '<tbody>' + ''.join('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>'
                                   for r in data) + '</tbody></table>'
        return out

    body = re.sub(r'(?:<p>\|[^<]*\|</p>\n?)+', conv_table, body)
    # 独立粗体行 → h2 小节标题（仅结构性小标题；联系方式等非标题行保留加粗）
    def bold_line(m):
        t = m.group(1).strip()
        if re.match(r'^(第[一二三四五六七八九十]+步|今天就能做的|写在最后)', t) or \
           re.match(r'^[一二三四五六七八九十]+[、．]', t) or (len(t) <= 30 and '：' not in t):
            return '<h2>%s</h2>' % t
        return '<p><strong>%s</strong></p>' % t

    body = re.sub(r'<p>\*\*([^*]+?)\*\*</p>', bold_line, body)
    # 行内加粗 / 斜体
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    body = re.sub(r'<p>\*(.+?)\*</p>', r'<p><em>\1</em></p>', body)
    # 引用行 → blockquote
    body = re.sub(r'<p>&gt;\s*(.*?)</p>', r'<blockquote><p>\1</p></blockquote>', body, flags=re.S)
    # 分隔线
    body = re.sub(r'<p>---</p>', '<hr>', body)
    # 转义 HTML 注释（页面上会显示为文本）
    body = re.sub(r'<p>&lt;!--.*?--&gt;</p>\n?', '', body)
    # 块级元素前后的多余 <br>
    body = re.sub(r'<br>\s*(?=<(?:h2|hr|table|blockquote)\b)', '', body)
    body = re.sub(r'(</(?:h2|hr|table|blockquote)>)\s*<br>\s*', r'\1\n', body)
    # 折叠 3 个以上空行
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body


def build_head(j) -> str:
    art = {"@context": "https://schema.org", "@type": "Article", "headline": j["title"],
           "description": j["desc"], "author": {"@type": "Person", "name": "何自刚"},
           "publisher": {"@type": "Organization", "name": j["publisher"]},
           "datePublished": j["date"], "dateModified": j["date"],
           "mainEntityOfPage": j["new_url"], "url": j["new_url"]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "博客", "item": j["blog_index"][0]},
        {"@type": "ListItem", "position": 3, "name": j["title"]}]}
    d = lambda o: json.dumps(o, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
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
        '<meta property="og:image" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '</head>\n'
    ) % (j["title"], BEACON, j["desc"], j["keywords"], j["title"], j["ogdesc"],
         j["new_url"], j["site_name"], j["img"], j["title"], j["ogdesc"],
         j["new_url"], d(art), d(bc))


# ---------- 1. 归位到主体目录 ----------
for j in JOBS:
    src = open(j["src"], encoding="utf-8").read()
    body = src[src.index("<body>"):]
    body = fix_md(body)
    assert "**" not in body, "markdown 加粗残留: " + j["dst"]
    assert "<p>|" not in body, "markdown 表格残留: " + j["dst"]
    assert "<p>---</p>" not in body, "markdown 分隔线残留: " + j["dst"]
    assert body.rstrip().endswith("</html>"), j["dst"]
    new = build_head(j) + body
    # JSON-LD 合法性
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', new, re.S):
        json.loads(blk)
    open(j["dst"], "w", encoding="utf-8").write(new)
    log.append("MOVED %s -> %s (%d->%d chars)" % (j["src"], j["dst"], len(src), len(new)))

# ---------- 2. 旧路径留跳转页 ----------
for j in JOBS:
    base = os.path.basename(j["src"])
    stub = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
            '<title>%s</title>\n'
            '<meta http-equiv="refresh" content="0; url=/%s">\n'
            '<link rel="canonical" href="%s">\n'
            '</head>\n<body>\n'
            '<p>本文由%s发布，跳转中… <a href="/%s">%s</a></p>\n'
            '</body>\n</html>\n') % (j["title"], j["dst"], j["new_url"],
                                    j["site_name"], j["dst"], j["title"])
    open(j["src"], "w", encoding="utf-8").write(stub)
    log.append("STUB %s -> /%s" % (j["src"], j["dst"]))

# ---------- 3. articles.json ----------
s = open("articles.json", encoding="utf-8").read()
data = json.loads(s)
for j in JOBS:
    u = "/" + j["dst"]
    data = [d for d in data if d.get("url") != u]
    data.insert(0, {"url": u, "title": j["title"], "date": j["date"], "site": j["subject"]})
    # 旧 articles/ 条目 site 归属修正
    for d in data:
        if d.get("url") == "/articles/" + os.path.basename(j["dst"]):
            d["site"] = j["subject"]
open("articles.json", "w", encoding="utf-8").write(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n")
json.loads(open("articles.json", encoding="utf-8").read())
log.append("articles.json: 新增 2 条主体条目 + 旧 articles/ 条目 site 校正")

# ---------- 4. sitemap.xml ----------
s = open("sitemap.xml", encoding="utf-8").read()
add = ""
for j in JOBS:
    if j["new_url"] in s:
        log.append("sitemap.xml: %s 已存在，跳过" % j["new_url"])
        continue
    add += ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
            "    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
            % (j["new_url"], j["date"]))
s = s.replace("</urlset>", add + "</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write(s)
log.append("sitemap.xml: 新增 %d 条主体 URL（loc=%d）" % (len(JOBS), s.count("<loc>")))

# ---------- 5. 主体索引：顶部卡片 + JSON-LD 首位 ----------
for j in JOBS:
    p = j["index"]
    s = open(p, encoding="utf-8").read()
    if j["index_href"] in s:
        log.append("%s: 卡片已存在，跳过" % p)
    else:
        card = ('  <div class="article-card">\n'
                '    <h2><a href="%s">%s</a></h2>\n'
                '    <div class="meta">%s %s · %s</div>\n'
                '    <p>%s</p>\n'
                '  </div>\n' % (j["index_href"], j["title"],
                               "".join('<span class="tag">%s</span>' % t for t in j["tags"]),
                               j["date"], j["index_brand"], j["desc"]))
        marker = '<div class="container">\n'
        i = s.find(marker)
        assert i > 0, p
        i += len(marker)
        s = s[:i] + card + s[i:]
        log.append("%s: 顶部插入 article-card" % p)
    key = '"blogPost": ['
    if j["new_url"] in s:
        log.append("%s: JSON-LD 已存在，跳过" % p)
    else:
        entry = ('{"@type": "BlogPosting", "headline": "%s", "url": "%s", '
                 '"datePublished": "%s", "description": "%s"}'
                 % (j["title"], j["new_url"], j["date"], j["desc"]))
        i = s.find(key)
        assert i > 0, p
        i += len(key)
        s = s[:i] + entry + ", " + s[i:]
        log.append("%s: JSON-LD BlogPosting 首位插入" % p)
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(p, "w", encoding="utf-8").write(s)

print("\n".join(log))
print("DONE")
