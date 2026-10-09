#!/usr/bin/env python3
"""fix-1009-siteops.py — 修复 20261009 mili AI短剧页缺陷 + 双索引补卡
用法: python3 fix-1009-siteops.py [--apply]
"""
import os, re, sys, json, html as htmllib

BASE = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv

SLUG = "20261009-mili-ai-short-drama-token-evidence"
TITLE = "AI短剧被整部搬走只赔2万，这3样证据你留了吗"
URL = "https://najieip.com/mili/blog/%s.html" % SLUG
DATE = "2026-10-09"
DESC = ("武汉江岸区法院在一起AI短剧侵权案中，首次把创作时烧掉的词元（Token）算力成本、"
        "以及购买商用AI工具的费用计入赔偿。47集AI短剧被改名后整部搬运到自家视频号，判赔2万元。"
        "本文拆解法院认定「视听作品」的三个创作环节，把法官点名的留痕要求翻译成创作人今天就能做的"
        "三层证据清单——权属与构思、生成过程、发布与成本凭证；并以北京两起AI文生图案对比"
        "「当时存」与「事后补」的天差地别，附广州盗录1700余部AI短剧已入刑的警示。")
KEYWORDS = "AI短剧,视听作品,著作权,词元成本,AI生成内容权属,侵权赔偿,创作留痕,版权保护"

TARGET = os.path.join(BASE, "mili/blog/%s.html" % SLUG)
TMPL = os.path.join(BASE, "mili/blog/20261008-mili-ai-math-solution-copyright.html")
TMPL_SLUG = "20261008-mili-ai-math-solution-copyright"

def load(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def save(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)

# ---------- 1. 修 head ----------
t = load(TARGET)
tt = load(TMPL)
t_orig = t
og_image = re.search(r'<meta property="og:image" content="([^"]*)"', tt).group(1)
site_name = "觅理律师事务所"

# description / og:description 换成真摘要
t = re.sub(r'<meta name="description" content="[^"]*">',
           '<meta name="description" content="%s">' % DESC, t, count=1)
t = re.sub(r'<meta property="og:description" content="[^"]*">',
           '<meta property="og:description" content="%s">' % DESC, t, count=1)
t = re.sub(r'<meta name="og:description"[^>]*>', '', t)  # no-op guard

# title 保留；追加缺失 head 标签
extra = []
extra.append('<meta name="keywords" content="%s">' % KEYWORDS)
extra.append('<meta property="og:site_name" content="%s">' % site_name)
extra.append('<meta property="og:image" content="%s">' % og_image)
extra.append('<meta name="twitter:card" content="summary_large_image">')
extra.append('<meta name="twitter:title" content="%s">' % TITLE)
extra.append('<meta name="twitter:description" content="%s">' % DESC)
# 删旧 twitter:card summary
t = re.sub(r'<meta name="twitter:card" content="summary">', '', t, count=1)

ld_article = {
    "@context": "https://schema.org", "@type": "Article",
    "headline": TITLE, "description": DESC,
    "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师",
               "worksFor": {"@type": "LegalService", "name": "北京觅理律师事务所",
                            "url": "https://najieip.com/mili/"}},
    "publisher": {"@type": "Organization", "name": "北京觅理律师事务所"},
    "image": og_image, "datePublished": DATE, "dateModified": DATE,
    "mainEntityOfPage": URL, "url": URL,
}
ld_crumb = {
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
        {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL},
    ],
}
blocks = "".join('\n<script type="application/ld+json">%s</script>'
                 % json.dumps(x, ensure_ascii=False) for x in (ld_article, ld_crumb))
extra.append(blocks)

t = t.replace("</head>", "".join("\n" + e for e in extra) + "\n</head>", 1)

# 断言：body 部分零改动
assert t[t.find("<body"):] == t_orig[t_orig.find("<body"):], "BODY CHANGED!"
# 断言：每个 ld+json 块 json.loads 通过
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    json.loads(m)
assert t.count('**') == 0

print("[page] %s: %d chars -> %d chars" % (SLUG, len(t_orig), len(t)))
print("[page] ld+json=%d og:image=%d h1=%d" % (
    t.count("application/ld+json"), t.count('property="og:image"'),
    len(re.findall(r"<h1[ >]", t))))
if APPLY:
    save(TARGET, t)

# ---------- 2. 补索引卡 ----------
def extract_card(text, key):
    """div 深度配对法提取包含 key 的 article-card 块"""
    i = 0
    while True:
        i = text.find('<div class="article-card">', i)
        if i < 0:
            return None
        # 找块结束
        depth = 0
        j = i
        while j < len(text):
            if text.startswith("<div", j):
                depth += 1
                j += 4
            elif text.startswith("</div>", j):
                depth -= 1
                j += 6
                if depth == 0:
                    break
            else:
                j += 1
        block = text[i:j]
        if key in block:
            return block
        i = j

def build_card(tmpl_block, href, title, desc, date, tags):
    c = tmpl_block
    # href 替换（保留相对/绝对形式）
    c = re.sub(r'(<h2><a href=")[^"]*(")', lambda m: m.group(1) + href + m.group(2), c, count=1)
    # 标题
    c = re.sub(r'(<h2><a href="[^"]*">)[^<]*(</a></h2>)', lambda m: m.group(1) + title + m.group(2), c, count=1)
    # tag span 组整段替换
    taghtml = "".join('<span class="tag">%s</span>' % x for x in tags)
    c2, n = re.subn(r'(?:\s*<span class="tag">[^<]*</span>)+', taghtml, c, count=1)
    if n:
        c = c2
    # 摘要 p（第一个 <p>...</p>）
    c = re.sub(r'<p>.*?</p>', '<p>%s</p>' % desc, c, count=1, flags=re.S)
    # 日期
    c = re.sub(r'\d{4}-\d{2}-\d{2}', date, c, count=1)
    return c

def insert_card(text, card, newdate, anchor_hint=None):
    """按日期降序插到第一张日期 < newdate 的卡之前；否则插到 container 后"""
    pos = None
    for m in re.finditer(r'<div class="article-card">', text):
        blk_start = m.start()
        # 该卡日期
        seg = text[blk_start:blk_start+3000]
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
        if dm and dm.group(1) < newdate:
            pos = blk_start
            break
    if pos is None:
        # 没有更旧的卡 → 插到 container 之后第一个卡前，或 container 后
        cm = re.search(r'<div class="container">\s*', text)
        pos = cm.end() if cm else text.find("<body")
        # 找到 container 后第一个卡
        fc = text.find('<div class="article-card">', cm.end() if cm else 0)
        if fc != -1:
            pos = fc
    t2 = text[:pos] + card + "\n  " + text[pos:]
    return t2

for path, keyprefix, brandkey in [
        (os.path.join(BASE, "mili/blog/index.html"), TMPL_SLUG, "mili"),
        (os.path.join(BASE, "blog/index.html"), TMPL_SLUG, "main")]:
    it = load(path)
    if SLUG in it:
        print("[index] %s: already has card, skip" % os.path.relpath(path, BASE))
        continue
    tmpl_block = extract_card(it, TMPL_SLUG)
    if tmpl_block is None:
        print("[index] %s: TEMPLATE CARD NOT FOUND" % path)
        continue
    rel_href = "./%s.html" % SLUG
    abs_href = "/mili/blog/%s.html" % SLUG
    href = rel_href if brandkey == "mili" else abs_href
    tags = KEYWORDS.split(",")[:3]
    card = build_card(tmpl_block, href, TITLE, DESC, DATE, tags)
    print("\n--- %s template card (first 400 chars) ---" % brandkey)
    print(tmpl_block[:400])
    print("--- new card (first 400 chars) ---")
    print(card[:400])
    n_card = len(re.findall(r'<div class="article-card">', card))
    assert n_card == 1, "card block malformed: %d article-card divs" % n_card
    t2 = insert_card(it, card, DATE)
    # 断言：只插入 card+\n
    if t2.replace(card + "\n  ", "", 1) != it:
        print("[index] %s: OUTER MUTATION ASSERT FAILED" % path)
        continue
    assert t2.count('<div class="article-card">') == it.count('<div class="article-card">') + 1
    for m in re.findall(r'<h2><a href="([^"]+)"', card):
        pass
    print("[index] %s: %d -> %d cards" % (os.path.relpath(path, BASE),
          it.count('<div class="article-card">'), t2.count('<div class="article-card">')))
    if APPLY:
        save(path, t2)

print("\nAPPLY=%s" % APPLY)
