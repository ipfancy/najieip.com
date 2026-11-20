import subprocess, re, json, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def curl(url, want_body=False):
    for _ in range(3):
        if want_body:
            r = subprocess.run(["curl", "-s", "--max-time", "60", "-A", UA, url], capture_output=True, text=True)
            if r.returncode == 0 and len(r.stdout) > 500:
                return r.stdout
        else:
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "40", "-A", UA, url], capture_output=True, text=True)
            if r.stdout.strip() == "200":
                return "200"
        time.sleep(5)
    return (r.stdout if not want_body else f"len={len(r.stdout)}")

cb = str(int(time.time()))
fails = []

pages = {
    "20261120-mili-device-procurement-firmware-checklist": True,
    "20261120-mili-dongcheng-branch": True,
}
for slug in pages:
    u = f"https://najieip.com/mili/blog/{slug}.html?cb={cb}"
    t = curl(u, True)
    if isinstance(t, str) and (t == "200" or t.startswith("len=")):
        fails.append(f"{slug} FETCH_FAIL {t}"); continue
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    okld = 0
    for b in lds:
        try: json.loads(b); okld += 1
        except Exception: pass
    h1 = len(re.findall(r"<h1", t))
    ogimg = 'property="og:image"' in t
    stars = len(re.findall(r"(?<![0-9*])\*\*(?![0-9])", t))
    tw = 'summary_large_image' in t
    size = len(t.encode())
    print(f"{slug}: bytes={size} h1={h1} ld={okld}/{len(lds)} og:image={ogimg} tw_large={tw} stars={stars}")
    if not (h1 == 1 and okld >= 2 and ogimg and tw and stars == 0):
        fails.append(f"{slug} six-item fail")

for slug in pages:
    code = curl(f"https://najieip.com/img/{slug}.png?cb={cb}")
    print("IMG", slug, code)
    if code != "200": fails.append(f"img {slug} {code}")

mi = curl(f"https://najieip.com/blog/?cb={cb}", True)
if isinstance(mi, str) and not mi.startswith("len="):
    n = len(re.findall(r'<h[23][^>]*><a href="[^"]*20261120-mili-dongcheng-branch', mi))
    cards = len(re.findall(r'<div class="article-card">', mi))
    print("main index: dongcheng cards =", n, "total cards =", cards)
    if n != 1: fails.append(f"main index dongcheng cards={n}")
else:
    fails.append("main index fetch fail")

bi = curl(f"https://najieip.com/mili/blog/?cb={cb}", True)
if isinstance(bi, str) and not bi.startswith("len="):
    print("mili index bytes =", len(bi.encode()))
    seg = re.search(r'20261120-mili-dongcheng-branch.{0,600}', bi, re.S)
    m = re.search(r'2026-11-\d\d · 觅理律师事务所', seg.group(0)) if seg else None
    print("mili dongcheng card date =", m.group(0) if m else "NONE")
    if not m or m.group(0) != "2026-11-20 · 觅理律师事务所": fails.append("mili brand card date")
else:
    fails.append("mili index fetch fail")

aj = curl(f"https://najieip.com/articles.json?cb={cb}", True)
if isinstance(aj, str) and not aj.startswith("len="):
    try:
        d = json.loads(aj); print("live articles.json =", len(d))
        if len(d) != 271: fails.append(f"live articles.json={len(d)}")
    except Exception as e:
        fails.append(f"articles.json parse {e}")
else:
    fails.append("articles.json fetch fail")

for u in ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/", "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]:
    c = curl(u)
    print(c, u)
    if c != "200": fails.append(f"{u} {c}")

print("FAILURES =", fails if fails else "NONE")
