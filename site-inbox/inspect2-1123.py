#!/usr/bin/env python3
import re, os, glob
REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
p = "site-inbox/20261123-mili-gaoqi-2026-no-new-standard.html"
t = open(p, encoding="utf-8").read()
slug = "20261123-mili-gaoqi-2026-no-new-standard"
print("size", os.path.getsize(p), "h1", len(re.findall(r"<h1[\s>]", t)), "h2", len(re.findall(r"<h2[\s>]", t)),
      "ld", t.count("application/ld+json"), "ogimg", "og:image" in t,
      "style", ("<style>" in t or "/style.css" in t), "star", t.count("**"), "rawtbl", len(re.findall(r"<p>\s*\|", t)))
m = re.search(r'<meta name="description" content="([^"]*)"', t)
print("desc_len", len(m.group(1)) if m else 0)
print("title", re.search(r"<title>(.*?)</title>", t).group(1))
nidx = open("najie/blog/index.html", encoding="utf-8").read()
midx = open("mili/blog/index.html", encoding="utf-8").read()
bidx = open("blog/index.html", encoding="utf-8").read()
print("cards mili", len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), midx)),
      "najie", len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), nidx)),
      "main", len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), bidx)))
print("page exists:", [b for b in ("mili", "najie", "aipunajie") if os.path.exists(f"{b}/blog/{slug}.html")])
print("covers:", [os.path.basename(x) for x in glob.glob(os.path.expanduser("~/wiki/digital-employees/articles/*gaoqi*2026*"))][:5])
print("h2 list:", re.findall(r"<h2[^>]*>(.*?)</h2>", t, re.S)[:8])
print("canonical:", re.search(r'<link rel="canonical" href="([^"]*)"', t).group(1) if 'rel="canonical"' in t else "NONE")
