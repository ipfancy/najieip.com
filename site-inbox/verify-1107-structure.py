#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, json, collections
R = os.path.expanduser("~/wiki/najieip-verify")
def rd(p): return open(p, encoding="utf-8").read()

def depth_hist(t):
    body = t[t.find("<body"):]
    depth = 0; hist = collections.Counter(); cards_depth = []
    for m in re.finditer(r"<(/?)div\b[^>]*>", body):
        if m.group(1) == "":
            if 'class="article-card"' in m.group(0): cards_depth.append(depth)
            depth += 1; hist[depth] += 1
        else:
            depth -= 1
            if depth < 0: return None, None, "stack-empty-close"
    return depth, hist, cards_depth

files = {"mili": "mili/blog/index.html", "najie": "najie/blog/index.html", "main": "blog/index.html"}
new_slugs = {
 "mili": ["20261107-mili-trademark-transition-rules-4-lines"],
 "najie": ["20261107-najie-patent-license-contract-6-clauses"],
 "main": ["20261107-mili-unjust-enrichment-default-judgment","20261107-najie-patent-license-contract-6-clauses","20261107-mili-trademark-transition-rules-4-lines"],
}
print("=== structure verify ===")
for k, f in files.items():
    t = rd(os.path.join(R, f))
    base = rd("/tmp/%s_idx.bak1107" % k)
    d, hist, cd = depth_hist(t)
    db, histb, cdb = depth_hist(base)
    if isinstance(d, str):
        print(k, "BAD", d); continue
    hrefs = collections.Counter(re.findall(r'<h[23][^>]*><a href="([^"]+)"', t))
    dups = {u: c for u, c in hrefs.items() if c > 1}
    print(f"{k}: depth_end={d} depth_end_base={db} cards={t.count('<div class=\"article-card\">')} cards_base={base.count('<div class=\"article-card\">')} "
          f"carddepth={collections.Counter(cd)} base={collections.Counter(cdb)} dups={len(dups)}")
    if dups: print("   DUPS", list(dups.items())[:5])
    for s in new_slugs[k]:
        print("   slug", s, "count_href", len(re.findall(r'<h[23][^>]*><a href="[^"]*'+re.escape(s), t)),
              "hrefs", re.findall(r'<h[23][^>]*><a href="([^"]*'+re.escape(s)+r')"', t))

print("\n=== page six-check (today's 3) ===")
pages = [
 "mili/blog/20261107-mili-unpaid-trial-shigang.html",
 "mili/blog/20261107-mili-trademark-transition-rules-4-lines.html",
 "najie/blog/20261107-najie-patent-license-contract-6-clauses.html",
 "mili/blog/20261107-mili-unjust-enrichment-default-judgment.html",
]
for p in pages:
    t = rd(os.path.join(R, p))
    h1 = len(re.findall(r"<h1[ >]", t)); ld = t.count("application/ld+json")
    oki = [] 
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: json.loads(m.group(1))
        except Exception as e: oki.append(str(e)[:40])
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
    ti2 = re.sub(r"\s*[—-]\s*纳杰觅理.*$", "", ti).strip()
    print(f"{p.split('/')[-1][:44]:46s} {len(t.encode()):6d}B h1={h1} ld={ld} ldparse={oki or 'ok'} ogimg={'og:image' in t} "
          f"desc{len(desc)} repeat={desc.strip()==ti2} **={t.count('**')} rawtab={len(re.findall(r'<p>\\s*\\|', t))}")

# md containment for unpaid page
import re as _re
M = os.path.expanduser("~/wiki/digital-employees/articles/20261107-mili-unpaid-trial-shigang.md")
md = rd(M)
md = md.split("---", 2)[2]
md = _re.sub(r"<!--.*?-->", " ", md, flags=_re.S)
md = _re.sub(r"^#+ .*$", " ", md, flags=_re.M)
def norm(s):
    s = _re.sub(r"[|*`\"“”‘’\s:\-–—]+", "", s)
    return s
t = rd(os.path.join(R, "mili/blog/20261107-mili-unpaid-trial-shigang.html"))
art = _re.search(r"<article.*?</article>", t, _re.S)
seg = art.group(0) if art else t[t.find("<body"):]
seg = _re.sub(r"<script.*?</script>", " ", seg, flags=_re.S)
seg = _re.sub(r"<h1>.*?</h1>", " ", seg, flags=_re.S)
seg = _re.sub(r"<figure.*?</figure>", " ", seg, flags=_re.S)
txt = _re.sub(r"<[^>]+>", " ", seg)
txt = txt.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", " ")
a, b = norm(md), norm(txt)
print("\nmd_contained:", a in b, "| md_len", len(a), "page_len", len(b))
if a not in b:
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            print("diff_at", i, repr(a[i-40:i+40]), "||", repr(b[i-40:i+40])); break
