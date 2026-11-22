#!/usr/bin/env python3
# 定位机顶盒文 + 两个 MISMATCH 归因
import os, re, difflib, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD = os.path.expanduser("~/wiki/digital-employees/articles")
BRANDS = ("mili", "najie", "aipunajie")

print("=== 找机顶盒/11-19 页面 ===")
for b in BRANDS:
    d = os.path.join(REPO, b, "blog")
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".html") and ("20261119" in fn or "20261118" in fn or "box" in fn.lower() or "jiding" in fn):
            print(f"  {b}: {fn}")

print("=== md 文件近 4 日 ===")
for fn in sorted(os.listdir(MD)):
    if fn.endswith(".md") and ("20261119" in fn or "2026112" in fn):
        print("  ", fn)

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'")
    return s

def norm(s):
    return re.sub(r"[*`|\-:：\s「」『』【】\"“”'’]", "", s)

for slug, brand, fn in [
    ("20261121-mili-divorce-game-account-88w", "mili", "20261121-mili-divorce-game-account-88w"),
    ("20261120-mili-device-procurement-firmware-checklist", "mili", "20261120-mili-device-procurement-firmware-checklist"),
]:
    p = os.path.join(REPO, brand, "blog", fn + ".html")
    t = open(p, encoding="utf-8").read()
    art = re.search(r"<article.*?</article>", t[t.find("<body"):], re.S)
    pgt = norm(textify(re.sub(r"<h[1-6].*?</h[1-6]>", " ", art.group(0), flags=re.S)).replace("北京纳杰知识产权代理有限公司 何自刚", ""))
    mdp = os.path.join(MD, fn + ".md")
    mdt = open(mdp, encoding="utf-8").read()
    mdt = re.sub(r"^---.*?---", "", mdt, flags=re.S)
    mdt = re.sub(r"<!--.*?-->", "", mdt, flags=re.S)
    lines = []
    for l in mdt.split("\n"):
        s = l.strip()
        if not s or s.startswith("#") or s.startswith("---") or s.startswith("***") or s.startswith(">"):
            continue
        lines.append(l)
    mdt = "\n".join(lines)
    mdt = re.sub(r"^\s*\d+\.\s*", "", mdt, flags=re.M)
    md = norm(mdt)
    print(f"=== {slug} md={len(md)} pg={len(pgt)} contained={md in pgt}")
    if md != pgt:
        # 逐段对比
        mpar = [norm(x) for x in re.split(r"\n\s*\n", mdt) if norm(x)]
        missing = [x[:40] for x in mpar if x not in pgt]
        extra = [x[:40] for x in [norm(y) for y in re.split(r"\n\s*\n", textify(art.group(0)))] if x and x not in md]
        print("  missing_paras:", len(missing), missing[:4])
        print("  extra_paras:", len(extra), extra[:4])
