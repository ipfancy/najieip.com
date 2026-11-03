import re, os, json, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")
IDX = os.path.join(REPO, "blog/index.html")
t = open(IDX, encoding="utf-8").read()
i = t.find('<div class="article-card">')
# first card sample
print(repr(t[i:i+900]))
print("--- card count:", t.count('<div class="article-card">'))
print("--- dates head:", re.findall(r'(\d{4}-\d{2}-\d{2})', t[t.find("<body"):])[:8])
