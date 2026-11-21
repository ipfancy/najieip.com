import re, json, os, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
f = os.path.join(REPO, "mili/blog/20261121-mili-divorce-game-account-88w.html")
t = open(f, encoding="utf-8").read()
print("SIZE", os.path.getsize(f))
print("TITLE", re.search(r"<title>(.*?)</title>", t, re.S).group(1))
m = re.search(r'<meta name="description" content="([^"]*)"', t)
print("DESC", repr(m.group(1) if m else None))
print("OG", re.findall(r'<meta property="(og:[a-z:_]+)" content="([^"]{0,70})', t))
print("TW", re.findall(r'<meta name="(twitter:[a-z:]+)" content="([^"]{0,50})', t))
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    o = json.loads(b)
    print("LD", o.get("@type"), "ctx=", o.get("@context"), "keys=", list(o.keys())[:12])
body = t[t.find("<article"):]
print("--- paras ---")
for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)[:10]:
    print(" -", re.sub(r"<[^>]+>", "", p).strip()[:110])
print("H2s", [re.sub(r"<[^>]+>", "", h)[:30] for h in re.findall(r"<h2[^>]*>(.*?)</h2>", t, re.S)])
print("COVERS", [os.path.basename(x) for x in glob.glob(os.path.expanduser("~/wiki/digital-employees/articles/cover-*")) if "1121" in x][:8])
print("IMG IN REPO", [os.path.basename(x) for x in glob.glob(os.path.join(REPO, "img/*")) if "20261121" in x])
