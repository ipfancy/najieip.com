#!/usr/bin/env python3
"""1006 残留 markdown 强调清理（限 <article> 区域内，DOTALL 非贪婪）"""
import re, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
PAGES = [
    "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
    "mili/blog/20261005-mili-gas-supply-cutoff-justification.html",
]
for rel in PAGES:
    p = f"{REPO}/{rel}"
    with open(p, encoding="utf-8") as f:
        t = f.read()
    a = t.find("<article")
    b = t.find("</article>")
    if a < 0 or b < 0:
        print(f"SKIP(no article) {rel}")
        continue
    body = t[a:b]
    left = re.findall(r"\*\*[^*]{0,120}?\*\*", body, re.S)
    print(f"{rel}: 残留 {len(left)} 处")
    for x in left[:8]:
        print("   ", repr(x[:120]))
    new = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body, flags=re.S)
    if new != body:
        with open(p, "w", encoding="utf-8") as f:
            f.write(t[:a] + new + t[b:])
        print(f"   -> 已转换，剩余 ** = {new.count('**')}")
