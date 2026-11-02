#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-02 线上终验"""
import os, re, json, subprocess, time

REPO = os.path.expanduser("~/wiki/najieip-verify")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
CB = str(int(time.time()))
fails = []

def fetch(url, binary=False):
    cmd = ["curl", "-sL", "-A", UA, "--max-time", "45", url]
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout

def status(url):
    for _ in range(3):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, "--max-time", "30", url],
                           capture_output=True, text=True)
        if r.stdout.strip() == "200":
            return "200"
        time.sleep(3)
    return r.stdout.strip()

PAGES = [
    ("https://najieip.com/najie/blog/20261102-najie-tech-export-catalog-48.html",
     "najie/blog/20261102-najie-tech-export-catalog-48.html"),
    ("https://najieip.com/najie/blog/20261102-najie-ai-search-summary-pay.html",
     "najie/blog/20261102-najie-ai-search-summary-pay.html"),
]
for url, local in PAGES:
    t = fetch(url + "?cb=" + CB).decode("utf-8", "replace")
    name = local.split("/")[-1][:34]
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = len(re.findall(r"application/ld\+json", t))
    oi = len(re.findall(r'property="og:image"', t))
    tw = len(re.findall(r'name="twitter:title"', t))
    stars = len(re.findall(r"\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", re.sub(r"<script.*?</script>", " ", t, flags=re.S))))
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    can = re.search(r'rel="canonical" href="([^"]*)"', t)
    size = len(t.encode())
    ok = (h1 == 1 and ld >= 2 and oi == 1 and tw == 1 and stars == 0 and desc and len(desc.group(1)) > 80
          and desc.group(1).strip() != title.group(1).strip() and f"/{local}" in (can.group(1) if can else ""))
    print(f"{'PASS' if ok else 'FAIL'} {name} size={size} h1={h1} ld={ld} ogimg={oi} tw={tw} stars={stars} desc={len(desc.group(1)) if desc else 0} can_ok={f'/{local}' in (can.group(1) if can else '')}")
    if not ok:
        fails.append(name)

# 本地/线上字节（文章页应严格一致）
for url, local in PAGES:
    lp = os.path.join(REPO, local)
    live = fetch(url + "?cb=" + CB)
    lb = open(lp, "rb").read()
    same = live == lb
    print(f"{'PASS' if same else 'NOTE'} bytes {local.split('/')[-1][:36]} local={len(lb)} live={len(live)} delta={len(live)-len(lb)}")
    if not same:
        import difflib
        a = lb.decode("utf-8", "replace").splitlines()
        b = live.decode("utf-8", "replace").splitlines()
        d = [l for l in difflib.unified_diff(a, b, lineterm="") if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        print("   diff lines:", len(d), d[:3])

# 封面
u = "https://najieip.com/img/20261102-najie-tech-export-catalog-48.png"
print(f"{'PASS' if status(u) == '200' else 'FAIL'} cover img 200")

# 索引卡
for idx, slugs in [("https://najieip.com/blog/", ["20261102-najie-tech-export-catalog-48", "20261102-najie-ai-search-summary-pay"]),
                   ("https://najieip.com/najie/blog/", ["20261102-najie-tech-export-catalog-48", "20261102-najie-ai-search-summary-pay"])]:
    t = fetch(idx + "?cb=" + CB).decode("utf-8", "replace")
    for s in slugs:
        n = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), t))
        print(f"{'PASS' if n == 1 else 'FAIL'} card {idx.split('/')[3] or 'root'} {s[-26:]} n={n}")
        if n != 1:
            fails.append(f"{idx}{s}")

# live articles.json
t = fetch("https://najieip.com/articles.json?cb=" + CB).decode("utf-8", "replace")
try:
    arr = json.loads(t)
    print(f"{'PASS' if len(arr) == 229 else 'FAIL'} live articles.json len={len(arr)} (expect 229)")
    for s in ["20261102-najie-tech-export-catalog-48", "20261102-najie-ai-search-summary-pay"]:
        hit = any(s in (x.get("url") or "") for x in arr)
        print(f"{'PASS' if hit else 'FAIL'} articles.json has {s[-26:]}")
except Exception as e:
    print("FAIL articles.json parse", e)
    fails.append("articles.json")

print("\nFAILURES:", fails if fails else "NONE")
