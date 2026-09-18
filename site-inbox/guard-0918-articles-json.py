#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guard-0918-articles-json.py — articles.json 卫生守卫（幂等，可每日跑）

规则（来自 NOTE-20260917-articles-json-bogus-entries.md）：
  1) url 必须指向仓库内**真实存在**的文件 —— 不存在 = 无页面条目
  2) url 必须落在品牌目录白名单：/najie/blog/ /mili/blog/ /aipunajie/blog/（含 /en/ /fr/ 子路径）
     —— 工作区路径（/site-inbox/...）与 /articles/ 老路径一律不合格
  3) 违例条目移入 articles-quarantine-<date>.json（可逆），articles.json 只留合格条目
  4) 保持原生 indent=2，避免整档重写撞并发写方

用法：
  python3 site-inbox/guard-0918-articles-json.py --check   # 只报（默认）
  python3 site-inbox/guard-0918-articles-json.py --apply   # 隔离并写回
"""
import json
import os
import sys
from datetime import date

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
APPLY = "--apply" in sys.argv
TODAY = date.today().isoformat()

AJ = "articles.json"
QF = "articles-quarantine-%s.json" % TODAY.replace("-", "")
WHITELIST = ("/najie/blog/", "/mili/blog/", "/aipunajie/blog/",
             "/en/blog/", "/fr/blog/")

d = json.load(open(AJ, encoding="utf-8"))
items = d if isinstance(d, list) else d.get("articles", [])

good, bad = [], []
for it in items:
    u = str(it.get("url", ""))
    p = u.lstrip("/")
    reasons = []
    if not u.endswith(".html"):
        reasons.append("非 .html")
    if not any(u.startswith(w) for w in WHITELIST):
        reasons.append("路径不在品牌白名单")
    if not os.path.exists(p):
        reasons.append("文件不存在")
    if reasons:
        e = dict(it)
        e["_quarantine_reason"] = " / ".join(reasons)
        e["_quarantined_at"] = TODAY
        bad.append(e)
    else:
        good.append(it)

print("articles.json: 总 %d | 合格 %d | 违例 %d" % (len(items), len(good), len(bad)))
from collections import Counter
print("  违例原因分布:", dict(Counter(
    r for b in bad for r in b["_quarantine_reason"].split(" / "))))

# 首页曝光位次（index.html: fetch('/articles.json').slice(0,6)）
top = sorted(good, key=lambda x: str(x.get("date", "")), reverse=True)[:6]
print("  首页 slice(0,6) 位次（全部有页面才安全）:")
for i, it in enumerate(top, 1):
    print("    %d %s %s" % (i, it.get("date"), it.get("url")))
assert all(os.path.exists(str(it.get("url", "")).lstrip("/")) for it in top), \
    "首页 top6 存在无页面条目 → 必须修复"

if APPLY:
    # 合并已有隔离档（累积，去重）
    merged = {}
    if os.path.exists(QF):
        old = json.load(open(QF, encoding="utf-8"))
        for e in (old if isinstance(old, list) else old.get("articles", [])):
            merged[e.get("url")] = e
    for e in bad:
        merged[e["url"]] = e
    with open(QF, "w", encoding="utf-8") as f:
        json.dump(sorted(merged.values(), key=lambda x: str(x.get("date", "")), reverse=True),
                  f, ensure_ascii=False, indent=2)
    print("  隔离档写入 %s（累计 %d 条）" % (QF, len(merged)))
    with open(AJ, "w", encoding="utf-8") as f:
        json.dump(good, f, ensure_ascii=False, indent=2)
    json.load(open(AJ, encoding="utf-8"))
    print("  articles.json 写回 %d 条（JSON 自检通过）" % len(good))
else:
    print("  (--check 模式，未写盘)")
