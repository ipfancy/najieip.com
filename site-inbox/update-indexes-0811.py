#!/usr/bin/env python3
"""SiteOps 2026-08-11 索引更新：
blog/index.html + mili/blog/index.html + sitemap.xml + articles.json + content.db 注册"""
import json, pathlib, sqlite3

home = pathlib.Path.home()
base = home / "wiki/najieip-verify"
TODAY = "2026-08-11"

# ============ 1. 主博客 index（2 张新卡片） ============
xa_card = '''  <div class="article-card">
    <h2><a href="/blog/20260810-xishuo-patent-invalid-huashan.html">专利无效攻防：一场没有硝烟的「华山论剑」</a></h2>
    <div class="meta"><span class="tag">专利无效</span><span class="tag">无效宣告</span><span class="tag">戏说IP</span> 2026年8月10日 · 爱普纳杰专利所</div>
    <p>请求人三把刀：新颖性、创造性、公开不充分；专利权人只有一个月应战。戏说IP系列用「华山论剑」拆解专利无效攻防全流程——无效掉一个好专利，比申请一个好专利还难。</p>
  </div>

'''
ai_card = '''  <div class="article-card">
    <h2><a href="/blog/20260811-ai-copyright-cn-us-overseas.html">中美AI版权"冰火两重天"：你的AI生成内容，出海怎么办？</a></h2>
    <div class="meta"><span class="tag">AI版权</span><span class="tag">著作权</span><span class="tag">出海</span> 2026年8月11日 · 觅理律师事务所</div>
    <p>美国最高法院拒审Thaler案——纯AI生成在美国不受版权保护；中国法院却认定AI图片可构成作品。幻之翼案输20万 vs 春风案赢500元，区别只有四个字：创作留痕。</p>
  </div>

'''
blog_idx = base / "blog/index.html"
html = blog_idx.read_text()
marker = '<div class="container">\n'
assert marker in html, "main blog marker not found"
assert 'xishuo-patent-invalid-huashan' not in html, "主博客已含华山论剑"
assert 'ai-copyright-cn-us-overseas' not in html, "主博客已含AI版权"
html = html.replace(marker, marker + "\n" + xa_card + ai_card, 1)
blog_idx.write_text(html)
print("OK blog/index.html 插入2卡片")

# ============ 2. mili blog index（1 张新卡片） ============
mili_card = '''  <div class="article-card">
    <h2><a href="./20260811-ai-copyright-cn-us-overseas.html">中美AI版权"冰火两重天"：你的AI生成内容，出海怎么办？</a></h2>
    <div class="meta"><span class="tag tag-ip">知识产权</span><span class="tag tag-litigation">著作权</span><span class="tag tag-civil">出海合规</span> 2026-08-11 · 觅理律师事务所</div>
    <p>美国最高法院拒审Thaler案——纯AI生成在美国不受版权保护；中国法院却认定AI图片可构成作品。幻之翼案输20万 vs 春风案赢500元，区别只有四个字：创作留痕。</p>
  </div>

'''
mili_idx = base / "mili/blog/index.html"
html = mili_idx.read_text()
marker = '<div class="container">\n'
assert marker in html, "mili marker not found"
assert 'ai-copyright-cn-us-overseas' not in html, "mili已含AI版权"
html = html.replace(marker, marker + "\n" + mili_card, 1)
mili_idx.write_text(html)
print("OK mili/blog/index.html 插入1卡片")

# ============ 3. sitemap.xml ============
smap_path = base / "sitemap.xml"
smap = smap_path.read_text()
new_urls = f'''  <url>
    <loc>https://najieip.com/blog/20260810-xishuo-patent-invalid-huashan.html</loc>
    <lastmod>2026-08-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/blog/20260811-ai-copyright-cn-us-overseas.html</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/mili/blog/20260811-ai-copyright-cn-us-overseas.html</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
assert "</urlset>" in smap
assert 'xishuo-patent-invalid-huashan' not in smap, "sitemap已含华山论剑"
assert 'ai-copyright-cn-us-overseas' not in smap, "sitemap已含AI版权"
smap = smap.replace("</urlset>", new_urls + "</urlset>", 1)
smap_path.write_text(smap)
print("OK sitemap.xml +3 URLs")

# ============ 4. articles.json ============
aj_path = base / "articles.json"
aj = json.loads(aj_path.read_text())
existing = {e.get("url") for e in aj}
new_entries = [
    {"url": "/blog/20260810-xishuo-patent-invalid-huashan.html", "title": "专利无效攻防：一场没有硝烟的「华山论剑」", "date": "2026-08-10", "site": "apnajie"},
    {"url": "/blog/20260811-ai-copyright-cn-us-overseas.html", "title": "中美AI版权\"冰火两重天\"：你的AI生成内容，出海怎么办？", "date": "2026-08-11", "site": "mili"},
    {"url": "/mili/blog/20260811-ai-copyright-cn-us-overseas.html", "title": "中美AI版权\"冰火两重天\"：你的AI生成内容，出海怎么办？", "date": "2026-08-11", "site": "mili"},
]
added = 0
for e in new_entries:
    if e["url"] not in existing:
        aj.append(e)
        added += 1
aj_path.write_text(json.dumps(aj, ensure_ascii=False, indent=1))
print(f"OK articles.json +{added} 条")

# ============ 5. content.db 注册 ============
db = sqlite3.connect(str(home / "wiki/database/content.db"))
# 查找最新 article_id
cur = db.execute("SELECT article_id FROM articles ORDER BY article_id DESC LIMIT 1")
print("最新article_id:", cur.fetchone())
cur = db.execute("SELECT COUNT(*) FROM articles WHERE title LIKE '%华山论剑%' OR title LIKE '%冰火两重天%'")
print("重复标题数:", cur.fetchone()[0])
db.close()
print("\n--- 索引更新完成 ---")
