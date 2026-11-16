#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 1116：主索引补 najie AI 图权属卡 + articles.json 补条目 + 隔离 2 条 stub"""
import os, re, json, sys, shutil, html

REPO = "/Users/ziganghe/wiki/najieip-verify"
MAIN = os.path.join(REPO, "blog", "index.html")
APPLY = "--apply" in sys.argv

SLUG = "20261116-najie-ai-image-copyright-three-layers"
TITLE = "图是我花钱做的，著作权为什么可能不在我名下——AI生成图片的权属要拆三层看"
DATE = "2026-11-16"
TAG = "纳杰"
ORG = "北京纳杰知识产权代理有限公司"
HREF = f"/najie/blog/{SLUG}.html"
DESC = ("AI生成图片的权属要拆三层看：付款不产生作者身份，委托合同未约定归属时著作权默认在受托人；"
        "AI把「受托人」拆成模型方、操作方与出资方三个人；法院数的不是「像不像画」，"
        "而是人在生成过程中做了多少选择。本文用《著作权法》第十一、十八、十九、二十七条与"
        "北京互联网法院、磐石、开福、张家港四组裁判，给出采购四个条款与自己做图的三样留痕。")

t = open(MAIN, encoding="utf-8").read()
report = {}

# ---- 1) 主索引补卡 ----
if HREF in t:
    report["main_card"] = "already"
else:
    # 逐卡扫描：div 深度配对取卡块 + 卡内 meta 取日期
    def blocks(txt):
        out = []
        for m in re.finditer(r'<div class="article-card">', txt):
            i = m.start()
            depth = 0
            j = i
            while j < len(txt):
                if txt.startswith("<div", j):
                    depth += 1
                    j += 4
                elif txt.startswith("</div>", j):
                    depth -= 1
                    j += 6
                    if depth == 0:
                        break
                else:
                    j += 1
            blk = txt[i:j]
            dm = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
            out.append((i, j, blk, dm.group(1) if dm else ""))
        return out

    card = (f'<div class="article-card">\n'
            f'    <h2><a href="{HREF}">{TITLE}</a></h2>\n'
            f'    <div class="meta"><span class="tag">{TAG}</span> {DATE} · {ORG}</div>\n'
            f'    <p>{DESC}</p>\n'
            f'  </div>')

    bl = blocks(t)
    target = None
    for i, j, blk, d in bl:
        if d and d < DATE:
            target = i
            break
    if target is None:
        raise SystemExit("找不到插入点")
    t2 = t[:target] + card + "\n  " + t[target:]

    # 校验
    n_before = len(re.findall(r'<div class="article-card">', t))
    n_after = len(re.findall(r'<div class="article-card">', t2))
    assert n_after == n_before + 1, (n_before, n_after)
    assert t2.replace(card + "\n  ", "", 1) == t, "插入块外被改动"
    # div 配平
    op, cl = len(re.findall(r'<div[\s>]', t2)), t2.count("</div>")
    op0, cl0 = len(re.findall(r'<div[\s>]', t)), t.count("</div>")
    report["div"] = f"{op0}/{cl0} -> {op}/{cl}"
    assert (op - op0) == (cl - cl0) and (op - op0) >= 1, report["div"]
    # 每卡以 h2 起
    mal = [1 for x in re.findall(r'<div class="article-card">(.*?)</div>\s*(?=<div class="article-card">|</div>)', t2, re.S) if '<h2><a href=' not in x]
    report["malformed"] = len(mal)
    # 深度直方图（基线校准）
    def hist(txt):
        h = {}
        for m in re.finditer(r'<div class="article-card">', txt):
            body = txt[txt.find("<body"):m.start()]
            d = len(re.findall(r'<div[\s>]', body)) - body.count("</div>")
            h[d] = h.get(d, 0) + 1
        return h
    h0, h1 = hist(t), hist(t2)
    report["hist"] = f"{h0} -> {h1}"
    delta = {k: h1.get(k, 0) - h0.get(k, 0) for k in set(h0) | set(h1)}
    assert sum(v for v in delta.values() if v > 0) - sum(-v for v in delta.values() if v < 0) == 0 or sum(delta.values()) == 1, delta
    assert all(v >= 0 for v in delta.values()), delta
    assert t2.count("**") == 0
    report["main_card"] = f"added ({n_before}->{n_after})"

# ---- 2) articles.json 补条目 ----
aj_path = os.path.join(REPO, "articles.json")
aj = json.load(open(aj_path, encoding="utf-8"))
if any(i.get("url") == HREF for i in aj):
    report["articles_json"] = "already"
else:
    entry = {"url": HREF, "title": TITLE, "date": DATE, "site": "najie"}
    idx = 0
    for k, it in enumerate(aj):
        if it.get("date", "") >= DATE:
            idx = k + 1
    aj.insert(idx, entry)
    report["articles_json"] = f"inserted at {idx} (total {len(aj)})"

# ---- 3) 隔离 stub 条目 ----
stubs = ["/najie/blog/20261010-mili-aigc-trade-secret-two-leaks.html",
         "/aipunajie/blog/20260804-ic-layout-design-regulations.html"]
qpath = os.path.join(REPO, "articles-quarantine-20261116.json")
q = []
if os.path.exists(qpath):
    q = json.load(open(qpath, encoding="utf-8"))
qurls = {e.get("url") for e in q}
quarantined = []
for s in stubs:
    for it in list(aj):
        if it.get("url") == s:
            aj.remove(it)
            if s not in qurls:
                it2 = dict(it)
                it2["_quarantine_reason"] = "无落地页面/stub（2026-11-16 守卫）"
                q.append(it2)
                qurls.add(s)
            quarantined.append(s)
report["quarantined"] = quarantined
report["aj_total"] = len(aj)

print("APPLY" if APPLY else "DRY", json.dumps(report, ensure_ascii=False, indent=1))

if APPLY:
    open(MAIN, "w", encoding="utf-8").write(t2)
    with open(aj_path, "w", encoding="utf-8") as f:
        json.dump(aj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("WRITTEN")
