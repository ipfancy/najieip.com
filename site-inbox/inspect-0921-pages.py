#!/usr/bin/env python3
# 0921 文章页结构对比：us-trademark vs 已上线正常页（renewal）
import os, re

REPO = os.path.expanduser("~/wiki/najieip-verify")
FILES = {
    "us-trademark(bad?)": "najie/blog/20260921-us-trademark-sanction-defense-window.html",
    "renewal(good)": "najie/blog/20260921-trademark-renewal-lapse-ten-years.html",
    "address(good)": "najie/blog/20260921-trademark-address-change-cancellation.html",
}
for label, rel in FILES.items():
    p = os.path.join(REPO, rel)
    t = open(p, encoding="utf-8").read()
    body = t[t.find("<body"):]
    tags = re.findall(r"<(h1|h2|h3|article|nav|section|div|script|footer|main|p)\b", body)
    from collections import Counter
    c = Counter(tags)
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    print(f"### {label}  size={os.path.getsize(p)}B")
    print("   tags:", dict(c))
    print("   ld+json blocks:", len(ld))
    for blk in ld:
        ty = re.search(r'"@type"\s*:\s*"([^"]+)"', blk)
        dp = re.search(r'"datePublished"\s*:\s*"([^"]+)"', blk)
        print("      @type:", ty.group(1) if ty else "?", "| datePublished:", dp.group(1) if dp else "-")
    print("   h1:", re.findall(r"<h1[^>]*>(.*?)</h1>", body, re.S)[:1])
    print("   meta desc len:", len(re.search(r'<meta name="description" content="([^"]*)"', t).group(1)) if re.search(r'<meta name="description" content="([^"]*)"', t) else 0)
    print("   hreflang:", len(re.findall(r'hreflang="([^"]+)"', t)), re.findall(r'hreflang="([^"]+)"', t))
    print("   og:image:", bool(re.search(r'og:image', t)), "| keywords:", bool(re.search(r'name="keywords"', t)))
    print("   '**' count:", body.count("**"), "| body start:", repr(re.sub(r"\s+", " ", body[:120])))
    print()
