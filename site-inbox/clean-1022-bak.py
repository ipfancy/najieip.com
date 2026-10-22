#!/usr/bin/env python3
import os
REPO = "/Users/ziganghe/wiki/najieip-verify"
removed = []
for root, dirs, files in os.walk(REPO):
    if ".git" in root:
        continue
    for f in files:
        if ".bak-1022" in f:
            p = os.path.join(root, f)
            os.remove(p)
            removed.append(os.path.relpath(p, REPO))
print("removed:", removed)
