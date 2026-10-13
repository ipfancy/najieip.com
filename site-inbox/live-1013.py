#!/usr/bin/env python3
"""SiteOps 1013 线上终验 — 只读。"""
import os, re, json, subprocess, time, urllib.request

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        code = getattr(e, "code", 0)
        return code, ""


def head_status(url, tries=3):
    last = 0
    for i in range(tries):
        out = subprocess.run(
            ["curl", "-sI", "-L", "-A", UA, "-o", "/dev/null", "-w", "%{http_code}", url, "--max-time", "25"],
            capture_output=True, text=True).stdout.strip()
        last = out
        if out == "200":
            return out, i + 1
        time.sleep(3)
    return last, tries


print("=== [A] 核心页 HTTP（首轮非 200 自动重试 3 次）===")
for u in ["", "mili/", "najie/", "blog/", "sitemap.xml", "llms.txt"]:
    code, tr = head_status("https://najieip.com/" + u)
    print(f"  {code}  /{u}  (try {tr})")

cb = str(int(time.time()))
print("\n=== [B] 修复页线上 6 项 ===")
target = "https://najieip.com/mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html?cb=" + cb
st, t = fetch(target)
res = {}
if st == 200:
    res["ld"] = t.count("application/ld+json")
    res["ogimg"] = t.count("og:image")
    res["stars"] = t.count("**")
    res["h1"] = len(re.findall(r"<h1[ >]", t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    res["desc_len"] = len(m.group(1)) if m else 0
    res["schema"] = t.count("https://schema.org")
    res["schema_bad"] = t.count("https://***")
    res["bytes"] = len(t.encode())
    print(f"  status={st} bytes={res['bytes']} h1={res['h1']} ld={res['ld']} og:image={res['ogimg']} "
          f"desc_len={res['desc_len']} **={res['stars']} schema.org={res['schema']} 脱敏={res['schema_bad']}")
    ok = res["h1"] == 1 and res["ld"] >= 2 and res["ogimg"] >= 1 and res["desc_len"] > 80 and res["stars"] == 0 and res["schema_bad"] == 0
    print("  判据:", "PASS" if ok else "FAIL")
else:
    print(f"  status={st} (非 200，稍后重试)")

print("\n=== [C] articles.json / sitemap / 索引卡片 ===")
st, aj = fetch("https://najieip.com/articles.json?cb=" + cb)
try:
    d = json.loads(aj)
    arts = d if isinstance(d, list) else d.get("articles", [])
    print(f"  live articles.json = {len(arts)} 条 | top1 = {arts[0].get('url')}")
except Exception as e:
    print("  articles.json 解析失败:", e)

st, sm = fetch("https://najieip.com/sitemap.xml?cb=" + cb)
locs = re.findall(r"<loc>(.*?)</loc>", sm)
blocks = re.findall(r"<url>(.*?)</url>", sm, re.S)
print(f"  live sitemap loc = {len(locs)} | 无 lastmod = {sum(1 for b in blocks if '<lastmod>' not in b)}")
print(f"  含修复页 loc = {'yes' if any('20261010-mili-aigc' in l for l in locs) else 'no'}")

for idx in ["mili/blog/", "blog/"]:
    st, h = fetch(f"https://najieip.com/{idx}?cb=" + cb)
    hit = h.count("20261010-mili-aigc")
    print(f"  {idx} 卡片 HIT = {hit}")

print("\n=== [D] 本地 vs origin ===")
print(" ", subprocess.run(["git", "rev-parse", "HEAD", "origin/main"], capture_output=True, text=True).stdout.strip().replace("\n", " | "))
print("  worktree:", subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip() or "(clean)")
