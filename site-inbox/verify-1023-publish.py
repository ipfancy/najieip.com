#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 1023 发布前校验：JSON-LD / 结构 / 引号 / 时效数字 / 主体归属 / 索引 / json / sitemap"""
import json, re, sys, os
import xml.etree.ElementTree as ET

REPO = "/mnt/c/Users/zigan/najieip-site"
PAGES = [
    ("najie/blog/20261023-najie-trademark-law-70-days.html", "najie",
     ["北京纳杰知识产权代理有限公司", "商标"], ["爱普纳杰", "觅理"]),
    ("aipunajie/blog/20261023-aipunajie-overseas-patent-fto.html", "aipunajie",
     ["北京爱普纳杰专利代理事务所", "专利"], ["纳杰知识产权", "北京纳杰", "觅理"]),
]
fail = 0


def chk(cond, msg):
    global fail
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fail += 1


for rel, cite, must, forbid in PAGES:
    p = os.path.join(REPO, rel)
    t = open(p, encoding="utf-8").read()
    print("===", rel)
    chk(os.path.getsize(p) > 8000, "size %d bytes" % os.path.getsize(p))
    # JSON-LD
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    chk(len(blocks) == 2, "JSON-LD blocks = %d (want 2)" % len(blocks))
    types = []
    for b in blocks:
        try:
            d = json.loads(b)
            types.append(d.get("@type"))
        except Exception as e:
            chk(False, "JSON-LD 解析失败: %s" % e)
    chk(types == ["Article", "BreadcrumbList"], "JSON-LD types = %s" % types)
    art = json.loads(blocks[0])
    chk(art["datePublished"] == "2026-10-23", "datePublished = %s" % art["datePublished"])
    chk(art["publisher"]["name"] == ("北京纳杰知识产权代理有限公司" if cite == "najie" else "北京爱普纳杰专利代理事务所"),
        "publisher = %s" % art["publisher"]["name"])
    # structure
    chk(t.count("<h1>") == 1, "h1 count = %d" % t.count("<h1>"))
    chk(t.count("<div") == t.count("</div>"), "div balance %d/%d" % (t.count("<div"), t.count("</div>")))
    chk("<article>" in t and "</article>" in t, "article wrapper")
    # 时效（仅商标法一文含倒计时）
    chk("72天" not in t, "无过期「72天」")
    if cite == "najie":
        chk(t.count("70天") >= 4, "「70天」出现 %d 次" % t.count("70天"))
    else:
        chk("FTO" in t, "含 FTO 关键词")
    # 引号规范：正文 p 内不应有 ASCII 双引号
    body = t.split("<article>", 1)[1]
    ascii_quotes = re.findall(r"<p>[^<]*\"[^<]*</p>", body)
    chk(not ascii_quotes, "正文无 ASCII 直引号（命中 %d）" % len(ascii_quotes))
    chk("“" in body and "”" in body, "中文弯引号已就位")
    # 主体归属：剔除站点级页脚模板后再查异主体
    seg = re.sub(r"<footer>.*?</footer>", "", body, flags=re.S)
    seg = seg.replace("© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所", "")
    for w in must:
        chk(w in seg, "含主体关键词「%s」" % w)
    for w in forbid:
        chk(w not in seg, "正文不含异主体「%s」" % w)
    # 图片
    chk(("/img/%s.png" % os.path.basename(rel).replace(".html", "")) in t, "封面图引用存在")
    chk("AI 辅助生成" in t, "AI 生成明示")

print("=== 索引卡片 ===")
for rel, slug, href in [
    ("najie/blog/index.html", "20261023-najie-trademark-law-70-days", "./20261023-najie-trademark-law-70-days.html"),
    ("aipunajie/blog/index.html", "20261023-aipunajie-overseas-patent-fto", "./20261023-aipunajie-overseas-patent-fto.html"),
    ("blog/index.html", "najie/blog/20261023-najie-trademark-law-70-days", "/najie/blog/20261023-najie-trademark-law-70-days.html"),
    ("blog/index.html", "aipunajie/blog/20261023-aipunajie-overseas-patent-fto", "/aipunajie/blog/20261023-aipunajie-overseas-patent-fto.html"),
]:
    t = open(os.path.join(REPO, rel), encoding="utf-8").read()
    pos = t.find("<!--")  # noop
    first_card = t.find('<div class="article-card">')
    idx = t.find('href="%s"' % href)
    chk(idx != -1, "%s 收录 %s" % (rel, href))
    chk(0 < idx and idx - first_card < 900, "%s 新卡片位于列表顶部（偏移 %d）" % (rel, idx - first_card))
    chk(t.count("<div") == t.count("</div>"), "%s div 平衡 %d/%d" % (rel, t.count("<div"), t.count("</div>")))

print("=== articles.json ===")
d = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
chk(len(d) == 250, "entries = %d" % len(d))
urls = [x.get("url") for x in d]
chk("/najie/blog/20261023-najie-trademark-law-70-days.html" in urls, "najie 条目已收录")
chk("/aipunajie/blog/20261023-aipunajie-overseas-patent-fto.html" in urls, "aipunajie 条目已收录")
chk(len(urls) == len(set(urls)), "URL 无重复")
miss = [x for x in d if not x.get("title") or not x.get("date") or not x.get("url")]
chk(not miss, "字段完整（缺字段 %d 条）" % len(miss))
newsite = [x for x in d[:2] if x.get("site") in ("najie", "aipunajie")]
chk(len(newsite) == 2, "新增条目 site 字段正确")

print("=== sitemap.xml ===")
tree = ET.parse(os.path.join(REPO, "sitemap.xml"))
root = tree.getroot()
ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
locs = [e.text for e in root.iter(ns + "loc")]
chk(len(locs) == 324, "loc = %d" % len(locs))
chk("https://najieip.com/najie/blog/20261023-najie-trademark-law-70-days.html" in locs, "najie URL 入 sitemap")
chk("https://najieip.com/aipunajie/blog/20261023-aipunajie-overseas-patent-fto.html" in locs, "aipunajie URL 入 sitemap")
chk(len(locs) == len(set(locs)), "sitemap 无重复")

print("\n%s (%d failures)" % ("全部通过" if fail == 0 else "存在问题", fail))
sys.exit(1 if fail else 0)
