#!/usr/bin/env python3
# 0921 终验：文章页 + najie 品牌索引 + 主索引（独立于生成脚本的结构断言）
import json
import os
import re
from collections import Counter

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
SLUG = "20260921-us-trademark-sanction-defense-window"
ok = True


def chk(name, cond, extra=""):
    global ok
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))
    if not cond:
        ok = False


def depth_scan(body):
    depth = 0
    under = 0
    dd2 = 0
    for m in re.finditer(r"<(/?)div[^>]*>", body):
        if m.group(1) == "/":
            if depth == 0:
                under += 1
            else:
                depth -= 1
        else:
            depth += 1
            if depth == 2 and body[m.start():m.start() + 31].startswith('<div class="article-card"'):
                dd2 += 1
    return depth, under, dd2


print("### 1. 文章页 najie/blog/%s.html" % SLUG)
t = open("najie/blog/%s.html" % SLUG, encoding="utf-8").read()
chk("字节数 > 6000", os.path.getsize("najie/blog/%s.html" % SLUG) > 6000, str(os.path.getsize("najie/blog/%s.html" % SLUG)))
chk("h1 恰 1 个", t.count("<h1>") == 1 and t.count("</h1>") == 1)
chk("h2 4 个", t.count("<h2>") == 4, str(t.count("<h2>")))
chk("有 <style>", "<style>" in t and len(re.search(r"<style>(.*?)</style>", t, re.S).group(1)) > 800)
ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
chk("ld+json 2 块可解析", len(ld) == 2 and all(json.loads(b) for b in ld), str(len(ld)))
types = [json.loads(b)["@type"] for b in ld]
chk("ld 类型 Article+Breadcrumb", set(types) == {"Article", "BreadcrumbList"}, str(types))
chk("schema.org ×2", t.count("https://schema.org") == 2)
chk("无 *** 污染", "https://***" not in t)
chk("无 ** 泄漏", t.count("**") == 0)
chk("无 frontmatter", "ai_smell" not in t and "检索词块" not in t and "合集:" not in t)
chk("canonical 正确", ('<link rel="canonical" href="https://najieip.com/najie/blog/%s.html">' % SLUG) in t)
chk("og:url 正确", ('<meta property="og:url" content="https://najieip.com/najie/blog/%s.html">' % SLUG) in t)
chk("og:image 存在", 'property="og:image"' in t)
chk("twitter summary_large_image", 'content="summary_large_image"' in t)
chk("keywords 存在", 'name="keywords"' in t)
d, u, dd2 = depth_scan(t[t.find("<body"):])
chk("文章页 div 配平", d == 0 and u == 0, "depth=%d under=%d" % (d, u))
chk("落款三行标准", "010-65150974 / 13911268604" in t and "何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰" in t)
chk("meta description 非标题复读", len(re.search(r'<meta name="description" content="([^"]*)"', t).group(1)) > 80)

print("\n### 2. najie 品牌索引")
nt = open("najie/blog/index.html", encoding="utf-8").read()
nb = nt[nt.find("<body"):]
chk("卡片 72", nb.count('<div class="article-card"') == 72, str(nb.count('<div class="article-card"')))
d, u, dd2 = depth_scan(nb)
chk("div 配平", d == 0 and u == 0, "depth=%d under=%d" % (d, u))
chk("depth2 卡片 == 总数", dd2 == nb.count('<div class="article-card"'), "%d vs %d" % (dd2, nb.count('<div class="article-card"')))
chk("首卡为新文", SLUG in nb[:400] or SLUG in nb[nb.find('<div class="article-card"'):nb.find('<div class="article-card"') + 300])
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', nt, re.S):
    dd = json.loads(blk)
    if dd.get("@type") == "Blog":
        chk("blogPost 首条为本文", dd["blogPost"][0]["url"].endswith(SLUG + ".html"), dd["blogPost"][0]["url"])
        chk("blogPost 数 70", len(dd["blogPost"]) == 70, str(len(dd["blogPost"])))

print("\n### 3. 主索引 blog/index.html")
mt = open("blog/index.html", encoding="utf-8").read()
mb = mt[mt.find("<body"):]
chk("卡片 169", mb.count('<div class="article-card"') == 169, str(mb.count('<div class="article-card"')))
d, u, dd2 = depth_scan(mb)
chk("div 配平", d == 0 and u == 0, "depth=%d under=%d" % (d, u))
chk("depth2 卡片 == 总数", dd2 == mb.count('<div class="article-card"'), "%d vs %d" % (dd2, mb.count('<div class="article-card"')))
hrefs = re.findall(r'<h2><a href="([^"]+)"', mb)
chk("href 唯一", len(set(hrefs)) == len(hrefs), "%d/%d" % (len(set(hrefs)), len(hrefs)))
chk("无 ** 泄漏", mb.count("**") == 0)
for s in [SLUG, "querren-buqinquan-zhisu-2026", "xin-shangbiaofa-2027"]:
    chk("含卡 %s" % s, s in mb)
# 新卡日期降序前缀断言
dates = re.findall(r"<div class=\"meta\">(?:<span class=\"tag\">[^<]*</span>)*[^<]*?(\d{4}-\d{2}-\d{2})", mb)
idx = [i for i, href in enumerate(hrefs) if SLUG in href]
chk("新卡前缀日期 >= 2026-09-21", all(x >= "2026-09-21" for x in dates[:idx[0]]) if idx else False, str(dates[:4]))
mal = [m for m in re.finditer(r'<div class="article-card">', mb) if not mb[m.end():m.end() + 60].lstrip().startswith("<h2><a href=")]
chk("每卡以 h2 起", not mal, str(len(mal)))
print("\nRESULT:", "ALL PASS" if ok else "HAS FAILURES")
