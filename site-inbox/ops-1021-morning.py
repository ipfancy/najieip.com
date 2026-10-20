#!/usr/bin/env python3
"""SiteOps 10-21 早检：近3日文章页六联判据 + 索引缺口（href 归一）"""
import re, os, subprocess, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

BASE = "https://najieip.com"

# ---- 1. 近 3 日 git 触及的文章页 ----
out = subprocess.run(["git", "log", "--since=3.days", "--name-only", "--diff-filter=AM",
                      "--pretty=format:"], capture_output=True, text=True).stdout
files = sorted({l.strip() for l in out.splitlines()
                if l.strip().endswith(".html") and re.search(r'(mili|najie|aipunajie|blog)/', l)})
files = [f for f in files if not f.endswith("index.html") and os.path.exists(f)]

print("=== 六联判据（近3日触及 %d 页）===" % len(files))
defects = []
for f in files:
    t = open(f, encoding="utf-8", errors="replace").read()
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = 1 if "og:image" in t else 0
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    mt = re.search(r"<title>(.*?)</title>", t, re.S)
    title = mt.group(1).strip() if mt else ""
    dd = desc.replace(" — 纳杰觅理", "").strip()
    rep = 1 if (desc and (desc in title or title.startswith(dd[:20]) and len(desc) < 60)) else 0
    stars = t.count("**")
    bare = len(re.findall(r"<p>\s*\|[^<]*\|", t))
    style = ('<style>' in t) or ('/style.css' in t)
    bad = []
    if h1 == 0: bad.append("h1=0")
    if ld < 2: bad.append("ld=%d" % ld)
    if not ogimg: bad.append("no-og:image")
    if rep: bad.append("desc-repeat")
    if stars: bad.append("**x%d" % stars)
    if bare: bad.append("bare-table x%d" % bare)
    if not style: bad.append("no-style")
    if bad:
        defects.append((f, bad))
        print("  ❌ %-70s %s" % (f, ",".join(bad)))
    else:
        print("  ✅ %-70s h1=%d ld=%d" % (f, h1, ld))
print("缺陷页数:", len(defects))

# ---- 2. 索引缺口（href 归一）----
def hrefs(path, base):
    t = open(path, encoding="utf-8").read()
    hs = re.findall(r'<h2><a href="([^"]+)"', t)
    res = set()
    for h in hs:
        if h.startswith("http"): continue
        if h.startswith("./"): h = base + "/" + h[2:]
        elif h.startswith("/"): pass
        else: h = base + "/" + h
        res.add(h.split("#")[0].split("?")[0])
    return res

main = hrefs("blog/index.html", "/blog")
print("\n=== 索引缺口（主索引 %d 卡）===" % len(main))
total_gap = 0
for brand in ("mili", "najie", "aipunajie"):
    p = os.path.join(brand, "blog", "index.html")
    if not os.path.exists(p): continue
    bs = hrefs(p, "/%s/blog" % brand)
    gaps = []
    for h in sorted(bs):
        f = h.lstrip("/")
        if not os.path.exists(f):
            continue  # 死链另计
        sz = os.path.getsize(f)
        t2 = open(f, encoding="utf-8", errors="replace").read()
        if sz < 1500 or 'http-equiv="refresh"' in t2:
            continue  # 跳转壳/内嵌页
        if h not in main:
            # 假缺口：同一文可能挂别的品牌路径
            slug = os.path.basename(h)[:-5]
            if re.search(r'<h2><a href="[^"]*' + re.escape(slug), open("blog/index.html", encoding="utf-8").read()):
                continue
            gaps.append(h)
    total_gap += len(gaps)
    print("  %-10s 卡 %3d  真缺口 %d" % (brand, len(bs), len(gaps)))
    for g in gaps: print("     GAP", g)
print("真缺口合计:", total_gap)
print("RESULT", json.dumps({"defects": len(defects), "gaps": total_gap}))
