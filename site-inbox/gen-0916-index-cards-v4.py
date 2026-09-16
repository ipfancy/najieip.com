#!/usr/bin/env python3
"""SiteOps 0916 补卡 v4（幂等）：把主 blog/index.html 缺失的文章卡片按日期降序插回。

继承 v3 安全机制：每次插入后重扫卡片位置（无过期偏移）；插入串 = 卡块 + '\n  '。
新增：日期取自品牌索引内嵌 BlogPosting JSON-LD（url→datePublished），
      标题/标签取自品牌索引卡片，摘要取自 og:description。
用法：python3 gen-0916-index-cards-v4.py [--apply]
"""
import re, sys, json, os
from collections import Counter

root = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(root)

IDX = 'blog/index.html'
APPLY = '--apply' in sys.argv
CARD = '<div class="article-card">'
BRAND_LABEL = {'mili': '觅理律师事务所', 'najie': '纳杰知识产权', 'aipunajie': '爱普纳杰专利代理'}
CANDS = json.load(open('site-inbox/missing-cards-0916.json', encoding='utf-8'))


def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


# ---- date map from brand-index embedded BlogPosting JSON-LD ----
date_map = {}
title_map = {}
for b in ('najie', 'mili', 'aipunajie'):
    idx = open(f'{b}/blog/index.html', encoding='utf-8').read()
    for url, d in re.findall(r'"url"\s*:\s*"([^"]+)"\s*,\s*"datePublished"\s*:\s*"([^"]+)"', idx):
        date_map[url] = d
    for url, h in re.findall(r'"headline"\s*:\s*"([^"]*)"[^}]*?"url"\s*:\s*"([^"]+)"', idx):
        title_map[h] = url
    # card titles: h2/h3 + a href
    for href, ttl in re.findall(r'<h[23]><a href="\./([^"]+)">([^<]*)</a></h[23]>', idx):
        title_map[f'file:{href}'] = clean(ttl)


DATE_OVERRIDE = {  # 品牌索引 JSON-LD 无 datePublished 的两篇：取 git 首次入库日
    '/najie/blog/overseas-trademark-strategy.html': '2026-07-31',
    '/mili/blog/uspto-tbmp-2026-ttab-center-estta-update.html': '2026-07-31',
}


def get_date(c):
    if c['path'] in DATE_OVERRIDE:
        return DATE_OVERRIDE[c['path']]
    url = 'https://najieip.com' + c['path']
    d = date_map.get(url) or c['date_published']
    if not d:
        m = re.search(r'(\d{4})(\d{2})(\d{2})', c['file'])
        if m:
            d = f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
    return d or ''


def get_title(c):
    # brand-index card title is authoritative (matches what the brand blog shows)
    t = title_map.get(c['og_title'])
    if t is None:
        for k, v in title_map.items():
            if k.startswith('file:') and k == f"file:{c['file']}":
                t = v
                break
    return clean(title_map.get(f"file:{c['file']}") or t or c['h1'] or c['og_title'])


BRAND_IDX = {b: open(f'{b}/blog/index.html', encoding='utf-8').read()
             for b in ('najie', 'mili', 'aipunajie')}


def get_excerpt(c):
    # 1) brand-index card <p> (what the brand blog already shows)
    idx = BRAND_IDX[c['brand']]
    m = re.search(r'<a href="\./' + re.escape(c['file']) + r'">.*?<p>(.*?)</p>', idx, flags=re.S)
    if m and len(clean(m.group(1))) >= 30:
        return clean(m.group(1))[:400]
    # 2) article page meta / first paragraph
    t = open(c['path'].lstrip('/'), encoding='utf-8').read()
    for pat in (r'<meta property="og:description" content="([^"]*)"',
                r'<meta name="description" content="([^"]*)"'):
        m = re.search(pat, t)
        if m and len(clean(m.group(1))) >= 20:
            return clean(m.group(1))[:400]
    for m in re.finditer(r'<p[^>]*>(.*?)</p>', t, flags=re.S):
        cc = clean(m.group(1))
        if len(cc) >= 60 and '版权' not in cc[:10]:
            return cc[:400]
    return ''


def build_block(c):
    tags = [x.strip() for x in re.split(r'[,，、]', c['kw']) if x.strip()][:3]
    taghtml = ''.join(f'<span class="tag">{k}</span>' for k in tags)
    ex = get_excerpt(c)
    title = get_title(c)
    assert len(ex) >= 30, f'excerpt too short: {c["path"]}'
    assert len(title) >= 6, f'title too short: {c["path"]}'
    return ('<div class="article-card">\n'
            f'    <h2><a href="{c["path"]}">{title}</a></h2>\n'
            f'    <div class="meta">{taghtml} {get_date(c)} · {BRAND_LABEL[c["brand"]]}</div>\n'
            f'    <p>{ex}</p>\n'
            '  </div>')


def markers(t):
    out = []
    for m in re.finditer(re.escape(CARD), t):
        w = t[m.start():m.start() + 900]
        d = re.search(r'(\d{4}-\d{2}-\d{2})', w)
        out.append((m.start(), d.group(1) if d else None))
    return out


t = open(IDX, encoding='utf-8').read()
base_cards = len(markers(t))
print('existing cards:', base_cards)

pre = markers(t)
ds_pre = [d for _, d in pre if d]
print('existing dated monotonic desc:', all(a >= b for a, b in zip(ds_pre, ds_pre[1:])),
      '| range', ds_pre[0] if ds_pre else None, '->', ds_pre[-1] if ds_pre else None)

def is_stub(c):
    """重定向跳转页/空壳页不是文章：<1500B 或带 meta refresh 跳转。"""
    if c.get('size', 0) < 1500:
        return 'small'
    t = open(c['path'].lstrip('/'), encoding='utf-8').read()
    if 'http-equiv="refresh"' in t:
        return 'redirect'
    if len(re.findall(r'<p', t)) < 2:
        return 'no-body'
    return None


todo = []
for c in CANDS:
    if f'href="{c["path"]}"' in t:
        print('SKIP (present):', c['path'])
        continue
    s = is_stub(c)
    if s:
        print('SKIP (stub:%s):' % s, c['path'], c.get('size'))
        continue
    blk = build_block(c)
    todo.append((get_date(c), c['path'], blk))
print('to insert:', len(todo))
print('no-date items:', [p for d, p, _ in todo if not d])

if not APPLY:
    for d, p, _ in sorted(todo, key=lambda x: (x[0] or '0'), reverse=True):
        print('  ', d or 'NO-DATE', p)
    print('[DRY RUN]')
    sys.exit(0)

for date, path, blk in sorted(todo, key=lambda x: (x[0] or '0'), reverse=True):
    ms = markers(t)
    pos = None
    if date:
        for p, d in ms:
            if d and d < date:
                pos = p
                break
    if pos is None:
        for p, d in ms:
            if d is None:
                pos = p
                break
    if pos is None:
        pos = ms[-1][0]
    t = t[:pos] + blk + '\n  ' + t[pos:]
    print('inserted', date or 'NO-DATE', path, 'at', pos)

open(IDX, 'w', encoding='utf-8').write(t)

print('\n=== VERIFY ===')
t2 = open(IDX, encoding='utf-8').read()
print('cards:', t2.count(CARD), 'expected', base_cards + len(todo))
print('<div:', t2.count('<div'), '</div>:', t2.count('</div>'),
      'balanced:', t2.count('<div') == t2.count('</div>'))
refs = re.findall(r'<h2><a href="([^"]+)"', t2)
dups = {k: v for k, v in Counter(refs).items() if v > 1}
print('total h2 links:', len(refs), '| duplicate hrefs:', dups)
miss = [p for _, p, _ in todo if t2.count(f'href="{p}"') != 1]
print('inserted s.t. href count != 1:', miss)
print('stray **:', t2.count('**'), '| corrupt schema:', t2.count('https://***'))
bad = [b[:60] for b in re.findall(r'<div class="article-card">(.*?)\n  </div>', t2, flags=re.S)
       if not ('<h2><a href=' in b and '<div class="meta">' in b and '<p>' in b)]
print('malformed cards:', len(bad), bad[:3])
ms = markers(t2)
ds = [d for _, d in ms if d]
print('dated cards:', len(ds), 'monotonic desc:', all(a >= b for a, b in zip(ds, ds[1:])),
      '| range', ds[0], '->', ds[-1])
print('undated cards:', sum(1 for _, d in ms if not d))
# structural: depth + direct-child card count
depth = 0
anom = 0
cards_at_depth2 = 0
for m in re.finditer(r'<(/?)(div)\b[^>]*>|(<div class="article-card">)', t2):
    if m.group(3):
        if depth == 2:
            cards_at_depth2 += 1
    if m.group(1) is None:
        depth += 1
    elif m.group(1):
        depth -= 1
        if depth < 0:
            anom += 1
print('div final depth:', depth, '| anomalies:', anom, '| cards at depth2:', cards_at_depth2)
