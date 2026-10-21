#!/usr/bin/env python3
import os, subprocess, glob, sys

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
removed = []
for p in glob.glob("**/*.bak-1021eve", recursive=True):
    os.remove(p); removed.append(p)
print("removed bak:", removed)

print(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout)
if "--commit" in sys.argv:
    for cmd in (["git", "add", "-A"],
                ["git", "commit", "-m",
                 "siteops(1021晚): 主索引补3卡(judge/3gpp/goods) 220->223 + judge页补og:image/twitter:image + articles.json 195->196"],
                ["git", "push", "origin", "main"]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        print("$", " ".join(cmd[:2]), "->", r.returncode, (r.stdout or r.stderr)[-400:])
