import os, re, shutil, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
IMG = "https://najieip.com/img/"

pairs = {
    "20261120-mili-device-procurement-firmware-checklist": {
        "cover": os.path.join(ART, "cover-20261120-mili-device-procurement-firmware-checklist.png"),
        "title": "强制认证只管4类设备，你买的摄像头一台都不在内",
    },
    "20261120-mili-dongcheng-branch": {
        "cover": None,  # already in repo img/
        "title": "觅理在东城开了个分所，只管两件事",
    },
}

# 1) copy cover for procurement
slug1 = "20261120-mili-device-procurement-firmware-checklist"
dst = os.path.join(REPO, "img", slug1 + ".png")
if not os.path.exists(dst):
    shutil.copy2(pairs[slug1]["cover"], dst)
    print("copied cover ->", dst, os.path.getsize(dst))
else:
    print("cover exists", os.path.getsize(dst))

# 2) head surgery
for slug, meta in pairs.items():
    p = os.path.join(REPO, "mili/blog", slug + ".html")
    t = open(p, encoding="utf-8").read()
    img = IMG + slug + ".png"
    add = []
    if 'property="og:image"' not in t:
        add.append(f'<meta property="og:image" content="{img}">')
    if 'name="twitter:image"' not in t:
        add.append(f'<meta name="twitter:image" content="{img}">')
    # twitter:card upgrade / add
    if 'name="twitter:card"' in t:
        t2 = re.sub(r'<meta name="twitter:card" content="summary">', '<meta name="twitter:card" content="summary_large_image">', t)
        if t2 != t:
            t = t2
            print(slug, ": twitter:card upgraded")
    else:
        add.append('<meta name="twitter:card" content="summary_large_image">')
    if 'name="twitter:title"' not in t:
        add.append(f'<meta name="twitter:title" content="{meta["title"]}">')
    if 'name="twitter:description"' not in t:
        d = re.search(r'<meta property="og:description" content="([^"]*)"', t)
        if d:
            add.append(f'<meta name="twitter:description" content="{d.group(1)}">')
    if add:
        assert t.count("</head>") == 1
        t = t.replace("</head>", "\n".join(add) + "\n</head>")
        print(slug, ": inserted", len(add), "tags")
    open(p, "w", encoding="utf-8").write(t)
    # verify
    v = open(p, encoding="utf-8").read()
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', v, re.S)
    for b in lds:
        json.loads(b)
    print(f"  verify {slug}: og:image={'property=\"og:image\"' in v} twitter:image={'twitter:image' in v} twcard={'summary_large_image' in v} ld={len(lds)} h1={len(re.findall(r'<h1', v))} size={os.path.getsize(p)}")

# 3) fix dongcheng brand card date 11-19 -> 11-20
bp = os.path.join(REPO, "mili/blog/index.html")
b = open(bp, encoding="utf-8").read()
i = b.find('20261120-mili-dongcheng-branch')
seg_end = b.find("</div>", i)
seg = b[i:seg_end]
old = '2026-11-19 · 觅理律师事务所'
if old in seg:
    b = b.replace(seg, seg.replace(old, '2026-11-20 · 觅理律师事务所'), 1)
    open(bp, "w", encoding="utf-8").write(b)
    print("brand card date fixed 11-19 -> 11-20")
else:
    print("brand card date: no change needed / pattern not found:", seg[:200])

# 4) main index card for dongcheng
mp = os.path.join(REPO, "blog/index.html")
m = open(mp, encoding="utf-8").read()
slug = "20261120-mili-dongcheng-branch"
cards_before = len(re.findall(r'<div class="article-card">', m))
dups = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), m))
assert dups == 0, f"main index already has {dups} cards"
desc = re.search(r'<meta property="og:description" content="([^"]*)"', open(os.path.join(REPO,"mili/blog",slug+".html"),encoding="utf-8").read()).group(1)
card = (
    '<div class="article-card">\n'
    '    <h2><a href="/mili/blog/' + slug + '.html">觅理在东城开了个分所，只管两件事</a></h2>\n'
    '    <div class="meta"><span class="tag">觅理</span> 2026-11-20 · 北京觅理律师事务所</div>\n'
    '    <p>' + desc + '</p>\n'
    '  </div>'
)
first = m.find('<div class="article-card">')
assert first > 0
m2 = m[:first] + card + "\n  " + m[first:]
# assertions
assert len(re.findall(r'<div class="article-card">', m2)) == cards_before + 1
assert m2.replace(card + "\n  ", "", 1) == m, "block-external modification detected"
o1, c1 = m.count("<div"), m.count("</div>")
o2, c2 = m2.count("<div"), m2.count("</div>")
assert (o2 - o1) == (c2 - c1) >= 1, f"div delta asymmetric {o2-o1}/{c2-c1}"
body = m2[m2.find("<body"):]
depth = 0; malformed = 0; first_card = None
for mm in re.finditer(r"<(/?)div\b[^>]*>", body):
    if mm.group(1): depth -= 1
    else:
        if depth == 0 and first_card is None and 'class="article-card"' in mm.group(0):
            first_card = mm.start()
        depth += 1
assert depth == 0, f"div depth not zero: {depth}"
assert first_card is not None and first_card < body.find("<h2>"), "new card not first"
open(mp, "w", encoding="utf-8").write(m2)
print(f"main index: cards {cards_before} -> {cards_before+1}, div delta {(o2-o1)}/{(c2-c1)}, depth=0")
