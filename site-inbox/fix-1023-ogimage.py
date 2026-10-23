import os, re, shutil, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
SLUG = "20261023-mili-hotel-safety-obligation"
PAGE = f"mili/blog/{SLUG}.html"
SRC_COVER = os.path.expanduser(f"~/wiki/digital-employees/articles/cover-{SLUG}.png")
DST_COVER = f"img/{SLUG}.png"
OG = f"https://najieip.com/img/{SLUG}.png"

# 1. cover into repo
if not os.path.exists(DST_COVER):
    shutil.copy2(SRC_COVER, DST_COVER)
    print("cover copied:", DST_COVER, os.path.getsize(DST_COVER), "B")
else:
    print("cover exists:", DST_COVER)

t = open(PAGE, encoding="utf-8").read()
orig = t

# 2. insert og:image + twitter:image right after og:site_name / twitter:card anchors
if "og:image" not in t:
    m = re.search(r'([ \t]*)<meta property="og:url"[^>]*>\n', t)
    assert m, "og:url anchor not found"
    t = t[:m.end()] + f'{m.group(1)}<meta property="og:image" content="{OG}">\n' + t[m.end():]
    print("og:image inserted after og:url")
if "twitter:image" not in t:
    m = re.search(r'([ \t]*)<meta name="twitter:card"[^>]*>\n', t)
    assert m, "twitter:card anchor not found"
    t = t[:m.end()] + f'{m.group(1)}<meta name="twitter:image" content="{OG}">\n' + t[m.end():]
    print("twitter:image inserted after twitter:card")

open(PAGE, "w", encoding="utf-8").write(t)

# 3. verifications
t2 = open(PAGE, encoding="utf-8").read()
h = t2[:t2.find("</head>")]
checks = {
    "h1==1": len(re.findall(r"<h1[ >]", t2)) == 1,
    "ld==2": t2.count("application/ld+json") == 2,
    "og:image": "og:image" in h,
    "twitter:image": "twitter:image" in h,
    "og:url": "og:url" in h,
    "canonical": "canonical" in h,
}
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
# JSON-LD parse
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    json.loads(blk)
print("ld+json all parse OK")
# body unchanged beyond head insertion: strip the two new meta lines and compare
back = t2.replace(f'<meta property="og:image" content="{OG}">\n', "", 1)
back = back.replace(f'<meta name="twitter:image" content="{OG}">\n', "", 1)
# indentation of removed lines
print("body/rest unchanged (ignoring indent of removed lines):",
      re.sub(r"\s+", "", back) == re.sub(r"\s+", "", orig))
print("size:", len(orig), "->", len(t2))
