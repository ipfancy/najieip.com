import os, re, json, glob, sqlite3

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")

targets = []
for brand in ("mili", "najie", "aipunajie"):
    for f in glob.glob(os.path.join(REPO, brand, "blog", "2026111[89]*.html")) + glob.glob(os.path.join(REPO, brand, "blog", "20261120*.html")):
        targets.append((brand, f))
targets.sort(key=lambda x: os.path.basename(x[1]))

main_idx = open(os.path.join(REPO, "blog", "index.html"), encoding="utf-8").read()
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
aj_urls = [a.get("url", "") for a in (aj if isinstance(aj, list) else aj.get("articles", []))]
aj_top6 = aj_urls[:6]

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<h[1-6].*?</h[1-6]>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"')
    for ch in '“”"\'’·|*#>:-—「」『』【】':
        s = s.replace(ch, "")
    s = re.sub(r"\s+", "", s)
    return s

BYLINES = ["何自刚|知识产权律师|爱普纳杰", "北京纳杰知识产权代理有限公司何自刚", "北京觅理律师事务所", "何自刚|知识产权律师|纳杰觅理"]

print("=== TARGETS ===")
for brand, f in targets:
    t = open(f, encoding="utf-8").read()
    slug = os.path.basename(f)[:-5]
    h1 = len(re.findall(r"<h1", t))
    h2 = len(re.findall(r"<h2", t))
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ldok = 0
    ltypes = []
    for b in lds:
        try:
            o = json.loads(b)
            ldok += 1
            ltypes.append(o.get("@type"))
        except Exception:
            ltypes.append("BAD")
    ogimg = 'property="og:image"' in t
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    dv = desc.group(1).strip() if desc else ""
    tv = re.sub(r"\s*—.*$", "", title.group(1)).strip() if title else ""
    rep = (dv[:20] == tv[:20]) or len(dv) < 40
    stars = len(re.findall(r"(?<![0-9*])\*\*(?![0-9])", t))
    tblpi = len(re.findall(r"<p>\s*\|", t))
    # brand index
    bidx = open(os.path.join(REPO, brand, "blog", "index.html"), encoding="utf-8").read()
    bcards = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), bidx))
    mcards = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), main_idx))
    # md containment
    mdpath = os.path.join(ART, slug + ".md")
    mdres = "NO_MD"
    if os.path.exists(mdpath):
        md = open(mdpath, encoding="utf-8").read()
        md = re.sub(r"^---.*?---\s*", "", md, flags=re.S)
        lines = []
        for ln in md.split("\n"):
            s = ln.strip()
            if not s: continue
            if s.startswith("#") or s.startswith("<!--"): continue
            if re.match(r"^\*\*[^*]{1,30}\*\*$", s) and len(s) <= 34 and not s.rstrip("*").endswith(("。", "！", "？")): continue
            if re.match(r"^[一二三四五六七八九十]、", s) and len(s) <= 30: continue
            s = re.sub(r"^-{3,}$", "", s)
            lines.append(s)
        mdt = textify("\n".join(lines))
        for b in BYLINES: mdt = mdt.replace(textify(b), "")
        mdt = re.sub(r"\d+\.", "", mdt)
        art = re.search(r"<article.*?</article>", t, re.S)
        pg = art.group(0) if art else t[t.find("<body"):]
        pgt = textify(pg)
        for b in BYLINES: pgt = pgt.replace(textify(b), "")
        mdres = (mdt in pgt) if mdt else False
        mdlen = (len(mdt), len(pgt))
    else:
        mdlen = (0, 0)
    inaj = "yes" if any(slug in u for u in aj_urls) else "NO"
    toppos = next((i + 1 for i, u in enumerate(aj_top6) if slug in u), 0)
    size = os.path.getsize(f)
    print(f"{brand}/{slug}: size={size} h1={h1} h2={h2} ld={len(lds)}(ok={ldok},{ltypes}) ogimg={ogimg} desc={len(dv)} rep={rep} stars={stars} tbl={tblpi} brandcard={bcards} maincard={mcards} md_contained={mdres} mdlen={mdlen} aj={inaj} top6={toppos}")
