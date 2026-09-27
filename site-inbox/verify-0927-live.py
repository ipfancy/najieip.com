#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 线上/本地字节 DIFF 归因 + 今日提交涉及页面的部署核验"""
import os, re, subprocess, difflib, urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

def get(url):
    req = urllib.request.Request(url + ('&' if '?' in url else '?') + 'cb=%d' % os.getpid(),
                                 headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

# 1) facts.html DIFF 归因
local = open('facts.html', encoding='utf-8').read()
live = get('https://najieip.com/facts.html')
d = list(difflib.unified_diff(local.splitlines(), live.splitlines(), lineterm='', n=0))
print('facts.html diff 行数:', len(d))
for line in d[:12]:
    print('   ', line[:200])

# 2) 今日提交 (de4a62c, 844d6e5) 涉及的站点文件
files = subprocess.run(['git', 'show', '--name-only', '--format=', '844d6e5'],
                       capture_output=True, text=True).stdout.split()
files += subprocess.run(['git', 'show', '--name-only', '--format=', 'de4a62c'],
                        capture_output=True, text=True).stdout.split()
files = [f for f in dict.fromkeys(files) if f.endswith('.html') and os.path.exists(f)]
print('\n=== 今日提交涉及 HTML %d 个 ===' % len(files))
for f in files:
    url = 'https://najieip.com/' + f
    try:
        rv = urllib.request.urlopen(urllib.request.Request(url + '?cb=%d' % os.getpid(),
             headers={'User-Agent': 'Mozilla/5.0'}), timeout=30)
        code, body = rv.getcode(), rv.read().decode('utf-8', 'replace')
    except Exception as e:
        print('  %-40s ERROR %s' % (f, e)); continue
    lb = os.path.getsize(f)
    rvb = len(body.encode('utf-8'))
    same = 'IDENTICAL' if lb == rvb else 'DIFF %+d' % (rvb - lb)
    # facts.html 关键内容是否上线
    key = ''
    if f == 'facts.html':
        key = ' | 含"觅理"=%d 含"爱普纳杰"=%d 含"纳杰"=%d 电话=%d' % (
            body.count('觅理'), body.count('爱普纳杰'), body.count('纳杰'), body.count('65150974'))
    print('  %-40s %d %8dB %-12s%s' % (f, code, lb, same, key))
