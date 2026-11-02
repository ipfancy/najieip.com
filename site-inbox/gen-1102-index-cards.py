#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-02: 索引补卡（najie 索引补 A；主索引补 B+A，日期降序）+ articles.json 补 B
幂等：已存在则跳过。"""
import os, re, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
DATE = "2026-11-02"
OWNER = "北京纳杰知识产权代理有限公司"

A = dict(slug="20261102-najie-tech-export-catalog-48",
         title="48号公告：40项技术出口先登记，判断错了没人替你兜底",
         tags=["技术出口", "出口管制", "涉外知识产权"], ts="05:00",
         desc=("商务部、科技部第48号公告拟增列40项技术（人工智能23项、生物医药5项、光伏12项），拟禁止14项、拟限制26项，"
               "11月15日是征求意见截止日；但临时出口前登记自2026年10月16日公告发布当天就已生效。登记义务由出口经营者自行判断，"
               "判断错了没有官方替你兜底。本文拆四类登记情形、六种出海形态对号入座、最易漏的控制权变更，以及条例第39条前置材料"
               "与第43、44条真正罚则的口径差别。"))
B = dict(slug="20261102-najie-ai-search-summary-pay",
         title="AI 搜索按千次卖，被摘要的网页按什么收钱",
         tags=["著作权", "AI搜索", "内容许可"], ts="14:08",
         desc=("AI 搜索把网页内容摘成几百字直接回答用户，平台按千次调用收费，被摘要的内容方一分未得。本文拆四层：摘要在著作权法第10条"
               "信息网络传播权上的落点（替代标准）、第24条适当引用的三个要件为何难过、避风港第4条的「仅提供」分水岭与第11条直接获利，"
               "以及内容方今天能做的三件事——可举证的禁止声明、真做的技术措施、靠许可而非单打收钱。"))

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def card(art, is_main):
    href = f"/najie/blog/{art['slug']}.html" if is_main else f"./{art['slug']}.html"
    tags = "".join(f'<span class="tag">{t}</span> ' for t in art["tags"])
    return (f'<div class="article-card">\n'
            f'    <h2><a href="{href}">{art["title"]}</a></h2>\n'
            f'    <div class="meta">{tags} {DATE} · {OWNER}</div>\n'
            f'    <p>{art["desc"]}</p>\n'
            f'  </div>')

def insert_card(path, art, is_main):
    t = rd(path)
    if art["slug"] in t:
        print(f"  SKIP (already present): {os.path.relpath(path, REPO)}")
        return 0
    c = card(art, is_main)
    # 目标：插在「第一张日期 < 2026-11-02 的卡」之前；同日按 ts 倒序（B 在 A 前）
    pos = None
    for m in re.finditer(r'<div class="article-card">', t):
        start = m.start()
        seg = t[start:start + 1400]
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
        if dm and dm.group(1) < DATE:
            pos = start
            break
    if pos is None:
        raise SystemExit(f"未找到插入点 {path}")
    t2 = t[:pos] + c + "\n  " + t[pos:]
    assert t2.replace(c + "\n  ", "", 1) == t, "插入块外被改动"
    with open(path, "w", encoding="utf-8") as f:
        f.write(t2)
    print(f"  INSERTED {os.path.relpath(path, REPO)}  +1 card")
    return 1

print("=== najie index ===")
n = insert_card(os.path.join(REPO, "najie/blog/index.html"), A, False)
print("=== main index ===")
n += insert_card(os.path.join(REPO, "blog/index.html"), B, True)   # 14:08 先插（更靠前）
n += insert_card(os.path.join(REPO, "blog/index.html"), A, True)
print(f"total inserted={n}")

# ---------- articles.json ----------
print("=== articles.json ===")
ap = os.path.join(REPO, "articles.json")
ajax = rd(ap)
arr = json.loads(ajax)
have = {x.get("url") for x in arr}
entry = {"url": f"/najie/blog/{B['slug']}.html", "title": B["title"], "date": DATE, "site": "najie"}
if entry["url"] in have:
    print("  SKIP B already in articles.json")
else:
    arr.insert(0, entry)
    # 保持原生 indent=2
    with open(ap, "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  ADDED B -> len={len(arr)}")
print(f"  A present: {any(A['slug'] in (x.get('url') or '') for x in arr)}")
print(f"  B present: {any(B['slug'] in (x.get('url') or '') for x in arr)}")
