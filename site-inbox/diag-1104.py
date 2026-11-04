#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 每日巡检 2026-11-04 — 一次过取数：HTTP 状态 + git 状态 + content.db 近2日 + 索引命中"""
import subprocess, sqlite3, os, json, re, time

REPO = os.path.expanduser("~/wiki/najieip-verify")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OUT = []

def http(url, tries=3):
    for i in range(tries):
        try:
            r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}",
                                "-A", UA, "--max-time", "25", url],
                               capture_output=True, text=True, timeout=40)
            code = r.stdout.strip()
            if code == "200":
                return code
            last = code
        except Exception as e:
            last = "ERR"
        time.sleep(2)
    return last

URLS = ["https://najieip.com/", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt",
        "https://najieip.com/en/", "https://najieip.com/fr/"]
print("=== HTTP ===")
for u in URLS:
    print(u, http(u))

print("\n=== GIT ===")
for cmd in (["git", "-C", REPO, "fetch", "origin", "--quiet"],
            ["git", "-C", REPO, "log", "origin/main", "--oneline", "-8"],
            ["git", "-C", REPO, "status", "--porcelain"],
            ["git", "-C", REPO, "log", "HEAD..origin/main", "--oneline"]):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    print("$", " ".join(cmd[3:]), "->", r.returncode)
    print(r.stdout.strip()[:2000] or "(empty)")
    if r.stderr.strip():
        print("ERR:", r.stderr.strip()[:400])

print("\n=== CONTENT.DB 近3日 published ===")
db = os.path.expanduser("~/wiki/database/content.db")
try:
    con = sqlite3.connect(db)
    cur = con.cursor()
    rows = cur.execute("SELECT article_id, title, publish_date, source_file FROM articles WHERE status='published' AND publish_date >= date('now','-3 days') ORDER BY publish_date DESC").fetchall()
    for r in rows:
        print(r)
    print("count:", len(rows))
    con.close()
except Exception as e:
    print("DB ERR:", e)

print("\n=== .published.json 近3日 ===")
pj = os.path.expanduser("~/wiki/digital-employees/articles/.published.json")
try:
    d = json.load(open(pj))
    items = d if isinstance(d, list) else d.get("published", d)
    out = []
    if isinstance(items, dict):
        for k, v in items.items():
            ts = v.get("published_at", "") if isinstance(v, dict) else str(v)
            if ts >= "2026-11-01":
                out.append((k, ts))
    elif isinstance(items, list):
        for v in items:
            ts = v.get("published_at", "")
            if ts >= "2026-11-01":
                out.append((v.get("slug") or v.get("stem") or v.get("title"), ts))
    for o in out:
        print(o)
    print("count:", len(out))
except Exception as e:
    print("PJ ERR:", e)

print("\n=== 品牌目录近3日新页 ===")
for brand in ("mili", "najie", "aipunajie"):
    d = os.path.join(REPO, brand, "blog")
    if not os.path.isdir(d):
        print(brand, "MISSING DIR"); continue
    files = sorted(os.listdir(d))
    recent = [f for f in files if re.match(r"^2026(10|11)\d{2}-.*\.html$", f) and f != "index.html"]
    print(brand, len(files), "files; recent:", recent[-8:])

print("\n=== 索引命中（近5日 slug）===")
idx_main = open(os.path.join(REPO, "blog", "index.html"), encoding="utf-8").read()
idxs = {b: open(os.path.join(REPO, b, "blog", "index.html"), encoding="utf-8").read()
        for b in ("mili", "najie", "aipunajie") if os.path.exists(os.path.join(REPO, b, "blog", "index.html"))}
# 收集近5日品牌目录页面 slug
slugs = []
for b in ("mili", "najie", "aipunajie"):
    d = os.path.join(REPO, b, "blog")
    if not os.path.isdir(d): continue
    for f in sorted(os.listdir(d)):
        if re.match(r"^2026(1031|11)\d{2}-.*\.html$", f):
            slugs.append((b, f[:-5], os.path.getsize(os.path.join(d, f))))
for b, s, sz in slugs:
    mc = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), idx_main))
    bc = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), idxs.get(b, "")))
    print(f"{b:10s} {s:60s} size={sz:6d} main_card={mc} brand_card={bc}")
print("\nmain index cards:", len(re.findall(r'<div class="article-card">', idx_main)))
for b, t in idxs.items():
    print(b, "index cards:", len(re.findall(r'<div class="article-card">', t)))
