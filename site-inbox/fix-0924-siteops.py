#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 重建裸发布畸形页（mili/malicious-litigation-supervision）
房屋模板 = 同日同品牌精修页 mili/blog/20260922-caichan-shouhu-07.html（外链 /style.css 版）
正文段落 = 沿用原页已渲染段（已与 md 源 30/30 0 差异核过），不加一字、不加 <br>
用法: python3 site-inbox/fix-0924-siteops.py [--apply]
"""
import os, re, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260924-malicious-litigation-supervision"
TARGET = os.path.join(REPO, "mili/blog/%s.html" % SLUG)
REF = os.path.join(REPO, "mili/blog/20260922-caichan-shouhu-07.html")
MD = os.path.expanduser("~/wiki/digital-employees/articles/%s.md" % SLUG)
APPLY = "--apply" in sys.argv

URL = "https://najieip.com/mili/blog/%s.html" % SLUG
TITLE = "被碰瓷式维权告了？最高检6月29日5案：5步把案子翻过来"
H1 = TITLE
DESC = ("最高检 6 月 29 日发布 5 件惩治知识产权恶意诉讼典型案例：从上市受理 12 天即被索赔 2300 万、"
        "抗诉后原告倒赔 40 万的专利碰瓷，到权利基础已失效仍申请执行、批量维权、抢注囤货、抢注公共资源，"
        "本文拆解 5 种手法与 5 步反制路径，并给出企业起诉前的三条自检。")
KEYWORDS = "知识产权恶意诉讼,最高检典型案例,检察监督,抗诉,碰瓷式维权,商标抢注"
OGIMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"
DATE = "2026-09-24"
# h2 路标：只加描述性标题，不引入新论点。键 = 其前置段落序号
H2 = {
    5: "最高检 6 月 29 日发布 5 件典型案例",
    6: "5 种碰瓷手法，一眼识破",
    12: "被碰瓷式维权告了：5 步把案子翻过来",
    18: "起诉之前，企业先过这三条自检",
    22: "2026 年之后，恶意诉讼的成本",
    25: "今天就能做的三件事",
}


def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ---------- 1. 畸形页正文段（HTML 原样保留）----------
cur = rd(TARGET)
raw_ps = re.findall(r"<p[^>]*>(.*?)</p>", cur, re.S)
content = [p for p in raw_ps if p.strip()]
# 剔除页脚/评论残渣段
content = [p for p in content if not p.strip().startswith("&lt;!--")
           and "纳杰觅理 ·" not in p and "Open Source" not in p]
assert len(content) == 30, "正文段数异常: %d" % len(content)

# ---------- 2. md 源逐段校验（允许免责声明的装饰性星号差异）----------
md = rd(MD).split("---", 2)[2]
md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
md_paras = [p.strip() for p in md.split("\n\n") if p.strip()]
assert len(md_paras) == 30, "md 段数异常: %d" % len(md_paras)
diff = 0
for i, (a, b) in enumerate(zip(content, md_paras)):
    a2 = re.sub(r"<[^>]+>", "", a).replace("&amp;", "&").replace("&quot;", '"').replace("&#x27;", "'").strip()
    # 两侧都剥掉 markdown 强调用的单个星号（房屋样式在页面上保留字面 *…*，md 源同）
    a2 = re.sub(r"^\*+|\*+$", "", a2).strip()
    b2 = re.sub(r"^\*+|\*+$", "", b.strip()).replace("&amp;", "&").strip()
    if a2 != b2:
        diff += 1
        if diff <= 5:
            print("  [DIFF %d] page=%s | md=%s" % (i, a2[:70], b2[:70]))
print("正文比对: %d 段 / DIFF %d" % (len(content), diff))
assert diff == 0, "正文与 md 源有差异，终止"

# ---------- 3. 取房屋模板 ----------
ref = rd(REF)
nav = re.search(r"<nav>.*?</nav>", ref, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", ref, re.S).group(0)
beacon = re.search(r"<script defer src='https://static\.cloudflareinsights\.com[^>]*></script>", ref).group(0)
print("模板 nav:", nav)
print("模板 beacon:", beacon[:80], "...")

# ---------- 4. 组正文（插入 h2 路标，去掉 <br>）----------
body_parts = []
for i, p in enumerate(content):
    if i in H2:
        body_parts.append("<h2>%s</h2>" % H2[i])
    body_parts.append("<p>%s</p>" % p)
body_html = "\n".join(body_parts)

# ---------- 5. 组 head ----------
ld_article = {
    "@context": "https://schema.org", "@type": "Article", "headline": TITLE,
    "description": DESC, "author": {"@type": "Person", "name": "何自刚"},
    "publisher": {"@type": "Organization", "name": "北京觅理律师事务所"},
    "datePublished": DATE, "dateModified": DATE,
    "mainEntityOfPage": URL, "url": URL,
}
ld_crumb = {
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
        {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
        {"@type": "ListItem", "position": 3, "name": TITLE},
    ],
}
d = json.dumps
HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
{beacon}
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="觅理律所">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="canonical" href="{url}">
<script type="application/ld+json">
{ld1}
</script>
<script type="application/ld+json">
{ld2}
</script>
</head>
<body>
{nav}
<article>
<h1>{h1}</h1>
{body}
</article>
{footer}
</body>
</html>
""".replace("{title}", TITLE).replace("{desc}", DESC).replace("{kw}", KEYWORDS) \
   .replace("{url}", URL).replace("{ogimg}", OGIMG).replace("{beacon}", beacon) \
   .replace("{nav}", nav).replace("{footer}", footer).replace("{h1}", H1) \
   .replace("{body}", body_html).replace("{ld1}", d(ld_article, ensure_ascii=False)) \
   .replace("{ld2}", d(ld_crumb, ensure_ascii=False))

# ---------- 6. 校验 ----------
print("\n=== 成品校验 ===")
checks = [
    ("h1 计数 == 1", HEAD.count("<h1") == 1),
    ("h2 计数 == %d" % len(H2), HEAD.count("<h2") == len(H2)),
    ("ld+json == 2", HEAD.count("application/ld+json") == 2),
    ("og:image 存在", "og:image" in HEAD),
    ("keywords 存在", 'name="keywords"' in HEAD),
    ("desc 长度 >80", len(DESC) > 80),
    ("desc != title", DESC != TITLE),
    ("schema.org >= 2", HEAD.count("https://schema.org") >= 2),
    ("无 *** 脱敏字面量", HEAD.count("https://***") == 0),
    ("无 ** 泄漏", HEAD.count("**") == 0),
    ("无 &lt;!-- 残渣", "&lt;!--" not in HEAD),
    ("无 <br> 分隔", "<br>" not in HEAD),
    ("正文 30 段全在", all("<p>%s</p>" % p in HEAD for p in content)),
]
ok = True
for name, res in checks:
    print("  %s %s" % ("PASS" if res else "FAIL", name))
    ok = ok and res

# div 深度配平
depth = 0
bad = False
for tag in re.findall(r"<(/?)div\b", HEAD):
    depth += -1 if tag else 1
    if depth < 0:
        bad = True
print("  %s div 深度归零 (end=%d, 异常=%s)" % ("PASS" if depth == 0 and not bad else "FAIL", depth, bad))
ok = ok and depth == 0 and not bad

# JSON-LD 可解析
for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', HEAD, re.S)):
    try:
        json.loads(blk)
        print("  PASS JSON-LD #%d 可解析" % (i + 1))
    except Exception as e:
        ok = False
        print("  FAIL JSON-LD #%d: %s" % (i + 1, e))

print("\n旧 %d B -> 新 %d B" % (len(cur.encode()), len(HEAD.encode())))
if not ok:
    print("!! 校验未全过，不写盘")
    sys.exit(1)
if APPLY:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(HEAD)
    print("已写入", TARGET)
else:
    print("(--dry-run，未写盘)")
