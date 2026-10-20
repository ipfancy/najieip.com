import os, re, json
SITE = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
NEW = ["20261020-mili-overtime-leave-evidence", "20261019-mili-community-correction-medical-standard"]
fails = []

def textify(s):
    b = s[s.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    b = b.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&#x27;", "'").replace("&quot;", '"')
    return re.sub(r"\s+", " ", b).strip()

for slug in NEW:
    p = os.path.join(SITE, "mili/blog", slug + ".html")
    t = open(p, encoding="utf-8").read()
    md = open(os.path.join(ART, slug + ".md"), encoding="utf-8").read()
    if md.startswith("---"):
        md = md.split("---", 2)[2]
    mdp = [re.sub(r"\s+", " ", re.sub(r"[*#>\-]", " ", x)).strip() for x in re.split(r"\n\s*\n", md) if x.strip()]
    mdp = [x for x in mdp if x and not x.startswith("<!--") and "合集" not in x[:6]]
    pt = textify(t)
    # check key probes: first 6 md paragraphs' first 12 chars appear in page text
    miss = 0
    for x in mdp[:12]:
        probe = re.sub(r"\s+", "", x)[:12]
        if probe and re.sub(r"\s+", "", pt).find(probe) < 0:
            miss += 1
    h1, h2 = t.count("<h1"), t.count("<h2")
    ld = t.count("application/ld+json")
    img = re.search(r'og:image" content="([^"]+)"', t)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
    # div balance
    opens = len(re.findall(r"<div\b", t)); closes = t.count("</div>")
    print(f"{slug}: bytes={os.path.getsize(p)} h1={h1} h2={h2} ld={ld} divs={opens}/{closes} **={t.count('**')} "
          f"schema={t.count('https://schema.org')} img={bool(img)} desc_len={len(desc.group(1)) if desc else 0} "
          f"para_miss={miss} title_ok={'纳杰觅理' in title}")
    if h1 != 1 or ld < 2 or not img or opens != closes or t.count("**") or t.count("https://***"):
        fails.append(slug + ":page")
    if os.path.getsize(p) < 3000:
        fails.append(slug + ":size")
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
        json.loads(b)
    cov = os.path.join(SITE, "img", slug + ".png")
    print("   cover:", os.path.exists(cov), os.path.getsize(cov) if os.path.exists(cov) else 0)

# index structure
for idx in ["mili/blog/index.html", "blog/index.html"]:
    p = os.path.join(SITE, idx)
    t = open(p, encoding="utf-8").read()
    cards = t.count('<div class="article-card">')
    opens, closes = len(re.findall(r"<div\b", t)), t.count("</div>")
    hits = {s: t.count(s) for s in NEW}
    print(f"{idx}: cards={cards} divs={opens}/{closes} hits={hits} **={t.count('**')}")
    if opens != closes:
        fails.append(idx + ":divbalance")
    for s in NEW:
        if hits[s] < 1:
            fails.append(idx + ":missing " + s)

# order check: new cards date ordering in first 6 cards
t = open(os.path.join(SITE, "blog/index.html"), encoding="utf-8").read()
seq = [m.group(1) for m in re.finditer(r'<div class="meta">.*?(\d{4}-\d{2}-\d{2})', t)][:6]
print("main top6 dates:", seq)
print("FAILS:", fails if fails else "NONE")
