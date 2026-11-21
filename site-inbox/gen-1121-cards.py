import re, os
from html import escape

REPO = os.path.expanduser("~/wiki/najieip-verify")
NEW = [
    dict(slug="20261121-mili-patent-agency-revoked-34", brand="mili", tag="觅理", org="北京觅理律师事务所",
         file="mili/blog/20261121-mili-patent-agency-revoked-34.html"),
    dict(slug="20261121-najie-sep-administrative-ruling-37-articles", brand="najie", tag="纳杰",
         org="北京纳杰知识产权代理有限公司", file="najie/blog/20261121-najie-sep-administrative-ruling-37-articles.html"),
]

def zh(s):
    return s.replace('"', "“")

# 取标题与摘要
for a in NEW:
    t = open(os.path.join(REPO, a["file"]), encoding="utf-8").read()
    a["title"] = re.search(r"<title>(.*?)\s*—", t, re.S).group(1).strip()
    a["desc"] = zh(re.search(r'<meta name="description" content="([^"]*)"', t).group(1).strip())
    print(a["slug"], "|", a["title"], "|", len(a["desc"]))

def card_blocks(txt):
    out = []
    for m in re.finditer(r'<div class="article-card">', txt):
        i = m.start(); d = 0; j = i
        while j < len(txt):
            nxt = re.search(r"<div\b|</div>", txt[j:])
            if not nxt:
                break
            tok = nxt.group(0); j += nxt.start()
            d += 1 if tok == "<div" else -1
            j += len(tok)
            if d == 0:
                out.append((i, j)); break
    return out

def build(a, is_main):
    href = ("/%s/blog/%s.html" % (a["brand"], a["slug"])) if is_main else ("./%s.html" % a["slug"])
    return ('<div class="article-card">\n'
            '    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta"><span class="tag">%s</span> 2026-11-21 · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>') % (href, escape(a["title"]), a["tag"], a["org"], escape(a["desc"]))

def insert(path, is_main, rel_brand):
    full = os.path.join(REPO, path)
    t = open(full, encoding="utf-8").read()
    bl = card_blocks(t)
    todays = [a for a in NEW if a["brand"] == rel_brand]
    added = 0
    for a in todays:
        bl = card_blocks(t)  # 每轮重扫
        # 找最大日期卡的位置，插在其前
        best = None
        for s, e in bl:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", t[s:e])
            if not m:
                continue
            d = m.group(1)
            if best is None or d > best[0]:
                best = (d, s)
        pos = best[1] if best else t.rfind("</div>")
        card = build(a, is_main)
        t2 = t[:pos] + card + "\n  " + t[pos:]
        # 断言
        assert t2.replace(card + "\n  ", "", 1) == t, "块外被改动"
        assert re.search(r'<h[23][^>]*><a href="[^"]*' + a["slug"] + r'[^"]*"', t2), "新卡定位失败"
        assert len(card_blocks(t2)) == len(bl) + 1, "卡数未 +1"
        assert t2.count("<div") - t.count("<div") == t2.count("</div>") - t.count("</div>") == 2, "div delta 应为 +2/+2"
        t = t2; added += 1
        print("  inserted", a["slug"][:44], "->", path, "pos", pos, "maxdate", best[0] if best else None)
    open(full, "w", encoding="utf-8").write(t)
    return added, len(card_blocks(t))

for path, is_main, brand in (("blog/index.html", True, None),
                             ("mili/blog/index.html", False, "mili"),
                             ("najie/blog/index.html", False, "najie")):
    n, total = insert(path, is_main, brand)
    print("==", path, "added", n, "total cards", total)

# 交叉污染检查
mili = open(os.path.join(REPO, "mili/blog/index.html"), encoding="utf-8").read()
najie = open(os.path.join(REPO, "najie/blog/index.html"), encoding="utf-8").read()
print("cross mili<-najie slug:", "sep-administrative-ruling" in mili)
print("cross najie<-mili slug:", "patent-agency-revoked" in najie)
