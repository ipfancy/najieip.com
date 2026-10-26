#!/usr/bin/env python3
# 线上终验 20261026
import subprocess, re, json, time, sys
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def curl(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "25",
                            url + ("&" if "?" in url else "?") + f"cb={int(time.time())}"],
                           capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 100:
            return r.stdout
        time.sleep(3)
    return ""
def head(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sI", "-A", UA, "-o", "/dev/null",
                            "-w", "%{http_code}", "--max-time", "20", url],
                           capture_output=True, text=True)
        if r.stdout.strip() == "200":
            return "200"
        time.sleep(3)
    return r.stdout.strip() or "000"

time.sleep(100)
fails = []
# 1 pages
pages = ["/mili/blog/20261026-mili-divorce-inheritance-property.html",
         "/najie/blog/20261026-najie-double11-ip-risk.html",
         "/mili/blog/20261026-trade-secret-secret-point-fixation.html",
         "/mili/secret-point-templates.html",
         "/mili/", "/najie/", "/"]
for p in pages:
    c = head("https://najieip.com" + p)
    ok = c == "200"
    print(f"{'OK ' if ok else 'FAIL'} {c} {p}")
    if not ok: fails.append(f"HTTP {p} = {c}")

# 2 main index live
mi = curl("https://najieip.com/blog/")
print(f"[live] blog/index bytes={len(mi.encode())} cards={mi.count('article-card')}")
for s in ["20261026-mili-divorce-inheritance-property", "20261026-najie-double11-ip-risk",
          "20261026-trade-secret-secret-point-fixation"]:
    hit = f'/{ "mili" if "mili" in s or "trade" in s else "najie"}/blog/{s}.html' in mi
    print(f"{'OK ' if hit else 'FAIL'} card {s}")
    if not hit: fails.append(f"card missing live: {s}")

# 3 live articles.json
aj = curl("https://najieip.com/articles.json")
try:
    data = json.loads(aj)
    print(f"[live] articles.json n={len(data)}")
    if not any("20261026-trade-secret-secret-point-fixation" in json.dumps(x, ensure_ascii=False) for x in data):
        fails.append("articles.json live missing trade-secret")
    for i, a in enumerate(data[:6], 1):
        print(f"  top{i} {a.get('date')} {a.get('url')}")
except Exception as e:
    fails.append(f"articles.json parse: {e}")

# 4 sitemap
sm = curl("https://najieip.com/sitemap.xml")
loc = sm.count("<loc>")
print(f"[live] sitemap loc={loc} trade_secret={'secret-point-fixation' in sm} templates={'secret-point-templates' in sm}")
if loc < 338: fails.append(f"sitemap loc {loc} < 338")

print("\nFAILS:", fails or "NONE")
