#!/usr/bin/env python3
# site-inbox/fix3-1123-gaoqi.py — 清除页面中泄漏的 frontmatter 段 + 重写摘要
import os, re, json, sys
REPO = os.path.expanduser("~/wiki/najieip-verify"); os.chdir(REPO)
APPLY = "--apply" in sys.argv
SLUG = "20261123-mili-gaoqi-2026-no-new-standard"
PAGE = f"najie/blog/{SLUG}.html"
t = open(PAGE, encoding="utf-8").read()

FM = re.compile(r'<p>\s*(?:&lt;!--[^<]*?--&gt;|(?:slug|title|style|voice|end|date|tags|author|category|summary)\s*[:：][^<]*)\s*</p>\s*(?:<br>\s*)?', re.S | re.I)
leaks = FM.findall(t)
t2 = FM.sub("", t)
print("frontmatter leaks removed:", len(leaks))
for l in leaks[:6]: print("   ", re.sub(r"<[^>]+>", "", l)[:70])

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"')
    return re.sub(r"\s+", " ", s).strip()

art = re.search(r"<article.*?</article>", t2[t2.find("<body"):], re.S).group(0)
paras = [p for p in (textify(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", art, re.S))
         if len(p) > 45 and "lt;!--" not in p]
print("body paras:", len(paras)); print("   p1:", paras[0][:60])
DESC = paras[1][:160] if len(paras) > 1 else paras[0][:160]
DESC = re.sub(r"[，、]$", "。", DESC)
if not DESC.endswith(("。", "！", "？")): DESC = DESC[:155] + "。"
print("NEW DESC:", DESC)

t3 = t2
t3 = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', t3, count=1)
t3 = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', t3, count=1)
t3 = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{DESC}">', t3, count=1)
# JSON-LD description 覆写
def fixld(m):
    o = json.loads(m.group(1))
    if o.get("@type") == "Article": o["description"] = DESC
    return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>"
t3 = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fixld, t3, flags=re.S)

assert t3.count("application/ld+json") == 2
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t3, re.S): json.loads(m)
assert len(re.findall(r"<h1[\s>]", t3)) == 1
assert t3.count("**") == 0
assert "lt;!--" not in t3[t3.find("<body"):], "leak remains"
print("OK size", len(t3.encode()), "desc_len", len(DESC))
if APPLY:
    open(PAGE, "w", encoding="utf-8").write(t3); print("APPLIED")
else: print("DRY-RUN")
