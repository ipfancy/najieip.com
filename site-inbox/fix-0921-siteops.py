#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-0921-siteops.py — 2026-09-21 晚间运营修复

问题（诊断所得）：
  1) najie/blog/20260921-us-trademark-sanction-defense-window.html 为上游裸发布：
     无 <style>（整页无样式）、无 h1、无 JSON-LD、无 og:image/keywords、
     meta description == 标题、保留 frontmatter 后的合集/检索词注释行。
     而该文在 articles.json 中位于首页 slice(0,6) 第 3 位 → 首页曝光位正在展示畸形页。
  2) 该文未进任何索引（najie 品牌索引 + 主索引均无卡片）。
  3) 主索引缺 2 张真缺口卡片（09-09 批次补发的 querren-buqinquan-zhisu-2026 / xin-shangbiaofa-2027）。

用法：
  python3 site-inbox/fix-0921-siteops.py          # dry-run（打印计划，不写盘）
  python3 site-inbox/fix-0921-siteops.py --apply  # 写盘
"""
import json
import os
import re
import shutil
import sys
from collections import Counter

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
APPLY = "--apply" in sys.argv
BAK = "-0921"
log = []


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)


def att(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ============================ 常量 ============================
SLUG = "20260921-us-trademark-sanction-defense-window"
ART_REL = "najie/blog/%s.html" % SLUG
URL = "https://najieip.com/" + ART_REL
TITLE = "商标还显示'已注册'？美国12连发，10月1日前只剩一扇窗"
OG_TITLE = TITLE
DATE = "2026-09-21"
IMG = "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200"
KEYWORDS = "美国商标被撤销,USPTO制裁,商标显示已注册,美国商标代理资质,涉外知识产权,海外维权"
DESC = ("USPTO 在 9 月 1 日合并令（In re Trademark Emergent, et al.）脚注中写明：注册被重开审理期间，"
        "系统因技术限制可能继续显示「已注册」——状态绿不等于安全。近一年美国制裁令几乎每月一发，"
        "单案曾一次性终止超 52,000 件。2026 年 10 月 1 日是合并令申辩截止日，商标权人须走 Petition to Director "
        "表单提交证据。本文讲清三类中枪画像、免费的国家海外维权网络，以及出海前必须自己做的三件事。")
CARD_DESC = ("USPTO 9 月 1 日合并令脚注写明：注册被重开审理期间，系统可能仍显示「已注册」——状态绿不等于安全。"
             "10 月 1 日是申辩截止日，须走 Petition to Director 表单并附证据。本文讲清三类中枪画像、"
             "免费的国家海外维权网络，与出海前必须自己做的三件事。")
H2S = [
    "一、一年 12 道制裁令：中枪的三类画像",
    "二、眼前这扇窗：10 月 1 日前必须走对渠道",
    "三、免费的靠山，和出海前必须自己做的三件事",
    "四、今晚就可以做的一件事",
]
# 每个 h2 之前的内容段落索引（0-based，共 10 段）
H2_BEFORE = [3, 6, 7, 9]

# ============================ Part 1: 文章页重建 ============================
p = ART_REL
cur = rd(p)
art = cur[cur.find("<article>") + len("<article>"): cur.rfind("</article>")]
paras = re.findall(r"<p>(.*?)</p>", art, re.S)
content = []
for x in paras:
    s = x.strip()
    if not s or "&lt;!--" in s or s.startswith("*本文仅代表") or s.startswith("何自刚 |"):
        continue
    content.append(s)
log.append("INFO 原文提取：<p> 共 %d 个 → 正文段落 %d 段" % (len(paras), len(content)))
assert len(content) == 10, "正文段落数异常: %d" % len(content)

# 保真校验：与 markdown 源逐段比对
MD = os.path.expanduser("~/wiki/digital-employees/articles/%s.md" % SLUG)
if os.path.exists(MD):
    md = rd(MD)
    mdbody = md.split("---", 2)[-1]
    md_paras = []
    for blk in [b.strip() for b in mdbody.split("\n\n")]:
        if not blk or blk.startswith("<!--") or blk.startswith("*本文仅代表") or blk.startswith("何自刚 |"):
            continue
        md_paras.append(re.sub(r"\s+", " ", blk))
    def norm(s):
        s = s.replace("&#x27;", "'").replace("&quot;", '"').replace("&amp;", "&").replace("&middot;", "·")
        s = re.sub(r"<[^>]+>", "", s)
        return re.sub(r"\s+", " ", s).strip()
    built = [norm(c_) for c_ in content]
    miss = [mp for mp in md_paras if mp not in built]
    log.append("CHECK md 源段落 %d 段 → 未在页面出现 %d 段" % (len(md_paras), len(miss)))
    for m_ in miss:
        log.append("      MISS-MD: " + m_[:60])
    assert not miss, "正文与 md 源不一致"

# 房屋样式：CSS + 导航 + 页脚 取自同日同品牌已精修页
REF = "najie/blog/20260921-trademark-renewal-lapse-ten-years.html"
ref = rd(REF)
css = re.search(r"<style>(.*?)</style>", ref, re.S).group(1)
refnav = re.search(r"<nav>.*?</nav>", ref, re.S).group(0)
_f = re.search(r"<footer>.*?</footer>", ref, re.S) or re.search(r"<footer>.*?</footer>", cur, re.S)
reffoot = _f.group(0)
beacon = re.search(r"<script defer src='https://static\.cloudflareinsights.*?</script>", ref, re.S).group(0)

article_ld = {
    "@context": "https://schema.org", "@type": "Article", "headline": OG_TITLE,
    "description": DESC,
    "author": {"@type": "Person", "name": "何自刚"},
    "publisher": {"@type": "Organization", "name": "北京纳杰知识产权代理有限公司"},
    "image": IMG, "datePublished": DATE, "dateModified": DATE, "inLanguage": "zh-CN",
    "keywords": KEYWORDS, "mainEntityOfPage": URL, "url": URL,
}
crumb_ld = {
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "博客", "item": "https://najieip.com/najie/blog/"},
        {"@type": "ListItem", "position": 3, "name": OG_TITLE},
    ],
}

body_parts = [refnav, "<article>", "<h1>%s</h1>" % TITLE,
              '<p class="byline">纳杰知识产权 &middot; 原创</p>']
prev = 0
for i, cp in enumerate(content):
    if i in H2_BEFORE:
        body_parts.append('<h2>%s</h2>' % H2S[H2_BEFORE.index(i)])
    body_parts.append("<p>%s</p>" % cp)
body_parts += [
    "<hr>",
    "<p>010-65150974 / 13911268604</p>",
    "<p>何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰</p>",
    "<p><em>本文仅代表作者个人观点，不构成法律意见。</em></p>",
    "</article>", reffoot,
]

new = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s — 纳杰觅理</title>
<style>%s</style>
<meta name="description" content="%s">
<meta name="keywords" content="%s">
<meta property="og:type" content="article">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:site_name" content="纳杰知识产权">
<meta property="og:image" content="%s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%s">
<link rel="canonical" href="%s">
%s
<script type="application/ld+json">
%s
</script>
<script type="application/ld+json">
%s
</script>
</head>
<body>
%s
</body>
</html>
""" % (TITLE, css, att(DESC), att(KEYWORDS), att(OG_TITLE), att(DESC), URL, IMG,
       att(OG_TITLE), att(DESC), IMG, URL, beacon,
       json.dumps(article_ld, ensure_ascii=False),
       json.dumps(crumb_ld, ensure_ascii=False),
       "\n".join(body_parts))

# 校验
assert new.count("https://schema.org") == 2, "schema.org 数量异常"
assert "https://***" not in new, "schema 脱敏污染"
assert new.count("**") == 0, "markdown ** 泄漏"
assert new.count("ai_smell") == 0, "frontmatter 泄漏"
assert "合集" not in new and "检索词块" not in new, "注释行残留"
assert new.count("<h1>") == 1 and new.count("</h1>") == 1, "h1 数量异常"
assert new.count("<h2>") == len(H2S), "h2 数量异常"
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', new, re.S):
    json.loads(blk)
d = 0
bd = new[new.find("<body"):]
for t in re.findall(r"<(/?)div[^>]*>", bd):
    d += -1 if t == "/" else 1
    assert d >= 0, "div 栈空闭合"
assert d == 0, "div 未配平 %d" % d
log.append("OK  文章页重建：%d B → %d B（h1×1 h2×%d ld×2 ** 0）" % (len(cur), len(new), len(H2S)))

if APPLY:
    shutil.copy(p, p + BAK)
    wr(p, new)

# ============================ Part 2: najie 品牌索引 ============================
np = "najie/blog/index.html"
nt = rd(np)
n_card = ('<div class="article-card">\n'
          '    <h2><a href="./%s.html">%s</a></h2>\n'
          '    <div class="meta">%s · 北京纳杰知识产权代理有限公司</div>\n'
          '    <p>%s</p>\n'
          '  </div>\n  ' % (SLUG, TITLE, DATE, CARD_DESC))
n_before = nt.count('<div class="article-card">')
if SLUG in nt:
    log.append("SKIP najie 索引已含该 slug")
else:
    pos = nt.find('<div class="article-card">')
    assert pos > 0
    nt2 = nt[:pos] + n_card + nt[pos:]
    # blogPost 数组头部插入
    key = '"blogPost": ['
    k = nt2.find(key)
    assert k > 0, "najie 索引无 blogPost 数组"
    entry = {"@type": "BlogPosting", "headline": TITLE, "url": URL,
             "datePublished": DATE, "description": CARD_DESC}
    i = k + len(key)
    nt2 = nt2[:i] + json.dumps(entry, ensure_ascii=False) + ", " + nt2[i:]
    assert nt2.count('<div class="article-card">') == n_before + 1
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', nt2, re.S):
        json.loads(blk)
    log.append("OK  najie 索引插卡 + blogPost 条目（%d → %d 卡）" % (n_before, n_before + 1))
    if APPLY:
        shutil.copy(np, np + BAK)
        wr(np, nt2)

# ============================ Part 3: 主索引补卡 ============================
mp = "blog/index.html"
mt = rd(mp)


def card_block(href, title, tags, date, label, desc):
    taghtml = "".join('<span class="tag">%s</span>' % t for t in tags)
    return ('<div class="article-card">\n'
            '    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta">%s%s · %s</div>\n'
            '    <p>%s</p>\n'
            '  </div>\n  ' % (href, title, taghtml, date, label, desc))


INSERT = [
    card_block("/najie/blog/%s.html" % SLUG, TITLE, ["美国商标", "USPTO制裁", "涉外知识产权"],
               DATE, "纳杰知识产权", CARD_DESC),
    card_block("/mili/blog/querren-buqinquan-zhisu-2026.html",
               "收到侵权警告函别慌：确认不侵权之诉9月1日新规",
               ["确认不侵权之诉", "著作权", "侵权警告函"], "2026-09-09", "觅理律师事务所",
               "法释〔2026〕18号2026年9月1日施行：确认不侵害著作权纠纷案件正式纳入著作权侵权纠纷受案范围，"
               "被警告企业可以主动起诉确认不侵权。附企业收到警告函后的4步走清单、被动应对vs主动确认不侵权对比表，"
               "以及什么情况下能提起的6个高频问答。"),
    card_block("/najie/blog/xin-shangbiaofa-2027.html",
               "新商标法2027年施行：恶意抢注囤积严打，企业做对5件事",
               ["商标抢注", "商标法修订", "商标新法2027"], "2026-09-09", "纳杰知识产权",
               "《商标法》（2026年修订）经国家主席令第七十七号公布，2027年1月1日施行：恶意抢注、囤积商标不予注册，"
               "驰名商标跨类保护扩大，动态标志可注册。附企业趁施行前要做的5件事、旧法vs新法对比表，"
               "以及商标已被抢注的三条处理路径。"),
]


def insert_date_desc(t, card, date, tag):
    """按日期降序插位：插到第一张日期 < date 的卡之前（每轮重扫，绝不复用偏移）"""
    body_start = t.find("<body")
    pos_dates = []
    for m in re.finditer(r'<div class="article-card">', t[body_start:]):
        s = body_start + m.start()
        nxt = t.find('<div class="article-card">', s + 10)
        seg = t[s:nxt if nxt > 0 else s + 1500]
        dm = re.search(r"<div class=\"meta\">.*?(\d{4}-\d{2}-\d{2})", seg, re.S)
        if dm:
            pos_dates.append((s, dm.group(1)))
    anchor = None
    for s, d_ in pos_dates:
        if d_ < date:
            anchor = s
            break
    assert anchor, "%s: 找不到插入锚点" % tag
    return t[:anchor] + card + t[anchor:], pos_dates


m_before = mt.count('<div class="article-card">')
if all(x in mt for x in ["/najie/blog/%s.html" % SLUG, "querren-buqinquan-zhisu-2026", "xin-shangbiaofa-2027"]):
    log.append("SKIP 主索引三张卡已齐")
    mt2 = mt
else:
    mt2 = mt
    for card, date, tag in [(INSERT[0], DATE, "us-trademark"),
                            (INSERT[1], "2026-09-09", "querren"),
                            (INSERT[2], "2026-09-09", "xin-shangbiaofa")]:
        if tag == "us-trademark" and "/najie/blog/%s.html" % SLUG in mt2:
            continue
        if tag != "us-trademark" and tag in mt2:
            continue
        mt2, pds = insert_date_desc(mt2, card, date, tag)
        log.append("OK  主索引插卡 %s（date=%s）→ 卡数 %d" % (tag, date, mt2.count('<div class="article-card">')))
    assert mt2.count('<div class="article-card">') == m_before + len(INSERT), "卡片数不符"

    # 结构终验
    bd = mt2[mt2.find("<body"):]
    depth = 0
    underflow = 0
    dd2 = 0
    for m in re.finditer(r"<(/?)div[^>]*>", bd):
        if m.group(1) == "/":
            if depth == 0:
                underflow += 1
            else:
                depth -= 1
        else:
            depth += 1
            if depth == 2 and bd[m.start():m.start() + 31].startswith('<div class="article-card"'):
                dd2 += 1
    n_cards = bd.count('<div class="article-card"')
    assert depth == 0, "div 深度未归零 %d" % depth
    assert underflow == 0, "栈空闭合 %d" % underflow
    assert dd2 == n_cards, "depth=2 卡片 %d != 卡片总数 %d" % (dd2, n_cards)
    hrefs = re.findall(r'<h2><a href="([^"]+)"', bd)
    dups = {h: c for h, c in Counter(hrefs).items() if c > 1}
    assert not dups, "href 重复 %s" % list(dups)[:3]
    assert bd.count("**") == 0, "** 泄漏"
    malformed = [s for s in re.finditer(r'<div class="article-card">', bd)
                 if not bd[s.end():s.end() + 60].lstrip().startswith("<h2><a href=")]
    assert not malformed, "卡片非以 h2 起 %d" % len(malformed)
    log.append("OK  主索引终验：卡 %d / depth 0 / depth2 卡 %d / href 唯一 / 无 **" % (n_cards, dd2))
    if APPLY:
        shutil.copy(mp, mp + BAK)
        wr(mp, mt2)

print("\n".join(log))
print("APPLY =", APPLY)
