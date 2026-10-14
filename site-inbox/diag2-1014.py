#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, subprocess
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))

main = open("blog/index.html", encoding="utf-8", errors="ignore").read()
print("=== 主索引 slug 出现次数 ===")
for s in ["patent-vs-trade-secret-layering-2026",
          "layout-design-originality-claim-322-2026",
          "20261014-trademark-pattern-packaging-confusion",
          "cnptes-three-layer-architecture-diagram",
          "bambu-stratasys-fto-decision-tree-20261004"]:
    print("  %-50s main=%d mili=%d najie=%d en=%d fr=%d" % (
        s, main.count(s),
        open("mili/blog/index.html", encoding="utf-8", errors="ignore").read().count(s),
        open("najie/blog/index.html", encoding="utf-8", errors="ignore").read().count(s),
        open("en/blog/index.html", encoding="utf-8", errors="ignore").read().count(s),
        open("fr/blog/index.html", encoding="utf-8", errors="ignore").read().count(s)))

print("\n=== ld+json 块类型 ===")
for f in ["najie/blog/20261014-trademark-pattern-packaging-confusion.html",
          "najie/blog/layout-design-originality-claim-322-2026.html",
          "mili/blog/patent-vs-trade-secret-layering-2026.html",
          "mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html",
          "en/blog/bambu-stratasys-fto-decision-tree-20261004-en.html",
          "fr/blog/bambu-stratasys-fto-decision-tree-20261004-fr.html",
          "blog/index.html", "mili/blog/index.html", "najie/blog/index.html",
          "en/blog/index.html", "fr/blog/index.html"]:
    if not os.path.exists(f):
        print("  MISSING", f); continue
    t = open(f, encoding="utf-8", errors="ignore").read()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    types = ["+".join(re.findall(r'"@type"\s*:\s*"([^"]+)"', b)) for b in blocks]
    print("  %d %-42s %s" % (len(blocks), str(types)[:60], f))

print("\n=== 今日新页关键字段 ===")
for f in ["najie/blog/20261014-trademark-pattern-packaging-confusion.html",
          "najie/blog/layout-design-originality-claim-322-2026.html",
          "mili/blog/patent-vs-trade-secret-layering-2026.html"]:
    t = open(f, encoding="utf-8", errors="ignore").read()
    md = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', t)
    tt = re.search(r"<title>(.*?)</title>", t, re.S)
    print("  %s\n     bytes=%d h1=%d ld=%d og:image=%s desc_len=%d title=%s" % (
        f, os.path.getsize(f), len(re.findall(r"<h1[\s>]", t)), t.count("application/ld+json"),
        "og:image" in t, len(md.group(1)) if md else 0,
        re.sub(r"\s+", " ", tt.group(1)).strip()[:40] if tt else "")[:200])
