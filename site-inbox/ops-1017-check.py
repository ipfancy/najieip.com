#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周任务附带体检：articles.json 前 6 条 + 近 3 日 git 触及文章页的六联判据（线上）"""
import json, os, re, subprocess, time

REPO = os.path.expanduser("~/wiki/najieip-verify")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
FAILS = []


def curl(url):
    for _ in range(3):
        r = subprocess.run(["curl", "-s", "-A", UA, "-m", "30", "-L",
                            url + ("&" if "?" in url else "?") + "cb=%d" % int(time.time())],
                           capture_output=True, text=True)
        if len(r.stdout) > 500:
            return r.stdout
        time.sleep(3)
    return r.stdout


# 近 3 日 git 触及 / 新增的 blog 文章页
files = subprocess.run(["git", "-C", REPO, "log", "--since=4.days", "--name-only", "--diff-filter=AM",
                        "--pretty=format:"], capture_output=True, text=True).stdout.split()
pages = sorted({f for f in files if re.match(r"^(mili|najie|blog)/.*\.html$", f) and not f.endswith("index.html")})
print("近 4 日 git 触及文章页:", len(pages))
for p in pages:
    print("  ", p)

print("\n== 六联判据（线上）==")
for p in pages:
    url = "https://najieip.com/" + p
    t = curl(url)
    if len(t) < 500:
        print("FETCH-FAIL", p, len(t)); FAILS.append(p + " fetch"); continue
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    ogimg = 'og:image' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = ti.group(1) if ti else ""
    tit = re.sub(r"\s*[—|-]\s*(纳杰觅理|Aipunajie).*$", "", title).strip()
    drep = (desc.strip() == tit.strip()) if desc else True
    stars = t.count("**")
    bare = len(re.findall(r"<p>\s*\|[^<]*\|", t))
    issues = []
    if h1 != 1: issues.append(f"h1={h1}")
    if ld < 2: issues.append(f"ld={ld}")
    if not ogimg: issues.append("no og:image")
    if drep: issues.append("desc==title")
    if stars: issues.append(f"**={stars}")
    if bare: issues.append(f"bare_table={bare}")
    print(("OK   " if not issues else "DEFECT ") + p + (" -> " + ", ".join(issues) if issues else ""))
    if issues:
        FAILS.append(f"{p}: {', '.join(issues)}")

print("\n== articles.json 前 6 条 ==")
aj = json.load(open(f"{REPO}/articles.json", encoding="utf-8"))
for a in aj[:6]:
    u = a.get("url") or a.get("path") or ""
    print(" ", a.get("date"), u)

print("\nDEFECTS:", len(FAILS))
for f in FAILS:
    print(" -", f)
