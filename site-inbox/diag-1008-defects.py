#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Six-point defect check on pages touched in last 3 days + content.db index presence."""
import subprocess, sqlite3, os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
DB = os.path.expanduser("~/wiki/database/content.db")

# --- A. pages touched by git in last 3 days ---
out = subprocess.run(["git", "log", "--since=3.days", "--name-only", "--pretty=format:%h %ad %s",
                      "--date=short", "--", "*/blog/*.html", "blog/*.html"],
                     cwd=REPO, capture_output=True, text=True).stdout
files = sorted({l.strip() for l in out.splitlines()
                if l.strip().endswith(".html") and not l.startswith(" ") and len(l.strip().split()) == 1})
print("=== A. pages touched last 3 days ===", len(files))
for f in files:
    print("  -", f)

def analyze(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    h1 = len(re.findall(r"<h1", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = len(re.findall(r'property="og:image"', t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = ti.group(1) if ti else ""
    desc_copy_title = desc.strip() == title.strip() or (desc and title and desc.strip()[:20] == title.strip()[:20])
    stars = t.count("**")
    rawtbl = len(re.findall(r"<p>\|", t))
    style = ('<style>' in t) or ('/style.css' in t and os.path.exists(os.path.join(REPO, "style.css")))
    return dict(size=len(t.encode()), h1=h1, ld=ld, ogimg=ogimg, desc_len=len(desc),
                desc_copy_title=desc_copy_title, stars=stars, raw_table_rows=rawtbl, style=style)

defects = []
for f in files:
    p = os.path.join(REPO, f)
    if not os.path.exists(p):
        print(f"  MISSING FILE {f}")
        continue
    a = analyze(p)
    bad = []
    if a["h1"] != 1: bad.append(f"h1={a['h1']}")
    if a["ld"] == 0: bad.append("ld=0")
    if a["ogimg"] == 0: bad.append("no og:image")
    if a["desc_copy_title"]: bad.append("desc=title")
    if a["raw_table_rows"] > 0: bad.append(f"raw_md_table={a['raw_table_rows']}")
    if a["stars"] > 0: bad.append(f"stars={a['stars']}")
    if not a["style"]: bad.append("NO-STYLE")
    flag = "DEFECT" if bad else "ok"
    print(f"  [{flag}] {f}  {a['size']}B  " + ("; ".join(bad) if bad else ""))
    if bad:
        defects.append((f, a, bad))

# --- B. content.db recent articles -> index presence ---
print("\n=== B. content.db recent -> index presence ===")
con = sqlite3.connect(DB)
rows = list(con.execute(
    "SELECT article_id, title, source_file, publish_date FROM articles "
    "WHERE status='published' AND publish_date >= date('now','-4 days') ORDER BY publish_date DESC"))
con.close()

idxs = {}
for name, path in [("main", "blog/index.html"), ("mili", "mili/blog/index.html"),
                   ("najie", "najie/blog/index.html"), ("aipunajie", "aipunajie/blog/index.html")]:
    fp = os.path.join(REPO, path)
    idxs[name] = open(fp, encoding="utf-8").read() if os.path.exists(fp) else ""

for r in rows:
    aid, title, sf, pd = r
    slug = os.path.basename(sf or "").replace(".md", "")
    base = slug[:8]
    hits = {k: v.count(base) for k, v in idxs.items()}
    where = [k for k, v in hits.items() if v > 0]
    status = "IN-INDEX" if where else "NOT-IN-ANY-INDEX"
    print(f"  [{status}] {pd} {aid} slug={slug} -> {where}")

# --- C. defect pages in articles.json top6 exposure ---
print("\n=== C. articles.json top6 files: defect check ===")
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
arts = aj if isinstance(aj, list) else aj.get("articles", [])
for a in arts[:6]:
    u = a.get("url") or a.get("link") or ""
    fp = os.path.join(REPO, u.lstrip("/"))
    if not os.path.exists(fp):
        print(f"  MISSING {u}")
        continue
    an = analyze(fp)
    bad = []
    if an["h1"] != 1: bad.append(f"h1={an['h1']}")
    if an["ld"] == 0: bad.append("ld=0")
    if an["ogimg"] == 0: bad.append("no og:image")
    if an["desc_copy_title"]: bad.append("desc=title")
    if an["stars"]: bad.append(f"stars={an['stars']}")
    if an["raw_table_rows"]: bad.append(f"rawtbl={an['raw_table_rows']}")
    print(f"  [{'DEFECT' if bad else 'ok'}] {u}  {an['size']}B  " + "; ".join(bad))

print("\nSUMMARY defects(3day window) =", len(defects))
for d in defects:
    print("  !", d[0], d[2])
