#!/usr/bin/env python3
"""SiteOps 1021晚 线上终验"""
import re, json, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
CB = str(int(time.time()))

def get(url, head=False):
    cmd = ["curl", "-s", "-m", "25", "-A", UA]
    if head:
        cmd += ["-o", "/dev/null", "-w", "%{http_code}"]
    cmd.append(url + ("?cb=" + CB if "?" not in url else "&cb=" + CB) if "najieip.com" in url else url)
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout

fails = []
PAGES = [
    "https://najieip.com/mili/blog/20261022-judge-liability-verdict-reversed.html",
    "https://najieip.com/mili/blog/20261021-3gpp-proposal-prior-art-date.html",
    "https://najieip.com/najie/blog/20261021-goods-names-acceptable-list-q4.html",
]
for u in PAGES:
    code = get(u, head=True)
    body = get(u)
    h1 = len(re.findall(r"<h1[\s>]", body))
    ld = body.count("application/ld+json")
    ogi = 'property="og:image"' in body
    twi = 'name="twitter:image"' in body
    stars = body.count("**")
    ok = code == "200" and h1 == 1 and ld >= 2 and ogi and stars == 0
    print(f"{'PASS' if ok else 'FAIL'} {u.split('/')[-1]} code={code} h1={h1} ld={ld} og:image={ogi} tw:image={twi} stars={stars}")
    if not ok: fails.append(u)

idx = get("https://najieip.com/blog/")
for s in ["20261022-judge-liability-verdict-reversed", "20261021-3gpp-proposal-prior-art-date",
          "20261021-goods-names-acceptable-list-q4"]:
    hit = s in idx
    print(f"{'PASS' if hit else 'FAIL'} 主索引线上含 {s}")
    if not hit: fails.append(s)
print("线上主索引卡片数 =", idx.count('class="article-card"'))

aj = get("https://najieip.com/articles.json")
try:
    live = json.loads(aj)
    print(f"{'PASS' if len(live) == 196 else 'FAIL'} 线上 articles.json = {len(live)} (期望 196), top1={live[0]['date']}")
    if len(live) != 196: fails.append("articles.json-count")
except Exception as e:
    print("FAIL live articles.json parse:", e, aj[:120]); fails.append("articles.json")

code = get("https://images.pexels.com/photos/5669619/pexels-photo-5669619.jpeg?auto=compress&cs=tinysrgb&w=1200", head=True)
print(f"{'PASS' if code == '200' else 'FAIL'} judge og:image 资源 code={code}")

print("\nFAILURES =", fails if fails else "NONE")
