#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 夜班修复：畸形页精修 + 4 页补 og:image + 封面入库 + articles.json 隔离"""
import os, re, json, copy, shutil, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
APPLY = "--apply" in sys.argv

HOUSE = os.path.join(REPO, "mili/blog/20261118-mili-refusal-execute-five-cases.html")
BAD = "20261119-mili-tv-box-backdoor-four-layers"
BADP = os.path.join(REPO, "mili/blog", BAD + ".html")
MD = os.path.join(ART, BAD + ".md")


def zh_quotes(s):
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("\u201c" if open_q else "\u201d"); open_q = not open_q
        else:
            out.append(ch)
    return "".join(out)


def ld_blocks(t):
    """返回 [(raw_json_str, obj)]"""
    res = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        raw = m.group(1)
        try:
            res.append((raw, json.loads(raw)))
        except Exception as e:
            res.append((raw, {"_parse_error": str(e), "_raw": raw[:120]}))
    return res


# ---------- 1. 读 md 源 ----------
md = open(MD, encoding="utf-8").read()
# 去 frontmatter
if md.startswith("---"):
    end = md.find("\n---", 3)
    if end != -1:
        md = md[end + 4:]
# 去 HTML 注释块（合集/检索词）
md_clean = re.sub(r"<!--.*?-->", "", md, flags=re.S)
lines = [l.rstrip() for l in md_clean.splitlines()]
# 摘要：取首个非标题、非空、较长段落的前 170 字
desc = ""
for l in lines:
    s = l.strip()
    if not s or s.startswith("#") or s.startswith("|") or s.startswith(">"):
        continue
    s2 = re.sub(r"\*\*", "", s)
    if len(s2) > 40:
        desc = s2[:170]
        break
desc = zh_quotes(desc)
print("DESC =", desc)

# ---------- 2. 读原页 & 房屋 ----------
t = open(BADP, encoding="utf-8").read()
house = open(HOUSE, encoding="utf-8").read()

# ---------- 3. head 重建（用原始 </head> 偏移） ----------
orig = t
head_end = t.find("</head>") + 7
head = t[:head_end]
body_rest = t[head_end:]

h1_m = re.search(r"<title>(.*?)</title>", head, re.S)
TITLE = h1_m.group(1).replace(" — 纳杰觅理", "").strip()
URL = "https://najieip.com/mili/blog/" + BAD + ".html"
IMG = "https://najieip.com/img/" + BAD + ".png"

# 房屋 JSON-LD 对象
hlds = [o for _, o in ld_blocks(house) if isinstance(o, dict) and "@type" in o]
art_tpl = next(o for o in hlds if o.get("@type") == "Article")
bc_tpl = next(o for o in hlds if o.get("@type") == "BreadcrumbList")

art = copy.deepcopy(art_tpl)
art = {"@context": "https://schema.org", **{k: v for k, v in art.items() if k != "@context"}}
art["headline"] = TITLE
art["description"] = desc
art["image"] = [IMG]
art["datePublished"] = "2026-11-19"
art["dateModified"] = "2026-11-19"
art["url"] = URL
if "mainEntityOfPage" in art:
    art["mainEntityOfPage"] = {"@type": "WebPage", "@id": URL} if isinstance(art["mainEntityOfPage"], dict) else URL
if "author" in art:
    art["author"] = {"@type": "Person", "name": "何自刚"}
if "publisher" in art:
    art["publisher"] = {"@type": "Organization", "name": "北京觅理律师事务所",
                        "logo": {"@type": "ImageObject", "url": "https://najieip.com/img/logo.png"}}

bc = copy.deepcopy(bc_tpl)
bc = {"@context": "https://schema.org", **{k: v for k, v in bc.items() if k != "@context"}}
if isinstance(bc.get("itemListElement"), list) and len(bc["itemListElement"]) >= 3:
    bc["itemListElement"][2] = {"@type": "ListItem", "position": 3, "name": TITLE, "item": URL}

new_ld = ('<script type="application/ld+json">\n' + json.dumps(art, ensure_ascii=False, indent=1) + '\n</script>\n'
          '<script type="application/ld+json">\n' + json.dumps(bc, ensure_ascii=False, indent=1) + '\n</script>\n')

# 替换/插入 meta
head2 = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{desc}">', head, count=1)
head2 = re.sub(r'<meta property="og:description" content="[^"]*">',
               f'<meta property="og:description" content="{desc}">', head2, count=1)
head2 = head2.replace('<meta name="twitter:card" content="summary">',
                      '<meta name="twitter:card" content="summary_large_image">')
extra = (f'<meta property="og:site_name" content="纳杰觅理">\n'
         f'<meta property="og:image" content="{IMG}">\n'
         f'<meta name="twitter:title" content="{TITLE}">\n'
         f'<meta name="twitter:description" content="{desc}">\n'
         f'<meta name="twitter:image" content="{IMG}">\n'
         f'<meta name="keywords" content="机顶盒后门,固件预置后门,网络安全,刑事风险,何自刚">\n')
head2 = head2.replace("</head>", extra + new_ld + "</head>")

# ---------- 4. body 插 h1（正文一字不改） ----------
body2 = body_rest
if "<h1" not in body2:
    body2 = body2.replace("<article>", f"<article>\n<h1>{TITLE}</h1>", 1)

t2 = head2 + body2

# ---------- 5. 断言 ----------
h1c = len(re.findall(r"<h1[\s>]", t2))
ldc = t2.count("application/ld+json")


def textify(b):
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<h1.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    s = b.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    return re.sub(r"[\s*]+", "", s)


ob = textify(orig[orig.find("<body"):])
nb = textify(t2[t2.find("<body"):])
print(f"h1={h1c} ld={ldc} body_text_unchanged={ob == nb} (orig={len(ob)} new={len(nb)})")
if ob != nb:
    import difflib
    d = list(difflib.unified_diff([ob[i:i+40] for i in range(0, len(ob), 40)],
                                  [nb[i:i+40] for i in range(0, len(nb), 40)], lineterm="", n=1))
    print("DIFF:", "\n".join(d[:12]))

# md 包含断言（只取 article 区间）
mda = re.sub(r"(?m)^\s*#.*$", "", md_clean)
mda = re.sub(r"<!--.*?-->", "", mda, flags=re.S)
mda = re.sub(r"(?m)^\s*\*\*([^*\n]{1,30})\*\*\s*$", "", mda)
mda = re.sub(r"(?m)^\s*[一二三四五六七八九十]、.*$", "", mda)
mda_n = re.sub(r"[\s*\"\u201c\u201d'`|:\-]+", "", mda)
m_art = re.search(r"<article>.*?</article>", t2, re.S)
pg = m_art.group(0) if m_art else t2
pg = re.sub(r"<h[1-6].*?</h[1-6]>", " ", pg, flags=re.S)  # 页面侧剥标题文字（md 侧已整行丢弃）
pg_n = re.sub(r"<[^>]+>", "", pg)
pg_n = re.sub(r"[\s*\"\u201c\u201d'`|:\-]+", "", pg_n)
BYLINE_MD = "何自刚|知识产权律师|爱普纳杰·觅理·纳杰"
mda_n = mda_n.replace(re.sub(r"[\s*|·]+", "", BYLINE_MD), "")
print(f"md_contained={mda_n in pg_n} md={len(mda_n)} page={len(pg_n)}")

if not APPLY:
    print("[DRY-RUN] 未写盘")
    sys.exit(0)

open(BADP, "w", encoding="utf-8").write(t2)
print("WRITE bad page OK", os.path.getsize(BADP))

# ---------- 6. 封面入库 ----------
src_cover = os.path.join(ART, "cover-" + BAD + ".png")
dst_cover = os.path.join(REPO, "img", BAD + ".png")
os.makedirs(os.path.dirname(dst_cover), exist_ok=True)
if os.path.exists(src_cover):
    shutil.copy2(src_cover, dst_cover)
    print("COVER copied", os.path.getsize(dst_cover))

# ---------- 7. 其余 4 页补 og:image ----------
others = ["aipunajie/blog/20261119-aipu-pct-30-months.html",
          "mili/blog/20261118-mili-foreign-law-proof.html",
          "mili/blog/20261119-mili-ai-law-firm-boundary.html",
          "mili/blog/20261119-mili-dooring-case.html"]
for rel in others:
    fp = os.path.join(REPO, rel)
    x = open(fp, encoding="utf-8").read()
    if "og:image" in x:
        print("SKIP has og:image", rel); continue
    slug = os.path.basename(rel)[:-5]
    img = f"https://najieip.com/img/{slug}.png"
    if not os.path.exists(os.path.join(REPO, "img", slug + ".png")):
        print("NO-IMG-FILE", rel, "→ skip"); continue
    add = f'<meta property="og:image" content="{img}">\n<meta name="twitter:image" content="{img}">\n'
    if 'name="twitter:image"' in x:
        add = f'<meta property="og:image" content="{img}">\n'
    if "og:site_name" not in x:
        add += '<meta property="og:site_name" content="纳杰觅理">\n'
    x2 = x.replace("</head>", add + "</head>", 1)
    # twitter:card 升级
    x2 = x2.replace('<meta name="twitter:card" content="summary">',
                    '<meta name="twitter:card" content="summary_large_image">')
    if textify(x2[x2.find("<body"):]) != textify(x[x.find("<body"):]):
        print("BODY-CHANGED ABORT", rel); continue
    open(fp, "w", encoding="utf-8").write(x2)
    print("OG-IMG added", rel, os.path.getsize(fp))
