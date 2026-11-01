import os, re, json, copy, shutil

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

SLUG = "20261101-najie-ip-foreign-transfer-review"
BRAND = "najie"
PAGE = f"{BRAND}/blog/{SLUG}.html"
TPL = f"{BRAND}/blog/20261031-najie-specialized-sme-patent-screen.html"
BASE = "https://najieip.com"
URL = f"{BASE}/{BRAND}/blog/{SLUG}.html"
IMG = f"{BASE}/img/{SLUG}.png"
TITLE = "专利出海还有第二道闸：试行8年，多数企业不知道要报"
DESC = ("《知识产权对外转让有关工作办法（试行）》2018年3月18日印发，试行至今已第八年，覆盖专利、"
        "集成电路布图设计专有权、计算机软件著作权、植物新品种权四类（商标不在其中）；三种动作需审："
        "权利人变更、实际控制人变更、独占实施许可，且是「先证后约」——未取得《技术出口许可意向书》"
        "不得实质性谈判或签约。本文拆四个常见误判，给出签约前五问自检表，并附2026年第48号公告的先行登记要求。")
KW = "知识产权对外转让,技术出口许可意向书,专利出海,独占许可,技术出口审查,2026年第48号公告"

t = open(PAGE, encoding="utf-8").read()
head_end = t.find("</head>") + 7
body = t[head_end:]
h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S).group(1)
assert re.sub(r"<[^>]+>", "", h1).strip() == TITLE, "title mismatch"

# template json-ld objects
tt = open(TPL, encoding="utf-8").read()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tt, re.S)
assert len(blocks) == 2, f"tpl ld count={len(blocks)}"
art, brd = [json.loads(b) for b in blocks]

art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMG
art["datePublished"] = "2026-11-01"
art["dateModified"] = "2026-11-01"
art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL}
art["url"] = URL
art["keywords"] = KW
art["author"]["worksFor"]["url"] = f"{BASE}/{BRAND}/"
brd["itemListElement"][1]["name"] = "纳杰博客"
brd["itemListElement"][1]["item"] = f"{BASE}/{BRAND}/blog/"
brd["itemListElement"][2]["name"] = TITLE
brd["itemListElement"][2]["item"] = URL

ld1 = json.dumps(art, ensure_ascii=False)
ld2 = json.dumps(brd, ensure_ascii=False)

new_head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<meta name="description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:site_name" content="纳杰知产">
<meta property="og:locale" content="zh_CN">
<meta name="keywords" content="{KW}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{IMG}">
<link rel="canonical" href="{URL}">
<link rel="alternate" hreflang="zh-CN" href="{URL}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<link rel="stylesheet" href="/style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<script type="application/ld+json">{ld1}</script>
<script type="application/ld+json">{ld2}</script>
</head>"""

def zh_quotes(s):
    return re.sub(r'"([^"\n]{1,300})"', "“\\1”", s)

parts = re.split(r"(<[^>]+>)", body)
for i in range(0, len(parts), 2):
    parts[i] = zh_quotes(parts[i])
new_body = "".join(parts)

def textify(h):
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", "", h)

assert textify(new_body) == textify(body), "body text changed!"
t2 = new_head + new_body
open(PAGE, "w", encoding="utf-8").write(t2)

# cover image
src = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-{SLUG}.png")
if not os.path.exists(src):
    alt = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-2026{SLUG[4:]}.png")
    src = alt if os.path.exists(alt) else None
print("cover src:", src)
if src:
    dst = f"img/{SLUG}.png"
    shutil.copyfile(src, dst)
    print("copied ->", dst, os.path.getsize(dst))

# verify
checks = {}
checks["h1"] = t2.count("<h1")
checks["ld"] = len(re.findall(r'application/ld\+json', t2))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    json.loads(b)
checks["ld_parse"] = "OK"
checks["og_image"] = t2.count('property="og:image"')
checks["stars"] = t2.count("**")
checks["bare_table"] = len(re.findall(r"<p>\s*\|", t2))
m = re.search(r'<meta name="description" content="([^"]*)"', t2)
checks["desclen"] = len(m.group(1))
checks["desc_repeat"] = m.group(1)[:20] == TITLE[:20]
checks["size"] = len(t2.encode())
print(json.dumps(checks, ensure_ascii=False))
