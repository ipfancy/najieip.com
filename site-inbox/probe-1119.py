#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-19 取证：畸形页结构、md 源、封面图、articles.json 违例"""
import os, re, json, glob, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")

bad = "mili/blog/20261119-mili-tv-box-backdoor-four-layers.html"
t = open(os.path.join(REPO, bad), encoding="utf-8").read()
print("=== 畸形页首 1200 字符 ===")
print(t[:1200])
print("\n=== 段落数 ===", len(re.findall(r"<p[ >]", t)))
print("=== 有 style?", "<style" in t, "| 外链css?", "/style.css" in t)
print("=== 注释残留 ===", t.count("<!--"))

print("\n=== md 源搜索 ===")
for pat in [f"{ART}/*tv-box*", f"{ART}/*backdoor*", f"{ART}/*机顶盒*"]:
    for f in glob.glob(pat): print("  ", f, os.path.getsize(f))

print("\n=== 房屋候选（同日 mili 精修页）===")
for f in sorted(glob.glob(os.path.join(REPO, "mili/blog/2026111*.html")))[-6:]:
    x = open(f, encoding="utf-8").read()
    print("  ", os.path.basename(f), os.path.getsize(f), "ld=", x.count("application/ld+json"),
          "ogimg=", "og:image" in x, "css=", "/style.css" in x, "h2=", len(re.findall(r"<h2[\s>]", x)))

print("\n=== 封面图候选 ===")
slugs = ["20261119-aipu-pct-30-months", "20261118-mili-foreign-law-proof",
         "20261119-mili-ai-law-firm-boundary", "20261119-mili-dooring-case",
         "20261119-mili-tv-box-backdoor-four-layers"]
for s in slugs:
    cands = glob.glob(os.path.join(ART, f"cover-*{s}*")) + glob.glob(os.path.join(ART, f"cover-{s}.png"))
    # 日期前缀变体：slug 形如 20261119-xxx → cover-20261119-xxx
    parts = s.split("-")
    if len(parts) > 1:
        rest = "-".join(parts[1:])
        cands += glob.glob(os.path.join(ART, f"cover-{parts[0]}-{rest}*.png"))
        cands += glob.glob(os.path.join(ART, f"cover-{rest}*.png"))
    cands = sorted(set(cands))
    repo_img = os.path.join(REPO, "img", s + ".png")
    print(f"  {s}: cand={[os.path.basename(c) for c in cands]} repo_img={'YES' if os.path.exists(repo_img) else 'no'}")

print("\n=== articles.json 守卫 check ===")
g = os.path.join(REPO, "site-inbox/guard-0918-articles-json.py")
if os.path.exists(g):
    r = subprocess.run(["python3", g, "--check"], capture_output=True, text=True, cwd=REPO)
    print(r.stdout[-1500:]); print(r.stderr[-500:])
else:
    print("  guard script missing")
