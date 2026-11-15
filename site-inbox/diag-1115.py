#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 每日巡检 2026-11-15：页面六项 + 正文包含 + 双索引卡 + articles.json top6"""
import os, re, json, glob, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"

def txt(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

def norm(s):
    s = s.replace("“","").replace("”","").replace('"',"").replace("'","").replace("’","")
    s = s.replace("「","").replace("」","").replace("『","").replace("』","").replace("【","").replace("】","")
    s = s.replace("|","").replace(":","").replace("-","")
    return re.sub(r"\s+", "", s)

def strip_labels(s):
    s = re.sub(r"<h1>.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2>.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return s

def page_check(path, slug):
    t = txt(path)
    body = t[t.find("<body"):] if "<body" in t else t
    h1 = len(re.findall(r"<h1[ >]", body))
    ld = len(re.findall(r'application/ld\+json', t))
    types = re.findall(r'"@type":\s*"([^"]+)"', t)
    ogimg = re.findall(r'property="og:image"\s+content="([^"]+)"', t)
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    h1txt = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    h1s = re.sub(r"<[^>]+>", "", h1txt.group(1)).strip() if h1txt else ""
    star = len(re.findall(r"[0-9*]\*{2}", body))
    baretable = len(re.findall(r"<p>\s*\|", body))
    ctx = t.count("https://schema.org")
    return dict(h1=h1, ld=ld, types=types, ogimg=ogimg, desc=desc, h1s=h1s,
                star=star, baretable=baretable, ctx=ctx, size=len(t.encode()))

def md_contained(slug_md, path):
    if not os.path.exists(slug_md):
        return None
    md = txt(slug_md)
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    lines = []
    for ln in md.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if re.match(r"^#{1,6}\s", s):
            continue
        if re.match(r"^\*\*[^*\n]{1,30}\*\*$", s) and not re.search(r"[。！？]$", s):
            continue
        if re.match(r"^[一二三四五六七八九十]、", s) and len(s) <= 30:
            continue
        if s.startswith("<!--") or "带货" in s:
            continue
        s = re.sub(r"^\d+\.\s*", "", s)
        s = s.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "")
        lines.append(s)
    mdn = norm("".join(lines))
    t = txt(path)
    art = t[t.find("<article"):t.find("</article>")] if "<article" in t else t[t.find("<body"):]
    pg = strip_labels(art).replace("北京纳杰知识产权代理有限公司 何自刚", "")
    pgn = norm(pg)
    return dict(contained=mdn in pgn, md_len=len(mdn), pg_len=len(pgn),
                diff_at=(next((i for i in range(min(len(mdn), len(pgn))) if mdn[i] != pgn[i]), -1)))

def cards(index_path, slug):
    t = txt(index_path)
    return len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug) + r'[^"]*"', t))

out = {}
# 1) 今日 + 近日文章
targets = [
    ("mili", "20261115-mili-payment-60days-b2b", "20261115-mili-payment-60days-b2b.md"),
    ("mili", "20261114-mili-face-recognition-compliance", "20261114-mili-face-recognition-compliance.md"),
    ("mili", "20261114-mili-copyright-financing-16-cases", "20261114-mili-copyright-financing-16-cases.md"),
    ("najie", "20261114-najie-design-view-projection-rejection", "20261114-najie-design-view-projection-rejection.md"),
]
for brand, slug, mdfile in targets:
    p = os.path.join(REPO, brand, "blog", slug + ".html")
    if not os.path.exists(p):
        out[slug] = dict(EXISTS=False)
        continue
    r = page_check(p, slug)
    r["EXISTS"] = True
    r["md"] = md_contained(os.path.join(ART, mdfile), p)
    r["card_brand"] = cards(os.path.join(REPO, brand, "blog", "index.html"), slug)
    r["card_main"] = cards(os.path.join(REPO, "blog", "index.html"), slug)
    r["sitemap"] = slug in txt(os.path.join(REPO, "sitemap.xml"))
    out[slug] = r

# 2) articles.json top6 页面存在性
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
items = aj if isinstance(aj, list) else aj.get("articles", [])
top6 = items[:6]
out["_articles_json"] = dict(total=len(items), top6=[(it.get("url"),
    os.path.exists(os.path.join(REPO, it.get("url", "").lstrip("/")))) for it in top6])

# 3) .published.json 近 3 天 vs 落地页
pub = {}
pp = os.path.join(ART, ".published.json")
if os.path.exists(pp):
    pj = json.load(open(pp, encoding="utf-8"))
    entries = pj if isinstance(pj, list) else list(pj.values())
    flat = []
    for e in entries:
        if isinstance(e, dict):
            flat.append(e)
    recent = []
    for e in flat:
        pa = str(e.get("published_at", ""))[:10]
        if pa >= "2026-11-13":
            recent.append((e.get("slug") or e.get("stem") or e.get("id"), pa))
    out["_published_recent_raw"] = recent[:12]
    out["_published_keys"] = list(flat[0].keys()) if flat else []

print(json.dumps(out, ensure_ascii=False, indent=1))
