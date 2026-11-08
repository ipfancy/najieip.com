#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补主索引卡：20261101-mili-ai-writing-judgment（品牌索引有卡、主索引零卡）"""
import re, os, sys, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
MAIN = os.path.join(REPO, "blog/index.html")
SLUG = "20261101-mili-ai-writing-judgment"
BRAND = "mili"
DATE = "2026-11-01"
HREF = f"/{BRAND}/blog/{SLUG}.html"

t = open(MAIN, encoding='utf-8').read()
if f'>{SLUG}.html' in t or f'/{BRAND}/blog/{SLUG}.html' in t:
    print("ALREADY PRESENT — no-op"); sys.exit(0)

# 取卡片：div 深度配对
def card_at(t, i):
    j = t.rfind('<div class="article-card">', 0, i)
    k, d = j, 0
    while True:
        m = re.search(r'<div\b|</div>', t[k:])
        if not m: raise RuntimeError('unbalanced card')
        pos = k + m.start()
        d += -1 if m.group(0) == '</div>' else 1
        k = pos + len(m.group(0))
        if d == 0: return j, k

# 用「同品牌近期已收录文」卡做模板（不当得利文为 11-07 mili 文）
tpl_i = t.find(f'/mili/blog/20261107-mili-unjust-enrichment-default-judgment.html')
tj, tk = card_at(t, tpl_i)
tpl_card = t[tj:tk]

title = "AI 会写文书了，凭什么还请律师"
desc = ("AI 能写检索报告、能写权利要求、能拟合同，律师凭什么还收费？客户买的从来不是「写」，是判断。"
        "能被标准化的部分确实在贬值——检索、格式、引用关系都已被压缩到几分钟；"
        "但品味（写三条硬的还是八条凑数）、判断力（信息不全时拍板并承担后果）、连接力（回复时效、坏消息先说、结案报告）三件事不会。"
        "附立案时写三条假设、结案回填的做法，用留痕看出自己在哪类判断上系统性偏乐观。"
        "分水岭不在用不用 AI，而在你处在链条的哪个位置。")
tags = ["AI与律师", "专业判断", "涉外转介"]

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

# 按模板重建卡（主索引口径：h2 绝对路径 + meta 带 tag/日期/主体）
m = re.search(r'<h2><a href="([^"]+)">(.*?)</a></h2>\s*<div class="meta">(.*?)</div>\s*<p>(.*?)</p>', tpl_card, re.S)
assert m, "模板卡结构不匹配"
meta_inner = m.group(3)
# 保留模板的 tag span 结构，整体替换 tag 组与日期/机构
tag_html = ''.join(f'<span class="tag">{esc(x)}</span>' for x in tags)
meta_new = re.sub(r'(?:<span class="tag">[^<]*</span>)+', tag_html, meta_inner, count=1)
meta_new = re.sub(r'\d{4}-\d{2}-\d{2}', DATE, meta_new, count=1)

card = (f'<div class="article-card">\n    <h2><a href="{HREF}">{esc(title)}</a></h2>\n'
        f'    <div class="meta">{meta_new}</div>\n'
        f'    <p>{esc(desc)}</p>\n  </div>')

# 插入点：第一张日期 < 2026-11-01 的卡之前；每轮重扫位置
def insert(t, card):
    for mt in re.finditer(r'<div class="article-card">', t):
        seg = t[mt.start():mt.start()+2500]
        dm = re.search(r'<div class="meta">.*?(\d{4}-\d{2}-\d{2})', seg, re.S)
        if not dm: continue
        if dm.group(1) < DATE:
            return t[:mt.start()] + card + '\n  ' + t[mt.start():]
    raise RuntimeError('no insertion point found')

t2 = insert(t, card)

# 终验
def divstats(s):
    d = 0; hist = {}; c = 0; mal = 0; dups = []
    body = s[s.find('<body'):]
    depth = 0; ok = True; cards = 0
    for mt in re.finditer(r'<div\b[^>]*>|</div>', body):
        tag = mt.group(0)
        if tag.startswith('</'):
            depth -= 1
            if depth < 0: ok = False
        else:
            if 'class="article-card"' in tag:
                cards += 1
                hist[depth] = hist.get(depth, 0) + 1
            depth += 1
    return cards, depth, ok, hist

c1, d1, ok1, h1 = divstats(t)
c2, d2, ok2, h2 = divstats(t2)
delta = {k: h2.get(k, 0) - h1.get(k, 0) for k in set(h1) | set(h2)}
print("cards", c1, "->", c2, "| depth_end", d1, "->", d2, "| ok", ok1, ok2)
print("hist", h1, "->", h2, "| delta", delta)
print("insert_only", t2.replace(card + "\n  ", "", 1) == t)
mal = len(re.findall(r'<div class="article-card">\s*<h2>', t2)) - len(re.findall(r'<div class="article-card">\s*<h2><a href=', t2))
print("malformed_head", mal)
urls = re.findall(r'<h2><a href="([^"]+)"', t2)
print("dups", [u for u in set(urls) if urls.count(u) > 1])
print("stars", t2.count('**'))

assert c2 == c1 + 1 and d2 == d1 and ok2
assert t2.replace(card + "\n  ", "", 1) == t
assert sum(v for v in delta.values() if v > 0) == 1 and not [v for v in delta.values() if v < 0]

if '--apply' in sys.argv:
    open(MAIN, 'w', encoding='utf-8').write(t2)
    print("WRITTEN", MAIN, len(t2.encode()), "bytes")
else:
    print("dry-run OK (use --apply)")
