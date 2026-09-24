#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 近 2 日已发布文章 × 三索引/sitemap/线上 全链路缺口扫描（href 归一比对）"""
import os, re, sqlite3, subprocess, urllib.request, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
DB = os.path.expanduser("~/wiki/database/content.db")
BASE = "https://najieip.com"


def rd(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()


def hrefs(idx_path, base):
    """索引卡 href 归一为绝对路径"""
    t = rd(idx_path)
    out = []
    for h in re.findall(r'<h2><a href="([^"]+)"', t):
        if h.startswith("http"):
            out.append(re.sub(r"^https://najieip\.com", "", h))
        elif h.startswith("/"):
            out.append(h)
        else:
            out.append(base + "/" + h.lstrip("./"))
    return set(out)


IDX = {
    "blog": hrefs("blog/index.html", ""),
    "mili": hrefs("mili/blog/index.html", "/mili/blog"),
    "najie": hrefs("najie/blog/index.html", "/najie/blog"),
}
aj = json.load(open(os.path.join(REPO, "articles.json")))
aj_urls = {a.get("url") for a in (aj if isinstance(aj, list) else aj.get("articles", []))}
sm = rd("sitemap.xml")

con = sqlite3.connect(DB)
rows = con.execute("SELECT article_id, title, publish_date, source_file, tags FROM articles "
                   "WHERE status='published' AND publish_date >= date('now','-2 days') "
                   "ORDER BY publish_date DESC").fetchall()
print("近 2 日已发布 %d 篇\n" % len(rows))
for aid, title, day, url, tags in rows:
    print("=" * 12, aid, day, title[:38])
    # 找本地页面
    cands = []
    for brand in ["mili", "najie", "blog", "aipunajie"]:
        d = os.path.join(REPO, brand, "blog") if brand != "blog" else os.path.join(REPO, "blog")
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".html") and fn != "index.html":
                    p = "%s/blog/%s" % (brand, fn) if brand != "blog" else "blog/%s" % fn
                    t = rd(p)
                    if title[:14] in t or (url and os.path.basename(url) == fn):
                        cands.append(p)
    print("  本地页面:", cands or "未找到")
    for p in cands:
        t = rd(p)
        key = "/" + p
        owned_brand = p.split("/")[0]
        in_main = key in IDX["blog"]
        in_brand = key in IDX.get(owned_brand, set())
        in_aj = key in aj_urls
        in_sm = (BASE + key) in sm
        print("    %s" % p)
        print("      主索引=%s | 品牌索引(%s)=%s | articles.json=%s | sitemap=%s" % (
            in_main, owned_brand, in_brand, in_aj, in_sm))
        print("      四件: h1=%d h2=%d ld=%d og:image=%s style=%s size=%dB" % (
            t.count("<h1"), t.count("<h2"), t.count("application/ld+json"),
            "og:image" in t, ("style>" in t or "/style.css" in t), len(t.encode())))
        # 线上
        try:
            req = urllib.request.Request(BASE + key, headers={"User-Agent": "Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=30)
            body = r.read().decode("utf-8", "replace")
            print("      线上 %s | h1=%d h2=%d ld=%d" % (r.status, body.count("<h1"),
                                                        body.count("<h2"), body.count("application/ld+json")))
        except Exception as e:
            print("      线上 ERR", e)
print("\n三索引卡数: 主=%d 觅理=%d 纳杰=%d" % (len(IDX["blog"]), len(IDX["mili"]), len(IDX["najie"])))
