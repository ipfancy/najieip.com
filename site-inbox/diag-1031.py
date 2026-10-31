#!/usr/bin/env python3
# SiteOps daily diagnostic (read-only) — 2026-10-31
import json, os, re, subprocess, sqlite3, datetime, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
HOME = os.path.expanduser("~")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def sh(cmd, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), -1

print("=== A. GIT ===")
out, err, rc = sh("git fetch origin 2>&1 | tail -2", cwd=REPO)
print(out or err)
out, _, _ = sh("git log origin/main --oneline -8", cwd=REPO)
print(out)
out, _, _ = sh("git status --porcelain", cwd=REPO)
print("STATUS:", repr(out[:800]))
out, _, _ = sh("git log --oneline -1", cwd=REPO)
print("LOCAL HEAD:", out)

print("\n=== B. HTTP ===")
urls = ["https://najieip.com/", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]
for u in urls:
    code = "000"
    for attempt in range(3):
        out, _, _ = sh(f'curl -sI -o /dev/null -w "%{{http_code}}" -A "{UA}" -m 20 "{u}"', timeout=40)
        code = out.strip() or "000"
        if code == "200":
            break
    print(f"{code}  {u}")

print("\n=== C. RECENT ARTICLES (content.db) ===")
db = os.path.join(HOME, "wiki/database/content.db")
try:
    con = sqlite3.connect(db); cur = con.cursor()
    cur.execute("SELECT article_id, title, publish_date FROM articles WHERE status='published' AND publish_date >= date('now','-3 days') ORDER BY publish_date DESC")
    rows = cur.fetchall()
    for r in rows:
        print(r)
    print("count:", len(rows))
except Exception as e:
    print("DB ERR", e)

print("\n=== D. RECENT SITE FILES (git, 3 days) ===")
out, _, _ = sh("git log --since=3.days --name-only --diff-filter=AM --pretty=format:%h\\ %ad origin/main -- '*blog/*.html' | head -80", cwd=REPO)
print(out)

print("\n=== E. PUBLISHED-VS-PAGE GAP ===")
pub = os.path.join(HOME, "wiki/digital-employees/articles/.published.json")
try:
    data = json.load(open(pub))
    items = data if isinstance(data, list) else data.get("articles", data)
    today = datetime.date.today()
    rec = []
    if isinstance(items, dict):
        for k, v in items.items():
            rec.append((k, v))
    for k, v in rec[-8:]:
        print("PUB:", k, str(v)[:160])
except Exception as e:
    print("PUB ERR", e)

print("\n=== F. INDEX GAPS (brand cards vs main index) ===")
main_i = open(os.path.join(REPO, "blog/index.html"), encoding="utf-8").read()
print("main index cards:", main_i.count('<div class="article-card">'))
for brand in ("mili", "najie", "aipunajie"):
    p = os.path.join(REPO, brand, "blog/index.html")
    if not os.path.exists(p):
        print(brand, "NO INDEX"); continue
    t = open(p, encoding="utf-8").read()
    cards = re.findall(r'<h[23][^>]*><a href="([^"]+)"', t)
    gaps = []
    for c in set(cards):
        base = os.path.basename(c.split("?")[0])
        if not base or base == "index.html":
            continue
        if base not in main_i:
            gaps.append(base)
    print(f"{brand}: cards={len(cards)} unique={len(set(cards))} main_missing={sorted(gaps)}")

print("\n=== G. articles.json guard (check only) ===")
out, err, rc = sh("python3 site-inbox/guard-0918-articles-json.py --check", cwd=REPO, timeout=180)
print("rc=", rc)
print((out or err)[-2500:])

print("\n=== H. sitemap loc count ===")
sm = os.path.join(REPO, "sitemap.xml")
if os.path.exists(sm):
    t = open(sm, encoding="utf-8").read()
    print("loc:", t.count("<loc>"), "lastmod:", t.count("<lastmod>"), "bytes:", os.path.getsize(sm))
