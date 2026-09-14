#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 SiteOps · 2026-09-14 两篇 site-inbox 待归位真稿上线（主体归属：纳杰 → najie/blog/）
来源：site-inbox/HANDOFF-20260913-sysop.md 第二节（SelfMaintenance 09-13 修分叉时取出，
      两稿从未进过 origin/main，线上 /articles/ 与 /najie/blog/ 两条路径均 404）。
铁律遵守：articles/ 零写入（禁新增文章，仅存历史跳转页）；新文只进主体目录。
动作：1) 主体目录落页 + head 站点标准（description/keywords/OG/Twitter/canonical/JSON-LD/
        Cloudflare beacon）
      2) 正文 markdown 残留清理（**加粗**、&gt; 引用、---、&lt;!-- 注释、散落 <br>）
      3) articles.json +2 条（品牌路径，site=najie）
      4) sitemap.xml +2 条 najie/blog URL（只增不删）
      5) najie/blog/index.html 顶部 article-card ×2 + JSON-LD blogPost 首位
      6) site-inbox/deploy-log.json +1 条目
"""
import re, json, os, html

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>")
BRAND = "纳杰知识产权"
PUBLISHER = "北京纳杰知识产权代理有限公司"
BLOG_INDEX = ("https://najieip.com/najie/blog/", "纳杰知识产权 · 商标版权观察")
TODAY = "2026-09-14"

JOBS = [
    dict(
        slug="20260912-ai-digital-employee-deployment",
        title="AI 接管执行后，专业服务只剩 3 件事",
        date="2026-09-12",
        desc=("凌晨 1:30 余额归零，10 个定时任务同时欠费失败，2 小时后系统自己爬起来补齐当天主文——"
              "全程无人碰键盘。把当天所有需要人的节点摊开，只剩五类：出钱、担责、在场、裁量、定义，"
              "收敛成 3 件事：当主体、当出资人、当提问者。附「流程按能不能担责分三类」的落地三步法，"
              "与三条今天就能做的判断：先分类再上工具、第一批只交高频低裁量环节、买可审计可停手而非全自动。"),
        keywords="数字员工,AI原生组织,人机分工,AI落地,专业服务机构,知识产权服务",
        tags=["AI原生组织", "数字员工", "人机分工"],
        og_image=("https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg"
                  "?auto=compress&cs=tinysrgb&w=1200"),
    ),
    dict(
        slug="20260913-trademark-report-defense-rights",
        title="商标被举报别慌：这4条程序权利，能救回你的商标",
        date="2026-09-13",
        desc=("国知局「心机商标」治理专栏累计公示 1782 件依职权宣告无效的商标，注册近 20 年、"
              "8 月 13 日单批新增 54 件也在名单里——注册年限救不了你。新《商标法》第 70 条 2027 年 1 月 1 日"
              "才施行，但「举报商标」这条路现在就能走通。被举报后你手里有四条程序权利：申辩、听证、"
              "不得因申辩加重处罚、未告知未听取申辩不得下处罚决定。监管时钟：15 个工作日核查、"
              "立案后 90 日内决定，真正致命的是「限期改正」逾期不改→撤销注册商标。另附合规举报竞品的三条红线。"),
        keywords="心机商标,商标被举报,商标法第70条,陈述申辩,听证,撤销注册商标,商标使用合规",
        tags=["心机商标", "商标法第70条", "程序权利"],
        og_image=("https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg"
                  "?auto=compress&cs=tinysrgb&w=1200"),
    ),
]

log = []


def head_block(j):
    new_url = "https://najieip.com/najie/blog/%s.html" % j["slug"]
    t_attr = html.escape(j["title"], quote=True)
    d_attr = html.escape(j["desc"], quote=True)
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": j["title"], "description": j["desc"],
        "author": {"@type": "Person", "name": "何自刚"},
        "publisher": {"@type": "Organization", "name": PUBLISHER},
        "datePublished": j["date"], "dateModified": TODAY,
        "mainEntityOfPage": new_url, "url": new_url,
    }, ensure_ascii=False)
    ld_crumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": "博客", "item": BLOG_INDEX[0]},
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
        '<meta property="og:image" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
        '<script type="application/ld+json">\n%s\n</script>\n'
    ) % (j["title"], BEACON, d_attr, j["keywords"], t_attr, d_attr, new_url, BRAND,
         j["og_image"], t_attr, d_attr, new_url, ld_article, ld_crumb)


def polish_body(body):
    """markdown→HTML 残留清理（只动结构，不动文字）"""
    # 真实注释（原为转义的 &lt;!-- --&gt;）
    body = re.sub(r'<p>&lt;!--(.*?)--&gt;</p>', lambda m: '<!--' + m.group(1) + '-->',
                  body, flags=re.S)
    body = re.sub(r'&lt;!--(.*?)--&gt;', lambda m: '<!--' + m.group(1) + '-->', body, flags=re.S)
    # markdown 引用行 → blockquote
    body = re.sub(r'<p>&gt;\s*(.*?)</p>', lambda m: '<blockquote>%s</blockquote>' % m.group(1).strip(),
                  body, flags=re.S)
    # 分隔线
    body = body.replace('<p>---</p>', '<hr>')
    # **加粗** → <strong>
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    # 去掉独立成行的 <br>（站点排版用 <p> 间距，不靠 <br>）
    body = re.sub(r'^[ \t]*<br>[ \t]*\n', '', body, flags=re.M)
    # 压缩多余空行
    body = re.sub(r'\n{3,}', '\n\n', body)
    # 裸 & → &amp;（footer 内），仅限 "& " 形式
    body = body.replace("愛普納傑专利所 & 觅理律所", "愛普納傑专利所 &amp; 觅理律所")
    return body


NEW_URLS = []
# ---------- 1) 主体目录落页 ----------
for j in JOBS:
    src = "site-inbox/%s.html" % j["slug"]
    dst = "najie/blog/%s.html" % j["slug"]
    raw = open(src, encoding="utf-8").read()
    bi = raw.find("<body>")
    assert bi > 0, src
    body = polish_body(raw[bi:])
    out = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n' + head_block(j) + '</head>\n' + body
    assert "**" not in out, "markdown 加粗残留: %s" % dst
    assert "&gt;" not in out.split("</head>")[1].replace("&gt;", "", 0), "引用残留"
    assert out.count("og:url") == 1 and out.count("canonical") == 1
    open(dst, "w", encoding="utf-8").write(out)
    NEW_URLS.append("https://najieip.com/najie/blog/%s.html" % j["slug"])
    log.append("PLACED %s -> %s (%d->%d chars)" % (src, dst, len(raw), len(out)))

# ---------- 2) articles.json（纯文本前插，保持原文件混合缩进不被重排） ----------
ap = "articles.json"
s = open(ap, encoding="utf-8").read()
assert s.startswith("[\n"), ap
have = {e.get("url") for e in json.loads(s)}
ins = ""
for j in JOBS:
    u = "/najie/blog/%s.html" % j["slug"]
    if u in have or ('"%s"' % u) in s:
        log.append("articles.json: %s 已存在，跳过" % u)
        continue
    ins += ('  {\n'
            '    "url": "%s",\n'
            '    "title": "%s",\n'
            '    "date": "%s",\n'
            '    "site": "najie"\n'
            '  },\n' % (u, j["title"], j["date"]))
if ins:
    s = "[\n" + ins + s[2:]
    json.loads(s)
    open(ap, "w", encoding="utf-8").write(s)
log.append("articles.json: 条目总数 %d" % len(json.load(open(ap, encoding="utf-8"))))

# ---------- 3) sitemap.xml（只增不删） ----------
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
log.append("sitemap.xml: +%d URL，总 <url> %d" % (len(JOBS), s.count("<url>")))

# ---------- 4) najie/blog/index.html：顶部卡片 + JSON-LD blogPost 首位 ----------
idxp = "najie/blog/index.html"
s = open(idxp, encoding="utf-8").read()
if JOBS[0]["slug"] in s:
    log.append("%s: 卡片已存在，跳过" % idxp)
else:
    cards = ""
    for j in JOBS:
        cards += ('  <div class="article-card">\n'
                  '    <h2><a href="./%s.html">%s</a></h2>\n'
                  '    <div class="meta">%s %s · %s</div>\n'
                  '    <p>%s</p>\n'
                  '  </div>\n'
                  % (j["slug"], html.escape(j["title"]),
                     "".join('<span class="tag">%s</span>' % t for t in j["tags"]),
                     j["date"], BRAND, html.escape(j["desc"])))
    marker = '<div class="container">\n'
    i = s.find(marker)
    assert i > 0, idxp
    i += len(marker)
    s = s[:i] + cards + s[i:]
    key = '"blogPost": ['
    k = s.find(key)
    assert k > 0, idxp
    k += len(key)
    entries = ""
    for j in JOBS:
        entries += json.dumps({
            "@type": "BlogPosting", "headline": j["title"],
            "url": "https://najieip.com/najie/blog/%s.html" % j["slug"],
            "datePublished": j["date"], "description": j["desc"],
        }, ensure_ascii=False) + ", "
    s = s[:k] + entries + s[k:]
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(idxp, "w", encoding="utf-8").write(s)
    log.append("%s: 顶部 article-card ×2 + JSON-LD blogPost 首位插入" % idxp)

# ---------- 5) deploy-log ----------
dl = "site-inbox/deploy-log.json"
d = json.load(open(dl, encoding="utf-8"))
d["deploys"].append({
    "date": TODAY, "time": "09:00", "commit": "pending",
    "trigger": "门丞 SiteOps cron：发布队列零新稿 → 落实 0913 分叉修复遗留的 2 篇待归位真稿（HANDOFF-20260913-sysop.md 第二节）",
    "changes": [
        "site-inbox/20260912-ai-digital-employee-deployment.html -> najie/blog/20260912-ai-digital-employee-deployment.html（AI 系统/数字员工/专业服务 → 纳杰）",
        "site-inbox/20260913-trademark-report-defense-rights.html -> najie/blog/20260913-trademark-report-defense-rights.html（商标程序权利/第70条 → 纳杰）",
        "两文补站点标准 head：description/keywords/OG（含 og:site_name=纳杰知识产权、og:image 已 curl 验证 200）/Twitter Card/canonical/JSON-LD Article+BreadcrumbList/Cloudflare beacon",
        "正文 markdown 残留清理：**加粗**→<strong>、&gt; 引用→<blockquote>、---→<hr>、转义注释→真实注释、去散落 <br>；文字内容零改动（第一稿为准）",
        "articles.json +2 条（品牌路径 /najie/blog/*，site=najie）",
        "sitemap.xml +2 条 najie/blog URL（lastmod 2026-09-14，只增不删，XML 校验通过）",
        "najie/blog/index.html 顶部 article-card ×2 + JSON-LD blogPost 首位插入（JSON-LD 全量校验通过）",
        "articles/ 零写入（铁律：仅存历史跳转页，不新增）",
    ],
    "deviations": [
        "HANDOFF 第二节第 2 项建议为两文在 /articles/{slug}.html 留跳转页——本轮未执行：①门丞 cron 章程明令 git add 只加主体目录、articles/ 禁新增；②两条 /articles/ URL 自创建起从未进过 origin/main，线上一直 404，无已收录权重；③全仓 + 发布队列（含 _wechat_drafts/、multi-platform/）grep 未发现任何指向这两条 /articles/ URL 的内外链。如后续发现公众号「阅读原文」曾指向该路径，再按 batch2 套路补跳转页。",
    ],
    "verification": {
        "queue_empty": True,
        "git_fetch_synced": True,
        "og_image_curl": {"3943716": 200, "5669602": 200, "48148(旧默认,弃用)": 404},
        "md_artifacts_remaining": 0,
    },
})
json.dump(d, open(dl, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log.append("deploy-log.json: +1 条目")

print("\n".join(log))
print("DONE")
