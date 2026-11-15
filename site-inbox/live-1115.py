#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-15 线上验证：Pages run 状态 + 页面六项 + 封面 + 索引卡 + articles.json"""
import json, re, subprocess, time, sys

SHA = "27c6f0f"
BASE = "https://najieip.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "20261115-mili-payment-60days-b2b"

def curl(url, timeout=60):
    r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", str(timeout), url],
                       capture_output=True, text=True, errors="replace")
    return r.stdout

def http(url):
    r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA,
                        "--max-time", "30", url], capture_output=True, text=True)
    return r.stdout.strip()

# 1) Pages run
run = None
for _ in range(20):
    try:
        d = json.loads(curl("https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=5"))
        for r in d.get("workflow_runs", []):
            if r.get("head_sha", "").startswith(SHA):
                run = r
                break
    except Exception as e:
        pass
    if run and run.get("status") == "completed":
        break
    time.sleep(15)
print("RUN:", run and run.get("status"), run and run.get("conclusion"), run and run.get("head_sha", "")[:7])

checks = {}
time.sleep(45)
for attempt in range(3):
    t = curl(f"{BASE}/mili/blog/{SLUG}.html?cb={int(time.time())}")
    ok = len(t) > 5000 and "<h1" in t
    if ok:
        break
    time.sleep(60)

lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
checks["page"] = dict(
    bytes=len(t.encode()),
    h1=len(re.findall(r"<h1[ >]", t)),
    ld=len(lds),
    types=[json.loads(b).get("@type") for b in lds if b.strip()],
    og_image=len(re.findall(r'property="og:image"', t)),
    star=t.count("**"),
    desc=re.search(r'<meta name="description" content="([^"]{0,50})', t).group(1) if re.search(r'<meta name="description"', t) else "",
    canonical=re.findall(r'canonical" href="([^"]+)"', t),
)

# 2) 封面图（二进制传播可能滞后）
img = 0
for i in range(3):
    img = http(f"{BASE}/img/{SLUG}.png")
    if img == "200":
        break
    time.sleep(10)
checks["img"] = img

# 3) 双索引卡（大文件用 -o 落地再 grep）
for name, path in [("mili_index", "/mili/blog/"), ("main_index", "/blog/")]:
    out = f"/tmp/v1115_{name}.html"
    subprocess.run(["curl", "-s", "-A", UA, "--max-time", "60",
                    f"{BASE}{path}?cb={int(time.time())}", "-o", out], check=False)
    try:
        body = open(out, encoding="utf-8", errors="replace").read()
    except Exception:
        body = ""
    checks[name] = dict(bytes=len(body.encode()),
                        card=len(re.findall(r'<h[23][^>]*><a href="[^"]*' + SLUG, body)))

# 4) articles.json
aj = curl(f"{BASE}/articles.json?cb={int(time.time())}")
try:
    items = json.loads(aj)
    items = items if isinstance(items, list) else items.get("articles", [])
    checks["articles_json"] = dict(total=len(items), first=items[0].get("url") if items else None)
except Exception as e:
    checks["articles_json"] = dict(error=str(e), head=aj[:100])

# 5) 核心页
checks["core"] = {u: http(BASE + u) for u in ["", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]}

fails = []
c = checks["page"]
if c["h1"] != 1: fails.append("h1")
if c["ld"] != 2: fails.append("ld")
if c["og_image"] != 1: fails.append("og:image")
if c["star"] != 0: fails.append("star")
if checks["img"] != "200": fails.append("img")
if checks["mili_index"]["card"] < 1: fails.append("mili_card")
if checks["main_index"]["card"] < 1: fails.append("main_card")
bad = {k: v for k, v in checks["core"].items() if v != "200"}
if bad: fails.append(f"core{bad}")

print(json.dumps(checks, ensure_ascii=False, indent=1))
print("FAILURES:", fails or "NONE")
