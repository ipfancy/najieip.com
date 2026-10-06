#!/usr/bin/env python3
"""SiteOps 1006 缺口扫描 + 新页六联缺陷体检"""
import re, os, json, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
BASE = "https://najieip.com"

def read(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

main_idx = read(f"{REPO}/blog/index.html")
mili_idx = read(f"{REPO}/mili/blog/index.html")
najie_idx = read(f"{REPO}/najie/blog/index.html")

print("=== 索引卡计数 ===")
for name, t in [("main/blog", main_idx), ("mili/blog", mili_idx), ("najie/blog", najie_idx)]:
    print(f"{name}: article-card={t.count('article-card')}")

# 品牌索引里的 href 归一（相对 ./slug.html -> /brand/blog/slug.html）
def brand_hrefs(idx, brand):
    hs = re.findall(r'<h2><a href="([^"]+)"', idx)
    out = {}
    for h in hs:
        if h.startswith("./"):
            full = f"/{brand}/blog/" + h[2:]
        elif h.startswith("/"):
            full = h
        else:
            full = f"/{brand}/blog/" + h
        out[full] = True
    return out

targets = [
    "20261006-mili-gas-post-judgment-six-checklist",
    "20261005-patent-annual-fee-ledger-5-signals",
    "20261005-trademark-law-2027-implementing-rules",
    "20261005-trade-secret-confidentiality-measures",
    "20261005-trademark-squatting-3-remedies",
    "20261005-mili-gas-supply-cutoff-justification",
    "20261004-mili-gas-deviation-settlement-account",
    "20261004-bambu-stratasys-fto-decision-tree",
    "20261003-trademark-invalidated-500w",
]

print("\n=== 逐文在主索引/品牌索引存在性（href 归一，前导斜杠） ===")
for slug in targets:
    incards = {}
    for name, idx in [("main", main_idx), ("mili", mili_idx), ("najie", najie_idx)]:
        incards[name] = slug in idx
    # 找实际文件
    files = []
    for p in glob.glob(f"{REPO}/**/{slug}.html", recursive=True):
        files.append(p.replace(REPO + "/", ""))
    print(f"{slug}: main={incards['main']} mili={incards['mili']} najie={incards['najie']} files={files}")

print("\n=== 新页六联缺陷体检（近 4 日 HTML，排除 index） ===")
recent = []
for p in glob.glob(f"{REPO}/**/*.html", recursive=True):
    if os.path.basename(p).startswith("index"):
        continue
    rel = p.replace(REPO + "/", "")
    if not re.search(r"2026(1003|1004|1005|1006)", rel):
        continue
    size = os.path.getsize(p)
    if size < 1500:
        continue
    recent.append(p)

for p in sorted(recent):
    t = read(p)
    rel = p.replace(REPO + "/", "")
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = t.count("application/ld+json")
    ogimg = "og:image" in t
    md = re.search(r'<meta name="description" content="([^"]*)"', t)
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    desc = md.group(1) if md else ""
    title = ti.group(1) if ti else ""
    defrep = (desc.strip()[:40] in title) if desc else True
    starstar = t.count("**")
    ptable = len(re.findall(r"<p>\|.*\|</p>", t))
    issues = []
    if h1 != 1: issues.append(f"h1={h1}")
    if ld == 0: issues.append("ld=0")
    if not ogimg: issues.append("no-og:image")
    if defrep: issues.append("desc=标题复读")
    if starstar: issues.append(f"**={starstar}")
    if ptable: issues.append(f"裸表={ptable}")
    print(f"{'OK ' if not issues else 'DEF'} {rel} ({size}B) {'; '.join(issues)}")
