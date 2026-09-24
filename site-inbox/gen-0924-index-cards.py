#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 索引补卡：mili/blog/index.html（相对 href + blogPost JSON-LD 首插）
                        blog/index.html（绝对 href）
日期 2026-09-24 > 两索引当前首卡（mili 09-22 / main 09-23）→ 均插首位
用法: python3 site-inbox/gen-0924-index-cards.py [--apply]
"""
import os, re, json, sys, subprocess, collections

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
APPLY = "--apply" in sys.argv

SLUG = "20260924-malicious-litigation-supervision"
TITLE = "被碰瓷式维权告了？最高检6月29日5案：5步把案子翻过来"
DESC = ("最高检 6 月 29 日发布 5 件惩治知识产权恶意诉讼典型案例：从上市受理 12 天即被索赔 2300 万、"
        "抗诉后原告倒赔 40 万的专利碰瓷，到权利基础已失效仍申请执行、批量维权、抢注囤货、抢注公共资源，"
        "本文拆解 5 种手法与 5 步反制路径，并给出企业起诉前的三条自检。")
TAGS = ["知识产权恶意诉讼", "最高检典型案例", "检察监督"]
DATE = "2026-09-24"


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)


def card(rel, href):
    tags = "".join('<span class="tag">%s</span>' % x for x in TAGS)
    return ('<div class="article-card">\n'
            '    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · 觅理律师事务所</div>\n'
            '    <p>%s</p>\n'
            '  </div>' % (href, TITLE, tags, DATE, DESC))


def depth_hist(t):
    """按 <body 起算 div 深度直方图 + depth==1 的 article-card 数（基线校准用）"""
    b = t[t.find("<body"):]
    depth = 0
    hist = collections.Counter()
    card_depth = None
    for m in re.finditer(r"<(/?)div\b([^>]*)>", b):
        closing = m.group(1) == "/"
        if not closing:
            hist[depth] += 1
            if 'class="article-card"' in m.group(2):
                card_depth = depth
            depth += 1
        else:
            depth -= 1
    return depth, dict(hist), card_depth


print("=== 基线校准（ORIGIN 版深度直方图）===")
for idx in ["mili/blog/index.html", "blog/index.html"]:
    origin = subprocess.run(["git", "show", "origin/main:%s" % idx],
                            capture_output=True, text=True).stdout
    d, h, cd = depth_hist(origin)
    print("  %s: end_depth=%d card_depth=%s hist=%s" % (idx, d, cd, h))

print("\n=== 修改 ===")
results = {}

# ---------- mili/blog/index.html ----------
p = "mili/blog/index.html"
t = rd(p)
assert SLUG not in t, "mili 索引已含该文"
c = card(p, "./%s.html" % SLUG)
anchor = "<!-- 财产守护系列 -->\n  "
occ = [m.start() for m in re.finditer(re.escape(anchor), t)]
assert occ, "锚点缺失"
pos = occ[0]          # 首次出现 = 系列起始标签（33798 处为遗留的重复注释，不在此插）
t2 = t[:pos] + c + "\n  " + t[pos:]
assert t2.replace(c + "\n  ", "", 1) == t, "插入块之外被改动"
results[p] = (t, t2, c)

# 同步 blogPost JSON-LD 首插
entry = {"@type": "BlogPosting", "headline": TITLE,
         "url": "https://najieip.com/mili/blog/%s.html" % SLUG,
         "datePublished": DATE, "description": DESC}
t2 = t2.replace('"blogPost": [', '"blogPost": [' + json.dumps(entry, ensure_ascii=False) + ", ", 1)
blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', t2, re.S)
j = json.loads(blocks[0])
print("  mili blogPost: %d -> %d，首条=%s" % (
    len(json.loads(re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', t, re.S)[0])["blogPost"]),
    len(j["blogPost"]), j["blogPost"][0]["@type"]))
assert j["blogPost"][0]["headline"] == TITLE, "blogPost 首条不对"
results[p] = (t, t2, c)

# ---------- blog/index.html ----------
p2 = "blog/index.html"
t = rd(p2)
assert SLUG not in t, "主索引已含该文"
c2 = card(p2, "/mili/blog/%s.html" % SLUG)
anchor2 = '<div class="container">\n  '
assert t.count(anchor2) == 1
t2b = t.replace(anchor2, anchor2 + c2 + "\n  ", 1)
assert t2b.replace(c2 + "\n  ", "") == t, "主索引插入块之外被改动"
results[p2] = (t, t2b, c2)

print("\n=== 终验 ===")
ok = True
for p, (t, t2, c) in results.items():
    print("--- %s" % p)
    n0 = t.count('<div class="article-card">')
    n1 = t2.count('<div class="article-card">')
    print("  卡片数 %d -> %d (%s)" % (n0, n1, "PASS" if n1 == n0 + 1 else "FAIL"))
    ok &= (n1 == n0 + 1)
    d1 = depth_hist(t2)
    print("  div 深度归零: end=%d %s | card_depth=%s" % (d1[0], "PASS" if d1[0] == 0 else "FAIL", d1[2]))
    ok &= (d1[0] == 0)
    # 每卡以 <h2><a href= 起
    b = t2[t2.find('<div class="container"'):]
    malformed = 0
    for m in re.finditer(r'<div class="article-card">', b):
        seg = b[m.end():m.end() + 120]
        if not re.match(r'\s*<h2><a href=', seg):
            malformed += 1
            print("  malformed:", repr(seg[:90]))
    print("  malformed=%d %s" % (malformed, "PASS" if malformed == 0 else "FAIL"))
    ok &= (malformed == 0)
    # 同 URL 重复卡
    dup = [u for u, n in collections.Counter(re.findall(r'<h2><a href="([^"]+)"', t2)).items() if n > 1]
    print("  重复 href: %d %s" % (len(dup), "PASS" if not dup else "FAIL " + str(dup[:3])))
    ok &= (not dup)
    # 插入点前缀降序
    cards = re.findall(r'<div class="article-card">.{0,1400}?(\d{4}-\d{2}-\d{2})', b, re.S)
    idx_new = cards.index(DATE)
    prefix = cards[:idx_new]
    mono = all(prefix[i] >= prefix[i + 1] for i in range(len(prefix) - 1))
    print("  插入点前缀降序: %s (前缀 %s)" % ("PASS" if mono else "FAIL", prefix[:5]))
    ok &= mono
    print("  新卡是首卡: %s" % ("PASS" if cards[0] == DATE else "FAIL"))
    ok &= (cards[0] == DATE)
    print("  ** 泄漏: %d | schema.org: %d | ***: %d" % (t2.count("**"), t2.count("https://schema.org"), t2.count("https://***")))

print("\n综合:", "PASS" if ok else "FAIL")
if not ok:
    sys.exit(1)
if APPLY:
    for p, (t, t2, c) in results.items():
        wr(p, t2)
        print("已写入", p, len(t2.encode()), "B")
else:
    print("(--dry-run)")
