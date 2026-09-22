#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 0922 深度诊断2：NO-STYLE 页样式来源 + 畸形页正文与 md 源比对 + stub 尺寸"""
import os, re, json, subprocess, hashlib

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

pages = [
    "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html",
    "mili/blog/20260922-criminal-non-filing-civil-claim.html",
    "mili/blog/20260920-family-wealth-isolation-three-firewalls.html",
    "najie/blog/20260921-us-trademark-sanction-defense-window.html",
]
for p in pages:
    t = rd(p)
    links = re.findall(r'<link[^>]+rel="stylesheet"[^>]*>', t)
    print("== %s (%d B)" % (p, len(t.encode())))
    print("   <style>:", "<style>" in t, " stylesheet links:", len(links))
    for l in links:
        href = re.search(r'href="([^"]+)"', l)
        h = href.group(1) if href else "?"
        fp = h.lstrip("/") if h.startswith("/") else os.path.join(os.path.dirname(p), h.lstrip("./"))
        print("      ", h, "-> exists:", os.path.exists(fp))
    print("   h1:", t.count("<h1"), " h2:", t.count("<h2"), " ld:", t.count("application/ld+json"),
          " og:image:", "og:image" in t, " canonical:", "canonical" in t,
          " nav:", "<nav" in t, " footer:", "<footer" in t, " beacon:", "cloudflare" in t.lower())

print("\n=== stub 尺寸核验（品牌索引有、主索引无） ===")
for f in ["najie/blog/cnptes-three-layer-architecture-diagram.html", "najie/blog/uspto-tbmp-2026-update.html"]:
    if os.path.exists(f):
        t = rd(f)
        print("  %-58s %d B refresh=%s p_tags=%d" % (f.split("/")[-1], os.path.getsize(f),
              'http-equiv="refresh"' in t, len(re.findall(r"<p[ >]", t))))
    else:
        print("  MISSING", f)

print("\n=== 09-22 畸形页：正文段落 vs md 源 ===")
mal = "najie/blog/20260922-us-trademark-sanction-three-step-selfcheck.html"
t = rd(mal)
ps = re.findall(r"<p[^>]*>(.*?)</p>", t, re.S)
print("  畸形页 <p> 数:", len(ps))
for i, x in enumerate(ps):
    print("   [%d] %s" % (i, re.sub(r"<[^>]+>", "", x).strip()[:110]))
print("  md 源 candidates:")
for mdp in ["~/wiki/digital-employees/articles/20260922-us-trademark-sanction-three-step-selfcheck.md",
            "~/wiki/digital-employees/articles/us-trademark-sanction-three-step-selfcheck.md"]:
    fp = os.path.expanduser(mdp)
    print("   ", mdp, "exists:", os.path.exists(fp))
# 也按 slug 模糊找
base = os.path.expanduser("~/wiki/digital-employees/articles")
if os.path.isdir(base):
    hits = [f for f in os.listdir(base) if "three-step" in f or "three_step" in f]
    print("   模糊匹配:", hits[:10])

print("\n=== 最近 5 commit 异常删除检查 ===")
r = subprocess.run(["git", "log", "--name-status", "-5", "--pretty=format:%h %s"], capture_output=True, text=True)
out = r.stdout
dels = [l for l in out.splitlines() if l.startswith("D\t")]
print("  删除条目数:", len(dels))
for l in dels[:15]:
    print("   ", l)

print("\n=== sitemap 0922 条目 ===")
sm = rd("sitemap.xml")
for u in re.findall(r"<url>(.*?)</url>", sm, re.S):
    if "three-step" in u or "criminal-non-filing" in u:
        print("  ", re.sub(r"\s+", " ", u.strip())[:200])
print("  total loc:", sm.count("<loc>"), " lastmod:", sm.count("<lastmod>"))
