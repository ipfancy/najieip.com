#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-11-26 夜班：修复打赏主播文（裸发布）+ 招贤帖 h1 重复/缺 Breadcrumb。
用法: python3 fix-1126-page.py [--apply]
"""
import os, re, sys, shutil, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
APPLY = "--apply" in sys.argv
SITE = "https://najieip.com"

def rd(p):
    return open(p, encoding="utf-8").read()
def wr(p, s):
    open(p, "w", encoding="utf-8").write(s)

def zh_quotes(s):
    out = []
    dq = 0
    sq = 0
    for ch in s:
        if ch == '"':
            out.append("“" if dq % 2 == 0 else "”"); dq += 1
        elif ch == "'":
            out.append("‘" if sq % 2 == 0 else "’"); sq += 1
        else:
            out.append(ch)
    return "".join(out)

def md_to_blocks(md):
    md = md.replace("\r\n", "\n")
    # strip frontmatter
    if md.startswith("---"):
        end = md.find("\n---", 3)
        if end != -1:
            md = md[end + 4:]
    blocks = []
    for raw in re.split(r"\n\s*\n", md.strip()):
        b = raw.strip()
        if not b:
            continue
        if b.startswith("<!--"):
            continue
        if b.startswith("## "):
            blocks.append(("h2", b[3:].strip()))
        elif b.startswith("# "):
            continue
        else:
            body = b.replace("\n", "")
            body = zh_quotes(body)
            body = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", body)
            blocks.append(("p", body))
    return blocks

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<h[1-6].*?</h[1-6]>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    for ch in '"“”\'‘’>|:*- 　':
        s = s.replace(ch, "")
    return re.sub(r"\s+", "", s)

def norm(s):
    for ch in '"“”\'‘’>|:*- 　':
        s = s.replace(ch, "")
    return re.sub(r"\s+", "", s)

# ---------- 1. 打赏主播文整页重建 ----------
SLUG = "20261126-mili-livestream-tip-divorce-recovery"
TARGET = f"{REPO}/mili/blog/{SLUG}.html"
HOUSE = f"{REPO}/mili/blog/20261121-mili-divorce-game-account-88w.html"
MD = f"{ART}/{SLUG}.md"
TITLE = "打赏主播的钱，离婚能追回吗：婚姻家庭编解释二第6条"
DESC = ("丈夫打赏87万，妻子一分没追回；另一案打赏124.87万，追回34.58万。解释（二）第六条把打赏定为"
        "“挥霍”，只在夫妻内部分割里少分或不分，条文没让平台退钱。真要把钱拿回来，得走第七条起诉主播，"
        "而且只追主播分成那部分——三个判例拼出的真实比例是三到五成。")

def build_livestream():
    house = rd(HOUSE)
    md = rd(MD)
    blocks = md_to_blocks(md)
    n_h2 = sum(1 for k, _ in blocks if k == "h2")
    art_parts = [f"<h1>{TITLE}</h1>"]
    for k, v in blocks:
        art_parts.append(f"<{k}>{v}</{k}>")
    art_html = "\n".join(art_parts)

    # head 重写：按原始 </head> 偏移切 body
    head_end = house.find("</head>") + 7
    head = house[:head_end]
    body_rest = house[head_end:]
    url = f"{SITE}/mili/blog/{SLUG}.html"
    img = f"{SITE}/img/{SLUG}.png"

    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE} — 纳杰觅理</title>", head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{DESC}">', head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">',
                  f'<meta property="og:title" content="{TITLE}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  f'<meta property="og:description" content="{DESC}">', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*">',
                  f'<meta property="og:url" content="{url}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">',
                  f'<link rel="canonical" href="{url}">', head)
    # og:image / og:site_name / twitter 补件
    if "og:image" not in head:
        head = head.replace("</head>",
            f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:site_name" content="纳杰觅理">\n'
            f'<meta name="twitter:title" content="{TITLE}">\n'
            f'<meta name="twitter:description" content="{DESC}">\n'
            f'<meta name="twitter:image" content="{img}">\n</head>')
    head = head.replace('<meta name="twitter:card" content="summary">',
                        '<meta name="twitter:card" content="summary_large_image">')

    # JSON-LD 块：deepcopy 覆写（不用 format / 占位符）
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
    new_lds = []
    for blk in lds:
        o = json.loads(blk)
        def deep_rewrite(x):
            if isinstance(x, dict):
                if x.get("@type") == "Article":
                    x["headline"] = TITLE
                    x["description"] = DESC
                    x["datePublished"] = "2026-11-26"
                    x["dateModified"] = "2026-11-26"
                    x["mainEntityOfPage"] = url
                    x["image"] = img
                    x.setdefault("@context", "https://schema.org")
                if x.get("@type") == "BreadcrumbList":
                    els = x.get("itemListElement", [])
                    if len(els) >= 3:
                        els[2]["name"] = TITLE
                        els[2]["item"] = url
                    x.setdefault("@context", "https://schema.org")
                for v in x.values():
                    deep_rewrite(v)
            elif isinstance(x, list):
                for v in x:
                    deep_rewrite(v)
        deep_rewrite(o)
        new_lds.append(json.dumps(o, ensure_ascii=False, indent=2))

    for old, new in zip(lds, new_lds):
        head = head.replace(old, new, 1)

    # body: 替换 article 内容
    a0 = body_rest.find("<article>") + len("<article>")
    a1 = body_rest.find("</article>")
    body_new = body_rest[:a0] + "\n" + art_html + "\n" + body_rest[a1:]
    page = head + body_new

    # 断言
    pg_raw = page[page.find("<article"):page.find("</article>")]
    pg_raw = re.sub(r"<h1.*?</h1>", " ", pg_raw, flags=re.S)
    pg_txt = norm(re.sub(r"<[^>]+>", "", pg_raw))
    md_body = md
    if md_body.startswith("---"):
        parts = md_body.split("\n---", 1)
        md_body = parts[1][4:] if len(parts) > 1 else md_body
    md_txt = norm(md_body).replace("##", "").replace("**", "").replace("*", "")
    contained = md_txt in pg_txt
    checks = {
        "h1": page.count("<h1") == 1,
        "ld_blocks": page.count("application/ld+json") >= 2,
        "og_image": "og:image" in page,
        "desc_not_title": DESC.strip() != TITLE.strip(),
        "stars": len(re.findall(r"(?<![0-9*])\*\*", page)) == 0,
        "schema_ctx": page.count("https://schema.org") == page.count("application/ld+json"),
        "md_contained": contained,
        "h2": page.count("<h2") == n_h2,
    }
    for b in new_lds:
        json.loads(b)
    print("LIVESTREAM checks:", checks, "size", len(page), "h2", n_h2)
    if APPLY and all(checks.values()):
        wr(TARGET, page)
        cov = f"{ART}/cover-{SLUG}.png"
        if os.path.exists(cov):
            shutil.copy(cov, f"{REPO}/img/{SLUG}.png")
            print("  cover copied ->", os.path.getsize(f"{REPO}/img/{SLUG}.png"), "bytes")
    return all(checks.values())

# ---------- 2. 招贤帖：h1 去重 + 补 BreadcrumbList ----------
COMM = f"{REPO}/mili/blog/20261126-mili-committees-recruitment.html"

def fix_committees():
    t = rd(COMM)
    h1s = [m.start() for m in re.finditer(r"<h1[^>]*>", t)]
    ok = True
    if len(h1s) == 2:
        # 第二个 h1 → 副标题 p
        second = h1s[1]
        end = t.find("</h1>", second) + 5
        seg = t[second:end]
        sub = re.sub(r"</?h1[^>]*>", "", seg).strip()
        t = t[:second] + f'<p class="lede"><strong>{sub}</strong></p>' + t[end:]
    # 补 BreadcrumbList（若缺）
    if '"BreadcrumbList"' not in t:
        house = rd(HOUSE)
        bl = re.search(r'<script type="application/ld\+json">(\{"@context".*?"BreadcrumbList".*?)</script>', house, re.S)
        if bl:
            o = json.loads(bl.group(1))
            url = f"{SITE}/mili/blog/20261126-mili-committees-recruitment.html"
            ttl = "觅理专业委员会公开招人：不问所别，只问手上有没有真功夫"
            els = o.get("itemListElement", [])
            if len(els) >= 3:
                els[2]["name"] = ttl
                els[2]["item"] = url
            blk = json.dumps(o, ensure_ascii=False, indent=2)
            t = t.replace("</head>", f'<script type="application/ld+json">{blk}</script>\n</head>', 1)
    checks = {"h1_one": t.count("<h1") == 1,
              "ld2": t.count("application/ld+json") >= 2,
              "og_image": "og:image" in t}
    print("COMMITTEES checks:", checks, "size", len(t))
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        json.loads(m)
    if APPLY:
        wr(COMM, t)
    return checks

ok1 = build_livestream()
ok2 = fix_committees()
print("RESULT:", "OK" if (ok1 and ok2["h1_one"] and ok2["ld2"]) else "ISSUES", "| apply=", APPLY)
