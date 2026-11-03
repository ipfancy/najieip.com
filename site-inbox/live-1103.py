import re, json, subprocess, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url, retries=3):
    for i in range(retries):
        r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "25", url], capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode("utf-8", "replace")
        time.sleep(3)
    return ""
def code(url, retries=3):
    for i in range(retries):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, "--max-time", "25", url],
                           capture_output=True, text=True)
        if r.stdout.strip() == "200":
            return "200"
        time.sleep(3)
    return r.stdout.strip()
F = []
def chk(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond: F.append(msg)

for u in ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]:
    chk(code("https://najieip.com" + u) == "200", f"HTTP {u}")

SLUGS = ["20261103-mili-unfair-competition-data-scraping", "20261103-mili-patrol-robot-four-questions"]
for s in SLUGS:
    url = f"https://najieip.com/mili/blog/{s}.html"
    t = get(url)
    ldc = len(re.findall(r'<script type="application/ld\+json">', t))
    chk(ldc >= 2, f"{s[:28]} ld={ldc}")
    chk("og:image" in t, f"{s[:28]} og:image")
    chk(len(re.findall(r"<h1[^>]*>", t)) == 1, f"{s[:28]} h1==1")
    bt = t[t.find("<body"):] if "<body" in t else t
    chk(len(re.findall(r"[0-9*]\*\*", bt)) == 0, f"{s[:28]} stars==0")
    d = re.search(r'<meta name="description" content="(.*?)">', t, re.S)
    chk(bool(d) and len(d.group(1)) > 80, f"{s[:28]} desc_len={len(d.group(1)) if d else 0}")
    chk(f'https://najieip.com/img/{s}.png' in t, f"{s[:28]} og:image self-hosted")
chk(code("https://najieip.com/img/20261103-mili-unfair-competition-data-scraping.png") == "200", "cover png 200")
idx = get("https://najieip.com/blog/?cb=%d" % int(time.time()))
for s in SLUGS:
    chk(len(re.findall(r'<h[23][^>]*><a href="[^"]*' + s, idx)) >= 1, f"main index card {s[:26]}")
mi = get("https://najieip.com/mili/blog/?cb=%d" % int(time.time()))
for s in SLUGS:
    chk(len(re.findall(r'<h[23][^>]*><a href="[^"]*' + s, mi)) >= 1, f"mili index card {s[:26]}")
aj = get("https://najieip.com/articles.json?cb=%d" % int(time.time()))
try:
    n = len(json.loads(aj)); chk(n == 231, f"live articles.json={n}")
except Exception as e:
    chk(False, f"live articles.json parse {e}")
print("FAILURES:", F if F else "NONE")
