#!/usr/bin/env python3
"""1006 收尾：结构终验 + JSON-LD description 兜底修正"""
import re, os, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)

PAGES = [
    "mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
    "mili/blog/20261005-mili-gas-supply-cutoff-justification.html",
    "mili/blog/20261004-mili-gas-deviation-settlement-account.html",
    "mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
    "najie/blog/20261005-patent-annual-fee-ledger-5-signals.html",
    "najie/blog/20261005-trademark-law-2027-implementing-rules.html",
    "najie/blog/20261003-trademark-invalidated-500w.html",
]

fails = []
for rel in PAGES:
    p = f"{REPO}/{rel}"
    t = read(p)
    # JSON-LD description 兜底：若与 headline 相同，用页面 meta description 替换
    if APPLY:
        md = re.search(r'<meta name="description" content="([^"]*)"', t)
        if md:
            m2 = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', t, re.S)
            if m2:
                try:
                    obj = json.loads(m2.group(2))
                    if obj.get("description") == obj.get("headline"):
                        obj["description"] = md.group(1)
                        t = t[:m2.start()] + m2.group(1) + json.dumps(obj, ensure_ascii=False) + m2.group(3) + t[m2.end():]
                        write(p, t)
                        print(f"  [fixdesc] {rel}")
                except Exception as e:
                    fails.append(f"{rel} fixdesc {e}")
    # 终验
    h1 = len(re.findall(r"<h1[ >]", t))
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ok_ld = 0
    for blk in lds:
        try:
            json.loads(blk); ok_ld += 1
        except Exception as e:
            fails.append(f"{rel} JSON-LD invalid: {e}")
    md = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = md.group(1) if md else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = ti.group(1) if ti else ""
    defrep = desc.strip()[:25] in title if desc else True
    depth = 0
    for tag in re.finditer(r"<div\b[^>]*>|</div>", t):
        depth += -1 if tag.group(0).startswith("</") else 1
    checks = {
        "h1==1": h1 == 1,
        "ld>=2": len(lds) >= 2,
        "ld_valid": ok_ld == len(lds) and len(lds) > 0,
        "og:image": "og:image" in t,
        "desc>80": len(desc) > 80,
        "desc!=title": not defrep,
        "**==0": t.count("**") == 0,
        "裸露表==0": len(re.findall(r"<p>\|.*\|</p>", t)) == 0,
        "div_bal": depth == 0,
        "schema_ok": t.count("https://schema.org") >= 1 and t.count("https://***") == 0,
        "裸引号属性": '"' not in desc,
    }
    bad = [k for k, v in checks.items() if not v]
    print(f"{'OK ' if not bad else 'FAIL'} {rel} {os.path.getsize(p)}B {'| '.join(bad)}")
    if bad:
        fails.append(f"{rel}: {bad}")

# 索引终验
for rel, needles in [
    ("mili/blog/index.html", ["20261006-mili-gas-post-judgment-six-checklist"]),
    ("blog/index.html", ["/mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
                          "/mili/blog/shuju-chanquan-dengji-2026.html",
                          "/najie/blog/jishu-hetong-zhuanli-guishu-2026.html"]),
]:
    p = f"{REPO}/{rel}"
    t = read(p)
    n = t.count('class="article-card"')
    depth = 0
    for tag in re.finditer(r"<div\b[^>]*>|</div>", t):
        depth += -1 if tag.group(0).startswith("</") else 1
    for nd in needles:
        hit = nd in t
        print(f"{'OK ' if hit and depth == 0 else 'FAIL'} {rel} cards={n} depth={depth} hit={hit} {nd}")
        if not (hit and depth == 0):
            fails.append(f"{rel} {nd}")

print("\nFAILS =", len(fails))
for f in fails:
    print("  ", f)
sys.exit(1 if fails else 0)
