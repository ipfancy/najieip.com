import json, os, re, sqlite3, subprocess, sys
from datetime import date, timedelta

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
BRANDS = ["mili", "najie", "aipunajie"]
today = date.today()
d2 = (today - timedelta(days=2)).isoformat()

print("=== A. content.db articles published >= " + d2 + " ===")
try:
    con = sqlite3.connect(os.path.expanduser("~/wiki/database/content.db"))
    rows = con.execute(
        "SELECT article_id, title, publish_date, status FROM articles "
        "WHERE status='published' AND publish_date >= date('now','-2 days') ORDER BY publish_date DESC"
    ).fetchall()
    for r in rows:
        print(" | ".join(str(x)[:70] for x in r))
    print("count:", len(rows))
    con.close()
except Exception as e:
    print("DB ERR", e)

print("\n=== B. .published.json recent 3 days ===")
pj = os.path.expanduser("~/wiki/digital-employees/articles/.published.json")
try:
    d = json.load(open(pj))
    items = d.items() if isinstance(d, dict) else [(x.get("slug", "?"), x) for x in d]
    for k, v in items:
        ts = v.get("published_at", "") if isinstance(v, dict) else str(v)
        if ts[:10] >= (today - timedelta(days=3)).isoformat():
            has = []
            for b in BRANDS:
                p = f"{b}/blog/{k}.html"
                if os.path.exists(p):
                    has.append(f"{b}:{os.path.getsize(p)}B")
            print(f"{ts[:16]} {k} -> {has or 'NO PAGE'}")
except Exception as e:
    print("PUB ERR", e)

print("\n=== C. pages touched in last 3 days (git) ===")
out = subprocess.run(["git", "log", "--since=3.days", "--name-only", "--diff-filter=AM",
                      "--pretty=format:", "--", "*/blog/*.html"],
                     capture_output=True, text=True).stdout
pages = sorted({l.strip() for l in out.splitlines() if l.strip().endswith(".html")
                and not l.strip().endswith("index.html")})
for p in pages:
    if os.path.exists(p):
        print(p, os.path.getsize(p), end=" ")
        t = open(p, encoding="utf-8", errors="replace").read()
        h1 = len(re.findall(r"<h1[ >]", t))
        ld = t.count('application/ld+json')
        ogi = "og:image" in t
        m = re.search(r'<meta name="description" content="(.*?)"', t, re.S)
        desc = m.group(1) if m else ""
        h2 = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)
        title = h1text = re.sub(r"<[^>]+>", "", h2[0]).strip() if h2 else ""
        repeat = bool(title) and (desc.strip()[:40] == title.strip()[:40])
        stars = t.count("**")
        baretab = len(re.findall(r"<p>\s*\|", t))
        flags = []
        if h1 != 1: flags.append(f"h1={h1}")
        if ld < 2: flags.append(f"ld={ld}")
        if not ogi: flags.append("NO-OG-IMG")
        if repeat: flags.append("DESC-REPEAT")
        if stars: flags.append(f"stars={stars}")
        if baretab: flags.append(f"baretab={baretab}")
        print("->", ",".join(flags) if flags else "OK")
    else:
        print(p, "MISSING")

print("\n=== D. index card presence for today's pages ===")
main = open("blog/index.html", encoding="utf-8").read()
for b in BRANDS:
    bp = f"{b}/blog/index.html"
    bi = open(bp, encoding="utf-8").read() if os.path.exists(bp) else ""
    for f in sorted(os.listdir(f"{b}/blog")):
        if not f.endswith(".html") or f == "index.html": continue
        if not re.match(r"^2026102[123]", f): continue
        slug = f[:-5]
        print(f"{b}/{f}: main={'HIT' if slug in main else 'MISS'} brand={'HIT' if slug in bi else 'MISS'}")

print("\n=== E. sitemap loc coverage for today's pages ===")
sm = open("sitemap.xml", encoding="utf-8").read()
locs = re.findall(r"<loc>(.*?)</loc>", sm)
print("total locs:", len(locs))
for b in BRANDS:
    for f in sorted(os.listdir(f"{b}/blog")):
        if f.endswith(".html") and f != "index.html" and re.match(r"^2026102[123]", f):
            url = f"https://najieip.com/{b}/blog/{f}"
            print(f"  {f}: {'IN' if url in locs else 'ABSENT'}")

print("\n=== F. articles.json health ===")
aj = json.load(open("articles.json"))
bad = []
for it in aj:
    u = it.get("url", "")
    if not u.startswith(("/mili/", "/najie/", "/aipunajie/", "/blog/")):
        bad.append(("prefix", u)); continue
    p = u.lstrip("/")
    if not os.path.exists(p):
        bad.append(("nofile", u))
print("entries:", len(aj), "violations:", len(bad))
for k, v in bad[:10]: print("  ", k, v)
