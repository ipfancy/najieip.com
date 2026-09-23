#!/usr/bin/env python3
# 0923 主索引补卡 v3方法(每次插入后重扫位置) — dry-run / --apply
import os, re, json, sys

ROOT = os.path.expanduser('~/wiki/najieip-verify')
os.chdir(ROOT)
APPLY = '--apply' in sys.argv

rows = json.load(open('site-inbox/gather-0923-all.json', encoding='utf-8'))
by_norm = {r['norm']: r for r in rows}

TARGETS = [
    '/najie/blog/shangbiao-bohuifushen-2026.html',
    '/najie/blog/zhiming-shangbiao-pinpai-pingjia-2026.html',
]
TARGETS += [f'/mili/blog/20260922-caichan-shouhu-0{i}.html' for i in range(1, 8)]

LABEL = {'mili': '觅理律师事务所', 'najie': '纳杰知识产权', 'aipunajie': '爱普纳杰专利代理'}

def build_card(r):
    raw = r['raw']
    end = raw.rindex('</div>') + 6
    inner = raw[:end]
    # 去掉旧 href 的相对前缀，换成主索引绝对路径
    inner = re.sub(r'href="\./[^"]*"', f'href="{r["norm"]}"', inner)
    inner = re.sub(r'href="/(?!/)([^"]*)"', f'href="{r["norm"]}"', inner, count=0)  # noop guard
    card = '<div class="article-card">' + inner
    assert card.count('<h2><a href=') == 1, card[:200]
    assert r['norm'] in card, card[:200]
    return card

def card_positions(t):
    return [(m.start(), m.group(1)) for m in
            re.finditer(r'<div class="article-card">(.*?)</div>\s*(?=<div class="article-card">|<div class="container"|</div>\s*</body>|$)', t, re.S)]

def date_of(match_body):
    m = re.search(r'<div class="meta">.*?(\d{4}-\d{2}-\d{2})', match_body, re.S)
    return m.group(1) if m else ''

t = open('blog/index.html', encoding='utf-8').read()
orig = t
before_cards = t.count('<div class="article-card">')
print(f"BEFORE cards={before_cards} chars={len(t)}")

plan = []
for norm in TARGETS:
    r = by_norm[norm]
    plan.append((r['date'], norm))
# 断言日期完整
for d, n in plan:
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', d), (d, n)
print("plan:", plan)

for date, norm in plan:
    r = by_norm[norm]
    card = build_card(r)
    # 重扫当前位置
    pos = card_positions(t)
    # 找第一张日期 < 新卡日期的卡
    anchor = None
    for start, body in pos:
        d = date_of(body)
        if d and d < date:
            anchor = (start, d)
            break
    assert anchor is not None, f"no anchor for {norm}"
    astart, adate = anchor
    ins = card + '\n  '
    print(f"\n--- INSERT {norm} (date={date}) before card date={adate} at {astart}")
    print("   context BEFORE:", repr(t[astart-40:astart]))
    print("   context AFTER :", repr(t[astart+len('<div class="article-card">'):astart+120]))
    t = t[:astart] + ins + t[astart:]

after_cards = t.count('<div class="article-card">')
print(f"\nAFTER cards={after_cards} (expected {before_cards + len(plan)}) chars={len(t)}")

# 终验
assert after_cards == before_cards + len(plan)
assert t.count('**') == 0
# div 配平 + depth==2 卡片数
body = t[t.find('<body'):]
depth = 0; ok = True; depth2 = 0; malformed = 0
for m in re.finditer(r'<(/?)div\b[^>]*>', body):
    tag = m.group(0)
    if tag.startswith('</'):
        depth -= 1
        if depth < 0:
            ok = False
    else:
        if depth == 1 and tag.startswith('<div class="article-card"'):
            depth2 += 1
        depth += 1
print(f"div depth end={depth} balanced_ok={ok} depth2_cards={depth2} total_cards={after_cards}")
# 每卡以 <h2><a href= 起
cards = re.findall(r'<div class="article-card">\s*(.{0,20})', t)
malformed = sum(1 for c in cards if not c.startswith('<h2><a href='))
print("malformed (not starting with h2>a):", malformed)
# 插入点前缀降序：新卡之前的卡日期均 >= 新卡日期
pos = card_positions(t)
newpos = {}
for target in TARGETS:
    for start, b in pos:
        if target in b:
            newpos[target] = (start, date_of(b))
            break
for target, (start, d) in newpos.items():
    prefix_dates = [date_of(b) for s, b in pos if s < start and date_of(b)]
    bad = [x for x in prefix_dates if x < d]
    print(f"  {target}: date={d} prefix_cards={len(prefix_dates)} violations={bad}")

assert ok and depth == 0 and depth2 == after_cards and malformed == 0
print("\nSTRUCTURE CHECKS PASS")

if APPLY:
    open('blog/index.html.bak-0923', 'w', encoding='utf-8').write(orig)
    open('blog/index.html', 'w', encoding='utf-8').write(t)
    print("APPLIED -> blog/index.html (bak: blog/index.html.bak-0923)")
else:
    print("DRY-RUN only (use --apply)")
