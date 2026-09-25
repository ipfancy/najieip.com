#!/usr/bin/env python3
"""0925 索引补卡：mili 品牌索引 + 主索引（今日新文零卡 → 补卡）
- v3 法：每次插入前重扫目标位置；插入串 = 卡块(无前导空格) + '\n  '
- 断言：t2.replace(card + "\n  ", "", 1) == t（防误改块外内容）
- 终验：卡片计数 +1、每卡以 <h2><a href= 起、div 深度以 ORIGIN 基线校准、markdown 星号 0
- mili 索引附博客 BlogPosting JSON-LD 条目（88 → 89）
用法：python3 gen-0925-index-cards.py [--apply]
"""
import json
import re
import shutil
import subprocess
import sys

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20260925-policy-cash-value-execution-2024-instance"
TITLE = "保单现金价值被划走28.5万！最少的一笔只有2970元"
DESC = ("2024年8月14日内蒙古海拉尔区法院对5人名下的保单逐笔扣划现金价值，最少的一笔只有2970元。"
        "本文拆清股权之外的这层财产：现金价值为何归投保人、按身份与按险种的双轴划分、"
        "江苏/北京/广东三地口径这几年的变化，以及收到冻结通知后的四个自救动作和三个最容易踩的误区。")
TAGS = ["保单现金价值", "强制执行", "保险避债"]
DATE = "2026-09-25"
APPLY = "--apply" in sys.argv

MILI_HREF = f"./{SLUG}.html"                       # 品牌索引：相对路径
MAIN_HREF = f"/mili/blog/{SLUG}.html"              # 主索引：绝对路径


def card(href: str) -> str:
    tags = "".join(f'<span class="tag">{t}</span>' for t in TAGS)
    return (f'<div class="article-card">\n'
            f'    <h2><a href="{href}">{TITLE}</a></h2>\n'
            f'    <div class="meta">{tags} {DATE} · 觅理律师事务所</div>\n'
            f'    <p>{DESC}</p>\n'
            f'  </div>')


def depth_hist(t: str):
    """从 <body 起统计 div 深度直方图 + 每深度下 article-card 计数"""
    body = t[t.find("<body"):]
    depth = 0
    hist = {}
    cards = {}
    for m in re.finditer(r"<(/?)div[^>]*>", body):
        closing = m.group(1) == "/"
        tag = m.group(0)
        if not closing:
            if 'class="article-card"' in tag:
                cards[depth] = cards.get(depth, 0) + 1
            depth += 1
            hist[depth] = hist.get(depth, 0) + 1
        else:
            depth -= 1
    return hist, cards, depth


def insert_card(path: str, c: str, label: str):
    t = open(path, encoding="utf-8").read()
    orig = t
    anchors = [m.start() for m in re.finditer(re.escape('<div class="article-card">'), t)]
    anchors = [a for a in anchors if a > t.find("<body")]
    if not anchors:
        print(f"  ❌ {label}: 未找到 article-card 锚点")
        return None
    pos = anchors[0]
    t2 = t[:pos] + c + "\n  " + t[pos:]
    if t2.replace(c + "\n  ", "", 1) != orig:
        print(f"  ❌ {label}: 块外内容被改动断言失败，放弃")
        return None
    n_before = len(re.findall(r'class="article-card"', orig))
    n_after = len(re.findall(r'<div class="article-card">', t2))
    ok_first = t2[t2.find("<body"):].find(SLUG) < t2[t2.find("<body"):].find("article-card") + 200
    hist, cards, final_depth = depth_hist(t2)
    base_hist, base_cards, base_depth = depth_hist(orig)
    print(f"  {label}")
    print(f"     卡片计数 {n_before} → {len(re.findall(chr(60)+'div class=.article-card.', t2))}（class 出现 {n_after} 次）")
    print(f"     div 深度基线 {base_hist} | 修改后 {hist} | 结束时深度 {final_depth}（基线 {base_depth}）")
    print(f"     卡片所在深度 基线={base_cards} 修改后={cards}")
    print(f"     新卡位于 body 首卡: {ok_first}")
    malformed = [m for m in re.findall(r'<div class="article-card">(.{0,40})', t2, re.S) if not m.lstrip().startswith("<h2><a href=")]
    print(f"     malformed 卡块: {len(malformed)} | markdown 星号: {t2.count('**')}")
    # 主索引/品牌索引首个日期单调性：新卡日期 >= 其后首卡日期
    dates = re.findall(r'(\d{4}-\d{2}-\d{2})', t2[t2.find("<body"):])
    print(f"     前 3 个日期: {dates[:3]}")
    good = (not malformed and t2.count("**") == 0 and final_depth == 0
            and len(re.findall(r'class="article-card"', t2)) == n_before + 1)
    if not good:
        print(f"  ❌ {label}: 终验未过")
        return None
    if APPLY:
        shutil.copy(path, path + ".bak-20260925")
        open(path, "w", encoding="utf-8").write(t2)
        print(f"     ✅ 已写入 {label}")
    return t2


print("=== 1. mili 品牌索引补卡 ===")
insert_card(f"{REPO}/mili/blog/index.html", card(MILI_HREF), "mili/blog/index.html")

print("\n=== 2. 主索引补卡 ===")
insert_card(f"{REPO}/blog/index.html", card(MAIN_HREF), "blog/index.html")

print("\n=== 3. mili 索引 BlogPosting JSON-LD 补条目 ===")
p = f"{REPO}/mili/blog/index.html"
t = open(p, encoding="utf-8").read()
blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S))
target = None
for m in blocks:
    try:
        d = json.loads(m.group(1))
    except Exception:
        continue
    if isinstance(d, dict) and "blogPost" in d:
        target = (m, d)
        break
if not target:
    print("  ❌ 未找到 blogPost JSON-LD")
else:
    m, d = target
    entry = {"@type": "BlogPosting", "headline": TITLE,
             "url": f"https://najieip.com/mili/blog/{SLUG}.html",
             "datePublished": DATE, "description": DESC}
    have = [e.get("url") for e in d["blogPost"]]
    if any(SLUG in str(u) for u in have):
        print("  已存在该条目，跳过")
    else:
        n0 = len(d["blogPost"])
        d["blogPost"].insert(0, entry)
        new_block = json.dumps(d, ensure_ascii=False)
        t2 = t[: m.start(1)] + new_block + t[m.end(1):]
        try:
            json.loads(new_block)
            print(f"  blogPost 条数 {n0} → {len(d['blogPost'])}；JSON 自检 PASS")
        except Exception as e:
            print("  ❌ JSON 自检失败", e)
            t2 = None
        if t2 and APPLY:
            open(p, "w", encoding="utf-8").write(t2)
            print("  ✅ JSON-LD 已写入")
        elif t2:
            print("  (dry-run)")
