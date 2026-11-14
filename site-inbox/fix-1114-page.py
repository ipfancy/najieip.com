#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-14 精修：mili 刷脸考勤页（裸发布畸形页 h1=0/ld=0/无og:image/desc复读/**×6）
房屋 = 同日同品牌精修页 20261114-mili-copyright-financing-16-cases.html
用法: python3 site-inbox/fix-1114-page.py [--apply]
"""
import os, re, sys, json, glob, copy, shutil, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261114-mili-face-recognition-compliance"
TARGET = os.path.join(REPO, "mili/blog", SLUG + ".html")
HOUSE = os.path.join(REPO, "mili/blog/20261114-mili-copyright-financing-16-cases.html")
MD = os.path.expanduser("~/wiki/digital-employees/articles/" + SLUG + ".md")
ART_DIR = os.path.expanduser("~/wiki/digital-employees/articles")
APPLY = "--apply" in sys.argv

TITLE = "刷脸考勤：10万人只是备案线，2026年盯的是第10条"
DESC = ("《人脸识别技术应用安全管理办法》第10条与10万人备案线是两件事：2026年个人信息保护专项行动把"
        "“能不用人脸就不用”列为重点治理问题。两百人的公司够不着备案线，却正好在治理清单上。"
        "文中拆开第8条本地存储、第10条双通道、第13条私密空间禁装三条硬要求，附三件今天就能做的事。")
KEYWORDS = "人脸识别,刷脸考勤,个人信息保护,第10条,双通道,企业合规"
DATE = "2026-11-14"

def textify(html):
    b = html
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<(h1|h2)[^>]*>.*?</\1>", " ", b, flags=re.S)
    b = re.sub(r"<figure.*?</figure>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    for a, c in [("&nbsp;", " "), ("&amp;", "&"), ("&gt;", ">"), ("&lt;", "<"), ("&quot;", '"'), ("&#x27;", "'")]:
        b = b.replace(a, c)
    b = re.sub(r"[“”\"'’「」『』【】:：\s|*\-]", "", b)
    return b

def zh_quotes(s):
    parts = re.split(r"(<[^>]+>)", s)
    out = []
    for p in parts:
        if p.startswith("<") and p.endswith(">"):
            out.append(p); continue
        cnt = [0]
        def rep(m):
            cnt[0] += 1
            return "“" if cnt[0] % 2 == 1 else "”"
        out.append(re.sub(r'"', rep, p))
    return "".join(out)

# ---------- 1. md → 正文 HTML ----------
raw = open(MD, encoding="utf-8").read()
raw = re.sub(r"^---.*?---\s*", "", raw, flags=re.S)
raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
lines = [l.rstrip() for l in raw.splitlines()]

blocks, i = [], 0
HEADINGS = {"10万人的线，卡在哪", "真正要动的是三条", "现在就能做的三件事"}
while i < len(lines):
    s = lines[i].strip()
    if not s:
        i += 1; continue
    m = re.fullmatch(r"\*\*([^*\n]{1,30})\*\*", s)
    if m and m.group(1) in HEADINGS:
        blocks.append(("h2", m.group(1))); i += 1; continue
    if re.match(r"^\d+\.\s", s):
        items = []
        while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
            items.append(re.sub(r"^\d+\.\s*", "", lines[i].strip())); i += 1
        blocks.append(("ol", items)); continue
    blocks.append(("p", s)); i += 1

BODY = [f'<h1>{TITLE}</h1>']
for kind, val in blocks:
    if kind == "h2":
        BODY.append(f"<h2>{val}</h2>")
    elif kind == "ol":
        BODY.append('<ol>\n' + "\n".join(f"  <li>{v}</li>" for v in val) + "\n</ol>")
    else:
        v = val.replace("**", "")
        if v.startswith("何自刚 |"):
            BODY.append('<p class="byline">何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰</p>')
        elif v.startswith("*本文"):
            BODY.append(f'<p class="disclaimer">{v}</p>')
        else:
            BODY.append(f"<p>{v}</p>")
article_html = "<article>\n" + "\n".join(BODY) + "\n</article>"

# ---------- 2. 房屋头 ----------
house = open(HOUSE, encoding="utf-8").read()
head_end = house.find("</head>") + len("</head>")
head = house[:head_end]
body_rest = house[head_end:]
# 去掉模板的 FAQPage（属模板文章自身内容）
head = re.sub(r'<script type="application/ld\+json">\s*\{[^<]*?"@type": "FAQPage".*?</script>\s*', "", head, flags=re.S)

URL = f"https://najieip.com/mili/blog/{SLUG}.html"

def sub_attr(h, key, val):
    pat = re.compile(r'(<' + key[0] + r'[^>]*(?:property|name)="' + re.escape(key[1]) + r'"[^>]*content=")[^"]*(")')
    h2, n = pat.subn(lambda m: m.group(1) + val.replace('"', "&quot;") + m.group(2), h)
    return h2, n

head = re.sub(r"<title>.*?</title>", f"<title>{TITLE} — 觅理律师事务所</title>", head, flags=re.S)
for key in [("meta", "description"), ("meta", "keywords"), ("meta", "og:title"), ("meta", "og:description"),
            ("meta", "og:url"), ("meta", "og:image"), ("meta", "og:site_name"), ("meta", "twitter:title"),
            ("meta", "twitter:description"), ("meta", "twitter:image"), ("meta", "author")]:
    v = {"description": DESC, "keywords": KEYWORDS, "og:title": TITLE,
         "og:description": DESC, "og:url": URL, "og:image": f"https://najieip.com/img/{SLUG}.png",
         "og:site_name": "觅理律师事务所", "twitter:title": TITLE, "twitter:description": DESC,
         "twitter:image": f"https://najieip.com/img/{SLUG}.png", "author": "何自刚"}[key[1]]
    head, _ = sub_attr(head, key, v)
head = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + URL + m.group(2), head)
head = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', lambda m: m.group(1) + URL + m.group(2), head)

# JSON-LD 覆写
def fix_ld(h):
    blocks_ld = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S))
    out = h
    for m in reversed(blocks_ld):
        o = json.loads(m.group(1))
        t = o.get("@type")
        if t == "Article" or t == "NewsArticle" or t == "BlogPosting":
            o["headline"] = TITLE
            o["description"] = DESC
            o["image"] = f"https://najieip.com/img/{SLUG}.png"
            o["datePublished"] = DATE
            o["dateModified"] = DATE
            o["keywords"] = KEYWORDS.split(",")
            if "mainEntityOfPage" in o:
                o["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
            if "url" in o:
                o["url"] = URL
            if "author" in o:
                o["author"] = {"@type": "Person", "name": "何自刚"}
        elif t == "BreadcrumbList":
            try:
                els = o["itemListElement"]
                if len(els) >= 3:
                    els[2]["name"] = TITLE
                    els[2]["item"] = URL
            except Exception:
                pass
        o = {"@context": "https://schema.org", **{k: v for k, v in o.items() if k != "@context"}}
        out = out[:m.start()] + '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>' + out[m.end():]
    return out

head = fix_ld(head)

# ---------- 3. 拼页 ----------
body_rest = re.sub(r"<article>.*?</article>", article_html, body_rest, count=1, flags=re.S)
# zh_quotes 只作用于 body：head 里的 JSON-LD 脚本体不是标签，被一起中文化会导致 json.loads 失败
newpage = head + zh_quotes(body_rest)

# ---------- 4. 断言 ----------
fails = []
if len(re.findall(r"<h1[ >]", newpage)) != 1: fails.append("h1")
lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', newpage, re.S)
if len(lds) != 2: fails.append(f"ld={len(lds)}")
for l in lds:
    try: json.loads(l)
    except Exception as e: fails.append("ldjson:" + str(e)[:40])
if newpage.count("https://schema.org") != 2: fails.append(f"ctx={newpage.count('https://schema.org')}")
if 'og:image' not in newpage: fails.append("ogimage")
if newpage.count("**") != 0: fails.append(f"stars={newpage.count('**')}")
if '"' in re.sub(r"<[^>]+>", "", re.sub(r"<script.*?</script>|<style.*?</style>", " ", newpage, flags=re.S)): fails.append("ascii_quote_in_text")
# md 全文包含
mdt = re.sub(r"^---.*?---\s*", "", open(MD, encoding="utf-8").read(), flags=re.S)
mdt = re.sub(r"<!--.*?-->", "", mdt, flags=re.S)
mlines = []
for line in mdt.splitlines():
    s = line.strip()
    if not s: continue
    if re.fullmatch(r"\*\*[^*\n]{1,30}\*\*", s) and s.strip("*") in HEADINGS: continue
    if re.match(r"^\d+\.\s", s): s = re.sub(r"^\d+\.\s*", "", s)
    mlines.append(s.replace("**", "").replace("*", ""))
mdn = textify("".join(mlines))
mdn = mdn.replace(textify("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰"), "")
art = re.search(r"<article>.*?</article>", newpage, re.S).group(0)
pgn = textify(art).replace(textify("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰"), "")
contained = mdn in pgn
if not contained:
    d = 0
    while d < min(len(mdn), len(pgn)) and mdn[d] == pgn[d]: d += 1
    fails.append(f"md_not_contained diff_at={d} md={mdn[d:d+40]!r} pg={pgn[d:d+40]!r}")
print(f"new_size={len(newpage.encode())}B  md_len={len(mdn)} pg_len={len(pgn)} contained={contained}")
print("h2 =", len(re.findall(r"<h2[ >]", newpage)))
print("FAILS:", fails if fails else "NONE")

# ---------- 5. 封面 ----------
cands = sorted(glob.glob(os.path.join(ART_DIR, "*face-recognition*.png"))) + \
        sorted(glob.glob(os.path.join(ART_DIR, "*20261114*face*.png")))
print("cover candidates:", [os.path.basename(c) for c in cands])
cover = cands[0] if cands else None

if APPLY and not fails:
    open(TARGET, "w", encoding="utf-8").write(newpage)
    print("WROTE", TARGET, len(newpage.encode()), "B")
    if cover:
        dst = os.path.join(REPO, "img", SLUG + ".png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(cover, dst)
        print("COVER ->", dst, os.path.getsize(dst), "B")
elif APPLY:
    print("NOT WRITTEN (asserts failed)")
