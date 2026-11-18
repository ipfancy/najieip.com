#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-18 夜班修复：① 芬兰用工文裸发布页整页重建（md 源 + mili 房屋）② 双索引补卡 6 张 + 修正 2 张卡摘要 ③ 封面入库"""
import os, re, json, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv
SLUG = "20261118-mili-finland-labor-four-gates"
TFILE = os.path.join(REPO, "mili", "blog", SLUG + ".html")
HOUSE = os.path.join(REPO, "mili", "blog", "20261118-mili-drug-linkage-9-cases.html")
MD = os.path.expanduser(f"~/wiki/digital-employees/articles/{SLUG}.md")
TITLE = "芬兰没最低工资，中国工地却月扣1600欧"
DESC = ("芬兰科特卡8亿欧元电池材料厂工地，300多名中国工人；赫尔辛基警方9月10日立案、10月30日通报劳动人口贩运与"
        "严重非法入境安排嫌疑，尚无定罪。芬兰没有全国最低工资，但行业集体协议有普遍约束力。四道关：主体、合同、钱、关系，另附出海用工三条清单。")
KW = "出海用工,芬兰集体协议,劳动人口贩运,外派劳动协议,欧盟强迫劳动条例"
IMG_LOCAL = os.path.join(REPO, "img", SLUG + ".png")
IMG_SRC = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-{SLUG}.png")
IMG_URL = f"https://najieip.com/img/{SLUG}.png"

def zh_quotes(s):
    out, ind = [], 0
    for ch in s:
        if ch == '"':
            out.append("“" if ind % 2 == 0 else "”"); ind += 1
        else:
            out.append(ch)
    return "".join(out)

# ---------- 1. 重建芬兰页 ----------
md_raw = open(MD, encoding="utf-8").read()
md_raw = re.sub(r"^---.*?\n---\n", "", md_raw, flags=re.S)
lines = [l.strip() for l in md_raw.split("\n") if l.strip()]
paras = [l for l in lines if not l.startswith("<!--")]

H2 = [
    ("先把话说明白", "芬兰科特卡案：预审调查，尚无定罪"),
    ("第一关，主体", "第一关：主体——法律上的雇主到底是谁"),
    ("第二关，合同", "第二关：合同——语言与告知"),
    ("第三关，钱", "第三关：钱——扣款、工时、最低标准"),
    ("第四关，关系", "第四关：关系——变更、退出、工会"),
    ("真正的时间点在这", "2027年12月14日：欧盟《强迫劳动条例》"),
    ("出海用工这事", "今天就能做的三条"),
]
body_parts, used = [], set()
for p in paras:
    for anchor, h2txt in H2:
        if anchor not in used and p.startswith(anchor):
            body_parts.append(f"<h2>{h2txt}</h2>")
            used.add(anchor)
            break
    txt = p
    if txt.startswith("*") and txt.endswith("*"):
        txt = txt.strip("*").strip()
    body_parts.append(f"<p>{zh_quotes(txt)}</p>")
assert len(used) == len(H2), f"h2 锚点未全命中: {set(a for a, _ in H2) - used}"

CTA = ('<!--CTA-STD-->\n<div style="margin:36px 0;padding:18px 24px;border-left:3px solid #4A2C6E;background:#F6F3FA;border-radius:6px">'
       '<p style="margin:0 0 6px"><strong>这篇文章的场景，落到你公司身上是什么样？</strong></p>'
       '<p style="margin:0;font-size:14px;color:#555">何自刚｜知识产权律师　电话 010-65150974 / 15321374076　微信同号</p></div>\n<!--/CTA-STD-->')

art = {
    "@context": "https://schema.org", "@type": "Article",
    "headline": TITLE, "description": DESC,
    "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师"},
    "publisher": {"@type": "Organization", "name": "北京觅理律师事务所"},
    "datePublished": "2026-11-18", "dateModified": "2026-11-18",
    "mainEntityOfPage": f"https://najieip.com/mili/blog/{SLUG}.html",
    "url": f"https://najieip.com/mili/blog/{SLUG}.html",
    "image": IMG_URL, "inLanguage": "zh-CN",
}

# 同品牌延伸阅读（仅收真实存在的页）
rel = []
for cand, label in [("mili/blog/20261113-byd-netherlands-evidence-seizure.html", "荷兰突击搜查3个月后撤销：出海企业必须懂的3步应对"),
                    ("mili/blog/20261115-mili-payment-60days-b2b.html", "「收到上家款再付」无效：国务院令第802号，逾期按日万分之五")]:
    if os.path.exists(os.path.join(REPO, cand)):
        rel.append(f'<li><a href="/{cand}">{label}</a></li>')
rel_html = f'<h2>延伸阅读</h2>\n<ul>{"".join(rel)}</ul>' if rel else ""

head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KW}">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:site_name" content="北京觅理律师事务所">
<meta property="og:locale" content="zh_CN">
<meta property="og:url" content="https://najieip.com/mili/blog/{SLUG}.html">
<meta property="og:image" content="{IMG_URL}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{IMG_URL}">
<link rel="canonical" href="https://najieip.com/mili/blog/{SLUG}.html">
<link rel="alternate" hreflang="zh-CN" href="https://najieip.com/mili/blog/{SLUG}.html">
<link rel="alternate" hreflang="x-default" href="https://najieip.com/mili/blog/{SLUG}.html">
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(art, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}, {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"}, {"@type": "ListItem", "position": 3, "name": TITLE}]}, ensure_ascii=False)}</script>
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
<h1>{TITLE}</h1>
"""
page = head + "\n<br>\n".join(body_parts) + ("\n" + rel_html if rel_html else "") + "\n" + CTA + "\n</article>\n<footer>\n<p>© 2026 北京觅理律师事务所</p>\n<p><a href=\"https://github.com/ipfancy/najieip.com\">Open Source</a></p>\n</footer>\n</body>\n</html>\n"

# 校验：md 全文包含（两侧剥 h1/h2/落款）
def norm(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<h1.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<ul>.*?</ul>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in [("&amp;", "&"), ("&gt;", ">"), ("&lt;", "<"), ("&quot;", '"'), ("&#x27;", "'"), ("&nbsp;", "")]:
        s = s.replace(a, b)
    s = re.sub(r"[“”‘’\"'「」『』【】]", "", s)
    s = re.sub(r"-{3,}", "", s)
    s = s.replace(":", "").replace("|", "").replace("*", "")
    return re.sub(r"\s+", "", s)

mdn = norm("".join(paras))
art_m = re.search(r"<article>.*?</article>", page, re.S)
pgn = norm(art_m.group(0))
md_ok = mdn in pgn
print(f"[finland] md_chars={len(mdn)} page_chars={len(pgn)} md_contained={md_ok} equal={mdn == pgn} bytes={len(page.encode())}")
if not md_ok:
    for i in range(min(len(mdn), len(pgn))):
        if mdn[i] != pgn[i]:
            print(f"  diff@{i}\n   md={mdn[max(0,i-40):i+40]!r}\n   pg={pgn[max(0,i-40):i+40]!r}")
            break
    else:
        print("  prefix ok, md longer than page")
        print(f"  md_tail={mdn[len(pgn)-40:][:120]!r}")
assert md_ok, "md 全文未包含于页面正文"
assert len(re.findall(r"<h1[ >]", page)) == 1
assert len(re.findall(r"application/ld\+json", page)) == 2
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
    json.loads(blk)
assert page.count("**") == 0 and page.count("https://***") == 0

# ---------- 2. 索引补卡 ----------
NEW = [
    ("mili", "20261118-mili-ai-tool-trade-secret"),
    ("mili", "20261118-mili-drug-linkage-9-cases"),
    ("mili", "20261118-mili-refusal-execute-five-cases"),
    ("najie", "20261118-najie-gi-15plan-2030"),
]
ORG = {"mili": ("觅理", "北京觅理律师事务所"), "najie": ("纳杰", "北京纳杰知识产权代理有限公司")}

def page_meta(brand, slug):
    t = open(os.path.join(REPO, brand, "blog", slug + ".html"), encoding="utf-8").read()
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else slug
    desc = d.group(1).strip() if d else title
    if len(desc) > 150: desc = desc[:148].rstrip() + "…"
    return title, desc

def card(brand, slug, title, desc, absolute):
    href = f"/{brand}/blog/{slug}.html" if absolute else f"./{slug}.html"
    tag, org = ORG[brand]
    return (f'  <div class="article-card">\n'
            f'    <h2><a href="{href}">{title}</a></h2>\n'
            f'    <div class="meta"><span class="tag">{tag}</span> 2026-11-18 · {org}</div>\n'
            f'    <p>{desc}</p>\n'
            f'  </div>')

def insert_card(t, blk):
    """按日期降序插到第一张 date < 2026-11-18 的卡之前；重扫位置"""
    for m in re.finditer(r'<div class="article-card">', t):
        s = m.start()
        d = 0; i = s
        while i < len(t):
            if t.startswith("<div", i): d += 1
            elif t.startswith("</div>", i):
                d -= 1
                if d == 0: break
            i += 1
        blk_txt = t[s:i + 6]
        dm = re.search(r"(\d{4}-\d{2}-\d{2})", blk_txt)
        if dm and dm.group(1) < "2026-11-18":
            return t[:s] + blk + "\n  " + t[s:], True
    return t + "\n" + blk + "\n", True

targets = {"main": os.path.join(REPO, "blog", "index.html"),
           "mili": os.path.join(REPO, "mili", "blog", "index.html"),
           "najie": os.path.join(REPO, "najie", "blog", "index.html")}

newfiles = {}
for key, path in targets.items():
    newfiles[key] = open(path, encoding="utf-8").read()

change_log = []
# 主索引：4 篇全补
for brand, slug in NEW:
    t = newfiles["main"]
    if re.search(r'href="[^"]*' + re.escape(slug), t):
        continue
    title, desc = page_meta(brand, slug)
    blk = card(brand, slug, title, desc, True)
    newfiles["main"], _ = insert_card(t, blk)
    change_log.append(f"main+{slug}")
# 品牌索引：只补该品牌自己的
for brand, slug in NEW:
    t = newfiles[brand]
    if re.search(r'href="[^"]*' + re.escape(slug), t):
        continue
    title, desc = page_meta(brand, slug)
    blk = card(brand, slug, title, desc, False)
    newfiles[brand], _ = insert_card(t, blk)
    change_log.append(f"{brand}+{slug}")

# 修正芬兰卡摘要（两处标题复读 -> 真摘要）
for key in ("main", "mili"):
    t = newfiles[key]
    old = f'<p>{TITLE}</p>'
    if old in t:
        newfiles[key] = t.replace(old, f"<p>{DESC[:120]}…</p>", 1)
        change_log.append(f"{key}~finland-desc")

# 结构校验
for key, t0 in [(k, open(p, encoding='utf-8').read()) for k, p in targets.items()]:
    t = newfiles[key]
    def card_depth(s):
        hist = {}
        for m in re.finditer(r'<div class="article-card">', s):
            dep = len(re.findall(r"<div", s[:m.start()])) - len(re.findall(r"</div>", s[:m.start()]))
            hist[dep] = hist.get(dep, 0) + 1
        return hist
    h0, c1 = card_depth(t0), card_depth(t)
    op0, cl0 = t0.count("<div"), t0.count("</div>")
    op1, cl1 = t.count("<div"), t.count("</div>")
    print(f"[{key}] cards {sum(h0.values())}->{sum(c1.values())} div {op0}/{cl0} -> {op1}/{cl1} hist {h0}->{c1}")
    assert sum(c1.values()) >= sum(h0.values())
    assert (op1 - op0) == (cl1 - cl0), "div 开合增量不对称"
    assert t.count("**") == 0, "索引出现 ** 泄漏"

print("[changes]", change_log)

if APPLY:
    open(TFILE, "w", encoding="utf-8").write(page)
    for key, path in targets.items():
        open(path, "w", encoding="utf-8").write(newfiles[key])
    if os.path.exists(IMG_SRC):
        os.makedirs(os.path.dirname(IMG_LOCAL), exist_ok=True)
        shutil.copy2(IMG_SRC, IMG_LOCAL)
        print(f"[img] copied {os.path.getsize(IMG_LOCAL)}B")
    print("APPLIED")
else:
    print("DRY-RUN (use --apply)")
