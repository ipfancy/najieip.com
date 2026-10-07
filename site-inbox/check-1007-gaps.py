#!/usr/bin/env python3
"""SiteOps 1007 daily: (A) new-page defect six-item scan, (B) index gap check (href-normalized),
(C) articles.json guard (delegates to guard-0918 script)."""
import os, re, json, subprocess, glob

REPO = "/Users/ziganghe/wiki/najieip-verify"
os.chdir(REPO)


def rd(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def defects(path):
    t = rd(path)
    d = {}
    d["h1"] = len(re.findall(r"<h1[\s>]", t))
    d["ld"] = len(re.findall(r"application/ld\+json", t))
    d["ogimg"] = len(re.findall(r'property="og:image"', t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    ttl = re.search(r"<title>(.*?)</title>", t, re.S)
    desc = (m.group(1) if m else "").strip()
    title = re.sub(r"\s*—\s*纳杰觅理\s*$", "", (ttl.group(1).strip() if ttl else ""))
    d["desc_repeat"] = int(desc == title)
    d["stars"] = t.count("**")
    d["raw_table"] = len(re.findall(r"<p>\|.*\|</p>", t))
    style_inline = "<style>" in t
    style_link = "/style.css" in t and os.path.exists(os.path.join(REPO, "style.css"))
    d["styled"] = int(style_inline or style_link)
    d["ok"] = (d["h1"] == 1 and d["ld"] >= 1 and d["ogimg"] >= 1 and not d["desc_repeat"]
               and d["stars"] == 0 and d["raw_table"] == 0 and d["styled"] == 1)
    return d


print("=== A. NEW PAGE DEFECT SCAN (brand blog pages touched in last 3 days) ===")
files = []
for brand in ("mili", "najie", "aipunajie"):
    files += glob.glob(f"{brand}/blog/*.html")
recent = []
for f in files:
    if f.endswith("index.html"):
        continue
    try:
        lg = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f],
                            capture_output=True, text=True).stdout.strip()
    except Exception:
        continue
    if lg >= "2026-10-05":
        recent.append((f, lg))
for f, lg in sorted(recent):
    d = defects(f)
    flag = "OK " if d["ok"] else "DEFECT"
    print(f"{flag} {f} ({lg}) h1={d['h1']} ld={d['ld']} ogimg={d['ogimg']} "
          f"desc_repeat={d['desc_repeat']} stars={d['stars']} rawTbl={d['raw_table']} styled={d['styled']}")
print(f"total recent brand pages: {len(recent)}")

print()
print("=== B. INDEX GAP CHECK (brand index cards vs main /blog/index.html) ===")
main = rd("blog/index.html")
main_hrefs = set(re.findall(r'<h2><a href="([^"]+)"', main))
print(f"main index cards: {len(main_hrefs)}")
missing = []
for brand in ("mili", "najie", "aipunajie"):
    idx = os.path.join(brand, "blog", "index.html")
    if not os.path.exists(idx):
        continue
    ix = rd(idx)
    hrefs = re.findall(r'<h2><a href="([^"]+)"', ix)
    base = f"/{brand}/blog"
    for h in hrefs:
        if h.startswith("http") or h.startswith("#"):
            continue
        key = h if h.startswith("/") else base + "/" + h.lstrip("./")
        key = re.sub(r"^/+", "/", key)
        fn = key.rsplit("/", 1)[-1]
        local = os.path.join(brand, "blog", fn)
        if not os.path.exists(local):
            continue                                    # card points nowhere, not a gap
        if os.path.getsize(local) < 1500:
            continue                                    # stub / redirect shell
        if "http-equiv=\"refresh\"" in rd(local):
            continue
        if key not in main_hrefs:
            missing.append((brand, key))
uniq = sorted(set(m[-1] for m in missing))
print(f"gap candidates (unique urls): {len(uniq)}")
for u in uniq:
    print("  MISSING:", u)
    path = u.lstrip("/")
    if os.path.exists(path):
        tt = rd(path)
        d = defects(path)
        print(f"    -> defect check: ok={d['ok']} h1={d['h1']} ld={d['ld']} ogimg={d['ogimg']} "
              f"desc_repeat={d['desc_repeat']} stars={d['stars']} rawTbl={d['raw_table']} styled={d['styled']}")

print()
print("=== C. ARTICLES.JSON GUARD ===")
g = "site-inbox/guard-0918-articles-json.py"
if os.path.exists(g):
    r = subprocess.run(["python3", g, "--check"], capture_output=True, text=True)
    print((r.stdout or "")[-1200:])
    print("rc=", r.returncode)
else:
    print("guard script missing")
