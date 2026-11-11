#!/usr/bin/env python3
"""2026-11-11 索引补卡 + articles.json 条目。用法: python3 gen-1111-cards.py [--apply]"""
import os, re, sys, json, copy

REPO = "/Users/ziganghe/wiki/najieip-verify"
APPLY = "--apply" in sys.argv

CARDS = [
    # brand, slug, date, title, tags, excerpt
    ("mili", "20261111-mili-earnest-money-cap", "2026-11-11",
     "合同标的 500 万，定金写 150 万：多写的 50 万，双倍不了",
     ["合同", "定金"], "定金上限是主合同标的额的 20%，超出部分不产生定金效力，违约时只能按预付款原额退回。500 万合同写 150 万定金，只认 100 万，双倍返还 200 万，另 50 万照原额退。文内拆 20% 的基数、定金与违约金择一、未实际交付无定金，附四档算例与三件今晚就能改合同的事。"),
    ("mili", "20261111-mili-fake-patent-marking-line", "2026-11-11",
     "包装上印错一个专利号：罚 25 万的是行政，判 3 年的是刑事",
     ["专利标识", "假冒专利"], "印错一个专利号落在两条轨上：行政轨看专利法第 68 条，刑事轨看刑法第 216 条，分界只有一个词——「他人专利」。本文拆五种情形与两个例外、25 万与 5 倍三个数字怎么用、什么情况下才真进刑事，库存还能不能卖也给了答案。"),
    ("najie", "20261111-najie-same-day-dual-filing-one-choice", "2026-11-11",
     "同日双申只能二选一：改权利要求绕开放弃，这条路封了",
     ["同日双申", "专利"], "同日双申在 2026 年 1 月 1 日只剩两条路：声明放弃实用新型，或发明申请被驳回。第 84 号令删掉了「修改权利要求使保护范围不同、两权并存」这第三条路。文内说明新旧对照、现在还能怎么补救，以及申报前该改哪几份文件。"),
]

def depth_end(t, start):
    """从 start 处的 <div 起，深度配对找闭合，返回结束索引（含 </div>）"""
    i, d = start, 0
    for m in re.finditer(r'<(/?)div\b[^>]*>', t[start:]):
        d += -1 if m.group(1) else 1
        if d == 0:
            return start + m.end()
    return -1

def find_card(t, slug):
    m = re.search(r'<h2[^>]*><a href="([^"]*' + re.escape(slug) + r'[^"]*)"', t)
    if not m:
        return None
    st = t.rfind('<div class="article-card">', 0, m.start())
    if st < 0:
        return None
    en = depth_end(t, st)
    return t[st:en], st, en, m.group(1)

def cards_dates(t):
    """返回 [(start, end, date)]"""
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        en = depth_end(t, m.start())
        blk = t[m.start():en]
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
        out.append((m.start(), en, dm.group(1) if dm else '0000-00-00'))
    return out

def build_card(tpl, href, title, date, tags, excerpt, brand_cn, org):
    b = tpl
    old_href = re.search(r'href="([^"]*)"', b).group(1)
    b = b.replace(f'href="{old_href}"', f'href="{href}"')
    b = re.sub(r'(<a href="[^"]*"[^>]*>)(.*?)(</a>)', lambda m: m.group(1) + title + m.group(3), b, count=1, flags=re.S)
    # 重建 meta 行：主体 tag + 日期 + 落款
    tag_html = ''.join(f'<span class="tag">{x}</span>' for x in tags)
    meta_new = f'<div class="meta"><span class="tag">{brand_cn}</span> {date} · {org}</div>'
    b2 = re.sub(r'<div class="meta">.*?</div>', meta_new, b, count=1, flags=re.S)
    assert 'class="meta"' in b2, 'meta 缺失'
    b = b2
    ps = list(re.finditer(r'<p[^>]*>.*?</p>', b, flags=re.S))
    if ps:
        last = ps[-1]
        b = b[:last.start()] + f'<p>{excerpt}</p>' + b[last.end():]
    return b

def insert_card(t, card, date):
    """按日期降序插到第一张日期 < date 的卡之前；无则追加到末尾第一张大卡前"""
    for st, en, d in cards_dates(t):
        if d < date:
            return t[:st] + card + '\n  ' + t[st:]
    # 全部日期 >= date：插到第一张卡前
    st, en, d = cards_dates(t)[0]
    return t[:st] + card + '\n  ' + t[st:]

targets = {}
for brand in ('mili', 'najie'):
    targets[(brand, 'brand')] = os.path.join(REPO, brand, 'blog', 'index.html')
targets[('main', 'main')] = os.path.join(REPO, 'blog', 'index.html')

report = []
for path in sorted(set(targets.values())):
    t = open(path, encoding='utf-8').read()
    base_count = t.count('<div class="article-card">')
    is_main = os.path.dirname(os.path.abspath(path)) == os.path.join(REPO, 'blog')
    brand_dir = 'main' if is_main else os.path.basename(os.path.dirname(os.path.dirname(path)))
    tpl_card, tpl_st, tpl_en, tpl_href = None, None, None, None
    added = 0
    for brand, slug, date, title, tags, excerpt in CARDS:
        target_here = is_main or brand == brand_dir
        if not target_here:
            continue
        if re.search(r'<h2[^>]*><a href="[^"]*' + re.escape(slug), t):
            continue  # 已有卡
        if tpl_card is None:
            # 取本索引中同品牌近期卡做模板
            found = None
            for b2, s2, d2, *_ in CARDS:
                if (is_main or b2 == brand_dir):
                    r = find_card(t, s2)
                    if r: found = r; break
            if not found:
                r = find_card(t, '20261112-mili-year-end-bonus-cancel') or find_card(t, '20261110-mili-will-partial-invalid')
                found = r
            if not found:
                cd = cards_dates(t)
                if cd:
                    st0, en0, _ = cd[0]
                    found = (t[st0:en0], st0, en0, re.search(r'href="([^"]*)"', t[st0:en0]).group(1))
            if not found:
                print(f"  !! {path}: 无模板卡"); break
            tpl_card = found[0]
        href = f'/{brand}/blog/{slug}.html' if is_main else f'./{slug}.html'
        bcn, org = ('纳杰', '北京纳杰知识产权代理有限公司') if brand == 'najie' else ('觅理', '北京觅理律师事务所')
        card = build_card(tpl_card, href, title, date, tags, excerpt, bcn, org)
        assert card.count('article-card') == 1, card[:120]
        assert slug in card and date in card and bcn in card
        t = insert_card(t, card, date)
        added += 1
    new_count = t.count('<div class="article-card">')
    opens = len(re.findall(r'<div\b', t)); closes = len(re.findall(r'</div>', t))
    print(f"{os.path.relpath(path, REPO)}: cards {base_count} -> {new_count} (+{added})  div {opens}/{closes}  **={t.count('**')}")
    report.append((path, added))
    if APPLY and added:
        open(path, 'w', encoding='utf-8').write(t)

# ---- articles.json ----
aj = os.path.join(REPO, 'articles.json')
d = json.load(open(aj, encoding='utf-8'))
print('articles.json type', type(d).__name__, 'len', len(d))
if isinstance(d, list):
    have = {x.get('url', '') for x in d}
    new_items = []
    for brand, slug, date, title, tags, excerpt in CARDS:
        url = f'/{brand}/blog/{slug}.html'
        if any(slug in h for h in have):
            continue
        new_items.append({'url': url, 'title': title, 'date': date, 'site': brand})
    print('articles.json new', len(new_items), [x['url'] for x in new_items])
    if APPLY and new_items:
        d2 = d + new_items
        d2.sort(key=lambda x: x.get('date', ''), reverse=True)
        open(aj, 'w', encoding='utf-8').write(json.dumps(d2, ensure_ascii=False, indent=2) + '\n')
        print('articles.json ->', len(d2))
