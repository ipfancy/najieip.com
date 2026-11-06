#!/usr/bin/env python3
# remove site-inbox upstream publish copies that are superseded (pages rebuilt from md)
import os
REPO = os.path.expanduser("~/wiki/najieip-verify")
for f in ["20261103-mili-guarantee-period-six-months.html",
          "20261104-mili-inventor-reward-5-percent.html",
          "20261106-mili-nda-vs-noncompete.html"]:
    p = os.path.join(REPO, "site-inbox", f)
    if os.path.exists(p):
        same = open(p, "rb").read() == open(os.path.join(REPO, "mili", "blog", f), "rb").read()
        os.remove(p)
        print("removed site-inbox copy", f, "| identical_to_published=", same)
