#!/usr/bin/env python3
"""1006 线上内容终验（直连 najieip.com，带 cache-buster）"""
import subprocess

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
PAGES = [
    "/mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
    "/mili/blog/20261005-mili-gas-supply-cutoff-justification.html",
    "/mili/blog/20261004-mili-gas-deviation-settlement-account.html",
    "/mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
    "/najie/blog/20261005-patent-annual-fee-ledger-5-signals.html",
    "/najie/blog/20261005-trademark-law-2027-implementing-rules.html",
    "/najie/blog/20261003-trademark-invalidated-500w.html",
]

def get(url):
    r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "30",
                        "-H", "Cache-Control: no-cache", "-H", "Pragma: no-cache", url],
                       capture_output=True, text=True, timeout=45)
    return r.stdout

import time
cb = int(time.time())
print("=== 线上文章页内容 ===")
bad = []
for rel in PAGES:
    d = get(f"https://najieip.com{rel}?cb={cb}")
    ld = d.count("application/ld+json")
    og = "og:image" in d
    st = d.count("**")
    h1 = d.count("<h1")
    ok = ld >= 2 and og and st == 0 and h1 == 1
    if not ok:
        bad.append(rel)
    print(f"  ld={ld} og:image={og} **={st} h1={h1} bytes={len(d.encode())} {'OK' if ok else 'FAIL'} {rel}")

print("\n=== 线上索引卡 ===")
for rel, needle in [("/mili/blog/", "20261006-mili-gas-post-judgment-six-checklist"),
                    ("/blog/", "20261006-mili-gas-post-judgment-six-checklist"),
                    ("/blog/", "shuju-chanquan-dengji-2026"),
                    ("/blog/", "jishu-hetong-zhuanli-guishu-2026")]:
    d = get(f"https://najieip.com{rel}?cb={cb}")
    print(f"  cards={d.count('article-card')} 含 {needle}: {needle in d}  ({rel})")

d = get(f"https://najieip.com/sitemap.xml?cb={cb}")
print(f"\nsitemap loc(线上) = {d.count('<loc>')}")
print("线上未达标:", bad)
