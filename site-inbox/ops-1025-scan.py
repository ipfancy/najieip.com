#!/usr/bin/env python3
# SiteOps daily scan 2026-10-25: published-vs-page gap + index coverage + six-point defect check
import json, os, re, glob, subprocess

ROOT = "/Users/ziganghe/wiki/najieip-verify"
PUB = "/Users/ziganghe/wiki/digital-employees/articles/.published.json"

pub = json.load(open(PUB))
recent = [p for p in pub if p.get("published_at", "") >= "2026-10-22"]
print("=== published since 10-22 ===")
brand_dirs = ["mili", "najie", "aipunajie"]
missing_page = []
for p in sorted(recent, key=lambda x: x["published_at"], reverse=True):
    stem = p["file"][:-3] if p["file"].endswith(".md") else p["file"]
    # find page: any brand dir with stem or stem+date variant
    found = []
    for b in brand_dirs:
        for pat in (f"{b}/blog/{stem}.html",):
            fp = os.path.join(ROOT, pat)
            if os.path.exists(fp) and os.path.getsize(fp) > 1500:
                found.append(pat)
    # also try slug variants: strip leading date from stem
    if not found:
        slug = re.sub(r"^\d{8}-", "", stem)
        for b in brand_dirs:
            for f in glob.glob(os.path.join(ROOT, b, "blog", "*.html")):
                bn = os.path.basename(f)
                if slug in bn and os.path.getsize(f) > 1500 and "index" not in bn:
                    found.append(f"{b}/blog/{bn}")
    status = "OK " if found else "MISSING-PAGE"
    if not found:
        missing_page.append((stem, p["title"]))
    print(f"{status} {p['published_at'][:16]} {stem} -> {found}")

print("\n=== index coverage (href-normalized) ===")
def hrefs(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    hs = re.findall(r'<h2><a href="([^"]+)"', t)
    out = set()
    base = "/" + os.path.relpath(path, ROOT).split("/")[0] + "/blog"
    for h in hs:
        if h.startswith("./"):
            h = base + h[1:]
        elif h.startswith("/"):
            pass
        else:
            h = base + "/" + h
        out.add(h.split("#")[0].split("?")[0])
    return out

main_h = hrefs(os.path.join(ROOT, "blog/index.html"))
brand_h = {}
for b in brand_dirs:
    ip = os.path.join(ROOT, b, "blog/index.html")
    if os.path.exists(ip):
        brand_h[b] = hrefs(ip)
        print(f"{b}/blog/index.html cards={len(brand_h[b])}")
print(f"main blog/index.html cards={len(main_h)}")

# brand cards missing from main index
missing_main = []
for b, hs in brand_h.items():
    for h in sorted(hs):
        if h not in main_h:
            missing_main.append(h)
print(f"brand cards missing from main index: {len(missing_main)}")
for h in missing_main[:20]:
    print("  MISS-MAIN", h)

# duplicate hrefs in main index
print("\n=== duplicate href check ===")
t = open(os.path.join(ROOT, "blog/index.html"), encoding="utf-8", errors="ignore").read()
from collections import Counter
c = Counter(re.findall(r'<h2><a href="([^"]+)"', t))
dups = {k: v for k, v in c.items() if v > 1}
print("dups:", dups if dups else "none")

print("\n=== six-point check: pages touched in last 4 days ===")
try:
    out = subprocess.run(["git", "-C", ROOT, "log", "--since=4.days", "--name-only", "--diff-filter=AM", "--pretty=format:"],
                         capture_output=True, text=True, timeout=120).stdout
    files = sorted({l.strip() for l in out.splitlines() if l.strip().endswith(".html")})
except Exception as e:
    print("git log failed", e); files = []
defects = []
for f in files:
    if not re.search(r"(mili|najie|aipunajie|en|fr)?/?blog/.*\.html$", f) or f.endswith("index.html"):
        continue
    fp = os.path.join(ROOT, f)
    if not os.path.exists(fp):
        continue
    b = open(fp, encoding="utf-8", errors="ignore").read()
    chk = {
        "h1": len(re.findall(r"<h1[ >]", b)),
        "ld": len(re.findall(r'application/ld\+json', b)),
        "ogimg": 1 if "og:image" in b else 0,
        "stars": len(re.findall(r"[0-9*]\*\*|\*\*", b)),
        "table": len(re.findall(r"<p>\|", b)),
    }
    m = re.search(r'<meta name="description" content="([^"]*)"', b)
    desc = m.group(1) if m else ""
    h1m = re.search(r"<h1[^>]*>(.*?)</h1>", b, re.S)
    h1txt = re.sub(r"<[^>]+>", "", h1m.group(1)).strip() if h1m else ""
    chk["desc_dup"] = 1 if (desc and h1txt and desc.strip()[:20] == h1txt[:20]) else 0
    bad = []
    if chk["h1"] != 1: bad.append(f"h1={chk['h1']}")
    if chk["ld"] < 2: bad.append(f"ld={chk['ld']}")
    if not chk["ogimg"]: bad.append("no-og:image")
    if chk["desc_dup"]: bad.append("desc=title")
    if chk["stars"]: bad.append(f"stars={chk['stars']}")
    if chk["table"]: bad.append("raw-md-table")
    print(f"{'DEFECT' if bad else 'OK    '} {f} {bad if bad else ''}")
    if bad:
        defects.append((f, bad))

print("\n=== summary ===")
print("missing_page:", len(missing_page))
print("missing_main_cards:", len(missing_main))
print("defect_pages:", len(defects))
