#!/usr/bin/env python3
"""11-25 线上终验：Pages 构建 → 索引卡 HIT / 页面六项 / 封面 200"""
import subprocess, time, json, re, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def curl(url, head=True, tries=3):
    for i in range(tries):
        cmd = ["curl", "-s", "-A", UA, "--max-time", "60"]
        if head:
            cmd += ["-I", "-o", "/dev/null", "-w", "%{http_code}"]
        cmd.append(url)
        r = subprocess.run(cmd, capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200":
            return code, ""
        time.sleep(4)
    return code, ""


def body(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "60", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout
        time.sleep(5)
    return ""


# 1) 等 Pages 构建
sha = subprocess.run(["git", "-C", "/Users/ziganghe/wiki/najieip-verify", "rev-parse", "HEAD"],
                     capture_output=True, text=True).stdout.strip()
print("HEAD:", sha[:7])
for i in range(10):
    r = subprocess.run(["curl", "-s", "--max-time", "30",
                        "https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=4"],
                       capture_output=True, text=True)
    try:
        runs = json.loads(r.stdout).get("workflow_runs", [])
    except Exception:
        runs = []
    hit = [x for x in runs if x.get("head_sha", "").startswith(sha[:7])]
    if hit:
        st, cc = hit[0].get("status"), hit[0].get("conclusion")
        print(f"  run {hit[0]['id']} {st}/{cc}")
        if st == "completed":
            if cc != "success":
                print("  BUILD_FAILED")
            break
    else:
        print(f"  run for {sha[:7]} not listed yet ({len(runs)} runs)")
    time.sleep(20)

time.sleep(45)

# 2) 线上检查
slugs = ["20261125-mili-ai-face-blend-portrait-1019",
         "20261125-najie-plant-variety-punitive-damages",
         "20261125-najie-patent-intensive-product-filing"]
cb = int(time.time())
main = body(f"https://najieip.com/blog/?cb={cb}")
print("main index bytes:", len(main))
for s in slugs:
    print(f"  main-card {s}: {len(re.findall(r'<h2><a href=\"[^\"]*' + s + r'\"', main))}")

page = body(f"https://najieip.com/mili/blog/{slugs[0]}.html?cb={cb}")
print("page bytes:", len(page))
print("  h1=%d ld=%d ogimg=%s tw=%s desc_len=%s" % (
    len(re.findall(r"<h1[\s>]", page)),
    len(re.findall(r"application/ld\+json", page)),
    'property="og:image"' in page,
    "summary_large_image" in page,
    (lambda m: len(m.group(1)) if m else 0)(re.search(r'<meta name="description" content="([^"]*)"', page))))

for u in ["/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt",
          "/img/20261125-mili-ai-face-blend-portrait-1019.png"]:
    code, _ = curl("https://najieip.com" + u)
    print(f"  {code} {u}")
