#!/usr/bin/env python3
"""SiteOps 每日巡检综合诊断 — 只读，不修改任何文件。"""
import os, re, json, glob, subprocess, sys

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

out = []
def p(*a):
    out.append(" ".join(str(x) for x in a))

# ---------- 1. 近 6 日新增/改动的 HTML 页面 ----------
p("=== [1] 近 6 日 git 触及的页面 ===")
files = sh("git log --since='6 days ago' --name-only --pretty=format: ").split("\n")
files = sorted({f for f in files if f.endswith(".html") and "/blog/" in f})
for f in files:
    if os.path.exists(f):
        p(f"  {os.path.getsize(f):>7}B  {f}")
if not files:
    p("  (无)")

# ---------- 2. 六联缺陷判据 ----------
p("\n=== [2] 六联缺陷扫描（近 6 日页面）===")
def analyze(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    d = {}
    d["h1"] = len(re.findall(r"<h1[\s>]", t))
    d["ld"] = t.count("application/ld+json")
    d["ogimg"] = t.count("og:image")
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', t)
    tt = re.search(r"<title>(.*?)</title>", t, re.S)
    d["desc"] = m.group(1) if m else ""
    d["title"] = re.sub(r"\s*[—\-|]\s*纳杰觅理.*$", "", tt.group(1)).strip() if tt else ""
    d["desc_repeat"] = bool(d["desc"]) and d["desc"].strip()[:24] == d["title"].strip()[:24]
    d["style"] = ("<style>" in t) or ("/style.css" in t)
    d["stars"] = t.count("**")
    d["naked_tbl"] = len(re.findall(r"<p>\s*\|[^<]*\|\s*</p>", t))
    d["size"] = len(t.encode())
    d["refresh"] = 'http-equiv="refresh"' in t
    d["schema_ok"] = t.count("https://schema.org")
    d["schema_bad"] = t.count("https://***")
    return d

defects = []
for f in files:
    if not os.path.exists(f):
        continue
    a = analyze(f)
    if a["size"] < 1500 or a["refresh"]:
        p(f"  [STUB] {f} ({a['size']}B)")
        continue
    bad = []
    if a["h1"] != 1: bad.append(f"h1={a['h1']}")
    if a["ld"] == 0: bad.append("ld=0")
    if a["ogimg"] == 0: bad.append("no-og:image")
    if a["desc_repeat"]: bad.append("desc=title")
    if a["stars"]: bad.append(f"**={a['stars']}")
    if a["naked_tbl"]: bad.append(f"naked_tbl={a['naked_tbl']}")
    if not a["style"]: bad.append("no-style")
    if a["schema_bad"]: bad.append(f"schema_broken={a['schema_bad']}")
    if bad:
        defects.append((f, bad))
        p(f"  [DEFECT] {f} :: {', '.join(bad)}")
    else:
        p(f"  [OK] {f}")
if not defects:
    p("  -> 近 6 日窗口零缺陷")

# ---------- 3. 索引缺口（href 归一）----------
p("\n=== [3] 主索引 vs 品牌索引缺口 ===")
main = open("blog/index.html", encoding="utf-8").read()
def cards(path):
    t = open(path, encoding="utf-8").read()
    return re.findall(r'<h2><a href="([^"]+)"', t)
brands = {"mili": "mili/blog/index.html", "najie": "najie/blog/index.html"}
gaps = []
for b, idx in brands.items():
    if not os.path.exists(idx):
        continue
    for href in cards(idx):
        key = href if href.startswith("/") else "/" + b + "/blog/" + href.lstrip("./")
        fn = key.rsplit("/", 1)[-1]
        if fn not in main:
            # 排除 stub/架构图
            local = key.lstrip("/")
            if os.path.exists(local):
                t2 = open(local, encoding="utf-8", errors="replace").read()
                if len(t2.encode()) < 1500 or 'http-equiv="refresh"' in t2 or t2.count("application/ld+json") == 0:
                    p(f"  [skip-架构图/stub] {key}")
                    continue
            gaps.append((b, key))
            p(f"  [GAP:{b}] {key}")
if not gaps:
    p("  -> 真缺口 0")

# ---------- 4. 主索引结构 ----------
p("\n=== [4] 主索引结构自检 ===")
t = main
p(f"  article-card 计数 = {t.count('<div class=\"article-card\">')}")
p(f"  malformed(不以 h2 起) = {len(re.findall(r'<div class=.article-card.>(?!\\s*<h2)', t))}")
import collections
c = collections.Counter(re.findall(r'<h2><a href="([^"]+)"', t))
dup = [k for k, v in c.items() if v > 1]
p(f"  重复 href = {dup if dup else 0}")
p(f"  '**' 泄漏 = {t.count('**')}")
# div 深度（body 内）
sub = t[t.find("<body"):]
depth = 0; maxd = 0; cards_d1 = 0; err = 0
for m in re.finditer(r"<(/?)div[^>]*>", sub):
    if m.group(1) == "":
        depth += 1
        if depth > maxd: maxd = depth
        tag = sub[m.start():sub.find(">", m.start())+1]
        if 'class="article-card"' in tag and depth == 1:
            cards_d1 += 1
    else:
        depth -= 1
        if depth < 0: err += 1
p(f"  div 终态深度 = {depth} (max={maxd}) ; depth==1 卡片数 = {cards_d1} ; 栈空闭合异常 = {err}")

# ---------- 5. articles.json 首页曝光 ----------
p("\n=== [5] articles.json 首页 slice(0,6) ===")
d = json.load(open("articles.json"))
arts = d if isinstance(d, list) else d.get("articles", [])
for i, a in enumerate(arts[:6]):
    url = a.get("url") or a.get("link") or ""
    local = url.lstrip("/")
    exists = os.path.exists(local)
    p(f"  rank{i+1}: exists={exists} {url}")

# ---------- 6. sitemap ----------
p("\n=== [6] sitemap ===")
sm = open("sitemap.xml", encoding="utf-8").read()
locs = re.findall(r"<loc>(.*?)</loc>", sm)
p(f"  loc 总数 = {len(locs)}")
blocks = re.findall(r"<url>(.*?)</url>", sm, re.S)
nolastmod = [b for b in blocks if "<lastmod>" not in b]
p(f"  无 lastmod = {len(nolastmod)}")
p(f"  sitemap 最后文件 mtime = {sh('git log -1 --date=short --pretty=%ad -- sitemap.xml')}")

# ---------- 7. 品牌索引 stub ----------
p("\n=== [7] 今日新增站点文件（未跟踪/新提交）===")
p(sh("git log --since='3 days ago' --diff-filter=A --name-only --pretty=format:  | sort -u | grep -v '^$' | head -30"))

print("\n".join(out))
