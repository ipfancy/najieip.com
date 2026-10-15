#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-15 — 修复 mili 新页（部分裸发布）+ 补双索引卡
用法: python3 fix-1015-page.py        # dry-run
      python3 fix-1015-page.py --apply
"""
import os, re, sys, json, copy, shutil, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
APPLY = "--apply" in sys.argv

SLUG = "20261015-ip-4-hard-deadlines-buju-revision"
TITLE = "4个知识产权硬时限速查：有一条15日今天作废了"
URL = "https://najieip.com/mili/blog/%s.html" % SLUG
PAGE = os.path.join(REPO, "mili/blog/%s.html" % SLUG)
TPL = os.path.join(REPO, "mili/blog/patent-vs-trade-secret-layering-2026.html")
DATE = "2026-10-15"
ORG = "北京觅理律师事务所"
TAGS = ["政策解读", "专利实务", "时限"]

DESC = ("2026年10月15日《集成电路布图设计保护条例》修订版施行，旧条例“自收到处理通知之日起15日内起诉”"
        "被删去，改为“可以依法向人民法院起诉”。本文用一张表捋清4个知识产权硬时限的起算点与法条依据："
        "商标驳回15日申请复审、30日起诉（商标法第34条）；专利驳回3个月请求复审、3个月起诉（专利法第41条）；"
        "药品专利纠纷45日（专利法第76条＋2021年第89号公告）；布图设计起诉改按842号条例。附版本对照，"
        "提醒即将施行的商标法2026修订（2027年1月1日起施行）会整体重排条号，避免收藏到过期表。")

print("=== 0. 前置检查 ===")
tpl = open(TPL, encoding="utf-8").read()
print("  template ok:", os.path.basename(TPL))
print("  图片候选:")
for f in sorted(os.listdir(os.path.join(REPO, "img")))[-12:]:
    print("    img/" + f)
cover = os.path.expanduser("~/wiki/digital-employees/articles/cover-%s.png" % SLUG)
print("  cover 源存在:", os.path.exists(cover), os.path.getsize(cover) if os.path.exists(cover) else "")
print("  目标 img/%s.png 已存在: %s" % (SLUG, os.path.exists(os.path.join(REPO, "img/%s.png" % SLUG))))
# 检查同日/近期品牌页是否使用 <br>
for f in ("mili/blog/patent-vs-trade-secret-layering-2026.html",
          "mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
          "mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html",
          "najie/blog/20261014-trademark-pattern-packaging-confusion.html"):
    p = os.path.join(REPO, f)
    s = open(p, encoding="utf-8").read()
    print("  %-58s <br>=%d" % (f, s.count("<br>")))

t = open(PAGE, encoding="utf-8").read()
orig = t
print("  目标页 bytes=%d  <br>=%d" % (len(t.encode()), t.count("<br>")))

# ---------- 1. 正文文本（用于不改一字断言） ----------
def body_text(html):
    b = html[html.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", b)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()

bt_before = body_text(orig)

# ---------- 2. head 重建 ----------
head_end = t.find("</head>") + 7
head = t[:head_end]

def set_meta(h, attr, key, value):
    pat = r'<meta\s+%s="%s"\s+content="[^"]*">' % (attr, re.escape(key))
    new = '<meta %s="%s" content="%s">' % (attr, key, value)
    if re.search(pat, h):
        return re.sub(pat, new.replace("\\", "\\\\"), h, count=1), "replaced"
    return None, "missing"

# description / og:description 替换为真摘要
m = re.search(r'<meta\s+name="description"\s+content="[^"]*">', head)
assert m, "no description tag"
head = head[:m.start()] + '<meta name="description" content="%s">' % DESC + head[m.end():]
m = re.search(r'<meta\s+property="og:description"\s+content="[^"]*">', head)
assert m, "no og:description"
head = head[:m.start()] + '<meta property="og:description" content="%s">' % DESC + head[m.end():]
# twitter:card -> summary_large_image
head = re.sub(r'<meta\s+name="twitter:card"\s+content="[^"]*">',
              '<meta name="twitter:card" content="summary_large_image">', head, count=1)

IMG = "https://najieip.com/img/%s.png" % SLUG
add = []
add.append('<meta name="keywords" content="%s">' % ",".join(TAGS + ["知识产权时限", "商标法2026修订", "布图设计保护条例"]))
add.append('<meta property="og:site_name" content="%s">' % ORG)
add.append('<meta property="og:image" content="%s">' % IMG)
add.append('<meta name="twitter:title" content="%s">' % TITLE)
add.append('<meta name="twitter:description" content="%s">' % DESC)
add.append('<meta name="twitter:image" content="%s">' % IMG)
block = "\n".join(add) + "\n"

# JSON-LD（deepcopy 模板对象，逐字段覆写）
lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S)
art = json.loads(lds[0])
bc = json.loads(lds[1])
art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMG
art["datePublished"] = DATE
art["dateModified"] = DATE
art["mainEntityOfPage"] = URL
art["url"] = URL
bc["itemListElement"][2]["name"] = TITLE
bc["itemListElement"][2]["item"] = URL
ld_html = ('<script type="application/ld+json">%s</script>\n'
           '<script type="application/ld+json">%s</script>\n'
           % (json.dumps(art, ensure_ascii=False), json.dumps(bc, ensure_ascii=False)))

# 插到 </head> 之前
head2 = head.replace("</head>", block + ld_html + "</head>", 1)
assert head2 != head
t2 = head2 + t[head_end:]

# ---------- 3. 校验 ----------
def qa_check(s, label):
    b = s[s.find("<body"):]
    chk = {
        "h1": len(re.findall(r"<h1[ >]", s)),
        "ld": s.count("application/ld+json"),
        "og:image": s.count('property="og:image"'),
        "twitter:image": s.count('name="twitter:image"'),
        "stars": b.count("**"),
        "raw_table": len(re.findall(r"<p>\s*\|", b)),
        "div_balance": 0,
    }
    d = 0
    for mm in re.finditer(r"<(/?)div[^>]*>", b):
        d += 1 if mm.group(1) == "" else -1
    chk["div_balance"] = d
    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', s)
    chk["desc_len"] = len(desc_m.group(1)) if desc_m else 0
    print("  [%s] %s" % (label, json.dumps(chk, ensure_ascii=False)))
    return chk

chk = qa_check(t2, "new")
assert chk["h1"] == 1 and chk["ld"] == 2 and chk["og:image"] == 1, "head fix failed"
assert chk["stars"] == 0 and chk["raw_table"] == 0 and chk["div_balance"] == 0
assert chk["desc_len"] > 120, "description too short"
# 所有 ld+json 必须能 parse
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    json.loads(m.group(1))
print("  ld+json parse: OK")
# 正文不改一字
bt_after = body_text(t2)
print("  body text identical:", bt_before == bt_after)
assert bt_before == bt_after, "BODY CHANGED"
print("  schema.org count:", t2.count("https://schema.org"), " *** count:", t2.count("https://***"))
assert t2.count("https://***") == 0

# ---------- 4. 索引卡 ----------
def build_card(idx_path, href, indent):
    s = open(idx_path, encoding="utf-8").read()
    m = re.search(r'<div class="article-card">', s)
    i = m.start(); depth = 0; j = i
    for mm in re.finditer(r"<(/?)div[^>]*>", s[i:]):
        depth += 1 if mm.group(1) == "" else -1
        if depth == 0:
            j = i + mm.end(); break
    card = s[i:j]
    sep = "\n" + indent
    # 整段替换 tag span 组
    card2 = re.sub(r'(?:\s*<span class="tag">[^<]*</span>)+',
                   "".join('<span class="tag">%s</span>' % x for x in TAGS), card, count=1)
    card2 = re.sub(r'<h2><a href="[^"]*">.*?</a></h2>', '<h2><a href="%s">%s</a></h2>' % (href, TITLE), card2, count=1, flags=re.S)
    card2 = re.sub(r'<p>.*?</p>', '<p>%s</p>' % DESC, card2, count=1, flags=re.S)
    card2 = re.sub(r'\d{4}-\d{2}-\d{2} · [^<]*', '%s · %s' % (DATE, ORG), card2, count=1)
    assert card2 != card, "card template unchanged: " + idx_path
    return s, card2, i

for idx_path, href, indent in (("mili/blog/index.html", "./%s.html" % SLUG, "  "),
                               ("blog/index.html", "/mili/blog/%s.html" % SLUG, "  ")):
    s, card, _ = build_card(idx_path, href, indent)
    occ = [m.start() for m in re.finditer(re.escape('<div class="article-card">'), s)]
    pos = occ[0]
    s2 = s[:pos] + card + "\n" + indent + s[pos:]
    assert s2.replace(card + "\n" + indent, "", 1) == s, "outer changed: " + idx_path
    assert s2.count('<div class="article-card">') == s.count('<div class="article-card">') + 1
    d = 0; depths = {}
    for mm in re.finditer(r"<(/?)div[^>]*>", s2[s2.find("<body"):]):
        if mm.group(1) == "":
            d += 1
            if mm.group(0).startswith('<div class="article-card"'):
                depths[d] = depths.get(d, 0) + 1
        else:
            d -= 1
    print("  [%s] cards=%d depths=%s depth_end=%d" % (idx_path, s2.count('<div class="article-card">'), depths, d))
    assert d == 0 and depths == {2: s2.count('<div class="article-card">')}, "structure broken: " + idx_path
    print("  [%s] card preview: %s" % (idx_path, card[:220].replace("\n", "⏎")))
    if APPLY:
        shutil.copy2(idx_path, idx_path + ".bak-1015")
        open(idx_path, "w", encoding="utf-8").write(s2)
        print("  WRITE", idx_path)

if APPLY:
    shutil.copy2(PAGE, PAGE + ".bak-1015")
    open(PAGE, "w", encoding="utf-8").write(t2)
    print("  WRITE", PAGE)
    if os.path.exists(cover) and not os.path.exists(os.path.join(REPO, "img/%s.png" % SLUG)):
        shutil.copy2(cover, os.path.join(REPO, "img/%s.png" % SLUG))
        print("  WRITE img/%s.png" % SLUG)
    print("  bytes: %d -> %d" % (len(orig.encode()), len(t2.encode())))
else:
    print("\n[DRY-RUN] 未写盘。加 --apply 执行。")
print("DONE")
