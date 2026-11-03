import re, os, json, subprocess, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")
IDX = os.path.join(REPO, "blog/index.html")
APPLY = "--apply" in sys.argv
CARDS = [
    dict(slug="20261103-mili-patrol-robot-four-questions", brand="mili", date="2026-11-03",
         title="巡逻机器人上岗前，物业要先答的四个问题",
         tags=["个人信息保护法", "人脸识别", "物业"],
         desc=None),
    dict(slug="20261103-mili-unfair-competition-data-scraping", brand="mili", date="2026-11-03",
         title="抓一次数据：罚53万，再赔500万",
         tags=["数据抓取", "反不正当竞争", "数据权益"],
         desc=None),
]
for c in CARDS:
    p = os.path.join(REPO, c["brand"], "blog", c["slug"] + ".html")
    t = open(p, encoding="utf-8").read()
    c["desc"] = re.search(r'<meta name="description" content="(.*?)">', t, re.S).group(1).strip()
    if not c["title"]:
        c["title"] = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S).group(1).strip()
BRANDNAME = {"mili": "北京觅理律师事务所", "najie": "北京纳杰知识产权代理有限公司"}

def mkcard(c):
    tags = "".join(f'<span class="tag">{x}</span> ' for x in c["tags"])
    return ('<div class="article-card">\n'
            f'    <h2><a href="/{c["brand"]}/blog/{c["slug"]}.html">{c["title"]}</a></h2>\n'
            f'    <div class="meta">{tags}  {c["date"]} · {BRANDNAME[c["brand"]]}</div>\n'
            f'    <p>{c["desc"]}</p>\n'
            '  </div>')

def depth_hist(s):
    hist, depth = {}, 0
    for m in re.finditer(r"<(/?)div\b", s[s.find("<body"):]):
        if m.group(1):
            depth -= 1
            assert depth >= 0, "stack underflow"
        else:
            hist[depth] = hist.get(depth, 0) + 1
            depth += 1
    assert depth == 0, f"unbalanced div depth={depth}"
    return hist

base = subprocess.run(["git", "show", "HEAD:blog/index.html"], cwd=REPO,
                      capture_output=True, text=True).stdout
hist0 = depth_hist(base)
print("BASE cards", base.count('<div class="article-card">'), "hist", hist0, "bytes", len(base.encode()))

t = open(IDX, encoding="utf-8").read()
added = 0
for c in CARDS:
    if re.search(r'<h[23][^>]*><a href="[^"]*' + c["slug"], t):
        print("SKIP (already has card):", c["slug"]); continue
    card = mkcard(c)
    # re-scan insertion point each round: first card whose date < new date
    pos = None
    for m in re.finditer(r'<div class="article-card">', t):
        seg = t[m.start():m.start() + 2000]
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", seg)
        if dm and dm.group(1) < c["date"]:
            pos = m.start(); break
    if pos is None:
        pos = t.find('<div class="article-card">')
    before = t
    t = t[:pos] + card + "\n  " + t[pos:]
    assert t.replace(card + "\n  ", "", 1) == before, f"outside-block change for {c['slug']}"
    added += 1
    print("INSERT", c["slug"], "at", pos)

# structure checks
n_cards = t.count('<div class="article-card">')
hist1 = depth_hist(t)
delta = {k: hist1.get(k, 0) - hist0.get(k, 0) for k in set(hist0) | set(hist1)}
print("NEW cards", n_cards, "delta", {k: v for k, v in delta.items() if v}, "bytes", len(t.encode()))
assert n_cards == base.count('<div class="article-card">') + added
# depth_hist counts ALL divs: each new card adds 1 div at its depth (0) + 1 meta div at depth+1
assert delta.get(0, 0) == added and delta.get(1, 0) == added and all(v >= 0 for v in delta.values()), delta
body = t[t.find("<body"):]
mal = sum(1 for m in re.finditer(r'<div class="article-card">', body)
          if not re.match(r'<div class="article-card">\s*<h2><a href=', body[m.start():m.start() + 200]))
print("malformed", mal, "| stars", t.count("**"))
assert mal == 0 and t.count("**") == 0
# insertion-point date ordering: cards above inserted ones must be >= date
if APPLY:
    open(IDX, "w", encoding="utf-8").write(t)
    print("APPLIED")
else:
    print("DRY-RUN (use --apply)")
