import re, os
from html import escape

REPO = os.path.expanduser("~/wiki/najieip-verify")
t = open(os.path.join(REPO, "mili/blog/index.html"), encoding="utf-8").read()
for m in re.finditer("sep-administrative-ruling", t):
    print("POS", m.start(), "CONTEXT:", t[max(0, m.start() - 90):m.start() + 60].replace("\n", "\\n"))

print("--- main insert ---")
main_path = os.path.join(REPO, "blog/index.html")
mt = open(main_path, encoding="utf-8").read()

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

NEW = [
    dict(slug="20261121-mili-patent-agency-revoked-34", brand="mili", tag="觅理", org="北京觅理律师事务所",
         title="34家专利代理机构被吊销：代理所还能提交吗",
         desc="国家知识产权局依法吊销34家专利代理机构执业许可证，委托方手头的在审案件怎么办？三步自查：换所衔接、官文送达地址变更、已缴官费与年费不断档。"),
    dict(slug="20261121-najie-sep-administrative-ruling-37-articles", brand="najie", tag="纳杰",
         org="北京纳杰知识产权代理有限公司",
         title="SEP纠纷多一条8个月通道：立案10日、审限8个月",
         desc="2026年标准必要专利行政裁决新规落地：37条程序清单、立案10日、审限8个月。SEP权利人被卡谈判时，行政裁决与法院诉讼怎么选、材料怎么备。"),
]

for a in NEW:
    bl = card_blocks(mt)
    best = None
    for s, e in bl:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", mt[s:e])
        if m and (best is None or m.group(1) > best[0]):
            best = (m.group(1), s)
    pos = best[1] if best else mt.rfind("</div>")
    card = ('<div class="article-card">\n'
            '    <h2><a href="/%s/blog/%s.html">%s</a></h2>\n'
            '    <div class="meta"><span class="tag">%s</span> 2026-11-21 · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>') % (a["brand"], a["slug"], escape(a["title"]), a["tag"], a["org"], escape(a["desc"]))
    t2 = mt[:pos] + card + "\n  " + mt[pos:]
    assert t2.replace(card + "\n  ", "", 1) == mt, "块外被改动"
    assert len(card_blocks(t2)) == len(bl) + 1
    assert t2.count("<div") - mt.count("<div") == t2.count("</div>") - mt.count("</div>") == 2
    mt = t2
    print("inserted", a["slug"][:44], "pos", pos, "maxdate", best[0])

open(main_path, "w", encoding="utf-8").write(mt)
print("main cards now", len(card_blocks(mt)), "size", os.path.getsize(main_path))

# 终验：三索引逐 slug 卡数
for name, p in (("main", "blog/index.html"), ("mili", "mili/blog/index.html"), ("najie", "najie/blog/index.html")):
    txt = open(os.path.join(REPO, p), encoding="utf-8").read()
    bl = card_blocks(txt)
    malformed = sum(1 for s, e in bl if not txt[s:e].lstrip().startswith('<div class="article-card">'))
    h2 = sum(1 for s, e in bl if "<h2><a href=" in txt[s:e])
    print(name, "cards", len(bl), "h2cards", h2, "malformed", malformed,
          "divopen", txt.count("<div"), "divclose", txt.count("</div>"),
          "stars", txt.count("**"))
    for s in ("20261121-mili-patent-agency-revoked-34", "20261121-najie-sep-administrative-ruling-37-articles"):
        print("   ", s[:42], len(re.findall(r'<h[23][^>]*><a href="[^"]*' + s, txt)))
