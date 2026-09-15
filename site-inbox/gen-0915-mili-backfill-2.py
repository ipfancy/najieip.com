#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 SiteOps · 2026-09-15 · 9/14 两稿「补发官网」(mili/blog)

何律 2026-09-15 令《发布链路无等待铁律》动作1：时效稿先落自有渠道（官网 mili/blog），
不等王刚/知乎。

取件（如己已核准 md5，用「知乎发布版」同源文本——该版本已去内部元信息与法条核验表）：
  · /mnt/i/.../市场部/知乎发布版_20260914/知乎_无人继承遗产_发布版_20260914.md   md5 7a38dc694f
      标题《9位叔姑舅姨争遗产，房子为什么归了国家？》
  · /mnt/i/.../市场部/知乎发布版_20260914/知乎_胖东来学员制_发布版_20260914.md    md5 39f00a35f4
      标题《"四年学员制、到期不续签"：胖东来的新规，法律上站得住吗？》

主体归属：两篇均为法律/家事继承/劳动用工 → 觅理 mili/blog（三主体铁律）
动作：1) mili/blog 落页（markdown→HTML，复用站点 /style.css，文字零改动）
      2) articles.json +2；sitemap.xml +2
      3) mili/blog/index.html 顶部卡片 + JSON-LD blogPost
      4) site-inbox/deploy-log.json +1
      5) articles/ 零写入；不投 publish_queue 以外新管道
退出码：0=全部成功；非0=有断言失败（不写半成品）
"""
import re, json, os, hashlib, pathlib

ROOT = "/mnt/c/Users/zigan/najieip-site"
MKT = "/mnt/i/内省II耳目手足爪牙/文件存放/市场部"
QUEUE = "/mnt/j/hermes-data/publish_queue"  # 仅登记，不写入
os.chdir(ROOT)

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>")
TODAY = "2026-09-14"          # 稿件日期（补发上线日 2026-09-15 记入 deploy-log）
PUB_DAY = "2026-09-15"
OG_IMAGE = ("https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg"
            "?auto=compress&cs=tinysrgb&w=1200")
FOOTER = ('<footer>\n<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>\n'
          '<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>\n</footer>')

JOBS = [
    dict(
        slug="20260914-inheritance-no-heir-state",
        title="9位叔姑舅姨争遗产，房子为什么归了国家？",
        src=MKT + "/知乎发布版_20260914/知乎_无人继承遗产_发布版_20260914.md",
        md5_expect="7a38dc694f",
        desc=("人民法院案例库参考案例：赵女士无配偶、无子女、无兄弟姐妹，父母已故，2022年6月于北京昌平去世。"
              "9名叔姑舅姨主张分遗产，法院判房产收归国家，存款与保险权益按扶养情况酌分。"
              "两条规则讲清：叔姑舅姨不在《民法典》第1127条法定继承顺序内（继承权本不存在），"
              "无人继承遗产依第1160条归国家，而扶养较多者可依第1131条酌分适当遗产。"
              "附立遗嘱、签遗赠扶养协议、日常留痕三条实务建议。觅理律师事务所出品。"),
        keywords=("无人继承遗产,归国家所有,民法典继承编,第1127条,第1160条,第1131条,"
                  "叔姑舅姨,法定继承人,遗赠扶养协议,遗嘱,扶养较多,继承纠纷"),
        tags=["继承纠纷", "民法典", "遗产规划"],
    ),
    dict(
        slug="20260914-pangdonglai-trainee-labor-contract",
        title="\u201c四年学员制、到期不续签\u201d：胖东来的新规，法律上站得住吗？",
        src=MKT + "/知乎发布版_20260914/知乎_胖东来学员制_发布版_20260914.md",
        md5_expect="39f00a35f4",
        desc=("据于东来2026年9月13日社交媒体发文，胖东来新招员工将全部为\u201c学员\u201d、劳动合同四年一签到期不再续签"
              "（企业方面回应称尚未收到相关通知）——这是创始人的公开表态，不是已经落地的制度。"
              "假如真落地，四个法律要点：《劳动合同法》第44条（到期终止不当然违法）、第46条第5项与第47条"
              "（到期不续签要给经济补偿，四年约四个月工资）、第7条（\u201c学员\u201d称谓不改变\u201c用工即劳动关系\u201d的认定）、"
              "第14条第二款第三项（连续两次固定期限后的无固定期限问题）。附企业与打工人双向建议。觅理律师事务所出品。"),
        keywords=("胖东来学员制,劳动合同到期不续签,经济补偿金,无固定期限劳动合同,劳动合同法第14条,"
                  "劳动关系认定,用工风险,劳动仲裁,劳动者权益"),
        tags=["劳动用工", "劳动合同法", "企业合规"],
    ),
]

log = []
NEW_URLS = []


# ---------------- markdown -> HTML ----------------
def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", t)
    return t


def md_to_html(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s == "---":
            out.append("<hr>")
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2).strip()), lvl))
            i += 1
            continue
        if s.startswith("> "):
            buf = []
            while i < n and lines[i].strip().startswith("> "):
                buf.append(inline(lines[i].strip()[2:].strip()))
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % "<br>".join(buf))
            continue
        if re.match(r"^[-*]\s+", s):
            buf = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                buf.append("<li>%s</li>" % inline(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            out.append("<ul>\n%s\n</ul>" % "\n".join(buf))
            continue
        if re.match(r"^\d+\.\s+", s):
            buf = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                buf.append("<li>%s</li>" % inline(re.sub(r"^\d+\.\s+", "", lines[i].strip())))
                i += 1
            out.append("<ol>\n%s\n</ol>" % "\n".join(buf))
            continue
        out.append("<p>%s</p>" % inline(s))
        i += 1
    return "\n".join(out)


# ---------------- head ----------------
def tw_trunc(d, limit=118):
    """Twitter 摘要：按句号截断，避免半句"""
    if len(d) <= limit:
        return d
    cut = d[:limit]
    p = cut.rfind("。")
    return cut[:p + 1] if p >= 40 else cut


def head_block(j):
    url = "https://najieip.com/mili/blog/%s.html" % j["slug"]
    t_attr = j["title"].replace('"', "&quot;")
    d_attr = j["desc"].replace('"', "&quot;")
    t_tw = t_attr
    d_tw = tw_trunc(j["desc"]).replace('"', "&quot;")
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": j["title"], "description": j["desc"],
        "author": {"@type": "Person", "name": "何自刚"},
        "publisher": {"@type": "Organization", "name": "北京觅理律师事务所"},
        "datePublished": TODAY, "dateModified": TODAY,
        "mainEntityOfPage": url, "url": url,
    }, ensure_ascii=False)
    ld_crumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
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
        '<meta property="og:site_name" content="觅理律所">\n'
        '<meta property="og:image" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
    ) % (j["title"], BEACON, d_attr, j["keywords"], t_attr, d_attr, url,
         OG_IMAGE, t_tw, d_tw, url, ld_article, ld_crumb)


# ---------------- 1) 落页 ----------------
for j in JOBS:
    raw = open(j["src"], encoding="utf-8").read()
    md5 = hashlib.md5(raw.encode("utf-8")).hexdigest()
    assert md5.startswith(j["md5_expect"]), "md5 不符: %s -> %s" % (j["src"], md5)
    body = md_to_html(raw)
    nav = '<nav><a href="/mili/">← 首页</a></nav>'
    out = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n' + head_block(j) + '</head>\n<body>\n'
           + nav + '\n<article>\n' + body + '\n</article>\n' + FOOTER + '\n</body>\n</html>\n')
    # 完整性断言
    assert "**" not in out, "markdown 加粗残留: %s" % j["slug"]
    assert out.count("<strong>") == out.count("</strong>"), "strong 不配对: %s" % j["slug"]
    assert body.count("<p") == body.count("</p>"), "p 不配对: %s" % j["slug"]
    assert out.count("<h1>") == 1 and out.count("</h1>") == 1, "h1 异常: %s" % j["slug"]
    assert out.count("canonical") == 1 and out.count("og:url") == 1
    assert "&gt;" not in body and "&lt;" not in body, "HTML 转义异常: %s" % j["slug"]
    # 落款核验（标准三行）
    for must in ["010-65150974 / 13911268604",
                 "何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰",
                 "本文仅代表作者个人观点，不构成法律意见。"]:
        assert must in body, "落款缺失: %s / %s" % (j["slug"], must)
    dst = "mili/blog/%s.html" % j["slug"]
    open(dst, "w", encoding="utf-8").write(out)
    NEW_URLS.append("https://najieip.com/mili/blog/%s.html" % j["slug"])
    log.append("PLACED %s -> %s (md=%d chars, html=%d chars, h2=%d, md5=%s)"
               % (os.path.basename(j["src"]), dst, len(raw), len(out),
                  out.count("<h2>"), md5[:10]))

# ---------------- 2) articles.json ----------------
ap = "articles.json"
data = json.load(open(ap, encoding="utf-8"))
have = {a.get("url") for a in data}
added = 0
for j in JOBS:
    u = "/mili/blog/%s.html" % j["slug"]
    if u in have:
        log.append("articles.json: %s 已存在，跳过" % u)
        continue
    data.append({"url": u, "title": j["title"], "description": j["desc"],
                 "date": TODAY, "site": "mili"})
    added += 1
data.sort(key=lambda a: a.get("date", ""), reverse=True)
# 去重（保留首次出现）
seen, dedup = set(), []
for a in data:
    if a.get("url") in seen:
        continue
    seen.add(a.get("url"))
    dedup.append(a)
json.dump(dedup, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(ap, encoding="utf-8"))
assert len(chk) == len(dedup)
for j in JOBS:
    u = "/mili/blog/%s.html" % j["slug"]
    assert sum(1 for a in chk if a["url"] == u) == 1, "articles.json 条目数异常: %s" % u
log.append("articles.json: +%d 条（总 %d 条，每条 slug 恰 1 条）" % (added, len(chk)))

# ---------------- 3) sitemap.xml ----------------
sm = "sitemap.xml"
s = open(sm, encoding="utf-8").read()
assert s.count("</urlset>") == 1
extra = ""
for u in NEW_URLS:
    if "<loc>%s</loc>" % u not in s:
        extra += ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                  "    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
                  % (u, TODAY))
s = s.replace("</urlset>", extra + "</urlset>")
open(sm, "w", encoding="utf-8").write(s)
import xml.dom.minidom
xml.dom.minidom.parse(sm)
assert all("<loc>%s</loc>" % u in s for u in NEW_URLS)
log.append("sitemap.xml: 总 <url> %d（+%d，XML 校验通过，只增不删）" % (s.count("<url>"), len(NEW_URLS)))

# ---------------- 4) mili/blog/index.html 卡片 + JSON-LD ----------------
idx = "mili/blog/index.html"
s = open(idx, encoding="utf-8").read()
marker = '<div class="container">\n'
cards = ""
ld_entries = ""
for j in JOBS:
    if j["slug"] in s:
        log.append("%s: 卡片已存在，跳过 %s" % (idx, j["slug"]))
        continue
    url = "https://najieip.com/mili/blog/%s.html" % j["slug"]
    cards += ('  <div class="article-card">\n'
              '    <h2><a href="./%s.html">%s</a></h2>\n'
              '    <div class="meta">%s %s · 觅理律师事务所</div>\n'
              '    <p>%s</p>\n  </div>\n'
              % (j["slug"], j["title"],
                 "".join('<span class="tag">%s</span>' % t for t in j["tags"]),
                 TODAY, j["desc"]))
    ld_entries += (json.dumps({"@type": "BlogPosting", "headline": j["title"], "url": url,
                               "datePublished": TODAY, "description": j["desc"]},
                              ensure_ascii=False) + ", ")
if cards:
    i = s.find(marker)
    assert i > 0, "未找到 <div class=\"container\">"
    i += len(marker)
    s = s[:i] + cards + s[i:]
    key = '"blogPost": ['
    k = s.find(key)
    assert k > 0, "未找到 blogPost 键"
    k += len(key)
    s = s[:k] + ld_entries + s[k:]
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(idx, "w", encoding="utf-8").write(s)
    log.append("%s: +%d 顶部卡片 + JSON-LD blogPost（全量 JSON-LD 校验通过）" % (idx, len(JOBS)))
# 校验每 slug 卡片恰 1 条
for j in JOBS:
    c = s.count('href="./%s.html"' % j["slug"])
    assert c == 1, "index 卡片数异常(%d): %s" % (c, j["slug"])

# ---------------- 5) deploy-log.json ----------------
dl = "site-inbox/deploy-log.json"
d = json.load(open(dl, encoding="utf-8"))
TRIG = ("何律 2026-09-15 令《发布链路无等待铁律》动作1：9/14 两稿补发官网（不等王刚/知乎）"
        "— siteops 上门丞执行")
if any(e.get("trigger") == TRIG for e in d["deploys"]):
    log.append("deploy-log.json: 本轮条目已存在，跳过")
else:
    d["deploys"].append({
    "date": PUB_DAY, "time": "16:0x", "commit": "pending",
    "trigger": TRIG,
    "changes": [
        "市场部/知乎发布版_20260914/知乎_无人继承遗产_发布版_20260914.md (md5 7a38dc694f) -> mili/blog/20260914-inheritance-no-heir-state.html",
        "市场部/知乎发布版_20260914/知乎_胖东来学员制_发布版_20260914.md (md5 39f00a35f4) -> mili/blog/20260914-pangdonglai-trainee-labor-contract.html",
        "两页 md→HTML，文字零改动（未删改任何正文/落款），复用站点 /style.css（2026-09-15 已补齐，线上 200）",
        "站点标准 head：description/og 五件套（含 og:image pexels 5669602）/Twitter Card/canonical/JSON-LD Article+BreadcrumbList/Cloudflare beacon",
        "articles.json +2 条（site=mili，含 description 字段，按日期倒序重排去重，共 %d 条）" % len(chk),
        "sitemap.xml +2 条（lastmod 2026-09-14，只增不删，XML 校验通过，共 %d 条 <url>）" % s.count("<url>"),
        "mili/blog/index.html 顶部 +2 article-card，JSON-LD blogPost 首位插 2 条（JSON-LD 全量校验通过）",
        "articles/ 零写入；未投 publish_queue 以外任何新管道；稿件未改内容",
    ],
    "deviations": [
        "稿件日期＝2026-09-14（内容日，与同批 9/14 纳杰/爱普纳杰两篇一致），补发上线日＝2026-09-15。slug 前缀沿用 20260914。",
        "取件用「知乎发布版」（如己 2026-09-14 复检记录指定），非长文底稿——底稿含内部线索栏与法条核验表，对外版已去。",
        "本批不经 publish_queue（何律令：先落自有渠道）；publish_queue 内无对应 visual 件，故无三层去重归档。",
    ],
    "verification": {
        "md5_source": {"inheritance": "7a38dc694f6ddc4c6a61f7e6e6bcc701",
                       "pangdonglai": "39f00a35f45edfaa1ed0eda553300c9b"},
        "signature_checked": True,
        "style_css": 200,
        "index_cards": {j["slug"]: 1 for j in JOBS},
    },
})
json.dump(d, open(dl, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log.append("deploy-log.json: +1 条目（共 %d）" % len(d["deploys"]))

print("\n".join(log))
print("NEW_URLS\t" + "\t".join(NEW_URLS))
print("DONE")
