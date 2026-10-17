#!/usr/bin/env python3
"""2026-10-17 daily check: today's article page + index presence."""
import os, re, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "customs-ip-post-filing-steps-20261017"
CANDS = [
    f"mili/blog/{SLUG}.html",
    f"najie/blog/{SLUG}.html",
    f"blog/{SLUG}.html",
]
path = None
for c in CANDS:
    p = os.path.join(REPO, c)
    if os.path.exists(p):
        path = p
        break

print("PAGE:", path)
if path:
    t = open(path, encoding="utf-8").read()
    print("SIZE_B:", os.path.getsize(path))
    print("h1:", len(re.findall(r"<h1[\s>]", t)))
    print("h2:", len(re.findall(r"<h2[\s>]", t)))
    print("ld_json:", len(re.findall(r'application/ld\+json', t)))
    print("og_image:", len(re.findall(r'property="og:image"', t)))
    print("og_site:", 1 if 'og:site_name' in t else 0)
    print("twitter_title:", 1 if 'twitter:title' in t else 0)
    print("keywords:", 1 if 'name="keywords"' in t else 0)
    print("stars_double:", t.count("**"))
    print("bare_table_rows:", len(re.findall(r"<p>\|.*\|</p>", t)))
    print("inline_style:", 1 if "<style>" in t else 0)
    print("ext_css:", 1 if "/style.css" in t else 0)
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    d = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    title = tm.group(1).strip() if tm else ""
    print("desc_len:", len(d))
    print("title:", title)
    print("DESC_EQ_TITLE:", d.strip() in title or title.startswith(d.strip()[:20]))
    print("desc:", d[:160])
    # ld blocks parse
    for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)):
        try:
            json.loads(blk)
            print(f"  ld[{i}] OK")
        except Exception as e:
            print(f"  ld[{i}] FAIL: {e}")
    print("schema_org:", t.count("https://schema.org"))
    print("bad_redact:", t.count("https://***"))
    # images
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', t):
        print("  img:", m.group(1))

print("\n--- INDEX PRESENCE ---")
for idx in ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html"]:
    p = os.path.join(REPO, idx)
    txt = open(p, encoding="utf-8").read()
    print(f"{idx}: slug_hits={txt.count(SLUG)} cards={txt.count('class=\"article-card\"')} size={os.path.getsize(p)}")

print("\n--- ARTICLES.JSON ---")
aj = os.path.join(REPO, "articles.json")
data = json.load(open(aj, encoding="utf-8"))
print("total:", len(data))
for i, e in enumerate(data[:8]):
    u = e.get("url", "")
    exists = os.path.exists(os.path.join(REPO, u.lstrip("/"))) if u else False
    print(f"  rank{i}: {e.get('date','')} exists={exists} {u}")
missing = [e for e in data if e.get("url") and not os.path.exists(os.path.join(REPO, e["url"].lstrip("/")))]
print("missing_pages:", len(missing))
