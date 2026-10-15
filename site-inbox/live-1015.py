#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交剩余脚本 + 线上终验（curl 直连 + ?cb=）"""
import os, re, subprocess, time, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
SLUG = "20261015-ip-4-hard-deadlines-buju-revision"
CB = str(int(time.time()))

def run(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, capture_output=True, text=True, env=e)
    return p

print("=== A. 提交剩余文件 ===")
run(["git", "add", "-A"])
p = run(["git", "commit", "-m", "siteops(1015): 巡检脚本 + quarantine 档入库"])
print(p.stdout.strip()[:400])
p = run(["git", "push", "origin", "main"])
if p.returncode != 0 or "publickey" in (p.stderr or ""):
    p = run(["git", "push", "origin", "main"],
            env={"GIT_SSH_COMMAND": "ssh -i /Users/ziganghe/.ssh/id_ed25519 -o IdentitiesOnly=yes"})
print("push rc=%d %s" % (p.returncode, (p.stderr or "").strip()[:200]))
print(run(["git", "status", "--porcelain"]).stdout.strip() or "(clean)")

def fetch(path):
    out = None
    for _ in range(3):
        p = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "25", BASE + path], capture_output=True, text=True)
        if p.stdout and len(p.stdout) > 200:
            out = p.stdout; break
        time.sleep(4)
    return out or ""

def flines():
    return open("blog/index.html", encoding="utf-8").read(), open("mili/blog/index.html", encoding="utf-8").read()

print("\n=== B. 核心页 HTTP ===")
for path in ("/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt",
             "/mili/blog/%s.html" % SLUG, "/mili/blog/", "/img/%s.png" % SLUG):
    code = "000"
    for _ in range(3):
        p = subprocess.run(["curl", "-sI", "-L", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA,
                            "--max-time", "20", BASE + path], capture_output=True, text=True)
        code = (p.stdout or "000").strip()
        if code == "200":
            break
        time.sleep(3)
    print("  %-52s %s" % (path, code))

print("\n=== C. 新页线上判据 ===")
h = fetch("/mili/blog/%s.html?cb=%s" % (SLUG, CB))
print("  bytes=%d" % len(h.encode()))
checks = {
    "h1==1": len(re.findall(r"<h1[ >]", h)) == 1,
    "ld>=2": h.count("application/ld+json") >= 2,
    "og:image": 'property="og:image"' in h,
    "twitter:image": 'name="twitter:image"' in h,
    "keywords": 'name="keywords"' in h,
    "desc_len>120": len(re.search(r'<meta\s+name="description"\s+content="([^"]*)"', h).group(1)) > 120 if re.search(r'<meta\s+name="description"\s+content="([^"]*)"', h) else False,
    "**==0": h.count("**") == 0,
    "schema.org": h.count("https://schema.org") >= 2,
}
for k, v in checks.items():
    print("    %-16s %s" % (k, "PASS" if v else "FAIL"))

print("\n=== D. 索引卡线上 HIT ===")
lm = fetch("/mili/blog/?cb=%s" % CB)
lb = fetch("/blog/?cb=%s" % CB)
print("  mili index bytes=%d  card_hit=%s" % (len(lm.encode()), SLUG in lm))
print("  main index bytes=%d  card_hit=%s" % (len(lb.encode()), SLUG in lb))
print("  mili live cards=%d loc_local=%d" % (lm.count('<div class="article-card">'),
                                            open("mili/blog/index.html", encoding="utf-8").read().count('<div class="article-card">')))
print("  main live cards=%d loc_local=%d" % (lb.count('<div class="article-card">'),
                                            open("blog/index.html", encoding="utf-8").read().count('<div class="article-card">')))

print("\n=== E. articles.json 线上条目数 ===")
aj = fetch("/articles.json?cb=%s" % CB)
try:
    d = json.loads(aj)
    print("  live entries =", len(d) if isinstance(d, list) else len(d.get("articles", d)))
except Exception as e:
    print("  parse fail:", e, aj[:200])

print("\n=== F. sitemap 线上 loc ===")
sm = fetch("/sitemap.xml?cb=%s" % CB)
L = re.findall(r"<loc>(.*?)</loc>", sm)
print("  loc=%d  含新页=%s" % (len(L), any(SLUG in u for u in L)))
