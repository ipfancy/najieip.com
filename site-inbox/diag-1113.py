#!/usr/bin/env python3
# 每日巡检：当日新文六项判据 + 双索引卡 + 正文 md 包含
import re, os, sys, json, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
MD_DIR = "/Users/ziganghe/wiki/digital-employees/articles"
SLUG = "20261113-byd-netherlands-evidence-seizure"
BRAND = "mili"

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

p = os.path.join(REPO, BRAND, "blog", SLUG + ".html")
t = rd(p)
print("=== 页面 ===", p, os.path.getsize(p), "B")

ld = len(re.findall(r'application/ld\+json', t))
types = re.findall(r'"@type":\s*"([^"]+)"', t)
h1 = len(re.findall(r'<h1[ >]', t))
h2 = len(re.findall(r'<h2[ >]', t))
ogimg = re.findall(r'property="og:image" content="([^"]*)"', t)
ogtitle = re.findall(r'property="og:title" content="([^"]*)"', t)
twname = re.findall(r'name="twitter:title" content="([^"]*)"', t)
kw = re.findall(r'name="keywords" content="([^"]*)"', t)
desc = re.findall(r'<meta name="description" content="([^"]*)"', t)
title = re.findall(r'<title>(.*?)</title>', t, re.S)
stars = len(re.findall(r'\*\*', t))
naked_tbl = len(re.findall(r'<p>\|', t))
style = ('<style>' in t) or ('/style.css' in t)
canon = re.findall(r'rel="canonical" href="([^"]*)"', t)

print("style:", style, "| h1:", h1, "| h2:", h2, "| ld:", ld, types)
print("og:image:", ogimg[:1])
print("og:title len:", [len(x) for x in ogtitle], "| tw:title:", [len(x) for x in twname], "| keywords:", bool(kw))
print("desc len:", [len(x) for x in desc])
print("title:", title[:1])
print("desc==title复读:", bool(desc and title and desc[0].strip() == re.sub(r'\s*—.*$', '', title[0]).strip()))
print("stars(**):", stars, "| 裸表<p>|:", naked_tbl)
print("canonical:", canon)

# 正文 md 包含
mds = [os.path.join(MD_DIR, SLUG + ".md")]
mdp = next((m for m in mds if os.path.exists(m)), None)
print("md源:", mdp)
if mdp:
    md = rd(mdp)
    md = re.sub(r'^---.*?---\s*', '', md, flags=re.S)
    def norm(s):
        s = re.sub(r'<h1.*?</h1>|<h2.*?</h2>', ' ', s, flags=re.S)
        s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
        s = re.sub(r'<[^>]+>', ' ', s)
        s = s.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"')
        for ch in '“”"「」『』【】、:,：|*#-— 　\n\t':
            s = s.replace(ch, '')
        s = re.sub(r'-{3,}', '', s)
        s = re.sub(r'\d+\.', '', s)
        return s
    # md 侧：丢掉小标题行
    kept = []
    for line in md.split('\n'):
        ls = line.strip()
        if not ls: continue
        if ls.startswith('#'): continue
        if re.fullmatch(r'\*\*[^*]{1,30}\*\*', ls) and not ls.rstrip('*').endswith(('。', '！', '？')): continue
        if re.match(r'^[一二三四五六七八九十]、', ls): continue
        if ls.startswith('<!--') or ls.startswith('何自刚 |'): continue
        kept.append(ls)
    mdn = norm('\n'.join(kept))
    body = t[t.find('<article'):]
    body = body[:body.find('</article>')] if '</article>' in body else body
    pgn = norm(body)
    BYLINE = norm('何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰')
    mdn2 = mdn.replace(BYLINE, '')
    pgn2 = pgn.replace(BYLINE, '')
    print("md归一 len:", len(mdn2), "| page归一 len:", len(pgn2), "| md_contained:", mdn2 in pgn2 or pgn2.startswith(mdn2[:200]))
    if mdn2 not in pgn2:
        # 找首个差异
        i = 0
        while i < min(len(mdn2), len(pgn2)) and mdn2[i] == pgn2[i]:
            i += 1
        print("  diff_at:", i, "md:", repr(mdn2[max(0,i-40):i+60]), "| pg:", repr(pgn2[max(0,i-40):i+60]))

# 双索引卡
for name, idx in [("mili", f"{REPO}/mili/blog/index.html"), ("main", f"{REPO}/blog/index.html")]:
    s = rd(idx)
    cards = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(SLUG), s))
    raw = len(re.findall(re.escape(SLUG), s))
    print(f"索引[{name}] 卡数:{cards} raw命中:{raw}")
# 昨日文复核
for slug2, br in [("20261112-maldives-trademark-law", "najie")]:
    p2 = f"{REPO}/{br}/blog/{slug2}.html"
    if os.path.exists(p2):
        t2 = rd(p2)
        print(f"复核 {slug2}: size={os.path.getsize(p2)} h1={len(re.findall(r'<h1[ >]',t2))} ld={len(re.findall(r'application/ld.json',t2))} og:image={bool(re.findall(chr(34)+'og:image'+chr(34),t2))} stars={len(re.findall(r'[*][*]',t2))}")
