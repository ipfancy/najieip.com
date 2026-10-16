#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-16 修复 najie 今日新页「部分裸发布」
用法: python3 site-inbox/fix-1016-page.py [--apply]
缺陷: h1=0 / 无 og:image / 无 og:site_name / 无 keywords / 无 twitter:title|description
      / description 复读标题 / 缺 BreadcrumbList JSON-LD / 3 个小标题仍是 <p>
"""
import os, re, sys, json, shutil, difflib

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
APPLY = "--apply" in sys.argv

TARGET = "najie/blog/customs-ip-filing-3-things-20261016.html"
SLUG = "customs-ip-filing-3-things-20261016"
TITLE = "海关半年拦下1.3万批侵权货，钥匙是份免费备案"
URL = "https://najieip.com/najie/blog/%s.html" % SLUG
IMG_REL = "img/%s.png" % SLUG
IMG_URL = "https://najieip.com/%s" % IMG_REL
DESC = "海关总署与国知局2026年10月14日联合发布国知发保字〔2026〕30号，强化知识产权协同保护。出口与跨境电商企业三个动作：查资格、做备案、盯续展。"
KEYWORDS = "海关知识产权备案,国知发保字2026-30号,跨境电商知产保护,海关主动保护,知识产权协同保护"
HEADINGS = ["海关知道得更多了", "谁该现在去备案", "不备案，到底亏在哪"]

def rd(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

def textify(s):
    """剥离标签后的纯文本（用于「正文不改一字」断言）；先摘除 h1（本次新增的标题位）"""
    b = s[s.find("<body"):]
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    b = b.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return re.sub(r"\s+", " ", b).strip()

t = rd(TARGET)
base_text = textify(t)

# ---- 0. 封面图入库 ----
cover_src = os.path.expanduser("~/wiki/digital-employees/articles/cover-%s.png" % SLUG)
alt = os.path.expanduser("~/wiki/digital-employees/articles/cover-20261016-customs-ip-filing-3-things.png")
if not os.path.exists(cover_src) and os.path.exists(alt):
    cover_src = alt
have_img = os.path.exists(cover_src)
if have_img and not os.path.exists(IMG_REL):
    if APPLY:
        os.makedirs("img", exist_ok=True)
        shutil.copy2(cover_src, IMG_REL)
    print("[cover] %s -> %s (%d bytes)" % (cover_src, IMG_REL, os.path.getsize(cover_src)))
elif os.path.exists(IMG_REL):
    have_img = True
    print("[cover] 已存在 %s (%d bytes)" % (IMG_REL, os.path.getsize(IMG_REL)))
else:
    print("[cover] 未找到 %s —— 不加 og:image" % cover_src)

# ---- 1. 固化 head 偏移（先取原始 </head> 位置，再改 head）----
head_end = t.find("</head>") + len("</head>")
assert head_end > 7, "no </head>"
head, body = t[:head_end], t[head_end:]

# ---- 2. head 改造 ----
h = head
old_desc = '<meta name="description" content="%s">' % TITLE
assert old_desc in h, "description 锚点未命中"
h = h.replace(old_desc, '<meta name="description" content="%s">\n<meta name="keywords" content="%s">' % (DESC, KEYWORDS), 1)

old_ogd = '<meta property="og:description" content="%s">' % TITLE
assert old_ogd in h, "og:description 锚点未命中"
h = h.replace(old_ogd, '<meta property="og:description" content="%s">\n<meta property="og:site_name" content="纳杰知识产权">' % DESC, 1)

if have_img:
    h = h.replace('<meta property="og:type" content="article">',
                  '<meta property="og:type" content="article">\n<meta property="og:image" content="%s">' % IMG_URL, 1)

h = h.replace('<meta name="twitter:card" content="summary">',
              '<meta name="twitter:card" content="summary_large_image">\n'
              '<meta name="twitter:title" content="%s">\n'
              '<meta name="twitter:description" content="%s">' % (TITLE, DESC), 1)

# BreadcrumbList
bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
    {"@type": "ListItem", "position": 2, "name": "纳杰博客", "item": "https://najieip.com/najie/blog/"},
    {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL}]}
bc_s = '<script type="application/ld+json">%s</script>\n' % json.dumps(bc, ensure_ascii=False)
h = h.replace("</head>", bc_s + "</head>", 1)

# Article JSON-LD 补 image
if have_img:
    h = h.replace('"datePublished": "2026-10-16"', '"image": "%s", "datePublished": "2026-10-16"' % IMG_URL, 1)

# ---- 3. body 改造：h1 + 小标题转 h2 ----
b = body
assert "<h1" not in b
b = b.replace("<article>\n", "<article>\n<h1>%s</h1>\n" % TITLE, 1)
assert "<h1" in b, "h1 插入失败"

converted = 0
for hd in HEADINGS:
    pat = "<p>%s</p>" % hd
    if pat in b:
        b = b.replace(pat, "<h2>%s</h2>" % hd, 1)
        converted += 1
    else:
        print("  !! 小标题未命中: %s" % hd)

new = h + b

# ---- 4. 断言 ----
print("\n--- 断言 ---")
ok = True
if textify(new) != base_text:
    ok = False
    d = list(difflib.unified_diff(base_text.split(" "), textify(new).split(" "), lineterm="", n=0))
    print("  FAIL 正文文本不一致:", d[:20])
else:
    print("  PASS 正文文本逐字相等（剥离标签后）")

checks = [("h1", new.count("<h1"), 1), ("h2", new.count("<h2"), len(HEADINGS)),
          ("ld+json", new.count("application/ld+json"), 2)]
for name, got, want in checks:
    flag = "PASS" if got == want else "FAIL"
    if got != want:
        ok = False
    print("  %s %s = %d (期望 %d)" % (flag, name, got, want))

for k, want in [("og:image", have_img), ("og:site_name", True), ("keywords", True),
                ("twitter:title", True), ("twitter:description", True)]:
    got = k in new
    flag = "PASS" if got == want else "FAIL"
    if got != want:
        ok = False
    print("  %s %s = %s" % (flag, k, got))

if new.count("**"):
    print("  WARN 残留 ** =", new.count("**"))
if "2026-10-16" not in new:
    print("  WARN 日期丢失")

# JSON-LD 逐块 json.loads
for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', new, re.S), 1):
    try:
        json.loads(blk)
        print("  PASS ld block %d json.loads" % i)
    except Exception as e:
        ok = False
        print("  FAIL ld block %d: %s" % (i, e))

# div 配平
divs = len(re.findall(r"<div\b", new)) - len(re.findall(r"</div>", new))
print("  div 配平差 =", divs)
if divs != 0:
    ok = False

print("\nbytes: %d -> %d" % (os.path.getsize(TARGET), len(new.encode("utf-8"))))
print("ALL OK =", ok)

if APPLY:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new)
    print("WROTE", TARGET)
else:
    print("(dry-run；加 --apply 落盘)")
