#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-23 内容同步: AI漫剧版权确权 精修上线 (blog + mili 双版本)"""
import re, json, html, os, sys

BASE = '/Users/ziganghe/wiki/najieip-verify'
sys.path.insert(0, f'{BASE}/site-inbox')
from gen_siteops import ARTICLES as _DUMMY  # noqa 确保模块可加载(实际不依赖)
# 直接复用 gen-siteops-0822.py 的函数(同目录有 gen_siteops.py 副本)
from gen_siteops import extract_article, build_article_html, build_stub, card_html, card_html_main

ARTICLES = [
    {
        "slug": "20260823-ai-manju-copyright-checklist",
        "inbox": "20260823-ai-manju-copyright-checklist.html",
        "title": "花18万做的AI漫剧，版权竟不是你的",
        "date": "2026-08-23",
        "desc": "2026年AI漫剧市场规模冲到400亿、同比暴涨138%，但完成完整版权确权的项目仅17.2%——83%的团队在裸奔做爆款。MCN花18万定制30集古风AI漫剧，上线前才发现合同只写了'非专有播放权'。四步确权闭环：合同锁权、全程留痕、存证+登记、出海先登记。附2026年4月备案新规与AI标识办法两条硬约束。",
        "keywords": "AI漫剧,版权确权,著作权,AI生成内容,人工智能,区块链存证",
        "tags": ["AI漫剧", "版权确权", "AI+知产"],
        "card": "AI漫剧400亿市场，83%的团队在裸奔做爆款——合同只写'非专有播放权'，18万定制剧版权悬空。四步确权闭环：合同锁权、全程留痕、存证+登记、出海先登记，附备案新规与AI标识硬约束。",
    },
]

def main():
    written = []
    a = ARTICLES[0]

    # 1) blog/ 主版本
    blog_path = os.path.join(BASE, 'blog', f"{a['slug']}.html")
    content = build_article_html(
        a, '爱普纳杰专利所', '爱普纳杰专利所',
        f"https://najieip.com/blog/{a['slug']}.html",
        '博客', 'https://najieip.com/blog/', '/')
    with open(blog_path, 'w', encoding='utf-8') as f:
        f.write(content)
    written.append(blog_path)
    print(f"OK blog/{a['slug']}.html")

    # 2) mili/blog/ 品牌版本 (版权/著作权 → 觅理)
    mili_path = os.path.join(BASE, 'mili', 'blog', f"{a['slug']}.html")
    content_m = build_article_html(
        a, '觅理律师事务所', '觅理律所',
        f"https://najieip.com/mili/blog/{a['slug']}.html",
        '觅理博客', 'https://najieip.com/mili/blog/', '/mili/')
    with open(mili_path, 'w', encoding='utf-8') as f:
        f.write(content_m)
    written.append(mili_path)
    print(f"OK mili/blog/{a['slug']}.html")

    # 3) articles/ 跳转 stub → blog/
    stub_path = os.path.join(BASE, 'articles', f"{a['slug']}.html")
    with open(stub_path, 'w', encoding='utf-8') as f:
        f.write(build_stub(a))
    written.append(stub_path)
    print(f"OK articles/{a['slug']}.html (stub)")

    # 4) blog/index.html 卡片插入
    idx_path = os.path.join(BASE, 'blog', 'index.html')
    with open(idx_path, encoding='utf-8') as f:
        idx = f.read()
    marker = '<div class="container">'
    if marker in idx:
        if f"/blog/{a['slug']}.html" in idx:
            print("blog/index.html 已含卡片, 跳过")
        else:
            insert_at = idx.index(marker) + len(marker)
            idx = idx[:insert_at] + '\n\n' + card_html_main(a) + '\n' + idx[insert_at:]
            with open(idx_path, 'w', encoding='utf-8') as f:
                f.write(idx)
            print("blog/index.html +1 卡片")
    else:
        print("!! blog/index.html 找不到 container 标记")

    # 5) mili/blog/index.html 卡片插入
    nidx_path = os.path.join(BASE, 'mili', 'blog', 'index.html')
    with open(nidx_path, encoding='utf-8') as f:
        nidx = f.read()
    if f"./{a['slug']}.html" in nidx:
        print("mili/blog/index.html 已含卡片, 跳过")
    else:
        m = re.search(r'<div class="article-card">', nidx)
        if m:
            nidx = nidx[:m.start()] + card_html(a) + '\n\n' + nidx[m.start():]
            with open(nidx_path, 'w', encoding='utf-8') as f:
                f.write(nidx)
            print("mili/blog/index.html +1 卡片")
        else:
            print("!! mili/blog/index.html 找不到 article-card 标记")

    # 6) sitemap.xml +2 URL
    sm_path = os.path.join(BASE, 'sitemap.xml')
    with open(sm_path, encoding='utf-8') as f:
        sm = f.read()
    if a['slug'] in sm:
        print("sitemap 已含条目, 跳过")
    else:
        new_urls = []
        for prefix in ('blog', 'mili/blog'):
            new_urls.append(f'''  <url>
    <loc>https://najieip.com/{prefix}/{a['slug']}.html</loc>
    <lastmod>2026-08-23</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')
        block = '\n'.join(new_urls)
        sm = sm.replace('</urlset>', block + '\n</urlset>')
        with open(sm_path, 'w', encoding='utf-8') as f:
            f.write(sm)
        print("sitemap.xml +2 URL")

    # 7) articles.json 路径 /articles/ → /blog/
    aj_path = os.path.join(BASE, 'articles.json')
    with open(aj_path, encoding='utf-8') as f:
        aj = json.load(f)
    arts = aj if isinstance(aj, list) else aj.get('articles', aj)
    changed = 0
    for item in arts:
        u = item.get('url', '')
        if a['slug'] in u and u.startswith('/articles/'):
            item['url'] = f"/blog/{a['slug']}.html"
            changed += 1
    with open(aj_path, 'w', encoding='utf-8') as f:
        json.dump(aj, f, ensure_ascii=False, indent=2)
    print(f"articles.json 路径更新 {changed} 条")

    print(f"\n写入文件 {len(written)} 个")

if __name__ == '__main__':
    main()
