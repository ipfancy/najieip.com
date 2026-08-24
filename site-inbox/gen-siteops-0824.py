#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-24 内容同步: 数据纠纷/竞业协议 精修上线 (blog + mili 双版本)"""
import re, json, os, sys

BASE = '/Users/ziganghe/wiki/najieip-verify'
sys.path.insert(0, f'{BASE}/site-inbox')
from gen_siteops import extract_article, build_article_html, build_stub, card_html, card_html_main

ARTICLES = [
    {
        "slug": "20260824-judicial-ip-plan-enterprise-checklist",
        "inbox": "20260824-judicial-ip-plan-enterprise-checklist.html",
        "title": "数据纠纷一年涨25.6%，竞业协议可能签了也白签",
        "date": "2026-08-24",
        "desc": "最高法印发《人民法院知识产权司法保护实施方案（2026—2030年）》（法发〔2026〕4号）：2025年全国法院新收知产案件55.26万件、涉数据权属和交易纠纷908件暴涨25.6%。两张自查表——数据资产三类定性（公共/企业/个人信息，附数据堂案全国首例数据知产登记证、反法数据专款、数据资产质押融资案例）+ 竞业协议五问自评（是否接触商业秘密、范围地域期限适配、2年红线、北京约30%补偿口径、替代手段优先）。",
        "keywords": "数据纠纷,竞业协议,知识产权司法保护,企业数据,商业秘密,竞业限制,数据资产",
        "tags": ["数据纠纷", "竞业限制", "数据资产"],
        "card": "数据纠纷一年涨25.6%，竞业协议可能签了也白签——最高法五年方案划出两条决策线：数据资产先归类（公共/企业/个人信息），竞业协议先自评（五问过一遍）。数据堂案确权判例+反法数据专款+数据质押融资案例，越早做归类越早避开纠纷。",
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

    # 2) mili/blog/ 品牌版本 (数据纠纷/竞业限制 → 觅理综合律所)
    mili_path = os.path.join(BASE, 'mili', 'blog', f"{a['slug']}.html")
    content_m = build_article_html(
        a, '觅理律师事务所', '觅理律所',
        f"https://najieip.com/mili/blog/{a['slug']}.html",
        '觅理博客', 'https://najieip.com/mili/blog/', '/mili/')
    with open(mili_path, 'w', encoding='utf-8') as f:
        f.write(content_m)
    written.append(mili_path)
    print(f"OK mili/blog/{a['slug']}.html")

    # 3) articles/ 跳转 stub → blog/ (铁律: 旧路径改跳转页)
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
    <lastmod>2026-08-24</lastmod>
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
