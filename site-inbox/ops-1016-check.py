#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-16 每日巡检 — 诊断段（只读）"""
import os, re, json, glob, sqlite3, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

def rd(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

print("=" * 60)
print("A. site-inbox 未跟踪文件")
print("=" * 60)
for f in sorted(glob.glob("site-inbox/*.html")):
    st = subprocess.run(["git", "status", "--porcelain", "--", f], capture_output=True, text=True).stdout.strip()
    if st:
        t = rd(f)
        print(f"  {f}  bytes={os.path.getsize(f)}  h1={t.count('<h1')}  ld={t.count('application/ld+json')}  "
              f"ogimg={'og:image' in t}  **={t.count('**')}  refresh={'http-equiv=\"refresh\"' in t}")

print()
print("=" * 60)
print("B. 近3日文章在三个索引中的存在性（href 归一）")
print("=" * 60)
conn = sqlite3.connect(os.path.expanduser("~/wiki/database/content.db"))
rows = conn.execute("""SELECT article_id, title, publish_date, source_file FROM articles
                       WHERE publish_date >= date('now','-4 days') ORDER BY publish_date DESC""").fetchall()
idx = {p: rd(p) for p in ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html"]}
for aid, title, pd, sf in rows:
    slug = os.path.basename(sf or "").replace(".md", "") if sf else ""
    print(f"\n  {aid} | {pd} | {title[:40]}")
    print(f"    source_file={sf}")
    for ip, it in idx.items():
        hit = slug and (slug in it)
        print(f"    {'HIT ' if hit else 'MISS'} {ip}")
    # find actual page files
    cands = glob.glob(f"*/blog/{slug}.html") + glob.glob(f"blog/{slug}.html")
    print(f"    pages={cands}")

print()
print("=" * 60)
print("C. 近3日新页「六联」缺陷检查")
print("=" * 60)
recent = subprocess.run(["git", "log", "--name-only", "--since=3.days", "--pretty=format:"],
                        capture_output=True, text=True).stdout.split()
files = sorted(set(f for f in recent if f.endswith(".html") and "/blog/" in f))
for f in files:
    if not os.path.exists(f):
        continue
    if os.path.basename(f) == "index.html":
        print(f"  SKIP(index) {f}")
        continue
    t = rd(f)
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    ogi = 'og:image' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    tit = tm.group(1).split(" — ")[0].strip() if tm else ""
    bad = []
    if h1 != 1: bad.append(f"h1={h1}")
    if ld == 0: bad.append(f"ld={ld}")
    if not ogi: bad.append("no-og:image")
    if desc and desc.replace("&quot;", '"').strip() == tit: bad.append("desc=title复读")
    if t.count("**"): bad.append(f"**={t.count('**')}")
    if re.search(r"<p>\|.*\|</p>", t): bad.append("裸markdown表")
    if '<style>' not in t and '/style.css' not in t: bad.append("no-style")
    print(f"  {'OK  ' if not bad else 'DEFECT'} {f}  {'; '.join(bad)}")

print()
print("=" * 60)
print("D. articles.json 状态 + sitemap loc")
print("=" * 60)
aj = json.load(open("articles.json", encoding="utf-8"))
arts = aj["articles"] if isinstance(aj, dict) else aj
print(f"  articles.json 条目数 = {len(arts)}")
missing = [a for a in arts if not os.path.exists((a.get("url") or "").lstrip("/"))]
print(f"  页面不存在的条目 = {len(missing)}")
sm = rd("sitemap.xml")
print(f"  sitemap loc = {len(re.findall(r'<loc>', sm))}")

print()
print("=" * 60)
print("E. 首页 slice(0,6) 曝光位（articles.json 前6条）")
print("=" * 60)
for i, a in enumerate(arts[:6], 1):
    u = (a.get("url") or "").lstrip("/")
    print(f"  {i}. exists={os.path.exists(u)}  {a.get('url')}")
