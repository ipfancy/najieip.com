#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 1014 巡检：近3日页面六联判据 + 索引缺口(href归一) + 结构基线"""
import os, re, json, subprocess, collections

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

# ---------- 1. 近3日 git 触及的 html ----------
files = [f for f in sh("git log --since='3 days ago' --name-only --pretty=format: | sort -u").split("\n")
         if f.strip().endswith(".html") and os.path.exists(f.strip())]
files = [f.strip() for f in files]

print("=== 1. 近3日页面六联判据 ===")
defects = []
for f in files:
    t = open(f, encoding="utf-8", errors="ignore").read()
    idx = os.path.basename(f) == "index.html"
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = t.count("application/ld+json")
    ogi = "og:image" in t
    md = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', t)
    tt = re.search(r"<title>(.*?)</title>", t, re.S)
    desc = md.group(1) if md else ""
    title = re.sub(r"\s+", " ", tt.group(1)).strip() if tt else ""
    rep = bool(desc) and bool(title) and (desc.strip()[:24] == title.strip()[:24])
    stars = t.count("**")
    naked = len(re.findall(r"<p>\|.*?\|</p>", t))
    style = ("<style>" in t) or ("/style.css" in t)
    issues = []
    if not idx and h1 != 1: issues.append(f"h1={h1}")
    if ld < 2: issues.append(f"ld={ld}")
    if not ogi: issues.append("no-og:image")
    if rep: issues.append("desc-repeat")
    if stars: issues.append(f"stars={stars}")
    if naked: issues.append(f"naked-table={naked}")
    # 引号截断快检
    for prop in ("og:title", "og:description", "twitter:title", "twitter:description"):
        m = re.search(r'property="%s"\s+content="([^"]*)"|name="%s"\s+content="([^"]*)"' % (prop, prop), t)
        v = (m.group(1) or m.group(2)) if m else None
        if v is not None and len(v) < 40 and prop.endswith("description"):
            issues.append(f"short-{prop}")
    if issues:
        defects.append((f, issues))
    print(("  DEFECT " if issues else "  OK     ") + f + ("  " + ", ".join(issues) if issues else ""))

# ---------- 2. 索引缺口（href 归一） ----------
print("\n=== 2. 索引缺口（品牌索引 href 归一 vs 主索引） ===")
main = open("blog/index.html", encoding="utf-8", errors="ignore").read()
brands = {"mili": "mili/blog/index.html", "najie": "najie/blog/index.html"}
def abslinks(t, base):
    out = set()
    for h in re.findall(r'<h2><a href="([^"]+)"', t):
        if h.startswith("./"):
            h = base + "/" + h[2:]
        out.add("/" + h.lstrip("/"))
    return out
missing = []
for b, p in brands.items():
    t = open(p, encoding="utf-8", errors="ignore").read()
    for link in sorted(abslinks(t, "/%s/blog" % b)):
        fn = link.rsplit("/", 1)[-1]
        # 跳过非文章/跳转壳/架构图
        fp = ROOT + link if os.path.exists(ROOT + link) else None
        if fp is None:
            continue
        if os.path.getsize(fp) < 1500 or 'http-equiv="refresh"' in open(fp, encoding="utf-8", errors="ignore").read():
            continue
        if fn not in main:
            missing.append((b, link))
print("  主索引真缺口:", len(missing))
for m in missing: print("   MISSING", m)

# ---------- 3. articles.json ----------
print("\n=== 3. articles.json ===")
d = json.load(open("articles.json"))
arts = d if isinstance(d, list) else d.get("articles", [])
bad = []
for a in arts:
    u = a.get("url") or a.get("path") or ""
    if not u: bad.append(("no-url", a.get("title"))); continue
    fp = ROOT + u
    if not os.path.exists(fp): bad.append(("no-file", u))
print("  total=%d  violations=%d" % (len(arts), len(bad)))
for b in bad[:10]: print("   ", b)
print("  top6:")
for a in arts[:6]:
    u = a.get("url") or ""
    ex = "HIT " if os.path.exists(ROOT + u) else "MISS"
    print("   %s %s" % (ex, u))
