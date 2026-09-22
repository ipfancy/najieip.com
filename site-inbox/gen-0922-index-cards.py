#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0922 索引补卡：najie 品牌索引 + 主索引 + najie blogPost JSON-LD
   插位规则：插到「第一张日期 < 新卡日期」的卡之前（尊重既有日期降序）
   插入法：每轮 re.finditer 重扫位置，插块 + '\\n  ' 落在目标卡 <div class="article-card"> 之前
"""
import os, re, json, sys, collections

REPO = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv
SLUG = "20260922-us-trademark-sanction-three-step-selfcheck"
NEWDATE = "2026-09-22"
TITLE = "美国商标'已注册'可能是假的！10月1日前5分钟三步自查"
CARD_DESC = ("USPTO 9 月 1 日合并令脚注写明：注册被重开审理期间系统可能仍显示「已注册」，绿字不等于安全。"
             "10 月 1 日东部时间 23:59 是申辩截止（北京时间 10 月 2 日 11:59），须走 Petition to Director 表单附证据。"
             "本文给出五分钟三步自查清单，并纠正中文信息里流传的「877 件」误传。")
URL = "https://najieip.com/najie/blog/%s.html" % SLUG
TAGS = ["美国商标制裁", "USPTO制裁名单", "商标显示已注册"]


def rd(p):
    with open(os.path.join(REPO, p), "r", encoding="utf-8") as f:
        return f.read()


def wr(p, t):
    with open(os.path.join(REPO, p), "w", encoding="utf-8") as f:
        f.write(t)


def card_positions(t):
    """返回 [(start, date)] —— 每次调用重扫"""
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        seg = t[m.start():m.start() + 900]
        dm = re.search(r'<div class="meta">(.*?)</div>', seg, re.S)
        d = None
        if dm:
            dm2 = re.search(r'(\d{4}-\d{2}-\d{2})', dm.group(1))
            d = dm2.group(1) if dm2 else None
        out.append((m.start(), d))
    return out


def validate(t, expect_cards, label):
    res = []
    res.append(("article-card=%d" % expect_cards, t.count('<div class="article-card">') == expect_cards))
    body = t[t.find("<body"):]
    depth = 0; under = 0; d2 = 0
    for m in re.finditer(r'<(/?)div[^>]*>', body):
        if m.group(1):
            depth -= 1
            if depth < 0:
                under += 1; depth = 0
        else:
            depth += 1
            if depth == 2 and m.group(0).startswith('<div class="article-card"'):
                d2 += 1
    res.append(("div深度归零", depth == 0 and under == 0))
    res.append(("depth2卡片=%d" % expect_cards, d2 == expect_cards))
    mal = 0
    for m in re.finditer(r'<div class="article-card">', body):
        nxt = body[m.end():m.end() + 30].lstrip()
        if not nxt.startswith("<h2><a href="):
            mal += 1
    res.append(("malformed=0", mal == 0))
    res.append(("'**'=0", t.count("**") == 0))
    c = collections.Counter(re.findall(r'<h2><a href="([^"]+)"', t))
    res.append(("无重复href", not [k for k, v in c.items() if v > 1]))
    # 插位：新卡之前的卡日期均 >= 新卡日期
    pos = [p for p, d in card_positions(t) if d]
    idx_new = None
    for i, p in enumerate([p for p, d in card_positions(t)]):
        if t[p:p + 400].find(SLUG) >= 0:
            idx_new = i
            break
    dates = [d for p, d in card_positions(t)]
    ok_order = True
    if idx_new is not None:
        for d in dates[:idx_new]:
            if d and d < NEWDATE:
                ok_order = False
    res.append(("插位日期降序", ok_order))
    # JSON-LD 全部可解析
    okjson = True
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(b)
        except Exception as e:
            okjson = False
            print("   JSON-LD FAIL", e)
    res.append(("JSON-LD 全可解析", okjson))
    print("  --- %s ---" % label)
    for n, ok in res:
        print("     %-22s %s" % (n, "PASS" if ok else "FAIL"))
    return all(ok for _, ok in res)


# ================= 1. najie 品牌索引 =================
t = rd("najie/blog/index.html")
assert SLUG not in t, "已存在，勿重复插入"
n_before = t.count('<div class="article-card">')
brand_card = (
    '<div class="article-card">\n'
    '    <h2><a href="./%s.html">%s</a></h2>\n'
    '    <div class="meta">%s · 北京纳杰知识产权代理有限公司</div>\n'
    '    <p>%s</p>\n'
    '  </div>' % (SLUG, TITLE, NEWDATE, CARD_DESC))
# 找插位：第一张日期 < NEWDATE 的卡
target = None
for p, d in card_positions(t):
    if d and d < NEWDATE:
        target = p
        break
print("najie 插位:", target, " 卡数:", n_before)
t2 = t[:target] + brand_card + "\n  " + t[target:]
assert t2.count('<div class="article-card">') == n_before + 1, "卡片数不对"
assert t2.replace(brand_card + "\n  ", "") == t, "除插入块外内容有变化（危险）"
# blogPost JSON-LD
anchor = '"blogPost": ['
assert t2.count(anchor) == 1
entry = json.dumps({"@type": "BlogPosting", "headline": TITLE, "url": URL,
                    "datePublished": NEWDATE, "description": CARD_DESC}, ensure_ascii=False)
t2b = t2.replace(anchor, anchor + entry + ", ", 1)
assert t2b.count('"@type": "BlogPosting"') == t.count('"@type": "BlogPosting"') + 1
print("brand index: %d B -> %d B" % (len(t.encode()), len(t2b.encode())))
ok1 = validate(t2b, n_before + 1, "najie/blog/index.html")

# ================= 2. 主索引 =================
m = rd("blog/index.html")
assert SLUG not in m, "主索引已存在"
n_m_before = m.count('<div class="article-card">')
main_card = (
    '<div class="article-card">\n'
    '    <h2><a href="/najie/blog/%s.html">%s</a></h2>\n'
    '    <div class="meta">%s 2026-09-22 · 纳杰知识产权</div>\n'
    '    <p>%s</p>\n'
    '  </div>' % (SLUG, TITLE, "".join('<span class="tag">%s</span>' % x for x in TAGS), CARD_DESC))
target2 = None
for p, d in card_positions(m):
    if d and d < NEWDATE:
        target2 = p
        break
print("\nmain 插位:", target2, " 卡数:", n_m_before)
m2 = m[:target2] + main_card + "\n  " + m[target2:]
assert m2.count('<div class="article-card">') == n_m_before + 1
assert m2.replace(main_card + "\n  ", "") == m, "除插入块外内容有变化"
print("main index: %d B -> %d B" % (len(m.encode()), len(m2.encode())))
ok2 = validate(m2, n_m_before + 1, "blog/index.html")

if APPLY and ok1 and ok2:
    wr("najie/blog/index.html", t2b)
    wr("blog/index.html", m2)
    print("\n*** APPLIED 两个索引 ***")
else:
    print("\n(dry-run 或 校验未过，未写入)  ok1=%s ok2=%s" % (ok1, ok2))
