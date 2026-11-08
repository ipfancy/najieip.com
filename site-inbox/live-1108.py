#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, subprocess, time, sys

SHA = "4e295cf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def curl(url, extra=None, binary=False):
    cmd = ["curl","-s","-A",UA,"--max-time","25"] + (extra or []) + [url]
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout if binary else r.stdout.decode('utf-8','ignore')

# 1. Actions run
run_id = None
for _ in range(20):
    try:
        d = json.loads(curl("https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=6"))
        for w in d.get("workflow_runs", []):
            if w.get("head_sha","").startswith(SHA):
                run_id = w["id"]
                print("RUN", run_id, w["status"], w["conclusion"])
                if w["status"] == "completed":
                    print("conclusion:", w["conclusion"])
                break
    except Exception as e:
        print("api err", e)
    if run_id:
        st = [w for w in d["workflow_runs"] if w["id"] == run_id][0]
        if st["status"] == "completed":
            print("FINAL", st["status"], st["conclusion"])
            break
    time.sleep(20)

time.sleep(45)
F = []
# 2. 页面六项
base = "https://najieip.com/mili/blog/20261108-mili-family-theft-leniency.html"
h = curl(base + "?cb=" + str(int(time.time())))
if not h or len(h) < 3000:
    print("page short, retry"); time.sleep(30); h = curl(base+"?cb="+str(int(time.time())))
ok = lambda c, m: (print(("PASS " if c else "FAIL ") + m), None if c else F.append(m))
ok(h.count('application/ld+json') == 2, "page ld=2")
ok(len(re.findall(r'<h1[ >]', h)) == 1, "page h1=1")
ok('og:image' in h and f'/img/20261108-mili-family-theft-leniency.png' in h, "page og:image")
ok(h.count('**') == 0, "page no **")
ok(h.count('<table class="data">') == 4, "page 4 tables")
m = re.search(r'<meta name="description" content="([^"]*)"', h)
ok(bool(m) and len(m.group(1)) > 80, "desc len>80")
ok('https://schema.org' in h and 'https://***' not in h, "schema.org intact")
m = re.search(r'<link rel="canonical" href="([^"]*)"', h)
ok(bool(m) and m.group(1).endswith('/mili/blog/20261108-mili-family-theft-leniency.html'), "canonical")
print("live bytes", len(h.encode()))

# 3. 封面图
for i in range(3):
    code = subprocess.run(["curl","-sI","-o","/dev/null","-w","%{http_code}","-A",UA,"--max-time","20",
                           "https://najieip.com/img/20261108-mili-family-theft-leniency.png"], capture_output=True).stdout.decode()
    if code == "200": break
    time.sleep(10)
ok(code == "200", f"cover img {code}")

# 4. 索引卡
for label, url, slug in [("main 11-08","https://najieip.com/blog/","20261108-mili-family-theft-leniency"),
                         ("mili 11-08","https://najieip.com/mili/blog/","20261108-mili-family-theft-leniency"),
                         ("main 11-01","https://najieip.com/blog/","20261101-mili-ai-writing-judgment")]:
    t = ""
    for i in range(3):
        t = curl(url + "?cb=" + str(int(time.time())))
        if slug in t: break
        time.sleep(25)
    ok(slug in t, f"card HIT {label}")

# 5. live articles.json
a = json.loads(curl("https://najieip.com/articles.json?cb=" + str(int(time.time()))))
arr = a if isinstance(a, list) else a.get('articles', [])
print("live articles.json", len(arr))

print("FAILURES", F if F else "NONE")
