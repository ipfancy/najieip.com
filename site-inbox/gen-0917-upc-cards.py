#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen-0917-upc-cards.py — 把 20260917-upc-injunction-counterattack 补进两个博客索引

背景（2026-09-17 巡检实测）：文章页线上 200、self-canonical，但
  · mili/blog/index.html 无卡片、Blog JSON-LD 的 blogPost 数组无该篇
  · blog/index.html（主索引）无卡片
即「已发布但任何索引都点不到」。

规则（沿用 v3「插入前重扫位置」+ 降序单调）：
  · 幂等：目标路径已出现即跳过该文件
  · 插入点 = 第一张日期 <= 2026-09-17 的卡片之前（保持日期非递增）
  · 校验：卡片数 +N、div 深度归零、每卡以 <h2><a href= 起、日期单调、无 markdown 泄漏

用法：python3 gen-0917-upc-cards.py [--apply]
"""
import os, re, sys, json

SITE = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260917-upc-injunction-counterattack"
DATE = "2026-09-17"
TITLE = "禁令突袭反被撤销：出海企业3招反打"
SUMMARY = ("2025年9月IFA展会现场，科沃斯以单方命令让石头科技展品被扣；UPC杜塞尔多夫地方分庭于同年12月19日"
           "认定该命令违法作出、溯及既往全额撤销，2026年3月16日上诉法院维持原判并定性为程序滥用。败因只有一条："
           "申请时未披露己方代理人已在亚马逊买到涉案产品。附保护函、限缩检查、复审三步反打要点。")
DESC_LD = SUMMARY
TAGS_MILI = ["涉外知识产权", "UPC", "临时禁令"]
TAGS_MAIN = ["专利诉讼", "UPC", "程序滥用"]
URL_LD = "https://najieip.com/mili/blog/%s.html" % SLUG
CARD_RE = re.compile(r'<div class="article-card">')
DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2}) ·')
H2_RE = re.compile(r'<h2><a href=')


def card_block(href, tags):
    t = "".join('<span class="tag">%s</span>' % x for x in tags)
    return ('<div class="article-card">\n'
            '    <h2><a href="%s">%s</a></h2>\n'
            '    <div class="meta">%s %s · 觅理律师事务所</div>\n'
            '    <p>%s</p>\n'
            '  </div>' % (href, TITLE, t, DATE, SUMMARY))


def insert_card(t, href, tags):
    """在第一张日期 <= DATE 的卡片之前插入。每轮重扫位置，绝不复用旧偏移。"""
    blocks = [(m.start(), card_date(t, m.start())) for m in CARD_RE.finditer(t)]
    assert blocks, "未找到任何 article-card"
    pos = None
    for start, d in blocks:
        if d and d <= DATE:
            pos = start
            break
    if pos is None:
        pos = blocks[-1][0]
    return t[:pos] + card_block(href, tags) + "\n  " + t[pos:], len(blocks) + 1


def card_date(t, start):
    m = DATE_RE.search(t[start:start + 700])
    return m.group(1) if m else None


def div_depth_ok(t):
    depth = 0
    for m in re.finditer(r'<(/?)div[ >]', t):
        if m.group(1):
            depth -= 1
            if depth < 0:
                return False, "栈空仍闭合"
        else:
            depth += 1
    return depth == 0, ("depth=%d" % depth)


def verify(t, label, expect_cards):
    depth_ok, msg = div_depth_ok(t)
    assert depth_ok, "%s div 不配平: %s" % (label, msg)
    n = len(CARD_RE.findall(t))
    assert n == expect_cards, "%s 卡片数 %d != %d" % (label, n, expect_cards)
    malformed = 0
    for m in CARD_RE.finditer(t):
        if not t[m.end():m.end() + 60].lstrip().startswith("<h2><a href="):
            malformed += 1
    assert malformed == 0, "%s 畸形卡 %d 张" % (label, malformed)
    # 全量单调性在这两个遗留索引上本就不成立（老卡由多方插入，9-14 后面还挂着 9-15），
    # 故只校验「新卡之前的卡日期均 >= DATE」——即插入点本身没插错位。
    starts = [m.start() for m in CARD_RE.finditer(t)]
    hit = [i for i, s in enumerate(starts) if SLUG in t[s:s + 400]]
    assert hit, "%s 未找到新卡" % label
    i_new = hit[0]
    pre = [card_date(t, s) for s in starts[:i_new]]
    bad = [d for d in pre if d and d < DATE]
    assert not bad, "%s 新卡前存在更早日期 %s" % (label, bad[:5])
    assert t.count("**") == 0, "%s markdown 泄漏" % label
    assert t.count("https://***") == 0, "%s 脱敏污染" % label
    added = [d for d in pre if d == DATE]
    return len(pre) - len([d for d in pre if not d]), len(added) + 1


def main():
    apply = "--apply" in sys.argv
    plan = [("mili/blog/index.html", "./%s.html" % SLUG, TAGS_MILI),
            ("blog/index.html", "/mili/blog/%s.html" % SLUG, TAGS_MAIN)]
    out = {}
    for rel, href, tags in plan:
        p = os.path.join(SITE, rel)
        t = open(p, encoding="utf-8").read()
        n_before = len(CARD_RE.findall(t))
        if SLUG in t:
            print("⏭ %s 已含该文（%d 卡）— 跳过" % (rel, n_before))
            out[rel] = t
            continue
        t2, exp = insert_card(t, href, tags)
        n, nd = verify(t2, rel, exp)
        print("✅ %s 卡片 %d → %d（新卡居第 %d 位，前有 %d 张带日期）" % (rel, n_before, exp, nd, n))
        out[rel] = t2

    # mili 索引内嵌 Blog JSON-LD 的 blogPost 数组（新条目置顶）
    mrel = "mili/blog/index.html"
    t = out.get(mrel)
    if t is not None:
        i = t.find('"blogPost": [')
        if i == -1:
            print("⏭ mili JSON-LD 未含 blogPost 数组 — 跳过")
        elif URL_LD in t:
            print("⏭ mili JSON-LD 已含该文 — 跳过")
        else:
            entry = json.dumps({"@type": "BlogPosting", "headline": TITLE, "url": URL_LD,
                                "datePublished": DATE, "description": DESC_LD}, ensure_ascii=False)
            # 锚点只到 '[' 为止，保留原首条目的开头 '{'（吃掉了就会得到 [{新条, "@type"... 非法 JSON）
            anchor = '"blogPost": ['
            t = t[:i + len(anchor)] + entry + ", " + t[i + len(anchor):]
            ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
            for b in ld:
                json.loads(b)  # 解析失败即抛错
            print("✅ mili JSON-LD blogPost 数组首插 1 条（%d 个 JSON-LD 块解析通过）" % len(ld))
            out[mrel] = t

    if not apply:
        print("[dry-run] 未写入。加 --apply 执行。")
        return
    for rel, t in out.items():
        open(os.path.join(SITE, rel), "w", encoding="utf-8").write(t)
    print("✅ 已写入 %d 个索引" % len(out))


if __name__ == "__main__":
    main()
