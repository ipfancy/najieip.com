#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live verification: main index cards, articles.json, page quality."""
import re, json

idx = open("/tmp/live_idx_1027.html", encoding="utf-8", errors="replace").read()
aj = json.load(open("/tmp/live_aj_1027.json", encoding="utf-8"))

NEW = ["/aipunajie/blog/20261027-aipunajie-oa-phone-amendment-decision.html",
       "/aipunajie/blog/20261026-aipunajie-patent-before-launch.html"]

fails = []
print("live index cards:", idx.count('class="article-card"'))
for h in NEW:
    ok = h in idx
    print(("HIT  " if ok else "MISS "), h)
    if not ok:
        fails.append(h)

print("live articles.json entries:", len(aj))
urls = [x.get("url") for x in aj[:3]]
print("top3:", urls)
if NEW[0] not in [x.get("url") for x in aj]:
    fails.append("articles.json: " + NEW[0])

# local vs live byte compare (expect small delta from CF beacon on index pages)
loc = open("/Users/ziganghe/wiki/najieip-verify/blog/index.html", encoding="utf-8").read()
print("local idx bytes %d | live %d | delta %d" % (len(loc.encode()), len(idx.encode()),
                                                   len(idx.encode()) - len(loc.encode())))
print("FAILS:", fails if fails else "NONE")
