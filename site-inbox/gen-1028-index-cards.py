#!/usr/bin/env python3
"""SiteOps 1028 补卡：主索引 4 张（mili×3 + najie×1）+ mili 索引 1 张（孕期辞退文）
用法: python3 gen-1028-index-cards.py [--apply]
规则（v3）：每轮重扫插入点；插串 = 卡块 + "\n  "；插前判 path 是否已存在；终验 div 配平。
"""
import re, os, sys, html, shutil

ROOT = "/Users/ziganghe/wiki/najieip-verify"
DATE = "2026-10-28"
APPLY = "--apply" in sys.argv

ENTITY = {"mili": "北京觅理律师事务所", "najie": "北京纳杰知识产权代理有限公司",
          "aipunajie": "北京爱普纳杰专利代理事务所"}

# 目标：主索引缺的 4 篇（顺序 = 期望的主索引顶部顺序，同日按发布先后倒序）
MAIN_NEW = [
    ("mili", "20261028-mili-entity-switch-repeat-infringement.html"),
    ("mili", "20261028-mili-pregnancy-disguised-dismissal-evidence.html"),
    ("mili", "20261028-mili-software-copyright-proof-chain.html"),
    ("najie", "20261028-najie-gi-zone-objection.html"),
]
MILI_NEW = [("mili", "20261028-mili-pregnancy-disguised-dismissal-evidence.html")]


def load(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def save(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)


def zh_quotes(s):
    return re.sub(r'"([^"]*)"', "\u201c\\1\u201d", s)


def esc_attr(s):
    return html.escape(s, quote=True)


def meta_of(brand, fn):
    t = load(os.path.join(ROOT, brand, "blog", fn))
    h2 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    title = re.sub(r'<[^>]+>', '', h2.group(1)).strip() if h2 else ""
    if not title:
        ti = re.search(r'<title>(.*?)</title>', t, re.S)
        title = re.sub(r'\s+—.*$', '', ti.group(1)).strip() if ti else ""
    kw = re.search(r'<meta name="keywords" content="([^"]*)"', t)
    tags = [x.strip() for x in kw.group(1).split(",") if x.strip()][:3] if kw else []
    de = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = de.group(1).strip() if de else ""
    return title, tags, desc


def main_card(brand, fn):
    title, tags, desc = meta_of(brand, fn)
    taghtml = "".join('<span class="tag">%s</span>' % esc_attr(t) for t in tags)
    return ('<div class="article-card">\n'
            '    <h2><a href="/%s/blog/%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>') % (brand, fn, esc_attr(title), taghtml, DATE, ENTITY[brand], esc_attr(desc))


def brand_card(brand, fn):
    title, tags, desc = meta_of(brand, fn)
    taghtml = "".join('<span class="tag">%s</span>' % esc_attr(t) for t in tags)
    return ('<div class="article-card">\n'
            '    <h2><a href="./%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>') % (fn, esc_attr(title), taghtml, DATE, ENTITY[brand], esc_attr(desc))


def cards_with_date(t):
    """返回 [(start, date)] — 用 div 深度配对定位每张卡并取其 meta 日期"""
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        s = m.start()
        k = s
        depth = 0
        end = None
        while True:
            nd = t.find("<div", k)
            nc = t.find("</div>", k)
            if nc == -1:
                break
            if nd != -1 and nd < nc:
                depth += 1
                k = nd + 4
            else:
                depth -= 1
                k = nc + 6
                if depth == 0:
                    end = k
                    break
        blk = t[s:end] if end else t[s:s + 2000]
        d = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
        out.append((s, d.group(1) if d else "0000-00-00"))
    return out


def insert_cards(t, cards):
    """插入一组卡，保持日期降序（每轮重扫）"""
    for card, path in cards:
        if path in t:
            print("  skip (already present):", path)
            continue
        pts = cards_with_date(t)
        pos = None
        for st, d in pts:
            if d < DATE:
                pos = st
                break
        if pos is None:
            print("  !! no insertion point for", path)
            return t
        t = t[:pos] + card + "\n  " + t[pos:]
        print("  inserted at", pos, ":", path)
    return t


def check_div(t, tag="div"):
    depth = 0
    bad = 0
    for m in re.finditer(r'</?div\b[^>]*>', t):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth < 0:
                bad += 1
        else:
            depth += 1
    return depth, bad


# ---------- 主索引 ----------
mp = os.path.join(ROOT, "blog/index.html")
mt = load(mp)
before_cards = len(re.findall(r'<div class="article-card">', mt))
before_depth = check_div(mt)
print("MAIN before: cards=%d divdepth=%s stars=%d" % (before_cards, before_depth, mt.count("**")))
new_cards = [(main_card(b, f), "/%s/blog/%s" % (b, f)) for b, f in MAIN_NEW]
mt2 = insert_cards(mt, new_cards)
after_cards = len(re.findall(r'<div class="article-card">', mt2))
after_depth = check_div(mt2)
print("MAIN after : cards=%d divdepth=%s stars=%d" % (after_cards, after_depth, mt2.count("**")))
assert after_cards == before_cards + len(new_cards), "card count mismatch"
assert after_depth == before_depth, "div depth changed"
assert mt2.count("**") == 0, "markdown stars leaked"
malformed = len(re.findall(r'<div class="article-card">\s*<(?!h2)', mt2))
print("  malformed cards:", malformed)

# ---------- mili 索引 ----------
bp = os.path.join(ROOT, "mili/blog/index.html")
bt = load(bp)
b_cards = len(re.findall(r'<div class="article-card">', bt))
b_depth = check_div(bt)
print("MILI before: cards=%d divdepth=%s" % (b_cards, b_depth))
bnew = [(brand_card(b, f), "%s" % f) for b, f in MILI_NEW]
# 品牌索引插卡：href 为 ./fn，用相同插位法但判据用文件名
bt2 = bt
for card, fn in bnew:
    if fn in bt2:
        print("  skip (already present):", fn)
        continue
    pts = cards_with_date(bt2)
    pos = None
    for st, d in pts:
        if d < DATE:
            pos = st
            break
    if pos is None:
        print("  !! no insertion point for", fn)
        break
    bt2 = bt2[:pos] + card + "\n  " + bt2[pos:]
    print("  inserted at", pos, ":", fn)
b_cards2 = len(re.findall(r'<div class="article-card">', bt2))
b_depth2 = check_div(bt2)
print("MILI after : cards=%d divdepth=%s stars=%d" % (b_cards2, b_depth2, bt2.count("**")))
assert b_cards2 == b_cards + 1, "mili card count mismatch"
assert b_depth2 == b_depth, "mili div depth changed"

if APPLY:
    for p in (mp, bp):
        shutil.copy(p, p + ".bak-20261028")
    save(mp, mt2)
    save(bp, bt2)
    print("APPLIED")
else:
    print("DRY-RUN (use --apply)")
