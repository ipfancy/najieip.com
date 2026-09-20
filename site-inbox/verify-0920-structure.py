#!/usr/bin/env python3
# 0920 补卡终验：结构 + 深度 + 日期 + 污染
import os, re, json
from collections import Counter

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "blog/index.html")
SLUG = "20260920-family-wealth-isolation-three-firewalls"
t = open(P, encoding="utf-8").read()
body_start = t.find("<body")
body = t[body_start:]
ok = True


def chk(name, cond, extra=""):
    global ok
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")
    if not cond:
        ok = False


n_cards = body.count('<div class="article-card"')
chk("卡片计数 ==163", n_cards == 163, f"got {n_cards}")

# div 深度 + 直接子节点深度分析
depth = 0; underflow = 0; dd2 = 0
stack = []
for m in re.finditer(r'<(/?)div[^>]*>', body):
    closing = m.group(1) == "/"
    if not closing:
        depth += 1
        if depth == 2:
            dd2 += 1
    else:
        if depth == 0:
            underflow += 1
        else:
            depth -= 1
chk("div 深度归零", depth == 0, f"depth={depth}")
chk("无栈空闭合", underflow == 0, f"underflow={underflow}")

# 逐卡：以 <h2><a href= 起
starts = [m.start() for m in re.finditer(r'<div class="article-card">', body)]
malformed = 0
for i, s in enumerate(starts):
    seg = body[s + len('<div class="article-card">'):]
    if not seg.lstrip().startswith('<h2><a href='):
        malformed += 1
chk("每卡以 <h2><a href= 起", malformed == 0, f"malformed={malformed}")

# container 直接子节点（depth=2）中卡片数 == 163
dd2_cards = 0
depth = 0
for m in re.finditer(r'<(/?)(div|h1|h2|p|a|span|header|script)[^>]*>', body):
    tag = m.group(2); closing = m.group(1) == "/"
    if tag != "div":
        continue
    if not closing:
        depth += 1
        if depth == 2 and body[m.start():m.start() + 31].startswith('<div class="article-card"'):
            dd2_cards += 1
    else:
        depth = max(0, depth - 1)
chk("depth=2 卡片数 ==163", dd2_cards == 163, f"got {dd2_cards}")

# href 唯一
hrefs = re.findall(r'<h2><a href="([^"]+)"', body)
dups = {h: c for h, c in Counter(hrefs).items() if c > 1}
chk("href 无重复", len(dups) == 0, f"dups={len(dups)} {list(dups)[:3]}")

# 新卡是首卡
first_href = hrefs[0] if hrefs else ""
chk("新卡为 body 首卡", SLUG in first_href, first_href)

# 插入点前缀日期降序
dates = re.findall(r'<span class="tag">[^<]*</span>(?:\s*<span class="tag">[^<]*</span>)*\s*(\d{4}-\d{2}-\d{2})', body)
prefix = dates[:3]
chk("前缀日期降序(09-20,09-19,09-19)", prefix == ['2026-09-20', '2026-09-19', '2026-09-19'], str(prefix))

# 污染
chk("无 markdown 泄漏", body.count("**") == 0, f"count={body.count('**')}")
chk("无未替换占位符", body.count("@@") == 0 and body.count("{{") == 0)

# 新卡块完整性 + 新卡描述不含导航残渣
i = body.find('<div class="article-card">')
seg = body[i:body.find('<div class="article-card">', i + 10)]
chk("新卡 <p> 描述存在且干净", "<p>" in seg and "← 首页" not in seg and len(re.findall(r'<p>', seg)) == 1)
print()
print("RESULT:", "ALL PASS" if ok else "HAS FAILURES")
