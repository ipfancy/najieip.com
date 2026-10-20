import os, re
SITE = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
slug = "20261019-mili-community-correction-medical-standard"
t = open(os.path.join(SITE, "mili/blog", slug + ".html"), encoding="utf-8").read()
md = open(os.path.join(ART, slug + ".md"), encoding="utf-8").read()
md = md.split("---", 2)[2] if md.startswith("---") else md
b = t[t.find("<body"):]
b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
b = re.sub(r"<[^>]+>", " ", b)
b = b.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"')
norm = re.sub(r"\s+", "", b)
paras = [x.strip() for x in re.split(r"\n\s*\n", md) if x.strip()]
for x in paras[:12]:
    probe = re.sub(r"\s+", "", re.sub(r"[*#>\-]", " ", x))[:14]
    ok = probe and probe in norm
    if not ok:
        print("MISS:", repr(x[:80]))
        print("  probe:", repr(probe))
print("html h2 count", t.count("<h2"))
