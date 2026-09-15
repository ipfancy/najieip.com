#!/usr/bin/env python3
"""SiteOps 0915 结构修复：主 blog/index.html 的两处历史缺陷（ddc6661 起）。

缺陷1（20300 附近）：`<div class="article-card">` 连续出现两次 —— 一个是孤儿包裹层，
   同时「光伏侵权=出局」卡片的开标签丢失（该卡片直接以 <h2> 开始）。
   成因：早期补卡脚本插入时把开标签切进相邻标签（与本次 v1 同类 bug）。
   修复：删掉重复开标签 + 在建卡 h2 前补回开标签（开合数量不变，配平不受影响）。
缺陷2：同一 URL 挂两张卡 —— shierwu-ip-exports-455yi-2026 另有旧标题
   「知识产权十五五规划解读：未来五年IP行业五大风向」（文章已改名为 455亿版）→ 删除旧卡。
用法：python3 fix-0915-index-structure.py [--apply]
"""
import re
import sys

IDX = 'blog/index.html'
APPLY = '--apply' in sys.argv
t = open(IDX, encoding='utf-8').read()
orig = t

# ---------- 缺陷1a：删掉重复的开标签 ----------
dup = '<div class="article-card">\n  <div class="article-card">\n    <h2><a href="/najie/blog/shangbiao-xuzhan-banli-2026.html">'
fix1a = '<div class="article-card">\n    <h2><a href="/najie/blog/shangbiao-xuzhan-banli-2026.html">'
assert t.count(dup) == 1, f'dup-open pattern count={t.count(dup)}'
t = t.replace(dup, fix1a)

# ---------- 缺陷1b：给光伏卡补回开标签 ----------
missing = '</p>\n  </div>\n\n    <h2><a href="/aipunajie/blog/20260821-pv-ip-compliance-checklist.html">'
fix1b = '</p>\n  </div>\n\n  <div class="article-card">\n    <h2><a href="/aipunajie/blog/20260821-pv-ip-compliance-checklist.html">'
assert t.count(missing) == 1, f'missing-open pattern count={t.count(missing)}'
t = t.replace(missing, fix1b)

# ---------- 缺陷2：删掉同 URL 的旧标题重复卡 ----------
stale = re.search(
    r'  <div class="article-card">\n    <h2><a href="/najie/blog/shierwu-ip-exports-455yi-2026\.html">知识产权十五五规划解读：未来五年IP行业五大风向</a></h2>'
    r'.*?\n  </div>\n', t, flags=re.S)
assert stale, 'stale duplicate card not found'
removed = stale.group(0)
t = t[:stale.start()] + t[stale.end():]
print('removed stale card block, %d chars' % len(removed))
print('  title:', re.search(r'<h2><a[^>]*>([^<]*)', removed).group(1))


def scan(x):
    b = x[x.find('<body'):]
    d = 0
    anom = []
    for m in re.finditer(r'<(/?)div\b[^>]*>', b):
        if m.group(1) == '/' and d == 0:
            anom.append(m.start())
        d += -1 if m.group(1) == '/' else 1
    return d, anom


print('\n-- before:', 'depth/anom', scan(orig), 'markers', orig.count('<div class="article-card">'))
print('-- after :', 'depth/anom', scan(t), 'markers', t.count('<div class="article-card">'))
nested = t.count('<div class="article-card">\n  <div class="article-card">') + t.count('<div class="article-card">\r\n')
bad = [b[:70] for b in re.findall(r'<div class="article-card">\n(.*?)\n  </div>', t, flags=re.S)
       if not b.lstrip().startswith('<h2><a href=')]
print('-- nested-card patterns:', nested, '| cards not starting with h2:', len(bad))

if not APPLY:
    print('\n[DRY RUN]')
    sys.exit(0)

open(IDX, 'w', encoding='utf-8').write(t)

# ---------- 终验 ----------
v = open(IDX, encoding='utf-8').read()
b = v[v.find('<body'):]
cards = re.findall(r'<div class="article-card">\n(.*?)\n  </div>', v, flags=re.S)
print('\n=== VERIFY ===')
print('markers:', v.count('<div class="article-card">'), '| parsed cards:', len(cards),
      '| all start with h2:', all(c.lstrip().startswith('<h2><a href=') for c in cards))
print('div depth/anomalies:', scan(v))
print('stray **:', v.count('**'), '| corrupt schema:', v.count('https://***'))
dates = [m.group(1) for m in re.finditer(r'(\d{4}-\d{2}-\d{2}) · ', v)]
print('dated cards:', len(dates), 'monotonic desc:', all(x >= y for x, y in zip(dates, dates[1:])),
      '|', dates[0], '→', dates[-1])
print('dup href shierwu:', v.count('href="/najie/blog/shierwu-ip-exports-455yi-2026.html"'))
print('15 new cards still present:',
      all(v.count(f'href="{p}"') == 1 for p in
          ['/mili/blog/20260914-pangdonglai-trainee-labor-contract.html',
           '/mili/blog/20260910-unfair-competition-nine-red-lines.html',
           '/najie/blog/20260901-copyright-jp18-compliance-checklist.html']))
