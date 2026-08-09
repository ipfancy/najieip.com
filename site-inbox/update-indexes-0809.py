#!/usr/bin/env python3
"""更新索引：blog/najie/mili index.html + sitemap.xml + articles.json"""
import json, pathlib, re

home = pathlib.Path.home()
base = home / "wiki/najieip-verify"
TODAY = "2026-08-09"

# ============ 1. 主博客 index ============
j1_card = '''  <div class="article-card">
    <h2><a href="/blog/20260809-ai-vs-employee.html">AI员工 vs 人类员工：一场算不清账的战争？——经济学/管理学/税收财务/心理学/哲学五维对比，给创业者和传统老板的最终答案</a></h2>
    <div class="meta"><span class="tag">AI</span><span class="tag">数字员工</span><span class="tag">用工成本</span> 2026年8月9日 · 纳杰知识产权</div>
    <p>从经济学、管理学、税收财务、心理学、哲学五个维度彻底算透AI原生与人力用工的真实成本——不是"用AI"或"用人"的二选一，而是一套按阶段切换的组合打法。</p>
  </div>

'''
j2_card = '''  <div class="article-card">
    <h2><a href="/blog/ai-agent-liability-chain-20260809.html">AI数字员工闯祸谁赔？从"养龙虾"暴雷到首案裁判，企业必看的责任链清单</a></h2>
    <div class="meta"><span class="tag">AI</span><span class="tag">数字员工</span><span class="tag">合规</span> 2026年8月9日 · 觅理律师事务所</div>
    <p>从OpenClaw"养龙虾"暴雷到杭州AI幻觉首案、广州双重授权裁定，拆解部署前、运行中、出事后三层责任链，附10项企业AI智能体部署合规自查表。</p>
  </div>

'''
blog_idx = base / "blog/index.html"
html = blog_idx.read_text()
marker = '<div class="container">\n'
assert marker in html, "main blog marker not found"
html = html.replace(marker, marker + "\n" + j1_card + j2_card, 1)
blog_idx.write_text(html)
print("OK blog/index.html 插入2卡片")

# ============ 2. najie blog index ============
najie_card = '''  <div class="article-card">
    <h2><a href="./20260809-ai-vs-employee.html">AI员工 vs 人类员工：一场算不清账的战争？——经济学/管理学/税收财务/心理学/哲学五维对比，给创业者和传统老板的最终答案</a></h2>
    <div class="meta">2026-08-09 · 纳杰知识产权推荐</div>
    <p>从经济学、管理学、税收财务、心理学、哲学五个维度彻底算透AI原生与人力用工的真实成本——不是"用AI"或"用人"的二选一，而是一套按阶段切换的组合打法。</p>
  </div>

'''
najie_idx = base / "najie/blog/index.html"
html = najie_idx.read_text()
marker = '<div class="container">\n'
assert marker in html, "najie marker not found"
html = html.replace(marker, marker + "\n" + najie_card, 1)
najie_idx.write_text(html)
print("OK najie/blog/index.html 插入1卡片")

# ============ 3. mili blog index ============
mili_card = '''  <div class="article-card">
    <h2><a href="./ai-agent-liability-chain-20260809.html">AI数字员工闯祸谁赔？从"养龙虾"暴雷到首案裁判，企业必看的责任链清单</a></h2>
    <div class="meta"><span class="tag tag-ip">知识产权</span><span class="tag tag-litigation">诉讼</span><span class="tag tag-civil">民法典</span> 2026-08-09 · 觅理律师事务所</div>
    <p>从OpenClaw"养龙虾"暴雷到杭州AI幻觉首案、广州双重授权裁定，拆解部署前、运行中、出事后三层责任链，附10项企业AI智能体部署合规自查表。</p>
  </div>

'''
mili_idx = base / "mili/blog/index.html"
html = mili_idx.read_text()
marker = '<div class="container">\n'
assert marker in html, "mili marker not found"
html = html.replace(marker, marker + "\n" + mili_card, 1)
mili_idx.write_text(html)
print("OK mili/blog/index.html 插入1卡片")

# ============ 4. sitemap.xml ============
smap_path = base / "sitemap.xml"
smap = smap_path.read_text()
new_urls = f'''  <url>
    <loc>https://najieip.com/blog/20260809-ai-vs-employee.html</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/najie/blog/20260809-ai-vs-employee.html</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/blog/ai-agent-liability-chain-20260809.html</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/mili/blog/ai-agent-liability-chain-20260809.html</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
assert "</urlset>" in smap
smap = smap.replace("</urlset>", new_urls + "</urlset>", 1)
smap_path.write_text(smap)
print("OK sitemap.xml +4 URLs")

# ============ 5. articles.json 修正 /articles/ -> 正式路径 ============
aj_path = base / "articles.json"
aj = json.loads(aj_path.read_text())
fixed = 0
for e in aj:
    if e.get("url") == "/articles/ai-agent-liability-chain-20260809.html":
        e["url"] = "/mili/blog/ai-agent-liability-chain-20260809.html"
        e["site"] = "mili"
        fixed += 1
    elif e.get("url") == "/articles/20260809-ai-vs-employee-综合对比.html":
        e["url"] = "/blog/20260809-ai-vs-employee.html"
        e["site"] = "najie"
        fixed += 1
aj_path.write_text(json.dumps(aj, ensure_ascii=False, indent=1))
print(f"OK articles.json 修正 {fixed} 条路径")

print("\n--- 索引更新完成 ---")
