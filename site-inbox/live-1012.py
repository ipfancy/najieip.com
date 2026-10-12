#!/usr/bin/env python3
# 线上终验 2026-10-12
import subprocess, time, json, re, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
SLUG = "bambu-stratasys-fto-decision-tree-20261004"
CB = str(int(time.time()))
FAIL = []


def json_ok(b):
    try:
        json.loads(b)
        return True
    except Exception:
        return False


def fetch(url, head=False):
    cmd = ["curl", "-s", "-A", UA, "--max-time", "25"]
    if head:
        cmd += ["-I"]
    r = subprocess.run(cmd + [url], capture_output=True, text=True)
    return r.stdout


def status(url):
    for attempt in range(3):
        out = fetch(url + ("&" if "?" in url else "?") + "cb=" + CB, head=True)
        m = re.search(r"HTTP/\S+\s+(\d{3})", out)
        if m and m.group(1) == "200":
            return "200"
        time.sleep(3)
    m = re.search(r"HTTP/\S+\s+(\d{3})", out)
    return m.group(1) if m else "000"


print("=== HTTP 状态（重试 3 次取终态）===")
CORE = ["https://najieip.com/", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/en/blog/", "https://najieip.com/fr/blog/"]
PAGES = [f"https://najieip.com/{p}" for p in
         [f"en/blog/{SLUG}-en.html", f"fr/blog/{SLUG}-fr.html", f"mili/blog/{SLUG}.html"]]
for u in CORE + PAGES + ["https://najieip.com/sitemap.xml", "https://najieip.com/articles.json"]:
    s = status(u)
    print(f"  {s}  {u}")
    if s != "200":
        FAIL.append(f"HTTP {s} {u}")

print("\n=== 新页内容判据 ===")
for lang in ("en", "fr"):
    t = fetch(f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html?cb={CB}")
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ok_ld = all(json_ok(b) for b in lds) if lds else False
    print(f"  [{lang}] bytes={len(t.encode())} h1={t.count('<h1')} ld={len(lds)} og:image={t.count('og:image')} "
          f"stars={t.count('**')} hreflang={t.count('hreflang')} h2={t.count('<h2>')}")
    if not (t.count("<h1") == 1 and t.count("og:image") == 1 and t.count("**") == 0
            and t.count("hreflang") == 4 and ok_ld):
        FAIL.append(f"{lang} live page criteria")

print("\n=== 索引卡 HIT ===")
for lang in ("en", "fr"):
    t = fetch(f"https://najieip.com/{lang}/blog/?cb={CB}")
    hit = f"/{lang}/blog/{SLUG}-{lang}.html" in t
    print(f"  [{lang}] card HIT={hit} cards={t[t.find('<body'):].count('<div class=\"article-card\">')}")
    if not hit:
        FAIL.append(f"{lang} index card not live")

print("\n=== sitemap / articles.json ===")
sm = fetch(f"https://najieip.com/sitemap.xml?cb={CB}")
print("  sitemap loc:", sm.count("<loc>"))
print("  en loc present:", f"<loc>https://najieip.com/en/blog/{SLUG}-en.html</loc>" in sm)
print("  fr loc present:", f"<loc>https://najieip.com/fr/blog/{SLUG}-fr.html</loc>" in sm)
if sm.count("<loc>") < 304:
    FAIL.append(f"sitemap loc {sm.count('<loc>')} < 304")

aj = fetch(f"https://najieip.com/articles.json?cb={CB}")
try:
    n = len(json.loads(aj))
    print("  articles.json entries:", n)
except Exception as e:
    print("  articles.json parse FAIL", e)
    FAIL.append("articles.json")

print("\n=== RESULT ===")
print("FAILURES:", len(FAIL))
for f in FAIL:
    print("  -", f)
