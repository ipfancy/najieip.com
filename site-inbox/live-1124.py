#!/usr/bin/env python3
import re, json, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def fetch(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "60", "-A", UA, url],
                           capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout
        time.sleep(6)
    return ""

def code(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}",
                            "-A", UA, "--max-time", "30", url], capture_output=True, text=True)
        if r.stdout.strip() == "200":
            return "200"
        time.sleep(6)
    return r.stdout.strip()

cb = str(int(time.time()))
fails = []
u = f"https://najieip.com/mili/blog/20261124-mili-punitive-damages-one-shot.html?cb={cb}"
t = fetch(u)
h1 = len(re.findall(r"<h1[ >]", t))
h2 = len(re.findall(r"<h2[ >]", t))
ld = t.count("application/ld+json")
og = 'property="og:image"' in t
stars = re.sub(r"[0-9]\*{2,}[0-9.]*", "", t).count("**")
desc = (re.search(r'<meta name="description" content="(.*?)"', t) or [None, ""])[1]
print(f"PAGE size={len(t.encode())} h1={h1} h2={h2} ld={ld} ogimg={int(og)} stars={stars} descLen={len(desc)}")
for k, v, good in [("h1", h1, 1), ("h2", h2, 3), ("ld", ld, 2), ("ogimg", int(og), 1), ("stars", stars, 0)]:
    if v != good: fails.append(f"page_{k}={v}")

img = code(f"https://najieip.com/img/20261124-mili-punitive-damages-one-shot.png?cb={cb}")
print("IMG", img)
if img != "200": fails.append("img")

for name, url in [("/", "https://najieip.com/"), ("/mili/", "https://najieip.com/mili/"),
                  ("/najie/", "https://najieip.com/najie/"), ("/blog/", "https://najieip.com/blog/")]:
    c = code(url + ("&" if "?" in url else "?") + "cb=" + cb)
    print("HTTP", name, c)
    if c != "200": fails.append(f"http{name}")

idx = fetch(f"https://najieip.com/mili/blog/?cb={cb}")
mc = re.findall(r'<h[23][^>]*><a href="[^"]*20261124-mili-punitive-damages-one-shot', idx)
print("mili index bytes", len(idx.encode()), "cards", len(mc))
if len(mc) < 1: fails.append("mili_index_card")

main = fetch(f"https://najieip.com/blog/?cb={cb}")
mm = re.findall(r'<h[23][^>]*><a href="[^"]*20261124-mili-punitive-damages-one-shot', main)
print("main index bytes", len(main.encode()), "cards", len(mm))
if len(mm) < 1: fails.append("main_index_card")

aj = fetch(f"https://najieip.com/articles.json?cb={cb}")
try:
    arr = json.loads(aj)
    arr = arr if isinstance(arr, list) else arr.get("articles", [])
    print("live articles.json n=", len(arr))
except Exception as e:
    print("articles.json parse fail", e); fails.append("aj")

print("FAILURES:", fails if fails else "NONE")
