import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

# 1) where are index cards pointing for the two 10-31/11-01 slugs
for slug in ["20261031-mili-ai-product-image-review-tool-neutrality",
             "20261101-najie-ip-foreign-transfer-review"]:
    print("=== slug:", slug)
    for f in ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html", "aipunajie/blog/index.html"]:
        t = open(f, encoding="utf-8").read()
        hrefs = sorted(set(re.findall(r'href="([^"]*' + re.escape(slug) + r'[^"]*)"', t)))
        print(f"  {f}: count={t.count(slug)} hrefs={hrefs}")

# 2) canonical of the mili-prefixed page living in najie
p = "najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html"
t = open(p, encoding="utf-8").read()
print("canonical:", re.search(r'rel="canonical" href="([^"]+)"', t).group(1))
print("og:url:", re.search(r'property="og:url" content="([^"]+)"', t).group(1) if 'og:url' in t else None)

# 3) md vs page for today's article
slug = "20261101-najie-ip-foreign-transfer-review"
md = open(os.path.expanduser(f"~/wiki/digital-employees/articles/{slug}.md"), encoding="utf-8").read()
md = re.sub(r"^---.*?---\s*", "", md, flags=re.S)
md = re.sub(r"<!--.*?-->", " ", md, flags=re.S)
mdp = [x.strip() for x in re.split(r"\n\s*\n", md) if x.strip()]
print("\n=== md paragraphs:", len(mdp))
for i, x in enumerate(mdp):
    print(i, x[:60].replace("\n", " "))
