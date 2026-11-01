import subprocess, time, re, json

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url, head=False):
    cmd = ["curl", "-s", "-A", UA, "--max-time", "25"]
    if head:
        cmd += ["-I", "-o", "/dev/null", "-w", "%{http_code}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout

def code(url):
    for _ in range(3):
        c = get(url, head=True).strip()
        if c == "200":
            return c
        time.sleep(3)
    return c

urls = [
    "https://najieip.com/najie/blog/20261101-najie-ip-foreign-transfer-review.html",
    "https://najieip.com/img/20261101-najie-ip-foreign-transfer-review.png",
    "https://najieip.com/blog/",
    "https://najieip.com/najie/blog/",
    "https://najieip.com/articles.json",
    "https://najieip.com/sitemap.xml",
]
for u in urls:
    print(code(u), u)

# wait for pages build then read page body
slug = "20261101-najie-ip-foreign-transfer-review"
body = ""
for i in range(6):
    body = get(f"https://najieip.com/najie/blog/{slug}.html?cb={int(time.time())}")
    if len(body.encode()) > 9000 and 'og:image' in body:
        break
    time.sleep(30)
print("page bytes:", len(body.encode()))
print("h1:", body.count("<h1"), "ld:", len(re.findall(r'application/ld\+json', body)),
      "og:image:", 'property="og:image"' in body, "stars:", body.count("**"),
      "cdn_beacon:", "beacon.min.js" in body)
m = re.search(r'<meta name="description" content="([^"]*)"', body)
print("desclen:", len(m.group(1)) if m else None)
print("canonical ok:", f'rel="canonical" href="https://najieip.com/najie/blog/{slug}.html"' in body)

# indexes live
for f in ["blog", "najie/blog"]:
    t = get(f"https://najieip.com/{f}/?cb={int(time.time())}")
    print(f, "card_hits:", t.count(slug))

aj = get(f"https://najieip.com/articles.json?cb={int(time.time())}")
try:
    d = json.loads(aj)
    items = d if isinstance(d, list) else d.get("articles", [])
    print("live articles.json count:", len(items))
except Exception as e:
    print("articles.json parse fail:", e, len(aj))
