#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps daily check: HTTP core pages + articles.json exposure + content.db gap scan."""
import subprocess, sqlite3, os, re, json, sys, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REPO = os.path.expanduser("~/wiki/najieip-verify")
DB = os.path.expanduser("~/wiki/database/content.db")

def http(url, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-sI", "-L", "-A", UA, "-o", "/dev/null",
                            "-w", "%{http_code}", "--max-time", "25", url],
                           capture_output=True, text=True)
        code = p.stdout.strip()
        if code == "200":
            return 200, i + 1
        time.sleep(3)
    return code or "000", tries

print("=== 1. HTTP CORE PAGES ===")
core = ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/sitemap.xml",
        "https://najieip.com/llms.txt", "https://najieip.com/en/", "https://najieip.com/fr/"]
for u in core:
    c, n = http(u)
    print(f"  {c}  tries={n}  {u}")

print("\n=== 2. content.db recent published (3 days) ===")
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cols = [r[1] for r in con.execute("PRAGMA table_info(articles)")]
print("  articles cols:", cols)
rows = list(con.execute(
    "SELECT * FROM articles WHERE status='published' AND publish_date >= date('now','-3 days') "
    "ORDER BY publish_date DESC"))
print(f"  count={len(rows)}")
for r in rows:
    d = dict(r)
    print("   -", d.get("article_id"), "|", d.get("publish_date"), "|", (d.get("title") or "")[:50],
          "|", d.get("source_file"))

print("\n=== 3. index gap scan (href-normalized) ===")
main_index = open(os.path.join(REPO, "blog", "index.html"), encoding="utf-8").read()
def cards(text):
    return set(re.findall(r'<h2><a href="([^"]+)"', text))

main_hrefs = cards(main_index)
brand_files = []
for brand in ("mili", "najie", "aipunajie"):
    p = os.path.join(REPO, brand, "blog", "index.html")
    if os.path.exists(p):
        brand_files.append((brand, p))
print(f"  main index cards = {len(main_hrefs)}")

missing = []
for brand, p in brand_files:
    t = open(p, encoding="utf-8").read()
    hrefs = cards(t)
    print(f"  {brand}: {len(hrefs)} cards")
    for h in sorted(hrefs):
        if h.startswith("./"):
            norm = f"/{brand}/blog/{h[2:]}"
        else:
            norm = h
        if norm not in main_hrefs:
            # check file exists, not stub
            fn = os.path.join(REPO, norm.lstrip("/"))
            if not os.path.exists(fn):
                missing.append((brand, norm, "file_missing", 0))
                continue
            sz = os.path.getsize(fn)
            body = open(fn, encoding="utf-8", errors="replace").read()
            if sz < 1500 or 'http-equiv="refresh"' in body:
                continue
            missing.append((brand, norm, "not_in_main_index", sz))

print(f"  GAPS = {len(missing)}")
for m in missing:
    print("   !", m)

print("\n=== 4. articles.json health ===")
aj_path = os.path.join(REPO, "articles.json")
if os.path.exists(aj_path):
    aj = json.load(open(aj_path, encoding="utf-8"))
    arts = aj if isinstance(aj, list) else aj.get("articles", [])
    print(f"  total entries = {len(arts)}")
    bad = []
    for i, a in enumerate(arts):
        u = a.get("url") or a.get("link") or ""
        if not u:
            continue
        fn = os.path.join(REPO, u.lstrip("/"))
        if not os.path.exists(fn):
            bad.append((i, u, a.get("date")))
    print(f"  entries without local file = {len(bad)}")
    for b in bad[:8]:
        print("   ord=", b[0], b[1], b[2])
    # homepage exposure top6
    top6 = [a.get("url") for a in arts[:6]]
    print("  top6:", top6)

con.close()
