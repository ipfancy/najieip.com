#!/usr/bin/env python3
# site-inbox/fix-1123-page.py  —— 精修 najie/blog/mili-food-oem-trademark-113-order-20261122.html
# 缺 ld=0 / 无 og:image / description 复读标题 → 补 Article+BreadcrumbList / og / twitter / keywords / 真摘要
import os, re, json, glob, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "mili-food-oem-trademark-113-order-20261122"
TGT = os.path.join(REPO, "najie/blog", SLUG + ".html")
URL = f"https://najieip.com/najie/blog/{SLUG}.html"
APPLY = "--apply" in sys.argv

DESC = ("12月1日《食品委托生产监督管理办法》施行，共30条。商标授权若同时满足按委托方要求、"
        "参与全部或部分生产、交付食品三个要素，即被认定为委托生产，“我只是授权不生产”不再免责；"
        "另含10个工作日报告义务与合同自查三句话。")
KEYWORDS = "食品委托生产,商标授权,贴牌,OEM,委托方受托方,食品标签,市场监管"

t = open(TGT, encoding="utf-8").read()
if t.count("application/ld+json") >= 2 and "og:image" in t:
    print("SKIP: already fixed"); sys.exit(0)

head_end = t.find("</head>") + 7       # 原始偏移，先固化
head, body = t[:head_end], t[head_end:]

# 1) 模板：最近的 najie 精修页（ld>=2 且 og:image），排除自身
tpl = None
for p in sorted(glob.glob(os.path.join(REPO, "najie/blog/*.html")), key=os.path.getmtime, reverse=True):
    if p.endswith("index.html") or SLUG in p: continue
    s = open(p, encoding="utf-8", errors="ignore").read()
    if s.count("application/ld+json") >= 2 and "og:image" in s:
        tpl = s; print("TEMPLATE:", os.path.basename(p)); break
assert tpl, "no template"

# 2) 取模板两块 ld+json（Article + BreadcrumbList），剔除任何 FAQPage
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S)
objs = []
for b in blocks:
    o = json.loads(b)
    if o.get("@type") == "FAQPage": continue
    objs.append(copy.deepcopy(o))
art = next(o for o in objs if o.get("@type") == "Article")
bc = next(o for o in objs if o.get("@type") == "BreadcrumbList")

# 3) 封面
img_rel = f"/img/{SLUG}.png"
covers = []
for pat in (f"{SLUG}.png", f"cover-{SLUG}.png", f"cover-20261122-{SLUG}.png", f"*food-oem*113*.png", f"*food-oem*.png"):
    covers += glob.glob(os.path.expanduser("~/wiki/digital-employees/articles/" + pat))
covers = sorted(set(covers))
print("COVER_CANDIDATES:", [os.path.basename(c) for c in covers][:5])
cover_ok = False
if covers:
    dst = os.path.join(REPO, img_rel.lstrip("/"))
    if APPLY:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(covers[0], dst)
    print("COVER:", os.path.basename(covers[0]), "->", img_rel, "bytes=", os.path.getsize(covers[0]))
    cover_ok = True
IMG = f"https://najieip.com{img_rel}" if cover_ok else art.get("image", "")

# 4) 覆写 Article
art.update({"@context": "https://schema.org", "headline": "12月1日起，商标授权不再是食品贴牌的免责理由",
            "description": DESC, "image": IMG, "datePublished": "2026-11-22", "dateModified": "2026-11-23",
            "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "url": URL, "inLanguage": "zh-CN",
            "keywords": KEYWORDS})
art["@context"] = "https://schema.org"
if "author" not in art: art["author"] = {"@type": "Person", "name": "何自刚"}
# 5) 覆写 BreadcrumbList 第三项
ile = bc.get("itemListElement", [])
if len(ile) >= 3:
    ile[2]["name"] = "12月1日起，商标授权不再是食品贴牌的免责理由"
    ile[2]["item"] = URL

# 6) head 手术（文本级，绕开 format/deepcopy 序列化坑）
new_tags = (
    f'\n<meta name="description" content="{DESC}">'
    f'\n<meta name="keywords" content="{KEYWORDS}">'
    f'\n<meta property="og:site_name" content="纳杰觅理">'
    f'\n<meta property="og:image" content="{IMG}">'
    f'\n<meta property="og:description" content="{DESC}">'
    f'\n<meta name="twitter:title" content="12月1日起，商标授权不再是食品贴牌的免责理由">'
    f'\n<meta name="twitter:description" content="{DESC}">'
    f'\n<meta name="twitter:image" content="{IMG}">'
    f'\n<meta name="twitter:card" content="summary_large_image">'
    f'\n<script type="application/ld+json">{json.dumps(art, ensure_ascii=False)}</script>'
    f'\n<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>'
    f'\n')
h2 = head
# 替换旧 description / og:description（标题复读）
h2 = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', h2, count=1)
h2 = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', h2, count=1)
h2 = h2.replace('<meta name="twitter:card" content="summary">', '<meta name="twitter:card" content="summary_large_image">')
# 在 </head> 前插入新标签
h2 = h2.replace("\n</head>", new_tags + "</head>") if "\n</head>" in h2 else h2.replace("</head>", new_tags + "</head>")

newpage = h2 + body
# 校验
assert newpage.count("application/ld+json") == 2, newpage.count("application/ld+json")
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', newpage, re.S):
    json.loads(m)
assert newpage.count("https://schema.org") == 2
assert len(re.findall(r"<h1[\s>]", newpage)) == 1
assert newpage.count("**") == 0
assert newpage[newpage.find("</head>")+7:] == body, "body shifted"
print("CHECKS OK; new size:", len(newpage.encode()), "cover_ok:", cover_ok)

if APPLY:
    open(TGT, "w", encoding="utf-8").write(newpage)
    print("APPLIED")
else:
    print("DRY-RUN")
