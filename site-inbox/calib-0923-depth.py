#!/usr/bin/env python3
# 对比 origin 版本 vs 修改版本的 div 深度分布，校准 depth 判据
import os, re, subprocess
os.chdir(os.path.expanduser('~/wiki/najieip-verify'))

def analyze(t, name):
    body = t[t.find('<body'):]
    depth = 0
    hist = {}
    ok = True
    for m in re.finditer(r'<(/?)div\b[^>]*>', body):
        tag = m.group(0)
        if tag.startswith('</'):
            depth -= 1
            if depth < 0:
                ok = False
        else:
            hist[(depth, 'article-card' if tag.startswith('<div class="article-card"') else tag.split('class="')[1].split('"')[0] if 'class="' in tag else '<div>')] = \
                hist.get((depth, 'article-card' if tag.startswith('<div class="article-card"') else tag.split('class="')[1].split('"')[0] if 'class="' in tag else '<div>'), 0) + 1
            depth += 1
    print(f"\n--- {name}: final depth={depth} balanced={ok}")
    for k, v in sorted(hist.items()):
        if v > 3 or k[1] == 'article-card':
            print(f"    depth={k[0]:<2} {k[1]:<28} x{v}")
    return body

cur = open('blog/index.html', encoding='utf-8').read()
base = subprocess.run(['git','show','origin/main:blog/index.html'], capture_output=True, text=True).stdout
analyze(base, 'ORIGIN (unmodified)')
analyze(cur, 'CURRENT (with inserts)')

print("\n=== first 8 div tags in ORIGIN body ===")
b = base[base.find('<body'):]
for m in list(re.finditer(r'<div\b[^>]*>', b))[:8]:
    print("   ", m.group(0)[:80])
