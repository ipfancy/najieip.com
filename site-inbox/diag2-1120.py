import os, re, glob, difflib

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
BYLINES = ["何自刚|知识产权律师|爱普纳杰", "北京纳杰知识产权代理有限公司何自刚", "北京觅理律师事务所", "何自刚|知识产权律师|纳杰觅理"]

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<h[1-6].*?</h[1-6]>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"')
    for ch in '“”"\'’·|*#>:-—「」『』【】':
        s = s.replace(ch, "")
    return re.sub(r"\s+", "", s)

for slug in ["20261120-mili-device-procurement-firmware-checklist", "20261119-mili-tv-box-backdoor-four-layers"]:
    t = open(os.path.join(REPO, "mili/blog", slug + ".html"), encoding="utf-8").read()
    md = open(os.path.join(ART, slug + ".md"), encoding="utf-8").read()
    md = re.sub(r"^---.*?---\s*", "", md, flags=re.S)
    lines = []
    for ln in md.split("\n"):
        s = ln.strip()
        if not s: continue
        if s.startswith("#") or s.startswith("<!--"): continue
        if re.match(r"^\*\*[^*]{1,30}\*\*$", s) and len(s) <= 34 and not s.rstrip("*").endswith(("。", "！", "？")): continue
        if re.match(r"^[一二三四五六七八九十]、", s) and len(s) <= 30: continue
        lines.append(re.sub(r"^-{3,}$", "", s))
    mdt = textify("\n".join(lines))
    for b in BYLINES: mdt = mdt.replace(textify(b), "")
    mdt = re.sub(r"\d+\.", "", mdt)
    art = re.search(r"<article.*?</article>", t, re.S)
    pgt = textify(art.group(0) if art else t[t.find("<body"):])
    for b in BYLINES: pgt = pgt.replace(textify(b), "")
    sm = difflib.SequenceMatcher(None, mdt, pgt, autojunk=False)
    print("###", slug, "md", len(mdt), "pg", len(pgt))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(f"  {tag}: md[{i1}:{i2}]={mdt[i1:i2][:90]!r} | pg[{j1}:{j2}]={pgt[j1:j2][:90]!r}")
    # cover candidates
    cands = glob.glob(os.path.join(ART, f"cover-*{slug[9:]}*")) + glob.glob(os.path.join(ART, f"cover-{slug}*"))
    print("  covers:", [os.path.basename(c) for c in set(cands)], "| repo img:", os.path.exists(os.path.join(REPO, "img", slug + ".png")))
    print("  ogimage line:", (re.search(r'<meta property="og:image"[^>]*>', t) or ["NONE"])[0] if re.search(r'<meta property="og:image"[^>]*>', t) else "NONE")
