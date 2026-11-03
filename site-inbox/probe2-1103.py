import re, os, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")
IDX = os.path.join(REPO, "mili/blog/index.html")
SLUG = "20261103-mili-unfair-competition-data-scraping"
t = open(IDX, encoding="utf-8").read()
m = re.search(r'<h2><a href="[^"]*20261103-mili-patrol-robot-four-questions', t)
i = t.rfind('<div class="article-card">', 0, m.start())
print("SAMPLE:", repr(t[i:i+520]))
print("cards:", t.count('<div class="article-card">'))
print("scraping cards:", len(re.findall(r'<h[23][^>]*><a href="[^"]*' + SLUG, t)))
