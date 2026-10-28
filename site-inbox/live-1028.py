#!/usr/bin/env python3
"""push 后线上终验：Actions run 状态 + 三索引/文章页 live 判据"""
import json, re, subprocess, time, sys

SHA = "bc0d446"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
EPOCH = str(int(time.time()))
SLUGS = [
    ("/mili/blog/20261028-mili-entity-switch-repeat-infringement.html", 2),
    ("/mili/blog/20261028-mili-pregnancy-disguised-dismissal-evidence.html", 2),
    ("/mili/blog/20261028-mili-software-copyright-proof-chain.html", 2),
    ("/najie/blog/20261028-najie-gi-zone-objection.html", 2),
]

def run_status():
    out = subprocess.check_output(["curl", "-s", "--max-time", "25",
        "https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=5"])
    d = json.loads(out)
    for r in d.get("workflow_runs", []):
        if r.get("head_sha", "").startswith(SHA):
            return r["status"], r.get("conclusion")
    return "not-found", None

for i in range(10):
    st, cc = run_status()
    print("actions run: %s / %s" % (st, cc))
    if st == "completed":
        break
    time.sleep(20)

time.sleep(45)

def get(url):
    for _ in range(3):
        p = subprocess.run(["curl", "-s", "--max-time", "40", "-A", UA, url],
                           capture_output=True, text=True)
        if p.returncode == 0 and len(p.stdout) > 500:
            return p.stdout
        time.sleep(3)
    return ""

fails = []
print("\n-- 文章页 --")
for path, minld in SLUGS:
    t = get("https://najieip.com" + path + "?cb=" + EPOCH)
    h1 = len(re.findall(r'<h1[\s>]', t))
    ld = len(re.findall(r'<script type="application/ld\+json">', t))
    og = 'property="og:image"' in t
    ok = bool(t) and h1 == 1 and ld >= minld and og
    print(("OK " if ok else "NG ") + "%s len=%d h1=%d ld=%d ogimg=%s" % (path, len(t), h1, ld, og))
    if not ok:
        fails.append(path)

print("\n-- 索引卡 HIT --")
main = get("https://najieip.com/blog/?cb=" + EPOCH)
print("main index len=%d cards=%d" % (len(main), len(re.findall(r'<div class="article-card">', main))))
for path, _ in SLUGS:
    hit = path in main
    print(("OK " if hit else "NG ") + path)
    if not hit:
        fails.append("main:" + path)
mili = get("https://najieip.com/mili/blog/?cb=" + EPOCH)
hit = "./20261028-mili-pregnancy-disguised-dismissal-evidence.html" in mili
print(("OK " if hit else "NG ") + "mili index pregnancy card (cards=%d)" % len(re.findall(r'<div class="article-card">', mili)))
if not hit:
    fails.append("mili-index")

print("\n-- 核心页 --")
for u in ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
          "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]:
    code = "000"
    for _ in range(3):
        p = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "30", "-A", UA, u],
                           capture_output=True, text=True)
        code = p.stdout.strip()
        if code == "200":
            break
        time.sleep(2)
    print(("OK " if code == "200" else "NG ") + code + " " + u)
    if code != "200":
        fails.append(u)

print("\nFAILS:", fails if fails else "NONE")
