import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
SLUG = "20261023-mili-hotel-safety-obligation"
PAGE = f"mili/blog/{SLUG}.html"
OG = f"https://najieip.com/img/{SLUG}.png"

t = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'(<script type="application/ld\+json">)(.*?)(</script>)', t, re.S)
print("blocks:", len(blocks))
changed = False
for open_tag, body, close_tag in blocks:
    o = json.loads(body)
    if o.get("@type") == "Article" and not o.get("image"):
        o["image"] = OG
        new_body = json.dumps(o, ensure_ascii=False, indent=2)
        t = t.replace(open_tag + body + close_tag, open_tag + new_body + close_tag, 1)
        changed = True
        print("image added to Article JSON-LD")
if not changed:
    print("no change needed")

if changed:
    open(PAGE, "w", encoding="utf-8").write(t)

t2 = open(PAGE, encoding="utf-8").read()
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    o = json.loads(blk)
    print("PARSE-OK", o.get("@type"), "image=", (o.get("image") or "")[-40:] if o.get("image") else None)
print("h1:", len(re.findall(r"<h1[ >]", t2)), "ld:", t2.count("application/ld+json"),
      "og:image:", "og:image" in t2, "size:", len(t2))
