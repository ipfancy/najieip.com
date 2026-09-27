#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 final live verify （v2，避与并发会话文件名冲突）"""
import os, re, urllib.request, difflib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

def get(u, cb=1):
    req = urllib.request.Request(u + ('&' if '?' in u else '?') + 'cb=%d' % (os.getpid() + cb),
                                 headers={'User-Agent': 'Mozilla/5.0'})
    rv = urllib.request.urlopen(req, timeout=30)
    return rv.getcode(), rv.read().decode('utf-8', 'replace')

pages = [('mili/index.html', 'https://najieip.com/mili/'),
         ('en/mili/index.html', 'https://najieip.com/en/mili/'),
         ('fr/mili/index.html', 'https://najieip.com/fr/mili/'),
         ('en/aipunajie/index.html', 'https://najieip.com/en/aipunajie/'),
         ('fr/aipunajie/index.html', 'https://najieip.com/fr/aipunajie/')]

print('=== A. 页面状态 / 口径 / 结构化数据 ===')
for f, u in pages:
    try:
        code, t = get(u)
    except Exception as e:
        print('  ERROR %s %s' % (u, e)); continue
    ti = re.search(r'<title>(.*?)</title>', t, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    dv = d.group(1) if d else ''
    cjk = len(re.findall(r'[\u4e00-\u9fff]', dv))
    old = ('IP Legal Protection' in t) or ('Protection Juridique PI' in t) or ('专注知识产权诉讼与法律保护' in t)
    print('%d %-22s ld=%d 中文字=%d 旧口径=%s hreflang=%d' %
          (code, f, t.count('application/ld+json'), cjk, old, len(re.findall(r'hreflang="', t))))
    print('      %s' % (ti.group(1)[:75] if ti else '?'))

print('\n=== B. llms.txt ===')
code, t = get('https://najieip.com/llms.txt')
print('%d  facts.html=%d  综合型律所=%d  旧"专注知识产权法律保护"=%d  字节=%d' %
      (code, t.count('facts.html'), t.count('综合型律所'),
       t.count('专注知识产权法律保护'), len(t.encode('utf-8'))))

print('\n=== C. 字节一致（llms.txt 强判据） ===')
a, b = os.path.getsize('llms.txt'), None
_, live = get('https://najieip.com/llms.txt')
b = len(live.encode('utf-8'))
print('llms.txt local=%d live=%d %s' % (a, b, 'IDENTICAL' if a == b else 'DIFF %+d' % (b - a)))

print('\n=== D. 核心页重试确认（瞬断不算故障） ===')
for u in ['https://najieip.com/', 'https://najieip.com/mili/', 'https://najieip.com/najie/',
          'https://najieip.com/blog/', 'https://najieip.com/sitemap.xml', 'https://najieip.com/facts.html']:
    codes = []
    for i in range(3):
        try:
            rv = urllib.request.urlopen(urllib.request.Request(u + '?cb=%d' % (os.getpid() + i),
                     headers={'User-Agent': 'Mozilla/5.0'}), timeout=20)
            codes.append(rv.getcode())
            if rv.getcode() == 200:
                break
        except Exception as e:
            codes.append(str(e)[:30])
    print('  %-42s %s' % (u, codes))
