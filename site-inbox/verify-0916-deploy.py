#!/usr/bin/env python3
"""Deployment verification: core pages + every href in main blog/index.html (brand-dir targets)."""
import re, subprocess, os, time
from concurrent.futures import ThreadPoolExecutor

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
t = open("blog/index.html", encoding="utf-8").read()
hrefs = re.findall(r'<h2><a href="([^"]+)"', t)
print("cards in index:", len(hrefs))

CORE = ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
        "https://najieip.com/blog/", "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]


def head(url):
    r = subprocess.run(["curl", "-sI", "-L", "-o", "/dev/null", "-w", "%{http_code}",
                        "--max-time", "20", url], capture_output=True, text=True)
    return url, r.stdout.strip()


with ThreadPoolExecutor(max_workers=8) as ex:
    core = list(ex.map(head, CORE))
print("=== CORE ===")
for u, c in core:
    print(("OK  " if c == "200" else "BAD "), c, u)

urls = ["https://najieip.com" + h for h in hrefs if h.startswith("/")]
with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(head, urls))
bad = [(u, c) for u, c in res if c != "200"]
print(f"=== CARD TARGETS: {len(urls)} checked, {len(bad)} non-200 ===")
for u, c in bad[:20]:
    print("  BAD", c, u)

# byte compare index pages (unique temp files, no shared /tmp race)
print("=== live vs local bytes ===")
for url, f in [("https://najieip.com/blog/", "blog/index.html"),
               ("https://najieip.com/mili/blog/", "mili/blog/index.html"),
               ("https://najieip.com/najie/blog/", "najie/blog/index.html"),
               ("https://najieip.com/aipunajie/blog/", "aipunajie/blog/index.html")]:
    tmp = f"/tmp/verify0916_{os.path.basename(os.path.dirname(f)) or 'root'}.html"
    subprocess.run(["curl", "-s", "--max-time", "30", f"{url}?cb={int(time.time())}", "-o", tmp])
    same = subprocess.run(["cmp", "-s", tmp, f]).returncode == 0
    print(("SAME " if same else "DIFF "), url, os.path.getsize(tmp), "vs", os.path.getsize(f))

# new cards visible on live index?
live = open("/tmp/verify0916_blog.html", encoding="utf-8", errors="replace").read()
print("=== new-card spot check on live blog/ ===")
for slug in ["20260916-data-asset-four-step", "20260918-personality-rights-injunction",
             "enterprise-ip-compliance-system", "trademark-squatting-guide-en", "ai-music-copyright-boundary"]:
    print("  ", "FOUND" if slug in live else "MISSING", slug)
print("  live cards:", live.count('<div class="article-card">'))
