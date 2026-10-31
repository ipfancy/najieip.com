#!/usr/bin/env python3
import os, re, glob
ART = os.path.expanduser("~/wiki/digital-employees/articles")
REPO = os.path.expanduser("~/wiki/najieip-verify")
slug = "20261031-mili-ai-product-image-review-tool-neutrality"
md = open(os.path.join(ART, slug + ".md"), encoding="utf-8").read()
print("MD chars:", len(md))
print("MD head:\n", md[:600])
print("...\nMD tail:\n", md[-700:])
c = os.path.join(ART, slug + "_cms.html")
if os.path.exists(c):
    ct = open(c, encoding="utf-8").read()
    print("\nCMS size:", len(ct), "h2:", len(re.findall(r"<h2[ >]", ct)), "p:", len(re.findall(r"<p[ >]", ct)), "ld:", ct.count("application/ld+json"), "ogimage:", "og:image" in ct)
print("\nIMG dir matches:")
for p in glob.glob(os.path.join(REPO, "img/*")) + glob.glob(os.path.join(REPO, "img/*/*")):
    if "product-image" in p or "tool-neutrality" in p or "specialized-sme" in p:
        print(" ", os.path.relpath(p, REPO), os.path.getsize(p))
print("\ncover:", [os.path.basename(p) + " " + str(os.path.getsize(p)) for p in glob.glob(os.path.join(ART, "cover-" + slug + "*"))])
