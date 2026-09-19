#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-19 主索引补卡（v5 = v3「每次插入后重扫位置」+ 日期降序插位）
用法: python3 site-inbox/gen-0919-index-cards.py [--apply]
"""
import re, os, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, 'blog/index.html')
GAPS = os.path.join(ROOT, 'site-inbox/missing-cards-20260919.json')
APPLY = '--apply' in sys.argv

BRAND_LABEL = {'mili': '觅理律师事务所', 'najie': '北京纳杰知识产权代理有限公司'}

CARD_OPEN = '<div class="article-card">'
CARD_RE = re.compile(
    r'<div class="article-card">\s*<h2><a href="([^"]+)">(.*?)</a></h2>\s*'
    r'<div class="meta">(.*?)</div>\s*<p>(.*?)</p>\s*</div>', re.S)


def build_card(g):
    tags = ''.join('<span class="tag">%s</span>' % t for t in g['tags'])
    label = BRAND_LABEL.get(g['brand'], '')
    meta = (tags + ' ' if tags else '') + g['date'] + (' · ' + label if label else '')
    block = (CARD_OPEN + '\n'
             + '    <h2><a href="%s">%s</a></h2>\n' % (g['href'], g['title'])
             + '    <div class="meta">%s</div>\n' % meta
             + '    <p>%s</p>\n' % g['desc']
             + '  </div>')
    return block


def card_dates(t):
    """返回 body 内每张卡的下标 + 日期（每次调用重扫，绝不复用偏移）"""
    b = t.find('<body')
    out = []
    for m in CARD_RE.finditer(t, b):
        d = re.search(r'(\d{4}-\d{2}-\d{2})', m.group(3))
        out.append((m.start(), d.group(1) if d else '', m.group(1)))
    return out


def insert(t, g):
    block = build_card(g)
    for start, date, href in card_dates(t):
        if date and date < g['date']:
            return t[:start] + block + '\n  ' + t[start:], href
    raise SystemExit('no insertion point found for ' + g['href'])


def main():
    data = json.load(open(GAPS, encoding='utf-8'))
    gaps = data['gaps']
    t = open(MAIN, encoding='utf-8').read()
    before = t.count(CARD_OPEN)
    print('cards before =', before)
    for g in gaps:
        t, anchor = insert(t, g)
        print('  inserted %s  before %s  (cards now %d)' % (g['href'], anchor, t.count(CARD_OPEN)))
    print('cards after =', t.count(CARD_OPEN), '(expect %d)' % (before + len(gaps)))

    # ---- 终验 ----
    ok = True

    def chk(name, cond, extra=''):
        nonlocal ok
        print(('  PASS ' if cond else '  FAIL ') + name + (' ' + str(extra) if extra else ''))
        if not cond:
            ok = False

    chk('card count', t.count(CARD_OPEN) == before + len(gaps))
    chk('no markdown leak', t.count('**') == 0)
    chk('schema.org intact', t.count('https://schema.org') >= 1 and t.count('https://***') == 0)

    # div 配平 + 深度
    depth = 0
    bad_close = 0
    direct_cards = 0
    container_depth = None
    for m in re.finditer(r'<(/?)div\b[^>]*>', t[t.find('<body'):]):
        tag = m.group(0)
        if m.group(1):
            if depth == 0:
                bad_close += 1
            depth -= 1
        else:
            depth += 1
            if 'class="container"' in tag:
                container_depth = depth
        if (not m.group(1)) and tag.startswith(CARD_OPEN):
            if depth == container_depth + 1:
                direct_cards += 1
    chk('div depth ends 0', depth == 0, depth)
    chk('no bad close', bad_close == 0, bad_close)
    chk('cards are direct .container children', direct_cards == before + len(gaps), direct_cards)

    # 每卡以 <h2><a href= 起
    b = t.find('<body')
    blocks = re.findall(r'<div class="article-card">(.*?)</div>\s*(?=<div class="article-card">|<div class="lang|</div>)', t[b:], re.S)
    malformed = sum(1 for blk in blocks if '<h2><a href=' not in blk[:60])
    chk('malformed cards = 0', malformed == 0, 'blocks=%d' % len(blocks))

    # 重复 href
    from collections import Counter
    hrefs = re.findall(r'<h2><a href="([^"]+)"', t[b:])
    dup = [h for h, c in Counter(hrefs).items() if c > 1]
    chk('no duplicate href', not dup, dup)

    # 插入点前缀日期降序：定位最后一张新卡的序号，只校验其前缀
    new_hrefs = set(g['href'] for g in gaps)
    seq = [(m.group(1), (re.search(r'(\d{4}-\d{2}-\d{2})', m.group(3)) or re.match(r'()', '')).group(1))
           for m in CARD_RE.finditer(t, t.find('<body'))]
    if container_depth is None:
        chk('container found', False)
    last_new = max(i for i, (h, d) in enumerate(seq) if h in new_hrefs)
    prefix = [d for h, d in seq[:last_new + 1]]
    mono = all(prefix[i] >= prefix[i + 1] for i in range(len(prefix) - 1))
    chk('insert-point prefix descending', mono, prefix)

    if APPLY and ok:
        open(MAIN, 'w', encoding='utf-8').write(t)
        print('WROTE', MAIN)
    elif APPLY and not ok:
        print('NOT written (checks failed)')
    else:
        print('dry-run only (add --apply)')


main()
