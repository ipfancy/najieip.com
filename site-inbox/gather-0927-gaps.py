#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 缺口扫描：三品牌索引 vs 主 blog/index.html（href 归一比对）
判据：品牌索引卡片 href 归一到 /<brand>/blog/<file> 后，文件名字符串是否出现在主索引全文。
剔除：stub（size<1500B / meta refresh）、架构图页（ld=0 且无文章日期）。
输出：missing-cards-0927.json"""
import os, re, json, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

IDX = {
    'aipunajie': 'blog/index.html',          # 主索引自身，跳过
    'mili': 'mili/blog/index.html',
    'najie': 'najie/blog/index.html',
}

main = open('blog/index.html', encoding='utf-8').read()

rows = []
for brand, rel in IDX.items():
    if brand == 'aipunajie':
        continue
    t = open(rel, encoding='utf-8').read()
    base_dir = '/' + brand + '/blog'
    # 卡片 href
    hrefs = re.findall(r'<h2><a href="([^"]+)"', t)
    seen = []
    for h in hrefs:
        if h.startswith('./'):
            key = base_dir + '/' + h[2:]
        elif h.startswith('/'):
            key = h
        elif h.startswith('http'):
            continue
        else:
            key = base_dir + '/' + h
        fname = key.rsplit('/', 1)[-1].split('?')[0].split('#')[0]
        if not fname.endswith('.html') or fname == 'index.html':
            continue
        if key in seen:
            continue
        seen.append(key)
    print('[%s] 卡片 href 归一 %d 条' % (brand, len(seen)))
    for key in seen:
        local = key.lstrip('/')
        if not os.path.exists(local):
            rows.append(dict(brand=brand, path=key, file=local, reason='file_not_found'))
            continue
        body = open(local, encoding='utf-8').read()
        if len(body.encode('utf-8')) < 1500 or 'http-equiv="refresh"' in body:
            rows.append(dict(brand=brand, path=key, file=local, reason='stub'))
            continue
        ld = body.count('application/ld+json')
        has_date = bool(re.search(r'\d{4}-\d{2}-\d{2}', body))
        if ld == 0 and not has_date:
            rows.append(dict(brand=brand, path=key, file=local, reason='non_article_page'))
            continue
        fname = local.rsplit('/', 1)[-1]
        if fname not in main:
            rows.append(dict(brand=brand, path=key, file=local, reason='missing_in_main_index'))

json.dump(rows, open('site-inbox/missing-cards-0927.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n=== 结果 ===')
by = {}
for r in rows:
    by.setdefault(r['reason'], []).append(r)
for k, v in by.items():
    print('%s: %d' % (k, len(v)))
    for r in v[:20]:
        print('   ', r['brand'], r['file'])
if not rows:
    print('无缺口')
