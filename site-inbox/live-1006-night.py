#!/usr/bin/env python3
"""Live verification after push: direct najieip.com + cache buster, browser UA (CF blocks default UA)."""
import subprocess, re, os, json, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
SLUG = "20261006-nobel-icecube-patent-four-rules"

def get(url):
    for i in range(3):
        cb = f"?cb={int(time.time())}" if "?" not in url else f"&cb={int(time.time())}"
        r = subprocess.run(["curl", "-s", "-A", UA, "-L", "--max-time", "25", url + cb],
                           capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 400:
            return r.stdout
        time.sleep(3)
    return ""

ROOT = "/Users/ziganghe/wiki/najieip-verify"
checks = []
p = get(f"https://najieip.com/mili/blog/{SLUG}.html")
checks.append(("article 200/len", len(p) > 4000, len(p)))
checks.append(("ld+json >= 2", p.count("application/ld+json") >= 2, p.count("application/ld+json")))
checks.append(("og:image", "og:image" in p, "og:image" in p))
checks.append(("h1 == 1", p.count("<h1") == 1, p.count("<h1")))
checks.append(("** == 0", p.count("**") == 0, p.count("**")))
checks.append(("desc not title-repeat", "科学发现与专利的分界" in p, None))
checks.append(("og:title not truncated", 'og:title" content="诺奖给了中微子，专利法却说“不授权”：IceCube藏着4条创新规则"' in p, None))

for name, path, needle in [("mili index card", "/mili/blog/", f"{SLUG}.html"),
                           ("main index card", "/blog/", f"/mili/blog/{SLUG}.html")]:
    h = get("https://najieip.com" + path)
    checks.append((name, needle in h, len(h)))

aj = get("https://najieip.com/articles.json")
try:
    n = len(json.loads(aj))
except Exception as e:
    n = f"parse-fail {e}"
checks.append(("articles.json == 175", n == 175, n))

# local vs live byte compare (article page): CF injects beacon only
live_local = subprocess.run(["curl", "-s", "-A", UA, "-L", "--max-time", "25",
                             f"https://najieip.com/mili/blog/{SLUG}.html?cb={int(time.time())}"],
                            capture_output=True).stdout.decode("utf-8", "replace")
disk = open(os.path.join(ROOT, "mili/blog", SLUG + ".html"), encoding="utf-8").read()
import difflib
d = [l for l in difflib.unified_diff(disk.splitlines(), live_local.splitlines(), lineterm="", n=0)]
checks.append(("live==disk (beacon-only diff)", len(d) <= 8, f"{len(d)} diff lines"))

ok = True
for name, res, detail in checks:
    ok = ok and bool(res)
    print(f"{'PASS' if res else 'FAIL'}  {name}  ({detail})")
print("ALL LIVE CHECKS PASS" if ok else "SOME LIVE CHECKS FAILED")
