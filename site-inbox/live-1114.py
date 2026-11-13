import subprocess, os, re, json, time

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261113-byd-netherlands-evidence-seizure"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
fails = []

def fetch(url, out):
    for attempt in range(3):
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "60", "-A", UA, "-o", out,
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        code = (r.stdout or "").strip()
        if code == "200":
            return code
        time.sleep(5)
    return code

urls = {
 "en": f"https://najieip.com/en/blog/{SLUG}-en.html",
 "fr": f"https://najieip.com/fr/blog/{SLUG}-fr.html",
 "zh": f"https://najieip.com/mili/blog/{SLUG}.html",
 "enidx": "https://najieip.com/en/blog/",
 "fridx": "https://najieip.com/fr/blog/",
 "img": f"https://najieip.com/img/{SLUG}.png",
 "sitemap": "https://najieip.com/sitemap.xml",
}
for k, u in urls.items():
    p = f"/Users/ziganghe/.hermes/cache/scratch/live1114_{k}.out"
    code = fetch(u + ("&" if "?" in u else "?") + "cb=%d" % int(time.time()) if k != "img" and k != "sitemap" else u, p)
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"{k:8s} {code} {size}B")
    if code != "200" or size < 500:
        fails.append(f"{k} http={code} size={size}")

def txt(k):
    return open(f"/Users/ziganghe/.hermes/cache/scratch/live1114_{k}.out", encoding="utf-8", errors="ignore").read()

for lang in ("en", "fr"):
    t = txt(lang)
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    body = t[t.find("<body"):]
    cjk = len(re.findall(r"[\u4e00-\u9fff]", body))
    loc = t.count(f'/{lang}/blog/{SLUG}-{lang}.html')
    checks = dict(h1=t.count("<h1") == 1, ld=len(ld), ogimg=SLUG in t, hreflang=t.count("hreflang"),
                  cjk=cjk, stars=t.count("**"), h2=t.count("<h2"), slugrefs=loc)
    print(lang, checks)
    local = os.path.getsize(f"{REPO}/{lang}/blog/{SLUG}-{lang}.html")
    live = os.path.getsize(f"/Users/ziganghe/.hermes/cache/scratch/live1114_{lang}.out")
    print(f"  bytes local={local} live={live} delta={live-local}")
    if len(ld) != 2 or t.count("<h1") != 1 or cjk > 2 or t.count("**") != 0:
        fails.append(f"{lang} content")

en_idx = txt("enidx"); fr_idx = txt("fridx")
print("en idx cards", en_idx.count('class="article-card"'), "slug", en_idx.count(f"{SLUG}-en.html"))
print("fr idx cards", fr_idx.count('class="article-card"'), "slug", fr_idx.count(f"{SLUG}-fr.html"))
if en_idx.count(f"{SLUG}-en.html") < 1: fails.append("en idx missing card")
if fr_idx.count(f"{SLUG}-fr.html") < 1: fails.append("fr idx missing card")

sm = txt("sitemap")
print("sitemap locs", sm.count("<loc>"), "en", f"{SLUG}-en" in sm, "fr", f"{SLUG}-fr" in sm)
zt = txt("zh")
print("zh hreflang", zt.count("hreflang"), "h1", zt.count("<h1"))
if zt.count("hreflang") != 4: fails.append("zh hreflang")

print("FAILS:", fails if fails else "NONE")
