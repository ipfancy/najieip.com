#!/usr/bin/env python3
"""Compare live najieip.com/blog/ against local repo versions."""
import subprocess, re, difflib, os, time

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))


def fetch(url, out):
    subprocess.run(["curl", "-s", "--max-time", "30", "-H", "Cache-Control: no-cache",
                    url, "-o", out], check=True)
    return open(out, encoding="utf-8", errors="replace").read()


live_blog = fetch(f"https://najieip.com/blog/?cb={int(time.time())}", "/tmp/live0916-blog.html")
live_home = fetch(f"https://najieip.com/?cb={int(time.time())}", "/tmp/live0916-home.html")
before = open("/tmp/blog-index-0916-before.html", encoding="utf-8").read()
local_home = open("index.html", encoding="utf-8").read()

for name, a, b in [("blog/", before, live_blog), ("home", local_home, live_home)]:
    print("=" * 60)
    print(f"{name}: local {len(a)} B vs live {len(b)} B")
    print("  cards local/live:", a.count('<div class="article-card">'), b.count('<div class="article-card">'))
    print("  h2 link count local/live:", len(re.findall(r'<h2><a href=', a)), len(re.findall(r'<h2><a href=', b)))
    la = set(re.findall(r'<h2><a href="([^"]+)"', a))
    lb = set(re.findall(r'<h2><a href="([^"]+)"', b))
    print("  refs only live:", sorted(lb - la)[:8])
    print("  refs only local:", sorted(la - lb)[:8])

if True:
    d = list(difflib.unified_diff(before.splitlines(), live_blog.splitlines(), lineterm="", n=1))
    print("\n=== blog/ unified diff (first 40 lines) ===")
    print("\n".join(x[:220] for x in d[:40]))
    print("... total diff lines:", len(d))

d2 = list(difflib.unified_diff(local_home.splitlines(), live_home.splitlines(), lineterm="", n=1))
print("\n=== home unified diff (first 30 lines) ===")
print("\n".join(x[:220] for x in d2[:30]))
print("... total diff lines:", len(d2))
