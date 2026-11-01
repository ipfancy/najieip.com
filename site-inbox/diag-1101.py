import os, re, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
slugs = [
    ("najie", "20261101-najie-ip-foreign-transfer-review"),
    ("mili", "20261031-mili-ai-product-image-review-tool-neutrality"),
    ("mili", "20261031-mili-mofcom-trade-secret-sanctions"),
    ("najie", "20261031-najie-specialized-sme-patent-screen"),
]

def read(p):
    return open(os.path.join(REPO, p), encoding="utf-8").read()

main = read("blog/index.html")
idxs = {b: read(f"{b}/blog/index.html") for b in ("mili", "najie", "aipunajie")}

for brand, slug in slugs:
    path = f"{brand}/blog/{slug}.html"
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        print(f"== {path}: MISSING FILE")
        continue
    t = read(path)
    h1 = t.count("<h1")
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = 'og:image' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    h1t = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    h1txt = re.sub(r"<[^>]+>", "", h1t.group(1)) if h1t else ""
    # stars, excluding masked patent numbers
    t2 = re.sub(r'[0-9]\*{2,}[0-9.]*', '', t)
    stars = t2.count("**")
    baretable = len(re.findall(r'<p>\s*\|', t))
    # body completeness vs md
    mdp = os.path.expanduser(f"~/wiki/digital-employees/articles/{slug}.md")
    mdtxt = ""
    if os.path.exists(mdp):
        raw = open(mdp, encoding="utf-8").read()
        raw = re.sub(r"^---.*?---", "", raw, flags=re.S)
        raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
        raw = raw.replace("*", "").replace("#", "").replace("|", "")
        mdtxt = re.sub(r"\s+", "", raw)
    body = t[t.find("<body"):]
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
    btxt = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", body))
    contains = mdtxt in btxt if mdtxt else None
    desc_repeat = (desc and h1txt and desc.strip()[:20] == h1txt.strip()[:20])
    print(f"== {path} size={len(t.encode())}")
    print(f"   h1={h1} ld={ld} og:image={ogimg} stars={stars} baretable={baretable} desclen={len(desc)} desc_repeat={desc_repeat} md_contained={contains}")
    print(f"   canonical={re.search(r'rel=.canonical. href=.([^\"]+)', t).group(1) if re.search(r'rel=.canonical. href=.([^\"]+)', t) else 'NONE'}")
    print(f"   brand_card={idxs[brand].count(slug)} main_card={main.count(slug)}")
    mdp_ok = os.path.exists(mdp)
    print(f"   md_exists={mdp_ok}")
