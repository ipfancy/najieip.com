#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix2-0918.py — ①主索引新卡移到 09-19 卡之后（保持降序）②清理 najie 索引遗留 markdown 泄漏

用法: python3 site-inbox/fix2-0918.py [--apply]
"""
import json
import os
import re
import sys

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
APPLY = "--apply" in sys.argv

SLUG = "20260918-eu-digital-design-three-tables"
TITLE = "游戏界面中国不给专利，欧盟7月1日起能注册"
DESC = ("国内明确排除的游戏界面、纯数字皮肤和转场动画，从2026年7月1日起可在欧盟单独注册。"
        "本文用三张表说清：哪些数字设计现在能在欧盟拿到权利、一套设计稿能否中国/海牙/欧盟三地复用、"
        "以及防抢注的三样反制工具与12个月新颖性宽限窗的换算时点。")
TAGS = ["涉外知识产权", "欧盟外观设计", "海牙体系"]
LABEL = "纳杰知识产权代理有限公司"
log = []


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)


def depth_ok(t):
    body = t[t.find("<body"):]
    d = 0
    for m in re.finditer(r"<(/?)div[^>]*>", body):
        d += -1 if m.group(1) else 1
        if d < 0:
            return False, d
    return d == 0, d


def lds_ok(t):
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        json.loads(blk)


# ---------- ① 主索引：新卡移到第二位 ----------
mp = "blog/index.html"
t = rd(mp)
card = ('<div class="article-card">\n'
        '    <h2><a href="/najie/blog/%s.html">%s</a></h2>\n'
        '    <div class="meta">%s %s · %s</div>\n'
        '    <p>%s</p>\n'
        '  </div>' % (SLUG, TITLE, "".join('<span class="tag">%s</span>' % x for x in TAGS),
                     "2026-09-18", LABEL, DESC))
ins = card + "\n  "
n0 = t.count('<div class="article-card">')
if ins in t and t.count(card) == 1:
    t = t.replace(ins, "", 1)
    log.append("OK   新卡已从首位摘出")
    p1 = t.find('<div class="article-card">')
    p2 = t.find('<div class="article-card">', p1 + 1)
    assert p2 > 0, "找不到第二张卡"
    t = t[:p2] + ins + t[p2:]
    log.append("OK   新卡已插入第二位（09-19 卡之后）")
else:
    log.append("SKIP 主索引新卡位置无需调整 (ins in t=%s count=%d)"
               % (ins in t, t.count(card)))
assert t.count('<div class="article-card">') == n0, "卡片数变化"
d_ok, d = depth_ok(t)
lds_ok(t)
ds = re.findall(r'<div class="meta">(?:<span class="tag">[^<]*</span>)*[^<]*?(\d{4}-\d{2}-\d{2})', t)
mono = all(ds[i] >= ds[i + 1] for i in range(min(3, len(ds) - 1)))
log.append("主索引: depth=%d 卡=%d 顶部日期=%s 单调=%s" % (d, n0, ds[:3], mono))
assert d_ok and mono, "主索引校验失败"
if APPLY:
    wr(mp, t)
    log.append("WRITE %s" % mp)

# ---------- ② najie 索引：清理 wipo 卡遗留 markdown ----------
np = "najie/blog/index.html"
s = rd(np)
CLEAN = ("【编者按】吕国良先生（BMR2004），资深知识产权专家，长期关注国际IP治理与前沿技术交叉领域。"
         "本文为WIPO十二届AI对话会深度综述，以全球视野剖析AI对专利、版权制度的根本性挑战，推荐阅读。")
before = s.count("**")
s2 = re.sub(r'<p>WIPO知识产权与前沿技术对话会：AI如何重塑全球IP治理 — 纳杰觅理 ← 首页[^<]*</p>',
            '<p>%s</p>' % CLEAN, s, count=1)
s2 = re.sub(r'(WIPO知识产权与前沿技术对话会：AI如何重塑全球IP治理\\? )description": "WIPO知识产权与前沿技术对话会[^"]*"',
            r'\1description": "%s"' % CLEAN, s2, count=1)
# JSON-LD 内 description 泛化处理（含转义引号）
s2 = re.sub(r'("description": )"WIPO知识产权与前沿技术对话会[^"]*(?:\\"[^"]*)*"',
            r'\1"%s"' % CLEAN, s2, count=1)
log.append("najie 索引: '**' %d -> %d" % (before, s2.count("**")))
lds_ok(s2)
d_ok2, d2 = depth_ok(s2)
assert d_ok2, "najie 索引 div 不平衡"
assert s2.count('<div class="article-card">') == s.count('<div class="article-card">'), "卡片数变化"
if APPLY:
    wr(np, s2)
    log.append("WRITE %s" % np)

print("\n".join(log))
print("APPLY =", APPLY)
