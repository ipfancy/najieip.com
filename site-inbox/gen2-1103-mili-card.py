import re, os, json, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")
IDX = os.path.join(REPO, "mili/blog/index.html")
SLUG = "20261103-mili-unfair-competition-data-scraping"
PAGE = os.path.join(REPO, "mili/blog", SLUG + ".html")
t = open(IDX, encoding="utf-8").read()
if re.search(r'<h[23][^>]*><a href="[^"]*' + SLUG, t):
    print("SKIP: card exists"); sys.exit(0)
pg = open(PAGE, encoding="utf-8").read()
title = re.search(r"<h1[^>]*>(.*?)</h1>", pg, re.S).group(1).strip()
desc = re.search(r'<meta name="description" content="(.*?)">', pg, re.S).group(1).strip()
card = ('<div class="article-card">\n'
        f'    <h2><a href="./{SLUG}.html">{title}</a></h2>\n'
        '    <div class="meta"><span class="tag">数据抓取</span><span class="tag">反不正当竞争</span>'
        '<span class="tag">数据权益</span> 2026-11-03 · 北京觅理律师事务所</div>\n'
        f'    <p>{desc}</p>\n'
        '  </div>')

# locate patrol card block end (div depth pairing)
m = re.search(r'<div class="article-card">\s*<h2><a href="\./20261103-mili-patrol-robot-four-questions', t)
start = m.start()
depth, end = 0, None
for mm in re.finditer(r"<(/?)div\b", t[start:]):
    depth += -1 if mm.group(1) else 1
    if depth == 0:
        end = start + mm.end()
        # consume trailing </div>? no: depth 0 after closing outer div
        break
assert end, "card end not found"
# t[start:end] should end with the outer </div>
before = t
t2 = t[:end] + "\n  " + card + t[end:]
assert t2.replace("\n  " + card, "", 1) == before, "outside change"
n0, n1 = before.count('<div class="article-card">'), t2.count('<div class="article-card">')
def hist(s):
    h, d = {}, 0
    for mm in re.finditer(r"<(/?)div\b", s[s.find("<body"):]):
        if mm.group(1):
            d -= 1; assert d >= 0
        else:
            h[d] = h.get(d, 0) + 1; d += 1
    assert d == 0, f"unbalanced {d}"
    return h
h0, h1 = hist(before), hist(t2)
print("cards", n0, "->", n1, "| delta", {k: h1.get(k, 0) - h0.get(k, 0) for k in set(h0) | set(h1) if h1.get(k, 0) - h0.get(k, 0)})
assert n1 == n0 + 1
open(IDX, "w", encoding="utf-8").write(t2)
print("APPLIED; stars", t2.count("**"))
print("cards now:", len(re.findall(r'<h[23][^>]*><a href="[^"]*' + SLUG, t2)))
