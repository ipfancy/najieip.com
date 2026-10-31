#!/usr/bin/env python3
"""Insert index cards for 2026-10-31 articles into brand indexes + main index."""
import os, re, sys, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv
NEWDATE = "2026-10-31"

ITEMS = [
    # (brand_dir, slug, title, desc, tags)
    ("najie", "20261031-najie-specialized-sme-patent-screen",
     "专利凑数，专精特新认定真会被查出来",
     "工信厅联企业〔2026〕40号引入「专利前端排查机制」：排查专利异常、评价专利质量，对指标异常、数据矛盾、突增突减重点核查，造假企业取消认定且三年内不得再申报。本文给3条当天可执行的自查线。",
     ["专精特新", "专利质量"]),
    ("najie", "20261031-mili-ai-product-image-review-tool-neutrality",
     "「工具中立」还能用多久？反不正当竞争法第13条堵死了AI刷好评",
     "新反法把「帮别人刷」单列为违法行为（第9条第2款，上限200万），并把「数据和算法」写进第13条手段清单（攻击同行最高500万）。含AI商品图打标不等于免责的边界与电商、工具商各5条自查线。",
     ["反不正当竞争", "AI合规"]),
    ("mili", "20261031-mili-mofcom-trade-secret-sanctions",
     "外国公司偷你的技术，现在可以请商务部出手了",
     "商务部2026年10月26日发布《保护中国商业秘密特别规定（征求意见稿）》，意见截止11月24日。外国实体在经贸活动中侵害中国商业秘密并危害国家安全的，可被列入清单、限制贸易与投资。本文拆解适用路径与企业可做的事。",
     ["商业秘密", "涉外"]),
]

def cards_with_pos(t):
    """return list of (start, end, date) for each article-card div via depth pairing"""
    res = []
    for m in re.finditer(r'<div class="article-card">', t):
        start = m.start()
        i = m.end() - 1
        depth = 0
        end = None
        while i < len(t):
            no = t.find("<div", i + 1)
            nc = t.find("</div>", i + 1)
            if nc == -1:
                break
            if no != -1 and no < nc:
                depth += 1
                i = no + 4
            else:
                if depth == 0:
                    end = nc + len("</div>")
                    break
                depth -= 1
                i = nc + 5
        if end:
            blk = t[start:end]
            d = re.search(r"(\d{4}-\d{2}-\d{2})", blk)
            res.append((start, end, d.group(1) if d else ""))
    return res

def esc_attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

def make_card(tpl, href, title, desc, tags, date, is_main):
    b = tpl
    b = re.sub(r'(<h[23]><a href=")[^"]*(")', lambda m: m.group(1) + href + m.group(2), b, count=1)
    b = re.sub(r'(<a href="[^"]*"[^>]*>)[^<]*(</a>)', lambda m: m.group(1) + esc_attr(title) + m.group(2), b, count=1)
    taghtml = " ".join(f'<span class="tag">{esc_attr(x)}</span>' for x in tags)
    b2, n = re.subn(r'(?:<span class="tag">[^<]*</span>\s*)+', taghtml + " ", b, count=1)
    if n:
        b = b2
    b = re.sub(r"\d{4}-\d{2}-\d{2}", date, b)
    b = re.sub(r"(<p>)[^<]*(</p>)", lambda m: m.group(1) + esc_attr(desc) + m.group(2), b, count=1)
    return b

def process(index_path, brand=None, items=None):
    t = open(index_path, encoding="utf-8").read()
    blocks = cards_with_pos(t)
    if not blocks:
        print("NO CARDS in", index_path); return None
    tpl = t[blocks[0][0]:blocks[0][1]]
    is_main = os.path.dirname(os.path.abspath(index_path)) == os.path.join(REPO, "blog")
    made = 0
    for brand_dir, slug, title, desc, tags in items:
        if brand and brand_dir != brand:
            continue
        href = f"/{brand_dir}/blog/{slug}.html" if is_main else f"./{slug}.html"
        key = slug
        if key in t:
            print("SKIP (already present):", key); continue
        date = NEWDATE
        ins = None
        for (s, e, d) in cards_with_pos(t):
            if d and d < date:
                ins = s
                break
        card = make_card(tpl, href, title, desc, tags, date, is_main)
        if ins is None:
            idx = t.find("</div>", t.rfind('<div class="article-card">'))
            print("no position found; abort", key); return None
        t = t[:ins] + card + "\n  " + t[ins:]
        made += 1
        print("INSERTED", key, "->", os.path.relpath(index_path, REPO))
    return t, made

report = {}
targets = [
    (os.path.join(REPO, "najie", "blog/index.html"), "najie"),
    (os.path.join(REPO, "mili", "blog/index.html"), "mili"),
    (os.path.join(REPO, "blog", "index.html"), None),
]
for path, brand in targets:
    r = process(path, brand, ITEMS)
    if not r:
        continue
    new_t, made = r
    old_t = open(path, encoding="utf-8").read()
    # validations
    oc = old_t.count('<div class="article-card">')
    nc = new_t.count('<div class="article-card">')
    assert nc == oc + made, f"{path}: cards {oc}->{nc}, made {made}"
    assert new_t.count("<div") - new_t.count("</div>") == old_t.count("<div") - old_t.count("</div>"), "div imbalance"
    assert new_t.count("**") == 0, "stars leaked"
    for _, slug, *_ in ITEMS:
        if brand and _ != brand and path != os.path.join(REPO, "blog", "index.html"):
            continue
    print(f"{os.path.relpath(path, REPO)}: cards {oc} -> {nc}")
    report[path] = new_t
    if APPLY:
        open(path, "w", encoding="utf-8").write(new_t)

if not APPLY:
    # show one sample card
    p = os.path.join(REPO, "najie", "blog/index.html")
    t = report[p]
    m = re.search(r'<div class="article-card">(.*?)2026-10-31', t, re.S)
    print("\nSAMPLE (first 2026-10-31 card context):\n", t[t.find("2026-10-31") - 900: t.find("2026-10-31") + 40])
    print("\nDRY RUN (use --apply)")
else:
    print("APPLIED")
