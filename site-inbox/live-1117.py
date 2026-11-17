import re, json, subprocess, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "20261117-mili-dove-ad-role"
URL = "https://najieip.com/mili/blog/%s.html" % SLUG
F = []

def get(url, tries=3, max_time="45"):
    last = ""
    for i in range(tries):
        p = subprocess.run(["curl", "-s", "-A", UA, "--max-time", max_time, url + ("?cb=%d" % int(time.time()) if "?" not in url else "")],
                           capture_output=True, text=True)
        last = p.stdout
        if len(last) > 500:
            return last
        time.sleep(4)
    return last

def code(url):
    for _ in range(3):
        p = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA, "--max-time", "30", url],
                           capture_output=True, text=True)
        if p.stdout.strip() == "200":
            return "200"
        time.sleep(3)
    return p.stdout.strip()

t = get(URL)
print("page_bytes", len(t.encode()))
def chk(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name, extra)
    if not cond:
        F.append(name)
chk("h1==1", t.count("<h1") == 1, t.count("<h1"))
chk("h2==3", t.count("<h2") == 3, t.count("<h2"))
chk("ld==2", t.count('application/ld+json') == 2, t.count('application/ld+json'))
chk("schema.org==2", t.count("https://schema.org") == 2)
chk("og:image", 'property="og:image"' in t)
chk("twitter_large", 'summary_large_image' in t)
m = re.search(r'<meta name="description" content="([^"]*)"', t)
chk("desc_real", bool(m) and len(m.group(1)) > 100, len(m.group(1)) if m else 0)
body = re.sub(r"<script.*?</script>", " ", t[t.find("<body"):], flags=re.S)
chk("stars0", re.sub(r"[0-9]\*{2,}[0-9.]*", "", re.sub(r"<[^>]+>", "", body)).count("**") == 0)
chk("canonical_mili", ('canonical" href="https://najieip.com/mili/blog/%s.html' % SLUG) in t)
chk("cover_200", code("https://najieip.com/img/%s.png" % SLUG) == "200")

# 索引卡
idx = get("https://najieip.com/mili/blog/")
print("mili_idx_bytes", len(idx.encode()), "cards", idx.count('<div class="article-card">'))
chk("mili_card_hit", ('./%s.html' % SLUG) in idx)
main = get("https://najieip.com/blog/")
print("main_bytes", len(main.encode()), "cards", main.count('<div class="article-card">'))
chk("main_card_hit", ('/mili/blog/%s.html' % SLUG) in main)
feed = get("https://najieip.com/feed.xml")
chk("feed_hit", SLUG in feed)
aj = json.loads(get("https://najieip.com/articles.json"))
chk("articles_json_len", len(aj) == 259, len(aj))
e0 = [x for x in aj if SLUG in x.get("url", "")][0]
chk("aj_desc_real", len(e0.get("description", "")) > 100, len(e0.get("description", "")))
print("FAILURES", F if F else "NONE")
