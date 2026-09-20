#!/usr/bin/env python3
# 0920 线上验证：字节口径比较 + 新卡 grep + 关键页 200
import subprocess, os, time, difflib, re

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260920-family-wealth-isolation-three-firewalls"
cb = str(int(time.time()))


def curl_head(u):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-L", "--max-time", "25", u],
                       capture_output=True, text=True)
    return r.stdout.strip()


def fetch(u):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "25", u], capture_output=True)
    return r.stdout


print("=== 关键页 HTTP ===")
urls = [f"https://najieip.com/blog/?cb={cb}", f"https://najieip.com/mili/blog/?cb={cb}",
        f"https://najieip.com/mili/blog/{SLUG}.html?cb={cb}",
        f"https://najieip.com/najie/blog/?cb={cb}", f"https://najieip.com/sitemap.xml?cb={cb}",
        f"https://najieip.com/mili/?cb={cb}", f"https://najieip.com/najie/?cb={cb}"]
for u in urls:
    print(f"  {curl_head(u)}  {u.split('?')[0]}")

print("\n=== 线上 vs 本地 字节比较（同口径）===")
for path, local in [("/blog/", "blog/index.html"), ("/mili/blog/", "mili/blog/index.html"),
                    ("/najie/blog/", "najie/blog/index.html")]:
    live = fetch(f"https://najieip.com{path}?cb={cb}")
    lb = open(os.path.join(REPO, local), "rb").read()
    same = live == lb
    print(f"  {path}: live={len(live)}B local={len(lb)}B  {'IDENTICAL' if same else 'DIFF'}")
    if not same:
        a = live.decode("utf-8", "replace").splitlines()
        b = lb.decode("utf-8", "replace").splitlines()
        d = [l for l in difflib.unified_diff(b, a, lineterm="", n=0)][:12]
        for l in d:
            print("      ", l[:160])

print("\n=== 线上主索引新卡 ===")
live_blog = fetch(f"https://najieip.com/blog/?cb={cb}").decode("utf-8", "replace")
body = live_blog[live_blog.find("<body"):]
hrefs = re.findall(r'<h2><a href="([^"]+)"', body)
print(f"  线上卡片数={len(hrefs)}  首卡={hrefs[0] if hrefs else 'N/A'}")
print(f"  含新文 slug: {SLUG in live_blog}")
i = body.find('<div class="article-card"')
print("  首卡片段:", repr(body[i:i+260]))
print(f"  线上 md 泄漏: {live_blog.count('**')}")

print("\n=== 线上 sitemap/新文 ===")
s = fetch(f"https://najieip.com/sitemap.xml?cb={cb}").decode("utf-8", "replace")
print(f"  loc 总数={s.count('<loc>')}  含新文={SLUG in s}")
