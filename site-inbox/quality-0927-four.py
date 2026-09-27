#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 「房屋样式四件」质检：articles.json 首页 slice(0,6) + 近 4 天新增文章页
四联判据（同时成立=裸发布畸形页）：h1==0 且 ld+json==0 且 无 og:image 且 meta description==标题复读
双房屋写法：'<style>' in t 或 (含 /style.css 链接且该文件存在)
"""
import os, re, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

d = json.load(open('articles.json', encoding='utf-8'))
arts = d['articles'] if isinstance(d, dict) else d
arts.sort(key=lambda x: x.get('date', ''), reverse=True)
targets = [a['url'].lstrip('/') for a in arts[:6]]

import subprocess
recent = subprocess.run(['find', 'blog', 'mili/blog', 'najie/blog', '-name', '*.html',
                         '-mtime', '-4', '-not', '-name', 'index.html'],
                        capture_output=True, text=True).stdout.split()
targets += [f for f in recent if f not in targets]

print('=== 质检 %d 页 ===' % len(targets))
for f in targets:
    if not os.path.exists(f):
        print('  %-70s FILE MISSING' % f); continue
    t = open(f, encoding='utf-8').read()
    h1 = t.count('<h1')
    ld = t.count('application/ld+json')
    ogi = 'og:image' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ''
    tm = re.search(r'<title>(.*?)</title>', t, re.S)
    title = (tm.group(1).split('|')[0].strip() if tm else '')
    style = ("<style" in t) or (("/style.css" in t) and os.path.exists("style.css"))
    malformed = (h1 == 0 and ld == 0 and not ogi and desc.strip() == title.strip())
    flag = '❌畸形' if malformed else ('⚠️ 可疑' if (h1 == 0 or ld == 0) else '✅')
    print('  %s %-68s h1=%d ld=%d og:img=%s style=%s desc=%d' %
          (flag, f, h1, ld, ogi, style, len(desc)))
