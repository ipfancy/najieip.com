import json, re, subprocess, time, sys

SLUG = "20261109-mili-prepaid-card-refund"
SHA = "3d97e42"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def api(url):
    r = subprocess.run(["curl", "-s", "--max-time", "25", "-A", UA, url], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}

# poll actions
status = "?"
for i in range(14):
    d = api("https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=6")
    hit = None
    for run in d.get("workflow_runs", []):
        if run.get("head_sha", "").startswith(SHA):
            hit = run
            break
    if hit:
        status = "%s/%s" % (hit.get("status"), hit.get("conclusion"))
        if hit.get("status") == "completed":
            break
    time.sleep(15)
print("ACTIONS", status)

def get(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, url], capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout
        time.sleep(8)
    return ""

cb = str(int(time.time()))
base = "https://najieip.com"
fails = []
pg = get(base + "/mili/blog/%s.html?cb=%s" % (SLUG, cb))
checks = {
    "page_200": len(pg) > 5000,
    "h1_1": pg.count("<h1") == 1,
    "ld_2": pg.count("application/ld+json") >= 2,
    "og_image": 'property="og:image"' in pg,
    "og_site": "og:site_name" in pg,
    "desc_long": len(re.search(r'<meta name="description" content="([^"]*)"', pg).group(1)) > 80 if 'name="description"' in pg else False,
    "stars_0": pg.count("**") == 0,
    "canonical_ok": ("/mili/blog/%s.html" % SLUG) in pg,
    "keywords": 'name="keywords"' in pg,
}
print("BYTES", len(pg.encode()), "PAGE", checks)
for k, v in checks.items():
    if not v:
        fails.append("page:" + k)

im = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, base + "/img/%s.png" % SLUG], capture_output=True, text=True).stdout.strip()
print("IMG", im)
if im != "200":
    fails.append("img:" + im)

for path, needle in (("mili/blog/", "./" + SLUG + ".html"), ("blog/", "/mili/blog/" + SLUG + ".html")):
    t = get(base + "/" + path + "?cb=" + cb)
    ok = needle in t
    print("IDX", path, "bytes", len(t), "hit", ok, "cards", t.count('<div class="article-card">'))
    if not ok:
        fails.append("idx:" + path)

aj = get(base + "/articles.json?cb=" + cb)
try:
    j = json.loads(aj)
    print("LIVE articles.json", len(j), "has", any(SLUG in x["url"] for x in j[:3]))
except Exception as e:
    print("LIVE articles.json parse fail", len(aj), e)
    fails.append("articles.json")

print("FAILURES=", fails if fails else "NONE")
