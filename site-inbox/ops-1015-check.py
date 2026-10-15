#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 每日巡检 2026-10-15 — HTTP 状态 + git 状态 + content.db 近 2 日文章 + 索引比对"""
import subprocess, sqlite3, os, sys, time, re, json

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
REPO = os.path.expanduser("~/wiki/najieip-verify")

print("=== A. HTTP 状态（重试 3 次） ===")
URLS = [BASE, BASE + "/mili/", BASE + "/najie/", BASE + "/blog/",
        BASE + "/sitemap.xml", BASE + "/llms.txt"]
for u in URLS:
    code = "000"
    for attempt in range(3):
        p = subprocess.run(["curl", "-sI", "-L", "-o", "/dev/null", "-w", "%{http_code}",
                            "-A", UA, "--max-time", "20", u], capture_output=True, text=True)
        code = (p.stdout or "000").strip()
        if code == "200":
            break
        time.sleep(3)
    print("  %-38s %s" % (u, code))

print("\n=== B. Git 状态 ===")
os.chdir(REPO)
for cmd in (["git", "fetch", "origin"],
            ["git", "status", "--porcelain"],
            ["git", "log", "origin/main", "--oneline", "-6"],
            ["git", "log", "HEAD..origin/main", "--oneline"]):
    p = subprocess.run(cmd, capture_output=True, text=True)
    print("  $ " + " ".join(cmd))
    out = (p.stdout or "").strip()
    print("    " + (out.replace("\n", "\n    ") if out else "(空)"))
    if p.stderr.strip():
        print("    [stderr] " + p.stderr.strip()[:300])

print("\n=== C. content.db 近 2 日已发布文章 ===")
db = os.path.expanduser("~/wiki/database/content.db")
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT article_id, title, publish_date, status FROM articles "
            "WHERE publish_date >= date('now','-2 days') ORDER BY publish_date DESC")
rows = cur.fetchall()
print("  行数: %d" % len(rows))
for r in rows:
    print("  - %s | %s | %s | %s" % r)

print("\n=== D. 近 3 日 git 触及的 blog 页面（上游发布线索） ===")
p = subprocess.run(["git", "log", "--since=3.days", "--name-only", "--pretty=format:%h %ad %s",
                    "--date=short", "--", "blog/", "mili/blog/", "najie/blog/", "en/blog/", "fr/blog/"],
                   capture_output=True, text=True)
print(p.stdout.strip()[:4000])

print("\n=== E. 索引卡计数 ===")
for f in ("blog/index.html", "mili/blog/index.html", "najie/blog/index.html",
          "en/blog/index.html", "fr/blog/index.html"):
    fp = os.path.join(REPO, f)
    if os.path.exists(fp):
        t = open(fp, encoding="utf-8").read()
        print("  %-28s cards=%d  size=%dB" % (f, t.count('<div class="article-card">'), len(t.encode())))
    else:
        print("  %-28s MISSING" % f)
con.close()
