#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 · 主体归属纠偏
将 2026-09-12 误入无主体目录 blog/ 的两篇文章归位到主体目录：
  blog/dili-biaozhi-quyu-pinpai-2026.html  -> najie/blog/  (地理标志·证明商标 → 纳杰)
  blog/weifa-citui-2n-peichang-2026.html   -> mili/blog/    (劳动争议·仲裁 → 觅理)
同时修正 canonical / og:url / og:site_name / og:image / JSON-LD 主体、articles.json、sitemap、三个博客索引。
"""
import re, json, os, shutil, sys

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)

PEXELS_NAJIE = "https://images.pexels.com/photos/48148/documents-accent-tear-48148.jpeg?auto=compress&cs=tinysrgb&w=1200"
PEXELS_MILI  = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"

JOBS = [
    dict(src="blog/dili-biaozhi-quyu-pinpai-2026.html",
         dst="najie/blog/dili-biaozhi-quyu-pinpai-2026.html",
         old_url="https://najieip.com/blog/dili-biaozhi-quyu-pinpai-2026.html",
         new_url="https://najieip.com/najie/blog/dili-biaozhi-quyu-pinpai-2026.html",
         site_name="纳杰知识产权",
         publisher="北京纳杰知识产权代理有限公司",
         pexels=PEXELS_NAJIE,
         blog_index="https://najieip.com/najie/blog/"),
    dict(src="blog/weifa-citui-2n-peichang-2026.html",
         dst="mili/blog/weifa-citui-2n-peichang-2026.html",
         old_url="https://najieip.com/blog/weifa-citui-2n-peichang-2026.html",
         new_url="https://najieip.com/mili/blog/weifa-citui-2n-peichang-2026.html",
         site_name="觅理律师事务所",
         publisher="北京觅理律师事务所",
         pexels=PEXELS_MILI,
         blog_index="https://najieip.com/mili/blog/"),
]

OTHER = {
    "https://najieip.com/blog/dili-biaozhi-quyu-pinpai-2026.html":
        "https://najieip.com/najie/blog/dili-biaozhi-quyu-pinpai-2026.html",
    "https://najieip.com/blog/weifa-citui-2n-peichang-2026.html":
        "https://najieip.com/mili/blog/weifa-citui-2n-peichang-2026.html",
}

log = []

# ---------- 1. 移动文件 + 正文修正 ----------
for j in JOBS:
    s = open(j["src"], encoding="utf-8").read()
    orig = s
    # 自身旧 URL -> 新 URL（canonical / og:url / JSON-LD mainEntityOfPage / 内链）
    s = s.replace(j["old_url"], j["new_url"])
    # 同批另一篇的旧 URL 也一并纠正
    for o, n in OTHER.items():
        if o != j["old_url"]:
            s = s.replace(o, n)
    # 旧 og:image 路径（/images/ 目录不存在，实际 404）-> 本站统一图源
    s = re.sub(r'https://najieip\.com/images/[A-Za-z0-9\-_]+\.jpg', j["pexels"], s)
    # og:site_name 主体修正
    s = s.replace('<meta property="og:site_name" content="爱普纳杰专利所">',
                  '<meta property="og:site_name" content="%s">' % j["site_name"])
    s = s.replace('<meta property="og:site_name" content="纳杰知识产权">',
                  '<meta property="og:site_name" content="%s">' % j["site_name"])
    s = s.replace('<meta property="og:site_name" content="觅理律师事务所">',
                  '<meta property="og:site_name" content="%s">' % j["site_name"])
    # JSON-LD publisher 主体修正
    s = s.replace('"publisher":{"@type":"Organization","name":"北京纳杰知识产权代理有限公司"}',
                  '"publisher":{"@type":"Organization","name":"%s"}' % j["publisher"])
    s = s.replace('"publisher":{"@type":"Organization","name":"觅理律师事务所"}',
                  '"publisher":{"@type":"Organization","name":"%s"}' % j["publisher"])
    # 延伸阅读内链指向本主体博客索引
    s = s.replace('<a href="https://najieip.com/blog/">纳杰觅理法律观察</a>',
                  '<a href="%s">%s</a>' % (j["blog_index"],
                                           "纳杰知识产权 · 商标版权观察" if "najie" in j["dst"] else "觅理律师事务所 · 法律观察"))
    # 校验 JSON-LD 仍为合法 JSON
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(j["dst"], "w", encoding="utf-8").write(s)
    os.remove(j["src"])
    log.append("MOVED %s -> %s (%d->%d chars) ; 旧URL残留=%d" % (
        j["src"], j["dst"], len(orig), len(s), s.count("/blog/" + os.path.basename(j["src"]))))

# ---------- 2. 旧路径留跳转页 ----------
for j in JOBS:
    base = os.path.basename(j["src"])
    title = re.search(r'<title>(.*?)</title>', open(j["dst"], encoding="utf-8").read(), re.S).group(1)
    title = title.split("—")[0].strip()
    stub = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        '<meta http-equiv="refresh" content="0; url=/%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<title>%s</title>\n</head>\n<body>\n'
        '<p>文章已迁移：<a href="/%s">%s</a></p>\n</body>\n</html>\n'
    ) % (j["dst"], j["new_url"], title, j["dst"], title)
    open(os.path.join("blog", base), "w", encoding="utf-8").write(stub)
    log.append("STUB blog/%s -> /%s" % (base, j["dst"]))

# ---------- 3. articles.json ----------
ap = "articles.json"
s = open(ap, encoding="utf-8").read()
before = s
s = s.replace('"url": "/blog/dili-biaozhi-quyu-pinpai-2026.html"',
              '"url": "/najie/blog/dili-biaozhi-quyu-pinpai-2026.html"')
s = s.replace('"url": "/blog/weifa-citui-2n-peichang-2026.html"',
              '"url": "/mili/blog/weifa-citui-2n-peichang-2026.html"')
# 劳动争议 → 觅理（原误标 najie）：仅改该条目块
s = re.sub(r'(\{\s*"url": "/mili/blog/weifa-citui-2n-peichang-2026\.html",[\s\S]{0,200}?"site": )"najie"',
           r'\1"mili"', s)
json.loads(s)
open(ap, "w", encoding="utf-8").write(s)
log.append("articles.json: url 修正 %s ; mili 归属修正 %s" % (
    before != s, '"url": "/mili/blog/weifa-citui-2n-peichang-2026.html"' in s))

# ---------- 4. sitemap.xml ----------
sm = "sitemap.xml"
s = open(sm, encoding="utf-8").read()
for o, n in OTHER.items():
    s = s.replace("<loc>%s</loc>" % o, "<loc>%s</loc>" % n)
extra = ""
for j in JOBS:
    extra += ("  <url>\n    <loc>%s</loc>\n    <lastmod>2026-09-12</lastmod>\n"
              "    <changefreq>weekly</changefreq>\n    <priority>0.5</priority>\n  </url>\n"
              % j["old_url"])
s = s.replace("</urlset>", extra + "</urlset>")
open(sm, "w", encoding="utf-8").write(s)
log.append("sitemap.xml: 主体URL替换 + 旧路径跳转 %d 条" % len(JOBS))

# ---------- 5. blog/index.html（历史索引，卡片指向新主体路径） ----------
bi = "blog/index.html"
s = open(bi, encoding="utf-8").read()
s = s.replace('href="/blog/weifa-citui-2n-peichang-2026.html"', 'href="/mili/blog/weifa-citui-2n-peichang-2026.html"')
s = s.replace('href="/blog/dili-biaozhi-quyu-pinpai-2026.html"', 'href="/najie/blog/dili-biaozhi-quyu-pinpai-2026.html"')
s = s.replace('<span class="tag">劳动仲裁</span> 2026-09-12 · 纳杰知识产权',
              '<span class="tag">劳动仲裁</span> 2026-09-12 · 觅理律师事务所')
open(bi, "w", encoding="utf-8").write(s)
log.append("blog/index.html: 卡片指向主体路径")

# ---------- 6. 主体博客索引：顶部卡片 + JSON-LD BlogPosting ----------
CARDS = {
 "najie/blog/index.html": dict(
   href="./dili-biaozhi-quyu-pinpai-2026.html",
   title="地理标志公示期，产地企业用证明商标守住区域品牌",
   tags=["地理标志","证明商标","区域品牌"],
   brand="纳杰知识产权",
   desc="地理标志示范区名单公示期（9/1-9/30），产地企业用证明商标、集体商标加地理标志产品双轨保护，守住区域品牌、防地名被抢注和通用化。4步行动指南+三种商标对比表+6个高频问答。",
   url="https://najieip.com/najie/blog/dili-biaozhi-quyu-pinpai-2026.html"),
 "mili/blog/index.html": dict(
   href="./weifa-citui-2n-peichang-2026.html",
   title="被公司违法辞退，2N赔偿怎么拿？5个动作别做错",
   tags=["劳动争议","违法辞退","劳动仲裁"],
   brand="觅理律师事务所",
   desc="公司违法辞退能拿的不是N，是2N。N、N+1、2N差多少，2N赔偿怎么算、仲裁时效多久、要收集哪些证据——5个动作+一张对比表+取证清单，帮被辞退劳动者拿回该拿的2N赔偿。",
   url="https://najieip.com/mili/blog/weifa-citui-2n-peichang-2026.html"),
}

for path, c in CARDS.items():
    s = open(path, encoding="utf-8").read()
    card = ('  <div class="article-card">\n'
            '    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta">%s 2026-09-12 · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>\n' % (c["href"], c["title"],
                           "".join('<span class="tag">%s</span>' % t for t in c["tags"]),
                           c["brand"], c["desc"]))
    # 去重：若已存在则不重复插入
    if c["href"] in s:
        log.append("%s: 卡片已存在，跳过" % path)
    else:
        marker = '<div class="container">\n'
        idx = s.find(marker)
        assert idx > 0, path
        idx += len(marker)
        s = s[:idx] + card + s[idx:]
        log.append("%s: 顶部插入 article-card" % path)
    # JSON-LD BlogPosting 首位插入
    entry = ('{"@type": "BlogPosting", "headline": "%s", "url": "%s", "datePublished": "2026-09-12", '
             '"description": "%s"}' % (c["title"], c["url"], c["desc"]))
    key = '"blogPost": ['
    if c["url"] in s:
        log.append("%s: JSON-LD 已存在，跳过" % path)
    else:
        i = s.find(key)
        assert i > 0, path
        i += len(key)
        s = s[:i] + entry + ", " + s[i:]
        log.append("%s: JSON-LD BlogPosting 首位插入" % path)
    # JSON-LD 语法校验
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(blk)
    open(path, "w", encoding="utf-8").write(s)

print("\n".join(log))
print("DONE")
