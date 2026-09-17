#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quarantine-0917-articles-json.py — articles.json 剔除「无页面」条目（可逆隔离，不删数据）

背景（2026-09-17 巡检实测）：
  · index.html 前端 `fetch('/articles.json')` 后 `slice(0, 6)` 渲染首页最新 6 篇
  · articles.json 现 181 条，其中 **50 条指向本地不存在的文件**（47 条 {机构}/blog/ + 3 条 /site-inbox/），
    线上实测 47/47 = HTTP 404；按 date 降序，第一条无页面条目已在第 **10** 位
    → 再上线 4 篇即被推入首页卡片区，形成**顾客可见的首页死链**
  · 参照 site-inbox/NOTE-20260917-articles-json-bogus-entries.md 的「推荐 A」

做法（非破坏）：
  1) 50 条移入 articles-quarantine-20260917.json（保留 url/title/description/date/site + reason）
  2) articles.json 只保留本地存在文件的条目，保持原有字段顺序与缩进风格
  3) 若 go/no-go 决定给这 47 篇建规范页 → 从隔离文件一键还原即可

用法：python3 quarantine-0917-articles-json.py [--apply]
"""
import json, os, sys

SITE = os.path.expanduser("~/wiki/najieip-verify")
AJ = os.path.join(SITE, "articles.json")
QJ = os.path.join(SITE, "articles-quarantine-20260917.json")


def main():
    apply = "--apply" in sys.argv
    raw = open(AJ, encoding="utf-8").read()
    arts = json.loads(raw)

    keep, moved = [], []
    for a in arts:
        u = a.get("url", "")
        p = os.path.join(SITE, u.lstrip("/"))
        if u and os.path.exists(p):
            keep.append(a)
        else:
            reason = ("工作区路径（/site-inbox/）不应进站点数据源" if "/site-inbox/" in u
                      else "页面不存在（{机构}/blog/ 规范路径从未建页；线上 404）" if u.startswith(("/mili/", "/najie/", "/aipunajie/"))
                      else "页面不存在")
            moved.append(dict(a, _quarantine_reason=reason))

    print("articles.json: %d → %d（隔离 %d）" % (len(arts), len(keep), len(moved)))
    by = {}
    for m in moved:
        by.setdefault(m["_quarantine_reason"], []).append(m["url"])
    for r, us in by.items():
        print("  · %-46s %d 条" % (r, len(us)))
    print("  样本:", moved[0]["url"] if moved else "-")

    # 首页渲染面复核
    s = sorted(keep, key=lambda a: a.get("date", ""), reverse=True)
    print("  清理后首页前 6 条（全部有页面）:")
    for a in s[:6]:
        print("    %s  %s" % (a.get("date"), a["url"]))

    if not apply:
        print("[dry-run] 未写入。加 --apply 执行。")
        return

    with open(QJ, "w", encoding="utf-8") as f:
        json.dump(moved, f, ensure_ascii=False, indent=1)
    # articles.json 原生 indent=2：沿用原缩进，diff 才是「纯删除」
    with open(AJ, "w", encoding="utf-8") as f:
        json.dump(keep, f, ensure_ascii=False, indent=2)
    print("✅ 已写 %s（%d 条）" % (os.path.basename(QJ), len(moved)))
    print("✅ 已写 %s（%d 条）" % (os.path.basename(AJ), len(keep)))
    # 复核：磁盘上每条都能找到文件
    bad = [a for a in json.load(open(AJ, encoding="utf-8"))
           if not os.path.exists(os.path.join(SITE, a["url"].lstrip("/")))]
    print("✅ 复核：无页面条目残留 = %d" % len(bad))


if __name__ == "__main__":
    main()
