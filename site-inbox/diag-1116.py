#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 1116 夜检：页面六项 + 正文包含 + articles.json 守卫"""
import os, re, json, sys, sqlite3

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"

PAGES = [
    ("mili", "20261116-mili-protection-order-72hours"),
    ("mili", "20261115-mili-payment-60days-b2b"),
    ("mili", "20261114-mili-face-recognition-compliance"),
    ("najie", "20261116-najie-ai-image-copyright-three-layers"),
]

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def quality(brand, slug):
    p = os.path.join(REPO, brand, "blog", slug + ".html")
    if not os.path.exists(p):
        return {"slug": slug, "exists": False}
    t = read(p)
    ld = t.count('application/ld+json')
    types = re.findall(r'"@type"\s*:\s*"([^"]+)"', t)
    h1 = len(re.findall(r'<h1[\s>]', t))
    ogimg = 'og:image' in t
    # description 复读标题
    m = re.search(r'<meta name="description" content="([^"]*)"', t, re.S)
    desc = m.group(1) if m else ""
    m2 = re.search(r'<title>(.*?)</title>', t, re.S)
    title = m2.group(1) if m2 else ""
    tcore = re.sub(r'\s*[—\-|]\s*纳杰觅理.*$', '', title).strip()
    desc_disp = desc.strip()
    repeat = bool(desc_disp) and (desc_disp == tcore or tcore.startswith(desc_disp) or desc_disp.startswith(tcore[:20]))
    # ** 泄漏（排除专利号掩码）
    body_probe = re.sub(r'[0-9]\*{2,}[0-9.]*', '', t)
    stars = body_probe.count('**')
    # 裸 markdown 表
    rawtbl = len(re.findall(r'<p>\s*\|', t))
    # 正文包含
    md_path = os.path.join(ART, slug + ".md")
    contained = None
    mdlen = 0
    if os.path.exists(md_path):
        md = read(md_path)
        md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
        md = re.sub(r'<!--.*?-->', ' ', md, flags=re.S)
        BYLINE_MD = "何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰"
        md = md.replace(BYLINE_MD, "")
        mdlines = []
        for ln in md.split("\n"):
            s = ln.strip()
            if not s:
                continue
            if s.startswith("#"):
                continue
            if re.match(r'^\*\*([^*\n]{1,30})\*\*$', s):
                continue
            if re.match(r'^[一二三四五六七八九十]、', s):
                continue
            if re.match(r'^\|?[\s:|-]+\|?$', s):
                continue
            mdlines.append(s)
        mdt = " ".join(mdlines)
        seg = re.search(r'<article[^>]*>(.*?)</article>', t, re.S)
        b = seg.group(1) if seg else t[t.find("<body"):]
        b = re.sub(r'<script.*?</script>', ' ', b, flags=re.S)
        b = re.sub(r'<style.*?</style>', ' ', b, flags=re.S)
        b = re.sub(r'<h1>.*?</h1>', ' ', b, flags=re.S)
        b = re.sub(r'<h2>.*?</h2>', ' ', b, flags=re.S)
        b = re.sub(r'<h3>.*?</h3>', ' ', b, flags=re.S)
        btxt = re.sub(r'<[^>]+>', ' ', b)
        def norm(s):
            s = s.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "")
            s = s.replace("北京纳杰知识产权代理有限公司 何自刚", "")
            s = re.sub(r'[“”"\'’「」『』【】]', '', s)
            s = re.sub(r'[*>`|:\-\s]', '', s)
            return s
        mn, bn = norm(mdt), norm(btxt)
        contained = mn in bn
        mdlen = len(mn)
    return {"slug": slug, "exists": True, "size": len(t.encode()), "ld": ld,
            "ld_types": types, "h1": h1, "ogimg": ogimg, "desc_len": len(desc_disp),
            "desc_repeat": repeat, "stars": stars, "rawtbl": rawtbl,
            "md_contained": contained, "mdlen": mdlen,
            "is_index": False}

def main():
    print("=== 页面六项 ===")
    for brand, slug in PAGES:
        r = quality(brand, slug)
        print(json.dumps(r, ensure_ascii=False))

    print("\n=== articles.json 守卫 ===")
    aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
    print("total:", len(aj))
    bad = []
    for it in aj:
        u = it.get("url", "")
        fp = os.path.join(REPO, u.lstrip("/")) if u else None
        if not fp or not os.path.exists(fp):
            bad.append(u)
            continue
        txt = read(fp)
        if 'http-equiv="refresh"' in txt or len(txt) < 1500:
            bad.append(u + " [stub]")
    print("violations:", len(bad))
    for b in bad[:12]:
        print("  ", b)
    print("\n=== 首页 top6 曝光断言 ===")
    for i, it in enumerate(aj[:6], 1):
        u = it.get("url", "")
        fp = os.path.join(REPO, u.lstrip("/"))
        print(f"  {i}. {'OK ' if os.path.exists(fp) else 'MISS'} {u}")

if __name__ == "__main__":
    main()
