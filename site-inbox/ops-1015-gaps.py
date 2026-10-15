#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缺口扫描 + 新页质量 QA（六联判据）+ 索引比对（href 归一，前导斜杠）"""
import os, re, json, glob, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

IDX = {"main": "blog/index.html", "mili": "mili/blog/index.html",
       "najie": "najie/blog/index.html", "en": "en/blog/index.html", "fr": "fr/blog/index.html"}
texts = {k: open(v, encoding="utf-8").read() for k, v in IDX.items()}

print("=== A. 近 4 日新增/修改的文章页文件 ===")
import subprocess
p = subprocess.run(["git", "log", "--since=4.days", "--diff-filter=AM", "--name-only",
                    "--pretty=format:%h %ad", "--date=short", "--",
                    "mili/blog/", "najie/blog/", "blog/", "aipunajie/blog/"],
                   capture_output=True, text=True)
files = set()
for line in p.stdout.splitlines():
    line = line.strip()
    if line.endswith(".html") and "/blog/" in line and not line.endswith("/index.html"):
        files.add(line)
for f in sorted(files):
    print("  " + f)

print("\n=== B. 缺口扫描：近 4 日文章页是否出现在主索引/品牌索引（href 归一） ===")
for f in sorted(files):
    brand = f.split("/")[0]
    slug = os.path.basename(f)
    abs_path = "/" + f
    rel_path = "./" + slug
    row = {"file": f}
    for k, t in texts.items():
        hit_abs = abs_path in t
        hit_slug = slug in t
        row[k] = "ABS" if hit_abs else ("slug" if hit_slug else "-")
    print("  %-58s main=%s mili=%s najie=%s en=%s fr=%s" %
          (f, row["main"], row["mili"], row["najie"], row["en"], row["fr"]))

print("\n=== C. 六联缺陷 QA（近 4 日页面） ===")
def qa(path):
    t = open(path, encoding="utf-8").read()
    b = t[t.find("<body"):] if "<body" in t else t
    res = {}
    res["h1"] = len(re.findall(r"<h1[ >]", t))
    res["ld"] = t.count("application/ld+json")
    res["ogimage"] = ("og:image" in t)
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    mh = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    h1 = re.sub(r"<[^>]+>", "", mh.group(1)).strip() if mh else ""
    res["desc_len"] = len(desc)
    res["desc_dup_title"] = (desc.strip() == h1.strip() and len(desc) > 0)
    res["stars"] = b.count("**")
    res["raw_table"] = len(re.findall(r"<p>\s*\|", b))
    res["style"] = ("<style>" in t) or (bool(re.search(r'rel="stylesheet"[^>]*href="/style\.css"', t)))
    res["size"] = os.path.getsize(path)
    return res

for f in sorted(files):
    path = os.path.join(REPO, f)
    if not os.path.exists(path):
        print("  %-58s MISSING FILE" % f); continue
    r = qa(path)
    bad = []
    if r["h1"] != 1: bad.append("h1=%d" % r["h1"])
    if r["ld"] == 0: bad.append("no-ld")
    if not r["ogimage"]: bad.append("no-og:image")
    if r["desc_dup_title"]: bad.append("desc=dup-title")
    if r["stars"]: bad.append("**x%d" % r["stars"])
    if r["raw_table"]: bad.append("raw-table x%d" % r["raw_table"])
    if not r["style"]: bad.append("NO-STYLE")
    verdict = "OK" if not bad else "DEFECT: " + ",".join(bad)
    print("  %-58s %6dB  %s" % (f, r["size"], verdict))

print("\n=== D. 三索引卡片计数/结构 ===")
for k, v in IDX.items():
    t = texts[k]
    body = t[t.find("<body"):]
    # div 深度与卡片数
    depth = 0; cards_at = {}; stack_min = 0
    for m in re.finditer(r"<(/?)div[^>]*>", body):
        if m.group(1) == "":
            depth += 1
            if m.group(0).startswith('<div class="article-card"'):
                cards_at[depth] = cards_at.get(depth, 0) + 1
        else:
            depth -= 1
    print("  %-24s cards=%d depth_end=%d card_depths=%s stars=%d" %
          (v, t.count('<div class="article-card">'), depth, cards_at, t.count("**")))
print("\nDONE")
