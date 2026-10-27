#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Six-point defect scan for pages touched in the last 3 days."""
import re, os

BASE = os.path.expanduser("~/wiki/najieip-verify")
PAGES = [
    "mili/blog/20261026-mili-divorce-inheritance-property.html",
    "mili/blog/20261026-trade-secret-secret-point-fixation.html",
    "najie/blog/20261026-najie-double11-ip-risk.html",
    "aipunajie/blog/20261026-aipunajie-patent-before-launch.html",
    "aipunajie/blog/20261027-aipunajie-oa-phone-amendment-decision.html",
    "mili/blog/20261025-mili-ai-label-service.html",
    "mili/blog/20261025-defendant-info-query-beijing.html",
    "najie/blog/20261025-najie-license-filing.html",
]

for p in PAGES:
    f = os.path.join(BASE, p)
    if not os.path.exists(f):
        print("MISSING", p)
        continue
    t = open(f, encoding="utf-8").read()
    d = re.search(r'<meta name="description" content="([^"]*)"', t)
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    dup = bool(d and ti and d.group(1).strip() == ti.group(1).split(" — ")[0].strip())
    stars = len(re.findall(r"(?<![0-9*])\*\*", t))
    flags = []
    if len(re.findall("<h1", t)) != 1:
        flags.append("H1")
    if len(re.findall(r"application/ld\+json", t)) < 2:
        flags.append("LD")
    if "og:image" not in t:
        flags.append("OGIMG")
    if dup:
        flags.append("DUPDESC")
    if stars:
        flags.append("STARS%d" % stars)
    if re.search(r"<p>\|", t):
        flags.append("BARETBL")
    print("%-58s %s" % (os.path.basename(p)[:58], "OK" if not flags else "DEFECT:" + ",".join(flags)))
