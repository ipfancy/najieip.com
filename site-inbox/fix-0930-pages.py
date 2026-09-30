#!/usr/bin/env python3
"""0930 裸发布畸形页修复（第5/6例）— mili/blog 两篇 20260930 文章
问题：pipeline 裸发布，缺 description/keywords/og/twitter/canonical/JSON-LD/beacon，
      nav 指向 "/" ，正文裸 <br> 分隔。
处置：仅注入 head 元数据 + beacon，nav 归位 /mili/，剔裸 <br>；正文文字一字不改（逐段断言）。
用法：python3 fix-0930-pages.py [--apply]
"""
import json
import re
import sys
import shutil
from html import unescape

REPO = "/mnt/c/Users/zigan/najieip-site"
DATE = "2026-09-30"
BEACON = "<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"c80241f3caa4e708a12ed93baec1bde\"}'></script>"
OGIMG = "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"
SITE = "觅理律所"
PUBLISHER = "北京觅理律师事务所"

PAGES = {
    "20260930-ecommerce-only-refund-weiquan": {
        "title": "8.59元香菜遭“仅退款”，商家千里讨回：电商商家维权的症结在哪",
        "desc": "江苏徐州商家驱车往返约1000公里、花掉约1000元油费过路费，只为取回一单8.59元的香菜——买家以“香菜太老”为由申请仅退款。本文从《民法典》第610条、第566条与《消费者权益保护法》第24条拆解“仅退款不退货”的法律性质，分析标的额与维权成本倒挂的三层症结，并给出小额诉讼、证据固定、批量维权等可落地的维权路径。",
        "keywords": "仅退款,电商商家维权,商家权益,民法典610条,民法典566条,小额诉讼,网络交易平台规则监督管理办法,恶意退款,不当得利",
    },
    "20260930-drunk-passenger-drowning-liability": {
        "title": "醉酒乘客下车溺亡索赔30万被驳回：过错责任的法律边界",
        "desc": "男子李某醉酒乘车途中坚持下车，司机停车放行并通知了下单人，李某下车后溺亡，家属起诉司机、平台与河道管理方索赔30万元，天津静海法院一审驳回全部诉求。本文从《民法典》第1165条过错责任、第823条承运人免责例外出发，拆解“通知下单人”这一关键细节，说明为什么出了事不一定有人赔。",
        "keywords": "过错责任,侵权责任,承运人责任,民法典1165条,民法典823条,人身损害,安全保障义务,责任边界,免责事由",
    },
}


def norm(s):
    """归一去标签与空白，用于逐段文字一致性断言"""
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s)
    return re.sub(r"\s+", "", s)


APPLY = "--apply" in sys.argv
allok = True

for slug, meta in PAGES.items():
    path = f"{REPO}/mili/blog/{slug}.html"
    src = open(path, encoding="utf-8").read()
    url = f"https://najieip.com/mili/blog/{slug}.html"
    title = meta["title"]
    desc = meta["desc"]

    # --- 记录修复前正文文字（逐段） ---
    art_before = re.search(r"<article>(.*?)</article>", src, re.S).group(1)
    paras_before = [norm(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", art_before, re.S) if p.strip()]
    h2_before = len(re.findall(r"<h2", src))

    ld_article = {
        "@context": "https://schema.org", "@type": "Article", "headline": title,
        "description": desc,
        "author": {"@type": "Person", "name": "何自刚", "jobTitle": "知识产权律师",
                   "worksFor": {"@type": "LegalService", "name": PUBLISHER, "url": "https://najieip.com/mili/"}},
        "publisher": {"@type": "Organization", "name": PUBLISHER},
        "image": OGIMG, "datePublished": DATE, "dateModified": DATE,
        "mainEntityOfPage": url, "url": url,
    }
    ld_crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"},
            {"@type": "ListItem", "position": 2, "name": "觅理博客", "item": "https://najieip.com/mili/blog/"},
            {"@type": "ListItem", "position": 3, "name": title},
        ],
    }
    block = f"""{BEACON}
<meta name="description" content="{desc}">
<meta name="keywords" content="{meta['keywords']}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:image" content="{OGIMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="canonical" href="{url}">
<script type="application/ld+json">{json.dumps(ld_article, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld_crumb, ensure_ascii=False)}</script>"""

    out = src
    # 1) 在 stylesheet link 后注入
    m = re.search(r'<link rel="stylesheet"[^>]*>', out)
    assert m, "stylesheet link not found"
    out = out[:m.end()] + "\n" + block + out[m.end():]
    # 2) nav 归位
    out = out.replace('<nav><a href="/">← 首页</a></nav>', '<nav><a href="/mili/">← 首页</a></nav>')
    # 3) 剔裸 <br>（独占一行的分隔用）
    out = re.sub(r"^[ \t]*<br>[ \t]*\n", "", out, flags=re.M)

    # --- 终验 ---
    checks = []
    checks.append(("h1 == 1", len(re.findall(r"<h1", out)) == 1))
    checks.append((f"h2 保持 {h2_before}", len(re.findall(r"<h2", out)) == h2_before))
    checks.append(("ld+json == 2", out.count("application/ld+json") == 2))
    checks.append(("og:title/url/image 齐", all(k in out for k in ("og:title", "og:url", "og:image"))))
    checks.append(("canonical 存在", 'rel="canonical"' in out))
    checks.append(("description > 80", len(desc) > 80))
    checks.append(("无裸 <br>", "<br>" not in out))
    checks.append(("nav 已归位", 'href="/mili/"' in out))
    art_after = re.search(r"<article>(.*?)</article>", out, re.S).group(1)
    paras_after = [norm(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", art_after, re.S) if p.strip()]
    checks.append((f"段落数不变 ({len(paras_before)})", len(paras_after) == len(paras_before)))
    checks.append(("正文逐段文字 0 差异", paras_after == paras_before))
    checks.append(("schema 未脱敏", out.count("https://schema.org") == 2))

    print(f"\n===== {slug} =====")
    for name, ok in checks:
        allok &= ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if paras_after != paras_before:
        for i, (a, b) in enumerate(zip(paras_before, paras_after)):
            if a != b:
                print(f"    diff@{i}: {a[:60]} != {b[:60]}")
    print(f"  字节 {len(src.encode())} -> {len(out.encode())}")

    if APPLY and allok:
        shutil.copy(path, path + ".bak-20260930")
        open(path, "w", encoding="utf-8").write(out)
        print("  ✅ 已写入")

if not APPLY:
    print("\n(dry-run；加 --apply 生效)")
if APPLY and not allok:
    print("\n❌ 有断言未过")
    sys.exit(1)
