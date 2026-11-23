#!/usr/bin/env python3
"""11-23 evening live verification (direct najieip.com, cache-busted)."""
import subprocess, re, json, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url, tries=3, binary=False):
    for i in range(tries):
        cmd = ["curl", "-sL", "--max-time", "60", "-A", UA, url + ("?cb=%d" % int(time.time()) if "?" not in url else "&cb=%d" % int(time.time()))]
        if binary:
            r = subprocess.run(cmd + ["-o", "/dev/null", "-w", "%{http_code}"], capture_output=True, text=True)
            if r.stdout.strip() == "200":
                return "200"
        else:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.stdout and len(r.stdout) > 500:
                return r.stdout
        time.sleep(8)
    return None

G = "https://najieip.com/najie/blog/20261123-mili-gaoqi-2026-no-new-standard.html"
t = get(G)
res = {}
if t:
    body = t[t.find("<body"):]
    res["page_bytes"] = len(t.encode())
    res["h1"] = len(re.findall(r'<h1', t))
    res["ld"] = len(re.findall(r'application/ld\+json', t))
    res["ogimg"] = 'property="og:image"' in t
    res["fm_brand_leak"] = len(re.findall(r'<p>\s*brand\s*[:：]', t))
    res["hr_leak"] = len(re.findall(r'<p>\s*-{3,}\s*</p>', t))
    res["gt_leak"] = len(re.findall(r'<p[^>]*>\s*&gt;', t))
    res["h2"] = len(re.findall(r'<h2', t))
else:
    res["page"] = "FAIL"

# brand indices: card presence + byte size sanity
for brand, slug in [("najie", "20261123-mili-gaoqi-2026-no-new-standard"),
                    ("najie", "mili-food-oem-trademark-113-order-20261122"),
                    ("mili", "20261121-mili-divorce-game-account-88w")]:
    idx = get(f"https://najieip.com/{brand}/blog/")
    if idx:
        res[f"{brand}_idx_bytes"] = len(idx.encode())
        res[f"{brand}_card_{slug[:14]}"] = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), idx))
    else:
        res[f"{brand}_idx"] = "FAIL"

main = get("https://najieip.com/blog/")
if main:
    res["main_idx_bytes"] = len(main.encode())
    res["main_cards_total"] = len(re.findall(r'<div class="article-card">', main))
    for slug in ["20261123-mili-gaoqi-2026-no-new-standard", "mili-food-oem-trademark-113-order-20261122", "20261121-mili-divorce-game-account-88w"]:
        res["main_" + slug[:14]] = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), main))

aj = get("https://najieip.com/articles.json")
if aj:
    try:
        d = json.loads(aj)
        res["live_articles_json"] = len(d) if isinstance(d, list) else len(d.get("articles", []))
    except Exception as e:
        res["live_articles_json"] = "PARSE_FAIL:%s" % e

# cover image
for slug in ["20261123-mili-gaoqi-2026-no-new-standard", "mili-food-oem-trademark-113-order-20261122"]:
    res["img_" + slug[:12]] = get(f"https://najieip.com/img/{slug}.png", binary=True)

# sitemap loc count
sm = get("https://najieip.com/sitemap.xml")
if sm:
    res["sitemap_loc"] = len(re.findall(r'<loc>', sm))

print(json.dumps(res, ensure_ascii=False, indent=1))
