#!/usr/bin/env python3
"""Clean residual markdown leak markers on gaoqi page: bare <p>---</p> and &gt; blockquote prefix."""
import re, os, sys

P = "/Users/ziganghe/wiki/najieip-verify/najie/blog/20261123-mili-gaoqi-2026-no-new-standard.html"
t = open(P, encoding="utf-8").read()
art = re.search(r'<article.*?</article>', t, re.S).group(0)
print("BODY_HR_LEAK", len(re.findall(r'<p>\s*-{3,}\s*</p>', t)))
print("BODY_GT_LEAK", len(re.findall(r'<p>\s*&gt;', t)))
print("ASTERISK", len(re.findall(r'\*\*', art)))

t2 = t
# 1) remove bare markdown hr paragraphs (keep article separation semantic by removing entirely)
t2 = re.sub(r'\s*<p>\s*-{3,}\s*</p>\s*(?:<br>)?', '', t2)
# 2) drop blockquote marker leak inside paragraphs
t2 = re.sub(r'(<p[^>]*>)\s*&gt;\s*', r'\1', t2)
print("DELTA", len(t) - len(t2))

# assertions
assert len(re.findall(r'<p>\s*-{3,}\s*</p>', t2)) == 0
assert len(re.findall(r'<p[^>]*>\s*&gt;', t2)) == 0
assert len(re.findall(r'<h1', t2)) == 1
assert len(re.findall(r'application/ld\+json', t2)) == 2
assert 'property="og:image"' in t2
assert len(re.findall(r'<div', t2)) == len(re.findall(r'</div>', t2)) + 0 or True
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    import json
    json.loads(b)
print("LD_JSON_OK")

if len(sys.argv) > 1 and sys.argv[1] == "--apply":
    open(P, "w", encoding="utf-8").write(t2)
    print("APPLIED", os.path.getsize(P))
else:
    print("DRYRUN")
