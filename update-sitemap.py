#!/usr/bin/env python3
"""update-sitemap.py — 增量合并 sitemap（只增不删！）

从 articles.json 读取文章 URL，凡是 sitemap.xml 里还没有的，增量插入到
"文章"区块。绝不删除/替换 sitemap 中已有的任何 URL（含历史文章、多语言页、
旧路径跳转页）。

用法: python3 update-sitemap.py            # 增量合并
      python3 update-sitemap.py --check    # 只报告差异，不写文件
"""
import json, os, re, sys
from datetime import datetime

SITE = os.path.expanduser("~/wiki/najieip-verify")
ARTICLES = os.path.join(SITE, "articles.json")
SITEMAP = os.path.join(SITE, "sitemap.xml")

ARTICLE_MARKER = "<!-- ========== 文章 ========== -->"

def get_existing_urls(content):
    """从 sitemap 文本提取已有全部 URL（含 <loc> 标签）"""
    return set(re.findall(r"<loc>(https://najieip\.com[^<]*)</loc>", content))

def main():
    check_only = "--check" in sys.argv
    articles = json.load(open(ARTICLES, encoding="utf-8"))
    today = datetime.now().strftime("%Y-%m-%d")

    # 收集 articles.json 的文章 URL
    json_urls = {}
    seen = set()
    for a in articles:
        u = a.get("url", "")
        if not u:
            continue
        if "/blog/" not in u and "/articles/" not in u:
            continue
        if u in seen:
            continue
        seen.add(u)
        json_urls[f"https://najieip.com{u}"] = a.get("date", today)

    # 读取现有 sitemap
    if not os.path.exists(SITEMAP):
        print(f"❌ sitemap 不存在: {SITEMAP}")
        sys.exit(1)
    with open(SITEMAP, encoding="utf-8") as f:
        content = f.read()

    existing = get_existing_urls(content)

    # 找出需要新增的 URL
    to_add = []
    for url, date in json_urls.items():
        if url not in existing:
            to_add.append((date, url))

    print(f"articles.json: {len(json_urls)} 条 | sitemap 现有: {len(existing)} 条 | 需新增: {len(to_add)} 条")

    if check_only:
        for date, url in sorted(to_add, reverse=True):
            print(f"  + {date} {url}")
        return

    if not to_add:
        print("✅ 无需更新，sitemap 已是最新")
        return

    # 生成新增条目
    entries = []
    for date, url in sorted(to_add, reverse=True):
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
    block = "\n".join(entries) + "\n"

    # 在"文章"标记后插入（只插入，不替换任何内容）
    if ARTICLE_MARKER in content:
        content = content.replace(ARTICLE_MARKER, ARTICLE_MARKER + "\n" + block, 1)
    else:
        # 没有文章标记：在 </urlset> 前插入（保留全部现有内容）
        content = content.replace("</urlset>", block + "</urlset>", 1)

    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write(content)

    new_count = len(get_existing_urls(content))
    print(f"✅ 已新增 {len(to_add)} 条，sitemap 现有 {new_count} 条 URL（只增不删）")

if __name__ == "__main__":
    main()
