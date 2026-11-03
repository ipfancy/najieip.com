import re, os
REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles/20261103-mili-unfair-competition-data-scraping.md")
t = open(os.path.join(REPO,"mili/blog/20261103-mili-unfair-competition-data-scraping.html"), encoding="utf-8").read()
body = t[t.find("<body"):]
# printed structure of page
print("HEAD sample:", t[:400].replace("\n"," ")[:300])
print("STYLE inline:", "<style>" in t, "| ext css:", "/style.css" in t, "| nav:", "<nav" in t, "| footer:", "<footer" in t)
h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)
h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", t, re.S)
print("H1:", h1)
print("H2:", h2)
ps = re.findall(r"<p[^>]*>(.*?)</p>", body, re.S)
print("P count:", len(ps))
for i,p in enumerate(ps): print(f"  [{i}] {re.sub('<[^>]+>','',p)[:120]}")
md = open(MD, encoding="utf-8").read()
print("=== MD ===")
print(md[:1200])
print("... md_len:", len(md))
