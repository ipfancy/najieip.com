import re, json, os, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261121-mili-divorce-game-account-88w"
path = os.path.join(REPO, "mili/blog", SLUG + ".html")
t = open(path, encoding="utf-8").read()

# 1) 封面入库
src = os.path.expanduser("~/wiki/digital-employees/articles/cover-%s.png" % SLUG)
dst = os.path.join(REPO, "img", SLUG + ".png")
if os.path.exists(src):
    shutil.copyfile(src, dst)
    print("COVER copied ->", dst, os.path.getsize(dst), "B")
else:
    print("COVER MISSING", src)

DESC = ("离婚前一个月，他把88万的游戏账号卖给朋友，钱一分没花，法院仍把卖号款纳入共同财产分割："
        "女方三分之一、男方三分之二。为什么不是转移财产？看三个时间差——什么时候卖、卖了多少钱、钱进谁的账。")
DESC = DESC.replace('"', '“')

head_end = t.find("</head>") + 7
head, rest = t[:head_end], t[head_end:]

# 2) 补 og/twitter/description
head = re.sub(r'<meta name="description" content="[^"]*"', '<meta name="description" content="%s"' % DESC, head, count=1)
head = re.sub(r'<meta property="og:description" content="[^"]*"', '<meta property="og:description" content="%s"' % DESC, head, count=1)
if 'og:image' not in head:
    img = "https://najieip.com/img/%s.png" % SLUG
    add = ('\n<meta property="og:site_name" content="纳杰觅理">'
           '\n<meta property="og:image" content="%s">'
           '\n<meta property="og:image:width" content="1200">'
           '\n<meta property="og:image:height" content="630">'
           '\n<meta name="twitter:card" content="summary_large_image">'
           '\n<meta name="twitter:title" content="离婚前把游戏账号88万卖朋友，这钱分得走吗">'
           '\n<meta name="twitter:description" content="%s">'
           '\n<meta name="twitter:image" content="%s">') % (img, DESC, img)
    head = head.replace("</head>", add + "\n</head>")

# 3) Article JSON-LD 补 image + description
def fix_ld(m):
    o = json.loads(m.group(1))
    if o.get("@type") == "Article":
        o["image"] = "https://najieip.com/img/%s.png" % SLUG
        o["description"] = DESC
        return '<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=2) + "\n</script>"
    return m.group(0)

head = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, head, flags=re.S)

new = head + rest
open(path, "w", encoding="utf-8").write(new)

# 自检
t2 = open(path, encoding="utf-8").read()
print("SIZE", os.path.getsize(path), "h1", len(re.findall(r"<h1", t2)), "ld", len(re.findall(r"application/ld\+json", t2)))
print("ogimg", "og:image" in t2, "desc_len", len(re.search(r'<meta name="description" content="([^"]*)"', t2).group(1)))
ok = True
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    try:
        json.loads(b)
    except Exception as e:
        ok = False
        print("LD FAIL", e)
print("LD json.loads all ok:", ok)
print("NO https://*** :", "https://***" not in t2, "| schema.org count", t2.count("https://schema.org"))
print("body unchanged:", t[t.find("</head>") + 7:] == t2[t2.find("</head>") + 7:])

# 4) 索引卡模板 + 日期方向
def card_blocks(txt):
    out = []
    for m in re.finditer(r'<div class="article-card">', txt):
        i = m.start(); d = 0; j = i
        while j < len(txt):
            nxt = re.search(r'<div\b|</div>', txt[j:])
            if not nxt:
                break
            tok = nxt.group(0)
            j += nxt.start()
            d += 1 if tok == "<div" else -1
            j += len(tok)
            if d == 0:
                out.append((i, j))
                break
    return out

for name, p in (("main", "blog/index.html"), ("mili", "mili/blog/index.html"), ("najie", "najie/blog/index.html")):
    txt = open(os.path.join(REPO, p), encoding="utf-8").read()
    bl = card_blocks(txt)
    print("\n=====", name, "cards", len(bl))
    if bl:
        s, e = bl[0]
        print("FIRST CARD:\n" + txt[s:e][:760])
        dates = [re.search(r'(\d{4}-\d{2}-\d{2})', txt[a:b]).group(1) for a, b in bl if re.search(r'(\d{4}-\d{2}-\d{2})', txt[a:b])]
        print("dates head", dates[:3], "tail", dates[-2:])
