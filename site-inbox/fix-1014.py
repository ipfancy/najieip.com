#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1014 补卡(2张) + najie 20261014 页补 BreadcrumbList。默认 dry-run，--apply 落盘。"""
import re, os, sys, json, copy, collections
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
APPLY = "--apply" in sys.argv

MAIN = "blog/index.html"
NEWDATE = "2026-10-14"

def cards_with_pos(t):
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        i = m.start(); d = 0; j = i
        while j < len(t):
            if t.startswith("<div", j): d += 1; j += 4
            elif t.startswith("</div>", j):
                d -= 1; j += 6
                if d == 0: break
            else: j += 1
        out.append((i, j, t[i:j]))
    return out

def card_date(blk):
    m = re.search(r'class="tag">[^<]*</span>\s*(\d{4}-\d{2}-\d{2})', re.sub(r"(?:<span class=\"tag\">[^<]*</span>\s*)+", "", blk))
    m2 = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
    return m2.group(1) if m2 else "0000-00-00"

def build_card(template, href, title, tags, desc, date, publisher_keep=True):
    c = template
    # href
    c = re.sub(r'(<h2><a href=")[^"]+(">)', r"\g<1>" + href + r"\g<2>", c, count=1)
    # title
    c = re.sub(r'(<h2><a href="[^"]+">).*?(</a></h2>)', lambda m: m.group(1) + title + m.group(2), c, count=1, flags=re.S)
    # tag span group (wholesale)
    taghtml = "".join('<span class="tag">%s</span>' % x for x in tags)
    c = re.sub(r'(?:<span class="tag">[^<]*</span>\s*)+', taghtml + " ", c, count=1)
    # date
    c = re.sub(r"\d{4}-\d{2}-\d{2}", date, c, count=1)
    # description
    c = re.sub(r"(<p>).*?(</p>)", lambda m: m.group(1) + desc + m.group(2), c, count=1, flags=re.S)
    return c

t = open(MAIN, encoding="utf-8", errors="ignore").read()

JOBS = [
    dict(href="/najie/blog/layout-design-originality-claim-322-2026.html",
         tmpl_sub="20261014-trademark-pattern-packaging-confusion",
         title="版图被抄，权利要求却说不清？最高法：可以中途改，知产局不能一拒了之",
         tags=["集成电路布图设计", "布图设计行政裁决", "独创性声明"],
         desc="集成电路布图设计没有权利要求书，权利范围靠独创性主张划定。最高法入库案例（2022）最高法知行终322号明确：实质审理结束前可变更独创性主张，知产局不能一拒了之。10月15日修订后《集成电路布图设计保护条例》（国务院令第842号）施行，独创性声明成登记必备文件。附企业4个动作、3条红线与FAQ。"),
    dict(href="/mili/blog/patent-vs-trade-secret-layering-2026.html",
         tmpl_sub="20261010-mili-aigc-trade-secret-two-leaks",
         title='技术保护选错就白投：29号文第一次点名"专利＋商业秘密"分层',
         tags=["商业秘密", "专利与商业秘密", "分层布局"],
         desc='国知发服字〔2026〕29号第（七）项首次点名"专利与商业秘密协同保护、核心＋外围分层布局"。本文用一张判断表讲清：哪些技术走专利、哪些留作商业秘密，商业秘密三要件里最常被漏的"采取相应保密措施"怎么补，附分层四步清单与 4 个 FAQ，照着分就不会把核心往外送。'),
]

for job in JOBS:
    cs = cards_with_pos(t)
    tmpl = next((b for i, j, b in cs if job["tmpl_sub"] in b), None)
    assert tmpl, "template not found: " + job["tmpl_sub"]
    assert t.count(job["href"]) == 0, "already present: " + job["href"]
    card = build_card(tmpl, job["href"], job["title"], job["tags"], job["desc"], NEWDATE)
    # 插入点 = 第一张日期 < NEWDATE 的卡
    ins = None
    for i, j, b in cs:
        if card_date(b) < NEWDATE:
            ins = i; break
    assert ins is not None, "no insertion point"
    ctx = t[max(0, ins - 90):ins]
    print("--- insert %s at %d ; preceding ctx: %r" % (job["href"], ins, ctx[-60:]))
    print("    card: %r" % card[:260])
    t2 = t[:ins] + card + "\n  " + t[ins:]
    assert t2.replace(card + "\n  ", "", 1) == t, "outside-change guard failed"
    t = t2

# ---- 结构断言 ----
cs2 = cards_with_pos(t)
print("\ncards: %d -> %d" % (len(cards_with_pos(open(MAIN, encoding='utf-8').read())), len(cs2)))
assert len(cs2) == len(cards_with_pos(open(MAIN, encoding="utf-8", errors="ignore").read())) + 2
assert t.count("**") == 0, "star leak"
hrefs = collections.Counter(re.findall(r'<h2><a href="([^"]+)"', t))
dups = [h for h, n in hrefs.items() if n > 1]
print("dup hrefs:", dups)
assert not dups, "duplicate hrefs"
mal = sum(1 for i, j, b in cs2 if not b.startswith('<div class="article-card">\n'))
print("malformed:", mal)
# div 深度
body = t[t.find("<body"):]
d = 0; depth_cards = 0; neg = 0; hist = collections.Counter()
for m in re.finditer(r"<(/?)div[^>]*>", body):
    if m.group(1) == "": hist[d] += 1
    if m.group(1) == "":
        if body[m.start():].startswith('<div class="article-card"') and d == 1: depth_cards += 1
        d += 1
    else:
        d -= 1
        if d < 0: neg += 1
print("final depth:", d, "neg:", neg, "depth1 cards:", depth_cards, "total cards:", len(cs2))
assert d == 0 and neg == 0
assert depth_cards == len(cs2), "depth1 card mismatch"

# ---- najie 20261014 页补 BreadcrumbList ----
P = "najie/blog/20261014-trademark-pattern-packaging-confusion.html"
src = open("najie/blog/layout-design-originality-claim-322-2026.html", encoding="utf-8", errors="ignore").read()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
bcsrc = next(b for b in blocks if "BreadcrumbList" in b)
obj = json.loads(bcsrc)
last = obj["itemListElement"][-1]
print("\nbreadcrumb template last item:", json.dumps(last, ensure_ascii=False))
last["name"] = "别把大牌花纹印包装"
last["item"] = "https://najieip.com/najie/blog/20261014-trademark-pattern-packaging-confusion.html"
newblk = '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>\n"
pt = open(P, encoding="utf-8", errors="ignore").read()
assert pt.count("application/ld+json") == 1
assert "BreadcrumbList" not in pt
assert "schema.org" in newblk
p2 = pt.replace("</head>", newblk + "</head>", 1)
assert p2 != pt
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', p2, re.S):
    json.loads(b)
print("page ld blocks %d -> %d ; bytes %d -> %d" % (pt.count("application/ld+json"), p2.count("application/ld+json"), len(pt.encode()), len(p2.encode())))
print("body unchanged:", p2.replace(newblk, "", 1) == pt)

if APPLY:
    open(MAIN, "w", encoding="utf-8").write(t)
    open(P, "w", encoding="utf-8").write(p2)
    print("\nAPPLIED")
else:
    print("\nDRY RUN")
