#!/usr/bin/env python3
"""Live verification for 10-22 SiteOps run."""
import re, json, subprocess, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BASE = "https://najieip.com"
cb = str(int(time.time()))

def get(path, head=False):
    cmd = ["curl", "-s", "-A", UA, "--max-time", "25"]
    if head:
        cmd.append("-sI")
    cmd.append(f"{BASE}/{path}?cb={cb}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    return r.stdout

fails = []
def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name} {detail}")
    if not ok:
        fails.append(name)

# 1. core pages
for p in ["", "mili/", "najie/", "blog/", "sitemap.xml", "llms.txt"]:
    out = get(p)
    code = re.search(r"HTTP/\S+ (\d{3})", out)
    check(f"HTTP /{p}", bool(code) and code.group(1) == "200", code.group(1) if code else "no-response")

# 2. rebuilt page
slug = "najie/blog/20261022-najie-gaoqi-ip-30points.html"
t = get(slug)
check("gaoqi h1==1", t.count("<h1") == 1, str(t.count("<h1")))
check("gaoqi ld>=2", t.count("application/ld+json") >= 2, str(t.count("application/ld+json")))
check("gaoqi og:image", "og:image" in t)
check("gaoqi desc real", 'content="高企评分里知识产权占 30 分' in t)
check("gaoqi no bare table", not re.search(r"<p>\s*\|", t))
check("gaoqi no **", t.count("**") == 0, str(t.count("**")))
check("gaoqi size~9943", abs(len(t.encode()) - 9943) < 900, str(len(t.encode())))

# 3. cover image
out = get("img/20261022-najie-gaoqi-ip-30points.png", head=True)
code = re.search(r"HTTP/\S+ (\d{3})", out)
check("cover img 200", bool(code) and code.group(1) == "200", code.group(1) if code else "none")

# 4. index cards live
main = get("blog/")
njidx = get("najie/blog/")
check("main idx gaoqi card", "/najie/blog/20261022-najie-gaoqi-ip-30points.html" in main)
check("main idx safety card", "/mili/blog/20261022-safety-production-crimes.html" in main)
check("najie idx gaoqi card", "20261022-najie-gaoqi-ip-30points.html" in njidx)

# 5. articles.json live
aj = get("articles.json")
try:
    arts = json.loads(aj)
    arts = arts if isinstance(arts, list) else arts.get("articles", [])
    check("articles.json live ==198", len(arts) == 198, str(len(arts)))
except Exception as e:
    check("articles.json parse", False, str(e)[:60])

# 6. new mili pages still OK
for p in ["mili/blog/20261022-safety-production-crimes.html", "mili/blog/20261022-judge-liability-verdict-reversed.html"]:
    t2 = get(p)
    check(p.split("/")[-1][:38] + " h1/ld", t2.count("<h1") == 1 and t2.count("application/ld+json") >= 2,
          f"h1={t2.count('<h1')} ld={t2.count('application/ld+json')}")

print("\nFAILS:", fails if fails else "NONE")
