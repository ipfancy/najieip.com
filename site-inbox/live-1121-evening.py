import re, subprocess, time, json, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url, tries=3, max_time=60):
    for i in range(tries):
        p = subprocess.run(["curl", "-s", "-L", "--max-time", str(max_time), "-A", UA,
                            url + ("&" if "?" in url else "?") + "cb=%d" % int(time.time() * 1000)],
                           capture_output=True, text=True, errors="replace")
        if p.returncode == 0 and len(p.stdout) > 500:
            return p.stdout
        time.sleep(5)
    return ""

def code(url):
    for i in range(3):
        p = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "25", "-A", UA, url],
                           capture_output=True, text=True)
        c = p.stdout.strip()
        if c == "200":
            return c
        time.sleep(5)
    return c

F = 0
def chk(name, cond, extra=""):
    global F
    print(("PASS " if cond else "FAIL ") + name, extra)
    if not cond:
        F += 1

arts = ["/mili/blog/20261121-mili-divorce-game-account-88w.html",
        "/mili/blog/20261121-mili-patent-agency-revoked-34.html",
        "/najie/blog/20261121-najie-sep-administrative-ruling-37-articles.html"]
for a in arts:
    t = get("https://najieip.com" + a)
    h1 = len(re.findall(r"<h1", t)); ld = len(re.findall(r"application/ld\+json", t))
    chk(a.split("/")[-1][:44], bool(t) and h1 == 1 and ld >= 2 and "og:image" in t and t.count("**") == 0,
        "bytes=%d h1=%d ld=%d ogimg=%s stars=%d" % (len(t), h1, ld, "og:image" in t, t.count("**")))

chk("img cover", code("https://najieip.com/img/20261121-mili-divorce-game-account-88w.png") == "200")
for name, p, slugs in (("main", "/blog/", ["20261121-mili-patent-agency-revoked-34", "20261121-najie-sep-administrative-ruling-37-articles"]),
                       ("mili", "/mili/blog/", ["20261121-mili-patent-agency-revoked-34"]),
                       ("najie", "/najie/blog/", ["20261121-najie-sep-administrative-ruling-37-articles"])):
    t = get("https://najieip.com" + p)
    for s in slugs:
        chk("%s card %s" % (name, s[:40]), s in t, "bytes=%d" % len(t))

t = get("https://najieip.com/articles.json")
try:
    d = json.loads(t)
    chk("articles.json live", len(d) == 274, "entries=%d" % len(d))
except Exception as e:
    chk("articles.json live", False, str(e)[:60])

for p in ("/", "/mili/", "/najie/", "/sitemap.xml", "/llms.txt"):
    chk("HTTP" + p, code("https://najieip.com" + p) == "200")

print("FAILURES=%d" % F)
