#!/usr/bin/env python3
# 校验：md 全文（归一）完整包含于页面正文；div 配平；索引/线上
import re, os, sys
REPO = "/Users/ziganghe/wiki/najieip-verify"
MD = "/Users/ziganghe/wiki/digital-employees/articles/20261113-byd-netherlands-evidence-seizure.md"
SLUG = "20261113-byd-netherlands-evidence-seizure"
P = f"{REPO}/mili/blog/{SLUG}.html"

md = open(MD, encoding="utf-8").read()
md = re.sub(r'^---.*?---\s*', '', md, flags=re.S)
t = open(P, encoding="utf-8").read()

BYLINE = '何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰'

def norm(s, drop_titles=True):
    if drop_titles:
        s = re.sub(r'<h1.*?</h1>|<h2.*?</h2>', ' ', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&nbsp;', ' ')
    for a, b in [('&amp;', '&'), ('&gt;', '>'), ('&lt;', '<'), ('&quot;', '"')]:
        s = s.replace(a, b)
    for ch in '“”"「」『』【】、:,：|*#-— 　\n\t':
        s = s.replace(ch, '')
    s = re.sub(r'-{3,}', '', s)
    s = re.sub(r'\d+\.', '', s)
    return s

kept = []
for line in md.split('\n'):
    ls = line.strip()
    if not ls: continue
    if ls.startswith('#'): continue
    if re.fullmatch(r'\*\*[^*]{1,30}\*\*', ls) and not ls.rstrip('*').endswith(('。', '！', '？')): continue
    if re.match(r'^[一二三四五六七八九十]、', ls): continue
    if ls.startswith('<!--'): continue
    if ls.strip('*') .startswith(BYLINE): continue
    kept.append(ls)

mdn = norm('\n'.join(kept), drop_titles=False).replace(norm(BYLINE), '')
art = t[t.find('<article'):]
art = art[:art.find('</article>')]
pgn = norm(art).replace(norm(BYLINE), '')
print("md_norm len:", len(mdn), "| page_norm len:", len(pgn), "| md_contained:", mdn in pgn)
if mdn not in pgn:
    i = 0
    while i < min(len(mdn), len(pgn)) and mdn[i] == pgn[i]: i += 1
    print("  diff_at:", i, "\n  md:", repr(mdn[max(0,i-50):i+60]), "\n  pg:", repr(pgn[max(0,i-50):i+70]))

print("h1:", len(re.findall(r'<h1[ >]', t)), "h2:", len(re.findall(r'<h2[ >]', t)),
      "ld:", len(re.findall(r'application/ld\+json', t)), "og:image:", bool(re.search(r'property="og:image" content="https', t)))
print("stars:", t.count('**'), "naked_tbl:", len(re.findall(r'<p>\|', t)), "size:", os.path.getsize(P))
op, cl = t.count('<div'), t.count('</div>')
print("div:", op, "/", cl, "balanced:", op == cl)
print("canonical ok:", f'rel="canonical" href="{f"https://najieip.com/mili/blog/{SLUG}.html"}"' in t)
print("desc len:", len(re.findall(r'<meta name="description" content="([^"]*)"', t)[0]))
