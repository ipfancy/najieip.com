#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-0918-eu-design.py — 修复 09-18 新文章（欧盟外观设计）+ 补 najie/主索引卡片

用法：
  python3 site-inbox/fix-0918-eu-design.py            # 诊断（不写盘）
  python3 site-inbox/fix-0918-eu-design.py --apply    # 写入
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
DATE = "2026-09-18"
ART_REL = "najie/blog/%s.html" % SLUG
URL = "https://najieip.com/" + ART_REL
IMG = "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200"
KW = "涉外知识产权,欧盟外观设计,出海企业,海牙体系"
DESC = ("国内明确排除的游戏界面、纯数字皮肤和转场动画，从2026年7月1日起可在欧盟单独注册。"
        "本文用三张表说清：哪些数字设计现在能在欧盟拿到权利、一套设计稿能否中国/海牙/欧盟三地复用、"
        "以及防抢注的三样反制工具与12个月新颖性宽限窗的换算时点。")
TAGS = ["涉外知识产权", "欧盟外观设计", "海牙体系"]

log = []


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)


# ---------------- Part 1: 文章页修复 ----------------
p = ART_REL
t = rd(p)
orig_len = len(t)

# 1) 去掉 frontmatter 泄漏
fm = '<p>---</p>\n<p>ai_smell: 10.5</p>\n<p>---</p>\n<br>\n'
if fm in t:
    t = t.replace(fm, "", 1)
    log.append("OK   frontmatter 泄漏已清除")
else:
    log.append("SKIP frontmatter 泄漏未匹配（可能已修）")

# 2) description 富化
old_md = '<meta name="description" content="%s">' % TITLE
if old_md in t:
    t = t.replace(old_md, '<meta name="description" content="%s">' % DESC, 1)
    log.append("OK   meta description 富化")
old_ogd = '<meta property="og:description" content="%s">' % TITLE
if old_ogd in t:
    t = t.replace(old_ogd, '<meta property="og:description" content="%s">' % DESC, 1)
    log.append("OK   og:description 富化")

# 3) twitter card + og:image
if 'content="summary_large_image"' not in t:
    old_tc = '<meta name="twitter:card" content="summary">'
    new_tc = ('<meta name="twitter:card" content="summary_large_image">\n'
              '<meta name="twitter:title" content="%s">\n'
              '<meta name="twitter:description" content="%s">\n'
              '<meta name="twitter:image" content="%s">' % (TITLE, DESC, IMG))
    if old_tc in t:
        t = t.replace(old_tc, new_tc, 1)
        log.append("OK   twitter card 升级 + title/desc/image")
    else:
        log.append("WARN twitter:card 锚点未找到")
if 'property="og:image"' not in t:
    anc = '<link rel="canonical"'
    i = t.find(anc)
    if i > 0:
        t = t[:i] + '<meta property="og:image" content="%s">\n' % IMG + t[i:]
        # 把新增的 og:image 上移到 canonical 之后的原位置（保持在 head 内即可）
        log.append("OK   og:image 已加")

# 4) JSON-LD（Article + BreadcrumbList）
article_ld = {
    "@context": "https://schema.org", "@type": "Article", "headline": TITLE,
    "description": DESC, "image": IMG,
    "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师",
               "affiliation": {"@type": "Organization", "name": "爱普纳杰 · 觅理 · 纳杰"}},
    "publisher": {"@type": "Organization", "name": "北京纳杰知识产权代理有限公司",
                  "url": "https://najieip.com/najie/"},
    "mainEntityOfPage": URL, "url": URL,
    "datePublished": DATE, "dateModified": DATE, "inLanguage": "zh-CN", "keywords": KW,
}
crumb_ld = {
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "纳杰博客", "item": "https://najieip.com/najie/blog/"},
        {"@type": "ListItem", "position": 3, "name": TITLE},
    ],
}
if '"@type": "Article"' not in t:
    blk = ('<script type="application/ld+json">\n%s\n</script>\n'
           '<script type="application/ld+json">\n%s\n</script>\n'
           % (json.dumps(article_ld, ensure_ascii=False),
              json.dumps(crumb_ld, ensure_ascii=False)))
    t = t.replace("</head>", blk + "</head>", 1)
    log.append("OK   Article + BreadcrumbList JSON-LD 已加")

# 5) 尾部 markdown 泄漏清理
i = t.find("<p class=\"disclaimer\">")
if i < 0:
    m = re.search(r'<p>\*本文仅代表作者个人观点[^<]*\*</p>', t)
    if m:
        t = t[:m.start()] + '<p class="disclaimer">' + m.group(0)[3:-4].replace("*", "") + '</p>' + t[m.end():]
        log.append("OK   免责声明去 * 号 + disclaimer class")
    else:
        log.append("SKIP 免责声明未匹配")
# 合集行（已转义注释）整行删除
m = re.search(r'\n?<p>&lt;!--\s*合集[^\n]*?--&gt;</p>', t)
if m:
    t = t[:m.start()] + t[m.end():]
    log.append("OK   合集标记行已删除")

# 6) 文章页校验
assert t.count("https://schema.org") >= 2, "schema.org 缺失"
assert t.count("https://***") == 0, "schema 被脱敏污染"
assert t.count("**") == 0, "markdown ** 泄漏"
assert "ai_smell" not in t, "frontmatter 仍泄漏"
assert "合集" not in t, "合集行仍存在"
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    json.loads(blk)
log.append("OK   文章页校验：ld 块 %d 个可解析 / schema.org %d 处 / ** 0"
           % (t.count('application/ld+json'), t.count('https://schema.org')))

if APPLY:
    wr(p, t)
    log.append("WRITE %s (%d -> %d chars)" % (p, orig_len, len(t)))


# ---------------- Part 2: 索引卡片 ----------------
def newest_najie_card_html():
    """从主索引里取一张 najie 卡，用作格式参照"""
    t = rd("blog/index.html")
    m = re.search(r'<div class="article-card">\s*<h2><a href="(/najie/blog/[^"]+)"[^>]*>.*?</div>\s*</div>', t, re.S)
    return m.group(0) if m else None


def insert_into_array(t, entry):
    """把 entry 插到 blogPost 数组首位（锚点只到 [）"""
    key = '"blogPost": ['
    k = t.find(key)
    if k < 0:
        return t, False
    if entry["url"] in t:
        return t, False
    i = k + len(key)
    return t[:i] + json.dumps(entry, ensure_ascii=False) + ", " + t[i:], True


entry = {"@type": "BlogPosting", "headline": TITLE, "url": URL,
         "datePublished": DATE, "description": DESC}

# --- najie 品牌索引 ---
np = "najie/blog/index.html"
nt = rd(np)
n_card = ('<div class="article-card">\n'
          '    <h2><a href="./%s.html">%s</a></h2>\n'
          '    <div class="meta">%s · 北京纳杰知识产权代理有限公司</div>\n'
          '    <p>%s</p>\n'
          '  </div>' % (SLUG, TITLE, DATE, DESC))
n_before = nt.count('<div class="article-card">')
if SLUG in nt:
    log.append("SKIP najie 索引已有该卡")
else:
    pos = nt.find('<div class="article-card">')
    assert pos > 0, "najie 索引无卡片锚点"
    nt2 = nt[:pos] + n_card + "\n\n  " + nt[pos:]
    nt2, ok = insert_into_array(nt2, entry)
    log.append("OK   najie 索引插卡 + blogPost %s" % ("已插" if ok else "跳过"))
    # 校验
    assert nt2.count('<div class="article-card">') == n_before + 1
    body = nt2[nt2.find("<body"):]
    depth = 0
    for tag in re.findall(r"<(/?)div[^>]*>", body):
        depth += -1 if tag == "/" else 1
        assert depth >= 0, "div 栈空仍闭合"
    assert depth == 0, "div 未配平 depth=%d" % depth
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', nt2, re.S):
        json.loads(blk)
    assert nt2.count("https://***") == 0
    if APPLY:
        wr(np, nt2)
        log.append("WRITE %s (%d -> %d cards)" % (np, n_before, nt2.count('<div class="article-card">')))

# --- 主索引 ---
mp = "blog/index.html"
mt = rd(mp)
ref = newest_najie_card_html()
label = "纳杰知识产权代理有限公司"
if ref:
    m = re.search(r'<div class="meta">(.*?)&#?\w*;?\s*(\d{4}-\d{2}-\d{2})', ref, re.S)
    if m and "·" in m.group(1):
        label = m.group(1).split("·")[-1].strip() or label
m_card = ('<div class="article-card">\n'
          '    <h2><a href="/%s">%s</a></h2>\n'
          '    <div class="meta">%s %s · %s</div>\n'
          '    <p>%s</p>\n'
          '  </div>' % (ART_REL, TITLE, "".join('<span class="tag">%s</span>' % x for x in TAGS),
                       DATE, label, DESC))
m_before = mt.count('<div class="article-card">')
print("REF najmäcard meta label =", repr(label))
if SLUG in mt:
    log.append("SKIP 主索引已有该卡")
else:
    pos = mt.find('<div class="article-card">')
    assert pos > 0, "主索引无卡片锚点"
    mt2 = mt[:pos] + m_card + "\n  " + mt[pos:]
    mt2, ok = insert_into_array(mt2, entry)
    log.append("OK   主索引插卡 + blogPost %s" % ("已插" if ok else "跳过"))
    assert mt2.count('<div class="article-card">') == m_before + 1
    body = mt2[mt2.find("<body"):]
    depth = 0
    for tag in re.findall(r"<(/?)div[^>]*>", body):
        depth += -1 if tag == "/" else 1
        assert depth >= 0, "div 栈空仍闭合"
    assert depth == 0, "div 未配平 depth=%d" % depth
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', mt2, re.S):
        json.loads(blk)
    assert mt2.count("https://***") == 0
    assert mt2.count("**") == 0
    if APPLY:
        wr(mp, mt2)
        log.append("WRITE %s (%d -> %d cards)" % (mp, m_before, mt2.count('<div class="article-card">')))

print("\n".join(log))
print("APPLY =", APPLY)
