#!/usr/bin/env python3
"""Print remaining ** contexts after the narrow pass (pre-fix inspection)."""
import re, os

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
for p in ("mili/blog/geely-wm-trade-secret-20260814.html",
          "najie/blog/20260901-copyright-jp18-compliance-checklist.html"):
    t = open(p, encoding="utf-8", errors="replace").read()
    t2 = re.sub(r"\*\*([^*\n]{1,60})\*\*", r"<strong>\1</strong>", t)
    print("===", p, "orig stars:", t.count("**"), "after narrow:", t2.count("**"))
    for m in re.finditer(r"\*\*", t2):
        s, e = max(0, m.start() - 90), min(len(t2), m.end() + 90)
        print("   ...", re.sub(r"\s+", " ", t2[s:e]))
    # raw table rows context
    print("   raw table rows:", len(re.findall(r"<p>\|.*\|</p>", t2)))
