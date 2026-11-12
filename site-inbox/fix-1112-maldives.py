#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 20261112 马尔代夫商标法页：套同日 najie 房屋 + Article/BreadcrumbList + og:image + 真摘要"""
import os, re, json, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles")
SLUG = "20261112-maldives-trademark-law"
BRAND = "najie"
TARGET = os.path.join(REPO, BRAND, "blog", SLUG + ".html")
TPL = os.path.join(REPO, BRAND, "blog", "20261111-najie-same-day-dual-filing-one-choice.html")
URL = f"https://najieip.com/{BRAND}/blog/{SLUG}.html"
IMG = f"https://najieip.com/img/{SLUG}.png"
DATE = "2026-11-12"
TITLE = "马尔代夫商标法生效，12个月过渡期，公告不再等于权利"
DESC = ("马尔代夫第19号商标法（2025年）2026年11月11日生效：在报纸登警示性公告不再产生权利，"
        "旧权利须在2027年11月11日前搬进新注册簿。本文给盘点、重新注册、留证三步动作，"
        "并讲清先申请原则下为什么不能等实施细则，以及10万到200万拉菲亚的罚则。")
KW = "马尔代夫商标法,马尔代夫商标注册,报纸公告,商标过渡期,涉外商标,海外商标布局,先申请原则"

def rd(p): return open(p, encoding="utf-8").read()

def zh(s):
    # 文本节点内 ASCII 直引号 → 中文引号（成对处理）
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("“" if open_q else "”"); open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)

def inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = zh(s)
    return s

md = rd(os.path.join(MD, SLUG + ".md"))
md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S).strip()
lines = [l.rstrip() for l in md.split("\n")]

blocks = []
for ln in lines:
    if not ln.strip():
        continue
    if ln.startswith("# "):          # h1 由模板单独给
        continue
    if ln.startswith("<!--"):
        continue
    if ln.startswith("## "):
        blocks.append("<h2>%s</h2>" % inline(ln[3:].strip()))
        continue
    t = ln.strip()
    blocks.append("<p>%s</p>" % inline(t))

body_html = "\n".join(blocks)

# ---- 房屋 ----
tpl = rd(TPL)
head_end = tpl.find("</head>") + 7
head = tpl[:head_end]
tail_after_article = tpl[tpl.find("</article>"):]      # footer + CTA + 收尾
nav = '<nav><a href="/">← 首页</a> · <a href="https://najieip.com/najie/blog/">纳杰博客</a></nav>'

# head 改造
head = re.sub(r"<title>.*?</title>", f"<title>{TITLE} — 纳杰觅理</title>", head, flags=re.S)
for prop in ("name=\"description\"", "property=\"og:description\"", "name=\"twitter:description\""):
    head = re.sub(r'<meta ' + re.escape(prop) + r' content="[^"]*">',
                  f'<meta {prop} content="{DESC}">', head)
head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{TITLE}">', head)
head = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{TITLE}">', head)
head = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{KW}">', head)
head = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', head)
head = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{IMG}">', head)
head = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{IMG}">', head)
head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', head)
if 'og:site_name' not in head:
    head = head.replace('<meta property="og:locale"', '<meta property="og:site_name" content="纳杰知产">\n<meta property="og:locale"')
if 'twitter:card' not in head:
    head = head.replace('</head>', '<meta name="twitter:card" content="summary_large_image">\n</head>')
else:
    head = re.sub(r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary_large_image">', head)

# JSON-LD：剔除 FAQPage，改写 Article/BreadcrumbList
blocks_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
objs = []
for b in blocks_ld:
    o = json.loads(b)
    if o.get("@type") == "FAQPage":
        continue
    objs.append(o)
assert len(objs) == 2, [o.get("@type") for o in objs]

def rebuild_ld(objs):
    out = []
    for o in objs:
        if o.get("@type") == "Article":
            o = copy.deepcopy(o)
            o["headline"] = TITLE
            o["datePublished"] = DATE
            o["dateModified"] = DATE
            o["description"] = DESC
            o["mainEntityOfPage"] = URL
            o["url"] = URL
            o["image"] = IMG
            o["inLanguage"] = "zh-CN"
            o["keywords"] = KW
            o["articleSection"] = "涉外商标"
        elif o.get("@type") == "BreadcrumbList":
            o = copy.deepcopy(o)
            o["itemListElement"][1]["item"] = f"https://najieip.com/{BRAND}/blog/"
            o["itemListElement"][2]["name"] = "马尔代夫商标法生效"
            o["itemListElement"][2].pop("item", None)
        out.append(o)
    # najie 房屋模板缺 @context（生成器遗留）→ 统一补在首位
    return [{"@context": "https://schema.org", **o} for o in out]

new_ld = rebuild_ld(objs)
# 用新 ld 替换 head 中的原三块
head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', head, flags=re.S)
ld_html = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(o, ensure_ascii=False) for o in new_ld)
head = head.replace("</head>", ld_html + "</head>")

# 相关推荐（内链 2 篇）
related = ('<ul>'
           '<li><a href="/najie/blog/20261111-najie-same-day-dual-filing-one-choice.html">同日双申只能二选一：改权利要求绕开放弃，这条路封了</a></li>'
           '<li><a href="/najie/blog/20261107-najie-patent-license-contract-6-clauses.html">49.6万次专利转让许可备案：合同这6条不写死，许可费收不回</a></li>'
           '</ul>')

body = (
    nav + "\n<article>\n"
    f"<h1>{TITLE}</h1>\n"
    f'<figure><img src="/img/{SLUG}.png?v=20261112" alt="{TITLE}（信息图）" width="800" height="1200" loading="lazy" style="max-width:100%;height:auto"></figure>\n'
    + body_html + "\n"
    + related + "\n"
    + "<p>何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰</p>\n"
    + "<p>本文由 AI 辅助生成与整理，观点与判断由作者审定。本文仅代表作者个人观点，不构成法律意见。</p>\n"
    + tail_after_article
)

out = (head + body).replace("</body>", "</body>") if "</body>" in body else head + body

def norm(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    for ch in "“”\"'’>|:-*#`「」『』【】":
        s = s.replace(ch, "")
    return re.sub(r"\s+", "", s)

# 校验：md 是否完整包含（两边都丢标题行）
def md_plain():
    t = re.sub(r"^---\n.*?\n---\n", "", rd(os.path.join(MD, SLUG + ".md")), flags=re.S)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    keep = []
    for l in t.split("\n"):
        s = l.strip()
        if not s: continue
        if s.startswith("# "): continue
        if s.startswith("## "): continue     # 页面侧 h2 文字已剥
        keep.append(s)
    return "\n".join(keep)

art = out[out.find("<article>"):out.find("</article>")]
art = re.sub(r"<h1.*?</h1>", " ", art, flags=re.S)
art = re.sub(r"<h2.*?</h2>", " ", art, flags=re.S)
n_md, n_pg = norm(md_plain()), norm(art)
contained = n_md in n_pg

checks = {
    "h1": len(re.findall(r"<h1[ >]", out)),
    "h2": len(re.findall(r"<h2[ >]", out)),
    "ld": len(re.findall(r'application/ld\+json', out)),
    "ld_types": [json.loads(b).get("@type") for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S)],
    "og_image": "og:image" in out,
    "desc_len": len(DESC),
    "stars": re.sub(r"[0-9]\*{2,}[0-9.]*", "", out[out.find("<body"):]).count("**"),
    "schema": out.count("https://schema.org"),
    "md_contained": contained,
    "md_len": len(n_md), "pg_len": len(n_pg),
}
print(json.dumps(checks, ensure_ascii=False))
if not contained:
    for i in range(min(len(n_md), len(n_pg))):
        if n_md[i] != n_pg[i]:
            print("DIFF", i, "| MD:", n_md[max(0,i-30):i+40], "| PG:", n_pg[max(0,i-30):i+40]); break

if "--apply" in sys.argv and contained and checks["ld"] == 2:
    open(TARGET, "w", encoding="utf-8").write(out)
    src = os.path.join(MD, f"cover-{SLUG}.png")
    dst_dir = os.path.join(REPO, "img")
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(dst_dir, SLUG + ".png"))
    print("APPLIED", os.path.getsize(TARGET), "cover", os.path.getsize(os.path.join(dst_dir, SLUG + '.png')))
else:
    print("NOT APPLIED", "--apply" in sys.argv, contained, checks["ld"])
