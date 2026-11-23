#!/usr/bin/env python3
"""11-23 evening: fix residual frontmatter leak on gaoqi page + corrected md containment check."""
import re, os, glob, json, unicodedata, sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"
GAOQI = os.path.join(REPO, "najie/blog/20261123-mili-gaoqi-2026-no-new-standard.html")

BYLINES = ["北京纳杰知识产权代理有限公司何自刚", "何自刚", "何自刚知识产权律师爱普纳杰·觅理·纳杰",
           "何自刚｜知识产权律师｜纳杰觅理", "纳杰觅理", "爱普纳杰·觅理·纳杰"]

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r'[\s“”"\'’‘「」『』【】\[\]>:：\-—…、,，.。!！?？*|]', '', s)

def strip_fm(md):
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith("<!--") or s == "---" or re.match(
                r'^(title|date|slug|brand|style|voice|end|ai_smell|tags|author|category|cover|desc|description)\s*[:：]', s):
            i += 1
            continue
        break
    return "\n".join(lines[i:])

def mdn_of(path):
    md = strip_fm(open(path, encoding="utf-8").read())
    keep = []
    for ln in md.split("\n"):
        s = ln.strip()
        if not s or s.startswith("<!--") or s.startswith("#"):
            continue
        if re.match(r'^\*\*[^*\n]{1,32}\*\*$', s) or re.match(r'^[一二三四五六七八九十]、', s):
            continue
        if s.startswith("|"):
            if re.match(r'^\|[\s:|-]+\|$', s):
                continue
            s = re.sub(r'[|\-:]', '', s)
        s = re.sub(r'^\d+\.\s*', '', s)
        if "lt;!--" in s:
            continue
        keep.append(s)
    out = norm("".join(keep))
    for b in BYLINES:
        out = out.replace(norm(b), "")
    return out

def pg_of(hp):
    t = open(hp, encoding="utf-8").read()
    m = re.search(r'<article.*?</article>', t, re.S)
    seg = m.group(0) if m else t[t.find("<body"):]
    seg = re.sub(r'<script.*?</script>', ' ', seg, flags=re.S)
    seg = re.sub(r'<h[1-6].*?</h[1-6]>', ' ', seg, flags=re.S)
    pg = norm(re.sub(r'<[^>]+>', '\n', seg))
    for b in BYLINES:
        pg = pg.replace(norm(b), "")
    return pg

# ---- STEP 1: fix residual frontmatter leak on gaoqi page ----
t = open(GAOQI, encoding="utf-8").read()
leaks = re.findall(r'<p>\s*(?:slug|title|date|brand|style|voice|end|ai_smell|tags|author)\s*[:：][^<]*</p>', t)
print("LEAKS_BEFORE", leaks)
# remove the leaked frontmatter cluster: <p>---</p> <p>brand: mili</p> <p>---</p> <br>
pat = re.compile(r'(?:\s*<p>\s*---\s*</p>)?(?:\s*<p>\s*(?:slug|title|date|brand|style|voice|end|ai_smell|tags|author)\s*[:：][^<]*</p>\s*)+'
                 r'(?:\s*<p>\s*---\s*</p>)?(?:\s*<br>)?')
t2, n = pat.subn('', t, count=1)
print("REMOVED_BLOCKS", n, "delta", len(t) - len(t2))
leaks2 = re.findall(r'<p>\s*(?:slug|title|date|brand|style|voice|end|ai_smell|tags|author)\s*[:：][^<]*</p>', t2)
print("LEAKS_AFTER", leaks2)
if n == 1 and not leaks2:
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        open(GAOQI, "w", encoding="utf-8").write(t2)
        print("APPLIED", os.path.getsize(GAOQI))
    else:
        print("DRYRUN ok")
else:
    print("ABORT: pattern did not match cleanly")

# verify h1/ld intact after edit
chk = open(GAOQI, encoding="utf-8").read()
print("H1", len(re.findall(r'<h1', chk)), "LD", len(re.findall(r'application/ld\+json', chk)),
      "OGIMG", 'property="og:image"' in chk, "H2", len(re.findall(r'<h2', chk)))

# ---- STEP 2: containment check all three ----
print("--- containment ---")
for slug, brand in [("20261123-mili-gaoqi-2026-no-new-standard", "najie"),
                    ("mili-food-oem-trademark-113-order-20261122", "najie"),
                    ("20261121-mili-divorce-game-account-88w", "mili")]:
    mds = glob.glob(os.path.join(ART, slug + ".md"))
    if not mds:
        print(slug, "MD_NOT_FOUND"); continue
    md = mdn_of(mds[0]); pg = pg_of(os.path.join(REPO, brand, "blog", slug + ".html"))
    r = {"slug": slug, "md_len": len(md), "pg_len": len(pg), "contained": md in pg}
    if not r["contained"]:
        i = 0
        while i < min(len(md), len(pg)) and md[i] == pg[i]:
            i += 1
        r["diff_at"] = i; r["md_ctx"] = md[max(0, i-25):i+45]; r["pg_ctx"] = pg[max(0, i-25):i+45]
    print(json.dumps(r, ensure_ascii=False))
