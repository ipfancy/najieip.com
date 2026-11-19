#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 夜班巡检：近 3 日新文五段检查（只读，不改任何文件）"""
import os, re, json, subprocess, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

# 1) 近 3 日新增/修改的文章页（git）
files = sh(f'cd {REPO} && git log --since=3.days --name-only --diff-filter=AM --pretty=format: -- "*/blog/*.html" "blog/*.html"')
pages = sorted({f.strip() for f in files.splitlines() if f.strip().endswith(".html") and "index.html" not in f})
print("=== 近3日 git 触及文章页 ===")
for p in pages: print(" ", p)

# 2) .published.json 近 3 日
print("\n=== .published.json 近3日 ===")
pj_path = os.path.join(ART, ".published.json")
pub = []
if os.path.exists(pj_path):
    try:
        d = json.load(open(pj_path))
        items = d if isinstance(d, list) else d.get("articles", d.get("published", []))
        if isinstance(items, dict): items = list(items.values())
        for it in items:
            if not isinstance(it, dict): continue
            ts = str(it.get("published_at") or it.get("date") or "")
            if ts[:10] >= "2026-11-16":
                pub.append(it)
                print(" ", ts[:19], it.get("slug") or it.get("article_id") or "?")
    except Exception as e:
        print("  ERR", e)

# 3) 页面存在性 + 六项
print("\n=== 页面六项检查 ===")
NO_H1_MSG = []
for p in pages:
    fp = os.path.join(REPO, p)
    if not os.path.exists(fp):
        print(f"  MISSING-FILE {p}"); continue
    t = open(fp, encoding="utf-8", errors="ignore").read()
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = "og:image" in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = ti.group(1).strip() if ti else ""
    bare_tbl = len(re.findall(r"<p>\s*\|", t))
    stars = len(re.findall(r"(?<![0-9*])\*\*", t))
    bodytxt = re.sub(r"<[^>]+>", "", t)
    dup = desc.strip() and (desc.strip() == title.strip() or desc.strip() in title)
    flags = []
    if h1 != 1: flags.append(f"h1={h1}")
    if ld < 2: flags.append(f"ld={ld}")
    if not ogimg: flags.append("no-og:image")
    if dup: flags.append("desc=title")
    if bare_tbl: flags.append(f"bareTable={bare_tbl}")
    if stars: flags.append(f"**={stars}")
    print(f"  {'OK   ' if not flags else 'DEFECT'} {p}  size={os.path.getsize(fp)} ld={ld} h1={h1} {' '.join(flags)}")

# 4) 索引卡
print("\n=== 索引卡检查 ===")
idx = {
    "main": os.path.join(REPO, "blog/index.html"),
    "mili": os.path.join(REPO, "mili/blog/index.html"),
    "najie": os.path.join(REPO, "najie/blog/index.html"),
    "aipunajie": os.path.join(REPO, "aipunajie/blog/index.html"),
}
idxt = {k: open(v, encoding="utf-8", errors="ignore").read() for k, v in idx.items() if os.path.exists(v)}
for p in pages:
    slug = os.path.basename(p)[:-5]
    brand = p.split("/")[0] if "/" in p else "blog"
    row = []
    for k, t in idxt.items():
        n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), t))
        row.append(f"{k}={n}")
    live = sh(f'curl -s -o /dev/null -w "%{{http_code}}" --max-time 30 -A "Mozilla/5.0" "https://najieip.com/{p}"')
    print(f"  {slug[:52]:52s} brand={brand:10s} {' '.join(row)} live={live}")

# 5) articles.json top6
print("\n=== articles.json 前6位 ===")
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
arr = aj if isinstance(aj, list) else aj.get("articles", [])
for i, it in enumerate(arr[:6]):
    u = it.get("url", "")
    fp = os.path.join(REPO, u.lstrip("/"))
    print(f"  {i+1}. {u[:70]:70s} page={'YES' if os.path.exists(fp) else 'NO!!!'}")
print(f"  total={len(arr)}")
