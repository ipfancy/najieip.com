#!/usr/bin/env python3
"""SiteOps 1021晚：新页六联判据 + 三索引/articles.json/sitemap 收录比对"""
import os, re, json, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

NEW = [
    "mili/blog/20261022-judge-liability-verdict-reversed.html",
    "mili/blog/20261021-3gpp-proposal-prior-art-date.html",
    "najie/blog/20261021-goods-names-acceptable-list-q4.html",
]

def read(p):
    return open(p, encoding="utf-8").read()

print("="*70)
print("A. 六联判据（近3日新页）")
print("="*70)
for f in NEW:
    if not os.path.exists(f):
        print(f"  MISSING FILE: {f}")
        continue
    t = read(f)
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = t.count("application/ld+json")
    ogimg = 'property="og:image"' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    title = tm.group(1).strip() if tm else ""
    # 标题复读判定：desc 去掉标点后与 title 主干近似
    def norm(s):
        return re.sub(r"[^\w\u4e00-\u9fff]", "", s)
    repeat = bool(desc) and norm(desc) in norm(title) and len(desc) < len(title) + 10
    stars = t.count("**")
    bare_tbl = len(re.findall(r"<p>\s*\|", t))
    style = ("<style>" in t) or ("/style.css" in t)
    print(f"\n  {f}  ({len(t)} chars)")
    print(f"    h1={h1} ld={ld} og:image={ogimg} style={style}")
    print(f"    desc_len={len(desc)} repeat_title={repeat} stars={stars} bare_table_rows={bare_tbl}")
    probs = []
    if h1 != 1: probs.append(f"h1={h1}")
    if ld < 2: probs.append(f"ld={ld}")
    if not ogimg: probs.append("no og:image")
    if repeat: probs.append("desc=title重复")
    if not style: probs.append("no style")
    if stars: probs.append(f"**x{stars}")
    if bare_tbl: probs.append(f"裸表x{bare_tbl}")
    print("    => " + ("OK" if not probs else "缺陷: " + ", ".join(probs)))

print()
print("="*70)
print("B. 索引收录（href 归一比对）")
print("="*70)
idx = {
    "main": ("blog/index.html", "/"),
    "mili": ("mili/blog/index.html", "/mili/blog"),
    "najie": ("najie/blog/index.html", "/najie/blog"),
}
contents = {k: read(p) for k, (p, _) in idx.items()}
for f in NEW:
    slug = os.path.basename(f)[:-5]
    brand = f.split("/")[0]
    key = "/" + f[:-5] + ".html"
    print(f"\n  {slug} (品牌 {brand})")
    for k, (p, _) in idx.items():
        t = contents[k]
        hit = (key in t) or (slug in t)
        print(f"    {k:6s}: {'HIT' if hit else 'MISS'}")
    # 计数
print()
print("  卡片计数: main=%d mili=%d najie=%d" % tuple(
    contents[k].count('<div class="article-card">') for k in ("main","mili","najie")))

print()
print("="*70)
print("C. articles.json / sitemap")
print("="*70)
try:
    aj = json.load(open("articles.json", encoding="utf-8"))
    arts = aj if isinstance(aj, list) else aj.get("articles", [])
    print(f"  articles.json 条目 = {len(arts)}")
    for f in NEW:
        slug = os.path.basename(f)[:-5]
        hit = [a for a in arts if slug in json.dumps(a, ensure_ascii=False)]
        print(f"    {slug}: {'ENTRY' if hit else 'NO-ENTRY'}")
    print("  首页 top6:")
    for i, a in enumerate(arts[:6], 1):
        print(f"    {i}. {a.get('date','')} {str(a.get('title',''))[:34]} -> {a.get('url', a.get('link',''))}")
except Exception as e:
    print("  articles.json ERR:", e)

sm = read("sitemap.xml")
locs = re.findall(r"<loc>(.*?)</loc>", sm)
print(f"  sitemap loc = {len(locs)}")
for f in NEW:
    u = "https://najieip.com/" + f
    print(f"    {os.path.basename(f)}: {'IN' if u in locs else 'MISSING'}")
nomod = [b for b in re.findall(r"<url>(.*?)</url>", sm, re.S) if "<lastmod>" not in b]
print(f"  无 lastmod = {len(nomod)}")
