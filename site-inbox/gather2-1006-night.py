#!/usr/bin/env python3
import re, os, glob
ROOT = "/Users/ziganghe/wiki/najieip-verify"
tpl = os.path.join(ROOT, "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html")
t = open(tpl, encoding="utf-8").read()
print("=== template social meta lines ===")
for line in t.splitlines():
    if re.search(r'(og:image|twitter:(title|description|image)|og:site_name|og:locale|keywords|author|rel="canonical")', line):
        print(line.strip())

print("\n=== nobel md source ===")
md = open("/Users/ziganghe/wiki/digital-employees/articles/20261006-nobel-icecube-patent-four-rules.md", encoding="utf-8").read()
print(md[:3600])

print("\n=== 工程结算 article html? ===")
for p in glob.glob(ROOT + "/**/20261006-*", recursive=True) + glob.glob("/Users/ziganghe/wiki/digital-employees/articles/20261006-工程*"):
    print(p, os.path.getsize(p))
print("\n=== mili index: first 2 cards raw ===")
mi = open(ROOT + "/mili/blog/index.html", encoding="utf-8").read()
i = mi.find('<div class="article-card">')
print(mi[i:i+900])
print("\n=== main index: first card raw ===")
bi = open(ROOT + "/blog/index.html", encoding="utf-8").read()
j = bi.find('<div class="article-card">')
print(bi[j:j+900])
