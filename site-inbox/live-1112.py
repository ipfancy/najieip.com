#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def get(url, tries=3):
    last = ""
    for _ in range(tries):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "60", "-A", UA, url],
                           capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout
        last = "code=%s len=%s" % (r.returncode, len(r.stdout))
        time.sleep(6)
    return ""

def code(url):
    r = subprocess.run(["curl", "-sI", "-L", "-A", UA, "-o", "/dev/null",
                        "-w", "%{http_code}", "--max-time", "30", url],
                       capture_output=True, text=True)
    return r.stdout.strip()

F = []
def chk(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + extra if extra else ""))
    if not cond:
        F.append(name)

b = int(time.time())
base = "https://najieip.com"
urls = [
    (base + "/", 200), (base + "/mili/", 200), (base + "/najie/", 200),
    (base + "/blog/", 200), (base + "/sitemap.xml", 200), (base + "/llms.txt", 200),
    (base + "/najie/blog/20261112-maldives-trademark-law.html", 200),
    (base + "/img/20261112-maldives-trademark-law.png", 200),
    (base + "/mili/blog/20261112-mili-year-end-bonus-cancel.html", 200),
    (base + "/mili/blog/20261111-mili-earnest-money-cap.html", 200),
]
for u, exp in urls:
    c = code(u)
    if c != str(exp):
        c = code(u)   # 重试一次
    chk(f"HTTP {c} {u.replace(base,'')}", c == str(exp))

# 页面六项（online）
p = get(base + f"/najie/blog/20261112-maldives-trademark-law.html?cb={b}")
chk("online h1", len(re.findall(r"<h1[ >]", p)) == 1, str(len(p)))
chk("online h2>=1", len(re.findall(r"<h2[ >]", p)) >= 1)
chk("online ld=2", len(re.findall(r"application/ld\+json", p)) == 2)
chk("online og:image", "og:image" in p)
chk("online schema.org", p.count("https://schema.org") >= 2, str(p.count("https://schema.org")))
chk("online stars=0", re.sub(r"[0-9]\*{2,}[0-9.]*", "", p[p.find("<body"):]).count("**") == 0)
m = re.search(r'<meta name="description" content="([^"]*)"', p)
chk("online desc>80", bool(m and len(m.group(1)) > 80), str(len(m.group(1)) if m else 0))
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', p, re.S):
    try:
        json.loads(blk)
    except Exception as e:
        chk("online ld json.loads", False, str(e)[:60]); break
else:
    chk("online ld json.loads", True)

# 索引卡 HIT + 字节一致
for name, path, slug in [
    ("najie index", "/najie/blog/index.html", "20261112-maldives-trademark-law"),
    ("main index", "/blog/index.html", "20261112-maldives-trademark-law"),
    ("mili index", "/mili/blog/index.html", "20261112-mili-year-end-bonus-cancel"),
]:
    h = get(base + path + f"?cb={b}")
    chk(f"{name} card HIT {slug[:22]}", h.count(slug) >= 1, f"bytes={len(h.encode())}")

# 字节一致（索引 + 文章页）
import os
for name, remote, local in [
    ("najie index bytes", "/najie/blog/index.html?cb=%d" % b, "najie/blog/index.html"),
    ("article bytes", "/najie/blog/20261112-maldives-trademark-law.html?cb=%d" % b, "najie/blog/20261112-maldives-trademark-law.html"),
]:
    h = get(base + remote)
    lb = os.path.getsize(os.path.expanduser("~/wiki/najieip-verify/" + local))
    d = len(h.encode()) - lb
    # CF beacon 注入 ~367B 属正常
    chk(f"{name} delta", d == 0 or (abs(d) < 500 and "beacon.min.js" in h), f"remote={len(h.encode())} local={lb} delta={d}")

# live articles.json
live = get(base + f"/articles.json?cb={b}")
try:
    lj = json.loads(live)
    la = lj if isinstance(lj, list) else lj.get("articles", [])
    chk("live articles.json=250", len(la) == 250, str(len(la)))
    chk("live top1 = today", "20261112-maldives" in la[0].get("url", ""), la[0].get("url", ""))
except Exception as e:
    chk("live articles.json parse", False, str(e)[:60])

print("\nFAILURES:", F if F else "NONE")
