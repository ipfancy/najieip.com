#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 facts.html 权威口径提取 + EN/FR 页 schema.org 完整性核验"""
import os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

t = open('facts.html', encoding='utf-8').read()
body = t[t.find('<body'):]
txt = re.sub(r'<script.*?</script>', '', body, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', '\n', txt)
lines = [l.strip() for l in txt.split('\n') if l.strip()]
print('=== facts.html 正文(%d 行) ===' % len(lines))
for l in lines:
    print(l)

print('\n=== schema.org 完整性（须全为 0 个 ***） ===')
for f in ['facts.html', 'en/mili/index.html', 'fr/mili/index.html',
          'en/aipunajie/index.html', 'fr/aipunajie/index.html',
          'mili/index.html', 'index.html']:
    b = open(f, encoding='utf-8').read()
    print('%-28s schema.org=%d  "https://***"=%d  ld+json=%d' %
          (f, b.count('https://schema.org'), b.count('https://***'), b.count('application/ld+json')))
