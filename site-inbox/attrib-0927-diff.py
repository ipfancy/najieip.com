#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 今日提交页面线上 DIFF 逐行归因（只允许 CF 注入）"""
import os, difflib, urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
FILES = ['about.html', 'credentials.html', 'facts.html', 'index.html',
         'aipunajie/index.html', 'mili/index.html', 'najie/index.html']

ALLOWED = ('email-protection', '__cf_email__', 'email-decode.min.js',
           'beacon.min.js', 'static.cloudflareinsights.com')

def get(url):
    req = urllib.request.Request(url + '?cb=%d' % os.getpid(),
                                 headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

for f in FILES:
    local = open(f, encoding='utf-8').read()
    live = get('https://najieip.com/' + f)
    d = [l for l in difflib.unified_diff(local.splitlines(), live.splitlines(), lineterm='', n=0)
         if l[0] in '+-' and not l.startswith(('---', '+++'))]
    bad = [l for l in d if not any(a in l for a in ALLOWED)]
    print('%-24s diff=%3d  非CF注入行=%d' % (f, len(d), len(bad)))
    for l in bad[:6]:
        print('     ', l[:180])
