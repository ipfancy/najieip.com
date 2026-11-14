#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 每日巡检诊断 2026-11-14
1) 核心页面 HTTP（3 次重试取终态）
2) content.db 近 2 天已发布文章 vs 三索引 / articles.json
3) 当日新文页面六项 + 正文包含判据
"""
import subprocess, sqlite3, os, re, json, glob, datetime

REPO = "/Users/ziganghe/wiki/najieip-verify"
DB = "/Users/ziganghe/wiki/database/content.db"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def http(url, tries=3):
    last = "000"
    for i in range(tries):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}",
                            "-A", UA, "--max-time", "25", url],
                           capture_output=True, text=True)
        last = r.stdout.strip()
        if last == "200":
            return last
    return last

print("=== 1. 核心页面 HTTP ===")
core = ["https://najieip.com/", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]
for u in core:
    print(f"  {http(u)}  {u}")

print("\n=== 2. content.db 近 3 天已发布 ===")
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
rows = con.execute("""SELECT article_id, title, source_file, publish_date, status
                      FROM articles WHERE publish_date >= date('now','-3 days')
                      ORDER BY publish_date DESC""").fetchall()
for r in rows:
    print(f"  {r['publish_date']} | {r['status']} | {r['article_id']} | {(r['title'] or '')[:40]} | src={r['source_file']}")
if not rows:
    print("  (无)")

# .published.json 最近记录
pj = os.path.expanduser("~/wiki/digital-employees/articles/.published.json")
recent_pub = []
if os.path.exists(pj):
    data = json.load(open(pj))
    items = data if isinstance(data, list) else data.get("articles", data.get("published", []))
    today = datetime.date.today().isoformat()
    yday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    for it in items:
        if not isinstance(it, dict):
            continue
        pa = str(it.get("published_at") or it.get("date") or "")
        if pa[:10] in (today, yday):
            recent_pub.append(it)
    print(f"  .published.json 近2日条目: {len(recent_pub)}")
    for it in recent_pub:
        print(f"    {it.get('published_at')} | {it.get('slug') or it.get('article_id')} | {(it.get('title') or '')[:40]}")

print("\n=== 3. 索引命中检查 ===")
idx_files = {
    "main": os.path.join(REPO, "blog/index.html"),
    "mili": os.path.join(REPO, "mili/blog/index.html"),
    "najie": os.path.join(REPO, "najie/blog/index.html"),
    "aipunajie": os.path.join(REPO, "aipunajie/blog/index.html"),
}
slugs = set()
for it in recent_pub:
    s = it.get("slug") or it.get("article_id") or ""
    if s:
        slugs.add(s)
for r in rows:
    sf = r["source_file"] or ""
    if sf:
        slugs.add(os.path.basename(sf).replace(".md", "").replace(".html", ""))

# 当日/近2日 git 新增文章页
out = subprocess.run(["git", "-C", REPO, "log", "--since=3.days", "--name-only",
                      "--diff-filter=AM", "--pretty=format:"], capture_output=True, text=True).stdout
newpages = sorted({l.strip() for l in out.splitlines()
                   if re.search(r"/(mili|najie|aipunajie)/blog/", l.strip()) and l.strip().endswith(".html")
                   and not l.strip().endswith("index.html")})
print(f"  近3日 git 触及文章页: {len(newpages)}")
for p in newpages:
    s = os.path.basename(p).replace(".html", "")
    slugs.add(s)

for s in sorted(slugs):
    hits = []
    for k, f in idx_files.items():
        if not os.path.exists(f):
            continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        c = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), t))
        if c:
            hits.append(f"{k}={c}")
    # 页面落地
    landed = [p for p in glob.glob(os.path.join(REPO, "*", "blog", s + ".html"))]
    print(f"  {s}: pages={[os.path.relpath(p, REPO) for p in landed]} idx=[{', '.join(hits) if hits else 'NONE'}]")

print("\n=== 4. articles.json top6 ===")
aj = os.path.join(REPO, "articles.json")
try:
    arr = json.load(open(aj, encoding="utf-8"))
    print(f"  条目总数: {len(arr)}")
    for a in arr[:6]:
        u = a.get("url", "")
        fp = os.path.join(REPO, u.lstrip("/"))
        print(f"    {'OK ' if os.path.exists(fp) else 'MISS'} {a.get('date')} {u} | {(a.get('title') or '')[:30]}")
except Exception as e:
    print("  ERR", e)
