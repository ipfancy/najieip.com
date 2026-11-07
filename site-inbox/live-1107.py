import os, re, json, subprocess, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl","-4","-s","-A",UA,"--max-time","30",url], capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 200: return r.stdout
        time.sleep(6)
    return r.stdout or ""
def code(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl","-4","-sI","-A",UA,"-o","/dev/null","-w","%{http_code}","--max-time","30",url], capture_output=True, text=True)
        if r.stdout.strip() == "200": return "200"
        time.sleep(5)
    return r.stdout.strip()

PAGES = ["mili/blog/20261107-mili-unpaid-trial-shigang.html",
         "mili/blog/20261107-mili-trademark-transition-rules-4-lines.html",
         "najie/blog/20261107-najie-patent-license-contract-6-clauses.html",
         "mili/blog/20261107-mili-unjust-enrichment-default-judgment.html"]
FAIL = []
for p in PAGES:
    url = "https://najieip.com/" + p + "?cb=%d" % int(time.time())
    c = code(url); t = get(url) if c == "200" else ""
    h1 = len(re.findall(r"<h1[ >]", t)); ld = t.count("application/ld+json")
    ok = (c == "200" and h1 == 1 and ld >= 2 and "og:image" in t and t.count("**") == 0)
    print(f"{'PASS' if ok else 'FAIL'} {p.split('/')[-1][:46]:48s} http={c} bytes={len(t.encode())} h1={h1} ld={ld} ogimg={'og:image' in t} **={t.count('**')}")
    if not ok: FAIL.append(p)

# cover
c = code("https://najieip.com/img/20261107-mili-unpaid-trial-shigang.png")
print("cover:", c);  FAIL += [] if c == "200" else ["cover"]

# index cards live
IDX = {"mili": ("mili/blog/", ["20261107-mili-trademark-transition-rules-4-lines","20261107-mili-unpaid-trial-shigang"]),
       "najie": ("najie/blog/", ["20261107-najie-patent-license-contract-6-clauses"]),
       "main": ("blog/", ["20261107-mili-unjust-enrichment-default-judgment","20261107-najie-patent-license-contract-6-clauses","20261107-mili-trademark-transition-rules-4-lines"])}
for k, (base, slugs) in IDX.items():
    t = get("https://najieip.com/%s?cb=%d" % (base, int(time.time())))
    for s in slugs:
        hit = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(s), t))
        print(f"card {k:6s} {s[-40:]:42s} hit={hit}")
        if hit != 1: FAIL.append(k + ":" + s)

# live articles.json
aj = get("https://najieip.com/articles.json?cb=%d" % int(time.time()))
try:
    n = len(json.loads(aj)); print("live articles.json:", n)
    if n != 242: FAIL.append("articles.json live %d" % n)
except Exception as e:
    print("articles.json parse fail", e); FAIL.append("articles.json")

print("\nFAILURES:", FAIL if FAIL else "NONE")
