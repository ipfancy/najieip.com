#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re
REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
BAD = "20261119-mili-tv-box-backdoor-four-layers"
md = open(os.path.join(ART, BAD + ".md"), encoding="utf-8").read()
if md.startswith("---"):
    e = md.find("\n---", 3)
    if e != -1: md = md[e+4:]
md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
md = re.sub(r"(?m)^\s*#.*$", "", md)
md = re.sub(r"(?m)^\s*\*\*([^*\n]{1,30})\*\*\s*$", "", md)
md = re.sub(r"(?m)^\s*[一二三四五六七八九十]、.*$", "", md)
mn = re.sub(r"[\s*\"\u201c\u201d'`|:\-]+", "", md)

t = open(os.path.join(REPO, "mili/blog", BAD + ".html"), encoding="utf-8").read()
art = re.search(r"<article>.*?</article>", t, re.S).group(0)
pn = re.sub(r"<[^>]+>", "", art)
pn = re.sub(r"[\s*\"\u201c\u201d'`|:\-]+", "", pn)
# 最长公共前缀
i = 0
while i < min(len(mn), len(pn)) and mn[i] == pn[i]: i += 1
print("common prefix len:", i)
print("MD  around:", repr(mn[max(0,i-60):i+80]))
print("PG  around:", repr(pn[max(0,i-60):i+80]))
print("MD tail:", repr(mn[-160:]))
print("PG tail:", repr(pn[-160:]))
# 关键：md 各段落是否都能在页面找到
paras = [re.sub(r"[\s*\"\u201c\u201d'`|:\-]+", "", p) for p in re.split(r"\n\s*\n", md)]
missing = [p[:50] for p in paras if len(p) > 25 and p not in pn]
print("missing paras:", len(missing))
for m in missing[:6]: print("   MISSING:", m)
