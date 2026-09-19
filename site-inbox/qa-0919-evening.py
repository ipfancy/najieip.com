#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-19 晚间新页质检（线上抓取，纯 stdlib）
检查: HTTP状态 / h1 数 / og:title,og:image,og:description,twitter:card / canonical /
      ld+json 合法性与 schema.org / markdown 泄漏 ** / frontmatter 泄漏 ---
"""
import re, json, sys, urllib.request

URLS = [
    'https://najieip.com/mili/blog/wangluo-jishu-zhichi-kaishe-duchangzui-2026.html',
    'https://najieip.com/mili/blog/20260919-offer-to-sell-three-rules.html',
    'https://najieip.com/najie/blog/nongye-pinpai-ip-buju-2026.html',
    'https://najieip.com/mili/blog/20260918-personality-rights-injunction.html',
    'https://najieip.com/najie/blog/20260918-eu-digital-design-three-tables.html',
    'https://najieip.com/najie/gaoqi-selfcheck.html',
    'https://najieip.com/blog/',
    'https://najieip.com/mili/blog/',
    'https://najieip.com/najie/blog/',
]


def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 siteops-qa'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode('utf-8', 'replace')


rows = []
for u in URLS:
    try:
        st, t = get(u)
    except Exception as e:
        rows.append({'url': u, 'http': 'ERR', 'err': str(e)[:80]})
        continue
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ld_ok = 0
    ld_bad = []
    for b in ld:
        try:
            json.loads(b)
            ld_ok += 1
        except Exception as e:
            ld_bad.append(str(e)[:60])
    rows.append({
        'url': u, 'http': st,
        'h1': len(re.findall(r'<h1', t)),
        'og_title': bool(re.search(r'property="og:title"', t)),
        'og_desc_len': len((re.search(r'property="og:description" content="([^"]*)"', t) or type('x', (), {'group': lambda s, i: ''})()).group(1)),
        'og_image': bool(re.search(r'property="(og:image|twitter:image)"', t)),
        'twitter_card': (re.search(r'name="twitter:card" content="([^"]*)"', t) or type('x', (), {'group': lambda s, i: ''})()).group(1),
        'canonical': bool(re.search(r'rel="canonical"', t)),
        'ld_blocks': len(ld), 'ld_valid': ld_ok, 'ld_err': ld_bad,
        'schema_org': t.count('https://schema.org'), 'placeholder_hash': t.count('https://***'),
        'md_leak': t.count('**'), 'frontmatter': t.startswith('---') or '\n---\ntitle:' in t,
        'bytes': len(t.encode('utf-8')),
    })

bad = []
for r in rows:
    issues = []
    if r.get('http') != 200:
        issues.append('http=%s' % r.get('http'))
    if r.get('h1') not in (1, None) and '/blog/' not in r['url'].rstrip('/')[-6:]:
        issues.append('h1=%s' % r.get('h1'))
    if r.get('og_title') is False:
        issues.append('no og:title')
    if r.get('og_image') is False:
        issues.append('no og:image')
    if r.get('canonical') is False:
        issues.append('no canonical')
    if r.get('ld_valid', 0) != r.get('ld_blocks', 0):
        issues.append('bad ldjson %s' % r.get('ld_err'))
    if r.get('placeholder_hash'):
        issues.append('*** placeholder')
    if r.get('md_leak'):
        issues.append('md leak ** x%d' % r['md_leak'])
    if r.get('frontmatter'):
        issues.append('frontmatter leak')
    if issues:
        bad.append((r['url'], issues))

for r in rows:
    print('%-72s %s h1=%s og=%s tw=%s ld=%s/%s schema=%s **=%s %sB' % (
        r['url'][:72], r.get('http'), r.get('h1'), r.get('og_title'), r.get('twitter_card'),
        r.get('ld_valid'), r.get('ld_blocks'), r.get('schema_org'), r.get('md_leak'), r.get('bytes')))
print('\n=== 问题页 ===')
if not bad:
    print('none')
for u, i in bad:
    print(u, '->', '; '.join(i))
json.dump(rows, open('/Users/ziganghe/wiki/najieip-verify/site-inbox/qa-0919-evening.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
