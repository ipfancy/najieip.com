#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insert missing aipunajie cards into main blog/index.html (v3: rescan per insertion)."""
import re, os, sys

BASE = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(BASE, "blog/index.html")
APPLY = "--apply" in sys.argv

CARDS = [
    dict(date="2026-10-27",
         href="/aipunajie/blog/20261027-aipunajie-oa-phone-amendment-decision.html",
         title="审查员打电话让你改，当场答应对不对",
         tags=["审查意见答复", "权利要求修改", "保护范围"],
         desc="电话里那三分钟，决定的不是这一件案子能不能授权，而是保护范围还剩多少。三分支判断法（是否触及独权核心区别特征）、从权下放怎么用、为什么不能口头答应，以及电话挂断后必须做的三件事。"),
    dict(date="2026-10-26",
         href="/aipunajie/blog/20261026-aipunajie-patent-before-launch.html",
         title="先申请专利再开发布会",
         tags=["新颖性", "专利布局", "优先权"],
         desc="发布会、短视频、电商详情页都属于「为公众所知」，产品一亮相技术方案就成了现有技术，专利申请被自己废掉。《专利法》第24条的6个月宽限期不覆盖普通商业发布会，海外多数国家没有宽限期。附可落地顺序：外观设计先占位、技术点逐个对照、用优先权处理迭代（发明12个月／外观6个月），以及三个高频误区。"),
]

def card_html(c):
    tags = "".join('<span class="tag">%s</span>' % t for t in c["tags"])
    return ('<div class="article-card">\n'
            '    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · 北京爱普纳杰专利代理事务所</div>\n'
            '    <p>%s</p>\n'
            '  </div>') % (c["href"], c["title"], tags, c["date"], c["desc"])

def blocks_with_date(t):
    """Return list of (card_start_index, date_str) via div-depth pairing from each card start."""
    out, i = [], 0
    while True:
        i = t.find('<div class="article-card">', i)
        if i < 0:
            break
        depth, j = 0, i
        while True:
            m = re.search(r'<div\b|</div>', t[j:])
            if not m:
                break
            j += m.end()
            depth += 1 if m.group(0).startswith('<div') else -1
            if depth == 0:
                break
        blk = t[i:j]
        d = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
        out.append((i, d.group(1) if d else "0000-00-00", j))
        i = j
    return out

t = open(P, encoding="utf-8").read()
orig = t
print("cards before:", t.count('class="article-card"'))

for c in sorted(CARDS, key=lambda x: x["date"], reverse=True):
    if c["href"] in t:
        print("skip (already present):", c["href"]); continue
    bl = blocks_with_date(t)
    target = None
    for start, d, end in bl:
        if d < c["date"]:
            target = start
            break
    if target is None:  # append before container close? fallback to top
        target = bl[0][0]
    card = card_html(c)
    t = t[:target] + card + "\n  " + t[target:]
    print("inserted %s before card at %d (date=%s)" % (c["date"], target, c["date"]))

print("cards after:", t.count('class="article-card"'))
print("stars:", t.count("**"))

if APPLY:
    open(P, "w", encoding="utf-8").write(t)
    print("WRITTEN", len(t))
else:
    print("DRY-RUN only")
