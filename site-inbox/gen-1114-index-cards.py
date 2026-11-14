#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-14 索引补卡：当日两篇文品牌索引+主索引全零卡
用法: python3 site-inbox/gen-1114-index-cards.py [--apply]
"""
import os, re, sys, json, html as htmlmod

REPO = "/Users/ziganghe/wiki/najieip-verify"
APPLY = "--apply" in sys.argv
DATE = "2026-11-14"

ARTICLES = [
    # (relpath, brand_key, brand_name, org)
    ("mili/blog/20261114-mili-copyright-financing-16-cases.html", "mili", "觅理", "北京觅理律师事务所"),
    ("najie/blog/20261114-najie-design-view-projection-rejection.html", "najie", "纳杰", "北京纳杰知识产权代理有限公司"),
]
IDX = {"mili": os.path.join(REPO, "mili/blog/index.html"),
       "najie": os.path.join(REPO, "najie/blog/index.html"),
       "main": os.path.join(REPO, "blog/index.html")}

def zh_quotes(s):
    cnt = [0]
    def rep(m):
        cnt[0] += 1
        return "“" if cnt[0] % 2 else "”"
    return re.sub(r'"', rep, s)

def cards(t):
    """按 div 深度配对切卡：(start,end)"""
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        i, depth = m.end(), 1
        while depth and i < len(t):
            nx = re.search(r"<div\b|</div>", t[i:])
            if not nx: break
            if nx.group(0) == "</div>":
                depth -= 1
            else:
                depth += 1
            i += nx.end()
        out.append((m.start(), i))
        if i >= len(t): break
    return out

def card_dates(t):
    res = []
    for s, e in cards(t):
        blk = t[s:e]
        d = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
        res.append(d.group(1) if d else "")
    return res

def info(rel):
    t = open(os.path.join(REPO, rel), encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", t, re.S).group(1).split(" — ")[0].strip()
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = htmlmod.unescape(m.group(1)).strip() if m else ""
    return title, desc

def build_card(tpl, href, title, desc, date, tag, org, absolute):
    c = tpl
    c = re.sub(r'(<h2><a href=")[^"]*(")', lambda m: m.group(1) + href + m.group(2), c, count=1)
    c = re.sub(r'(<h2><a href="[^"]*">).*?(</a></h2>)', lambda m: m.group(1) + title + m.group(2), c, count=1, flags=re.S)
    if '<div class="meta">' in c:
        c = re.sub(r'<div class="meta">.*?</div>',
                   f'<div class="meta"><span class="tag">{tag}</span> {date} · {org}</div>', c, count=1, flags=re.S)
    else:
        c = re.sub(r'<div class="date">.*?</div>', f'<div class="date">{date}</div>', c, count=1, flags=re.S)
    if "<p>" in c:
        c = re.sub(r"<p>.*?</p>", lambda m: "<p>" + desc + "</p>", c, count=1, flags=re.S)
    return c

def insert(t, card, date):
    """插到第一张日期 < date 的卡之前；无则插到首卡之前"""
    ds = card_dates(t)
    cs = cards(t)
    pos = None
    for (s, e), d in zip(cs, ds):
        if d and d < date:
            pos = s; break
    if pos is None:
        pos = cs[0][0]
    return t[:pos] + card + "\n  " + t[pos:]

report = []
for rel, brand, tag, org in ARTICLES:
    slug = os.path.basename(rel).replace(".html", "")
    title, desc = info(rel)
    title = zh_quotes(title); desc = zh_quotes(desc)
    # 品牌索引
    bidx = IDX[brand]
    t = open(bidx, encoding="utf-8").read()
    c_hit = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), t))
    if c_hit == 0:
        cs = cards(t)
        n0 = len(cs)
        tpl = t[cs[0][0]:cs[0][1]]
        card = build_card(tpl, f"./{slug}.html", title, desc, DATE, tag, org, False)
        t2 = insert(t, card, DATE)
        n1 = len(re.findall(r'<div class="article-card">', t2))
        ok = (n1 == n0 + 1) and t2.replace(card + "\n  ", "", 1) == t and t2.count("<div") - t2.count("</div>") == t.count("<div") - t.count("</div>")
        print(f"[brand {brand}] {slug}: cards {n0}->{n1} insert_ok={ok}")
        if APPLY and ok:
            open(bidx, "w", encoding="utf-8").write(t2)
    else:
        print(f"[brand {brand}] {slug}: already {c_hit}")
        ok = True

    # 主索引
    t = open(IDX["main"], encoding="utf-8").read()
    m_hit = len(re.findall(r'<h2[^>]*><a href="[^"]*' + re.escape(slug), t))
    if m_hit == 0:
        cs = cards(t)
        n0 = len(cs)
        tpl = t[cs[0][0]:cs[0][1]]
        href = f"/{brand}/blog/{slug}.html"
        card = build_card(tpl, href, title, desc, DATE, tag, org, True)
        t2 = insert(t, card, DATE)
        n1 = len(re.findall(r'<div class="article-card">', t2))
        ok = (n1 == n0 + 1) and t2.replace(card + "\n  ", "", 1) == t and t2.count("<div") - t2.count("</div>") == t.count("<div") - t.count("</div>")
        print(f"[main] {slug}: cards {n0}->{n1} insert_ok={ok} href={href}")
        if APPLY and ok:
            open(IDX["main"], "w", encoding="utf-8").write(t2)
    else:
        print(f"[main] {slug}: already {m_hit}")

# 打印主索引首卡模板供目视
t = open(IDX["main"], encoding="utf-8").read()
cs = cards(t)
print("\nMAIN 首卡模板:\n" + t[cs[0][0]:cs[0][1]][:400])
print("\nMAIN 日期序列(前6):", card_dates(t)[:6])
