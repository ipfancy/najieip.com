#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 最终 QA：今日两个 commit 涉及的全站页面 200 + 房屋四件 + 实体口径抽查"""
import os, re, urllib.request, subprocess, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

def get(u, cb=0):
    req = urllib.request.Request(u + ('&' if '?' in u else '?') + 'cb=%d' % (os.getpid() + cb),
                                 headers={'User-Agent': 'Mozilla/5.0'})
    rv = urllib.request.urlopen(req, timeout=30)
    return rv.getcode(), rv.read().decode('utf-8', 'replace')

files = subprocess.run(['git', 'show', '--name-only', '--format=', 'de4a62c'],
                       capture_output=True, text=True).stdout.split()
files += subprocess.run(['git', 'show', '--name-only', '--format=', '75cc5e5'],
                        capture_output=True, text=True).stdout.split()
files += ['llms.txt', 'mili/index.html', 'en/mili/index.html', 'fr/mili/index.html',
          'en/aipunajie/index.html', 'fr/aipunajie/index.html', 'facts.html']
files = [f for f in dict.fromkeys(files) if os.path.exists(f) and f.endswith('.html')]

print('=== 今日变更页面线上 QA（%d 页） ===' % len(files))
bad = []
for f in files:
    try:
        code, t = get('https://najieip.com/' + f)
    except Exception as e:
        print('  ERR %-42s %s' % (f, str(e)[:40])); bad.append(f); continue
    h1 = t.count('<h1'); ld = t.count('application/ld+json')
    ogi = 'og:image' in t
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    ti = re.search(r'<title>(.*?)</title>', t, re.S)
    rep = (d and ti and d.group(1).strip() == ti.group(1).split('|')[0].strip() and len(d.group(1)) < 60)
    style = ('<style' in t) or ('/style.css' in t)
    ok = (h1 == 1) and (ld >= 1) and ogi and (not rep)
    print('  %s %-42s %d h1=%d ld=%d og:img=%s 复读=%s' %
          ('✅' if ok else '❌', f, code, h1, ld, ogi, rep))
    if not ok:
        bad.append(f)

print('\n结论：%d/%d 页合格；异常 %s' % (len(files) - len(bad), len(files), bad if bad else '无'))

# 实体口径抽查（AI 讲错的根因面）
print('\n=== 实体口径抽查（三主体 5 个核心页） ===')
for f in ['index.html', 'facts.html', 'about.html', 'najie/index.html', 'aipunajie/index.html']:
    try:
        _, t = get('https://najieip.com/' + f, cb=7)
    except Exception as e:
        print('  ERR', f, e); continue
    print('  %-24s 独立法人/独立机构=%d  综合型=%d  部门=%d  崇文门外=%d  宝钢大厦=%d' %
          (f, t.count('独立法人') + t.count('独立机构'), t.count('综合型'), t.count('内设部门'),
           t.count('崇文门外'), t.count('宝钢大厦')))
