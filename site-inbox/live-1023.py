import subprocess, re, time, json, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
fails = []

def code(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sI", "-L", "-A", UA, "-o", "/dev/null",
                            "-w", "%{http_code}", "--max-time", "25", url],
                           capture_output=True, text=True)
        c = r.stdout.strip()
        if c == "200":
            return c
        time.sleep(3)
    return c

def body(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "30",
                            url + ("?cb=%d" % int(time.time()))], capture_output=True, text=True)
        if r.stdout and len(r.stdout) > 500:
            return r.stdout
        time.sleep(4)
    return ""

print("=== 1. core pages ===")
for p in ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]:
    c = code(BASE + p)
    ok = c == "200"
    print(("PASS " if ok else "FAIL ") + c + " " + p)
    if not ok: fails.append("core " + p + " " + c)

print("\n=== 2. today's 4 pages (six-item) ===")
pages = [
    "/mili/blog/20261023-mili-hotel-safety-obligation.html",
    "/aipunajie/blog/20261023-aipunajie-overseas-patent-fto.html",
    "/najie/blog/20261023-najie-trademark-law-70-days.html",
    "/mili/blog/20261022-judge-liability-verdict-reversed.html",
]
for p in pages:
    h = body(BASE + p)
    if not h:
        print("FAIL no-body " + p); fails.append("body " + p); continue
    h1 = len(re.findall(r"<h1[ >]", h))
    ld = h.count("application/ld+json")
    ogi = "og:image" in h
    twi = "twitter:image" in h
    # stars excluding patent-number masks
    s = re.sub(r"[0-9]\*{2,}[0-9.]*", "", h)
    s = re.sub(r"[0-9*]\*{2,}", "", s)
    stars = s.count("**")
    baretab = len(re.findall(r"<p>\s*\|", h))
    m = re.search(r'<meta name="description" content="(.*?)"', h, re.S)
    desc = m.group(1) if m else ""
    h1t = re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    ti = re.sub(r"<[^>]+>", "", h1t[0]).strip() if h1t else ""
    repeat = bool(ti) and desc.strip()[:35] == ti.strip()[:35]
    flags = []
    if h1 != 1: flags.append("h1=%d" % h1)
    if ld < 2: flags.append("ld=%d" % ld)
    if not ogi: flags.append("no-og-img")
    if not twi: flags.append("no-tw-img")
    if stars: flags.append("stars=%d" % stars)
    if baretab: flags.append("baretab=%d" % baretab)
    if repeat: flags.append("desc-repeat")
    print(("PASS " if not flags else "FAIL ") + p + " " + (",".join(flags) if flags else "OK") + f" [{len(h)}B]")
    if flags: fails.append(p + ":" + ",".join(flags))

print("\n=== 3. cover image ===")
for p in ["/img/20261023-mili-hotel-safety-obligation.png"]:
    c = code(BASE + p)
    print(("PASS " if c == "200" else "FAIL ") + c + " " + p)
    if c != "200": fails.append("img " + p + " " + c)

print("\n=== 4. live articles.json ===")
r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "30",
                    BASE + "/articles.json?cb=%d" % int(time.time())],
                   capture_output=True, text=True)
try:
    d = json.loads(r.stdout)
    print(("PASS " if len(d) == 200 else "FAIL ") + "entries=%d (expect 200)" % len(d))
    if len(d) != 200: fails.append("live articles.json %d" % len(d))
    print("  top1:", d[0]["url"])
except Exception as e:
    print("FAIL parse", e); fails.append("live articles.json parse")

print("\n=== 5. live index cards ===")
for p, slug in [("/blog/", "20261023-mili-hotel-safety-obligation"),
                ("/mili/blog/", "20261023-mili-hotel-safety-obligation"),
                ("/najie/blog/", "20261023-najie-trademark-law-70-days"),
                ("/aipunajie/blog/", "20261023-aipunajie-overseas-patent-fto")]:
    h = body(BASE + p)
    ok = slug in h
    print(("PASS " if ok else "FAIL ") + p + " " + slug)
    if not ok: fails.append("index " + p + " " + slug)

print("\nFAILURES =", len(fails))
for f in fails: print("  -", f)
