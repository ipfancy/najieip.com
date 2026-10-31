#!/usr/bin/env python3
# inspect bare page + house template + md source
import os, re, glob, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
BARE = os.path.join(REPO, "najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html")
HOUSE = os.path.join(REPO, "najie/blog/20261031-najie-specialized-sme-patent-screen.html")

t = open(BARE, encoding="utf-8").read()
print("=== BARE head (first 1600) ===")
print(t[:1600])
print("\n=== BARE stats ===")
print("len", len(t), "chars", "style:", "<style>" in t, "/style.css:", "style.css" in t,
      "h2:", len(re.findall(r"<h2[ >]", t)), "p:", len(re.findall(r"<p[ >]", t)))
m = re.findall(r'<link rel="canonical" href="([^"]+)"', t)
print("canonical:", m)
print("og:url:", re.findall(r'property="og:url" content="([^"]+)"', t))
print("\n=== BARE body text (first 1200 of article) ===")
b = t[t.find("<body"):]
b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
print(re.sub(r"<[^>]+>", "\n", b)[:2000])

print("\n=== HOUSE head (first 1500) ===")
h = open(HOUSE, encoding="utf-8").read()
print(h[:1500])
print("\nHOUSE ld blocks types:", re.findall(r'"@type":\s*"([A-Za-z]+)"', h)[:8])

print("\n=== MD sources ===")
for pat in ("*tool-neutrality*", "*product-image*", "*0117*"):
    print(pat, glob.glob(os.path.join(ART, pat)))
