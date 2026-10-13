#!/usr/bin/env python3
"""收集修复输入 — 只读。"""
import os, re, json, glob, subprocess

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
out = []
def p(*a): out.append(" ".join(str(x) for x in a))

# 1. index 页 h1 规范检查（是否本来就是 h1=0）
p("=== index 页 h1 规范 ===")
for f in ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html",
          "en/blog/index.html", "fr/blog/index.html", "aipunajie/blog/index.html"]:
    t = open(f, encoding="utf-8", errors="replace").read()
    p(f"  {f}: h1={len(re.findall(chr(60)+'h1[ >]', t))} h2={len(re.findall(chr(60)+'h2[ >]', t))}")

# 2. 缺陷页全文结构
f = "mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html"
t = open(f, encoding="utf-8", errors="replace").read()
p(f"\n=== 缺陷页 {f} ({len(t.encode())}B) ===")
p("  h1 =", len(re.findall(r"<h1[ >]", t)))
p("  h2 列表:", re.findall(r"<h2[^>]*>(.*?)</h2>", t))
p("  p 段数 =", len(re.findall(r"<p[ >]", t)))
p("  strong =", t.count("<strong>"), " ** =", t.count("**"))
p("  '|' 裸表行 =", len(re.findall(r"<p>\s*\|[^<]*\|\s*</p>", t)))
p("  脚注/落款尾部:")
body = t[t.find("<footer"):] if "<footer" in t else t[-600:]
p("   " + re.sub(r"\s+", " ", body)[:400])

# 3. md 源
p("\n=== md 源定位 ===")
slug = "20261010"
cands = glob.glob(os.path.expanduser(f"~/wiki/digital-employees/articles/*{slug}*.md"))
cands += glob.glob(os.path.expanduser(f"~/wiki/najieip-verify/site-inbox/*{slug}*.html"))
for c in sorted(set(cands)):
    p(f"  {os.path.getsize(c):>7}B {c}")

# 4. 房屋模板尾部（同品牌同日近邻）
p("\n=== 房屋模板尾部 (20261009) ===")
ht = open("mili/blog/20261009-mili-ai-short-drama-token-evidence.html", encoding="utf-8").read()
p(re.sub(r"\s+", " ", ht[ht.find("<footer"): ht.find("<footer")+700]))

# 5. articles.json 该条
d = json.load(open("articles.json"))
arts = d if isinstance(d, list) else d.get("articles", [])
for a in arts:
    if "20261010-mili-aigc" in json.dumps(a, ensure_ascii=False):
        p("\n=== articles.json 条目 ===")
        p("  " + json.dumps(a, ensure_ascii=False)[:700])
        break

print("\n".join(out))
