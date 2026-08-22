#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-08-22 rebase 冲突合并: 并发(mili)为准 + 保留主blog版本"""
import re, json, subprocess, os

BASE = '/Users/ziganghe/wiki/najieip-verify'
SLUGS = ['20260821-beijing-shebao-2026', '20260821-beijing-shebao-tax', '20260822-us-tro-72hour-checklist']

def sh(cmd):
    r = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"!! {cmd}: {r.stderr[:300]}")
    return r.stdout

# ---- 1. articles.json: 取并发版本 (mili) ----
sh('git checkout --ours articles.json')
print("articles.json -> 并发版本 (mili/blog)")

# ---- 2. articles/ stub: 取并发版本 (指向 mili/blog) ----
for s in SLUGS:
    sh(f'git checkout --ours articles/{s}.html')
print("articles/ 3 stub -> 并发版本")

# ---- 3. blog/index.html: 手动合并双方卡片 ----
with open(f'{BASE}/blog/index.html', encoding='utf-8') as f:
    idx = f.read()

def resolve_marker(text, pick_ours=False):
    """手动指定解决: 返回处理后的文本"""
    return text

# 冲突块: 保留 HEAD 卡片(商标续展/法律体检) + a4d1e2c 卡片(社保/TRO)
head_cards = '''  <div class="article-card">
    <h2><a href="/blog/shangbiao-xuzhan-banli-2026.html">商标续展办理：有效期、宽展期、续展费用与常见误区</a></h2>
    <div class="meta"><span class="tag">商标续展</span><span class="tag">商标实务</span><span class="tag">续展办理</span> 2026年8月22日 · 纳杰知识产权</div>
    <p>商标续展办理怎么做？有效期10年、期满前12个月可续展、6个月宽展期，错过即注销且1年内近似申请不核准。梳理商标续展全流程、费用与常见误区。</p>
  </div>

  <div class="article-card">
    <h2><a href="/blog/qiye-falv-tijian-2026.html">企业法律体检：中小企业法律风险排查与合规体检全指南</a></h2>
    <div class="meta"><span class="tag">法律顾问</span><span class="tag">法律体检</span><span class="tag">合规</span> 2026年8月22日 · 纳杰知识产权</div>
    <p>企业法律体检是什么？查什么、怎么查、值不值？拆解六大模块、四步流程与常见高风险点，帮助中小企业用低成本发现高风险、从被动应对转向事前防控。</p>
  </div>

  <div class="article-card">
    <h2><a href="/blog/20260821-beijing-shebao-2026.html">北京社保基数涨了：下限7270元，企业多掏多少？</a></h2>
    <div class="meta"><span class="tag">社保</span><span class="tag">劳动用工</span><span class="tag">社保基数</span> 2026年8月22日 · 纳杰知识产权</div>
    <p>2026年7月起北京社保缴费基数调整：上限36348元、下限7270元。三档算账拆解单位每人每月1941.09元的真实成本，工伤行业费率差、公积金同步调、员工到手变化，附企业申报五步实操清单。</p>
  </div>

  <div class="article-card">
    <h2><a href="/blog/20260821-beijing-shebao-tax.html">社保基数涨了，企业反而能少缴税？7月补差这笔账怎么算</a></h2>
    <div class="meta"><span class="tag">社保</span><span class="tag">税务</span><span class="tag">劳动用工</span> 2026年8月22日 · 纳杰知识产权</div>
    <p>多缴的社保费是企业所得税与个税的税前扣除项——100人企业一年约省8600元企业所得税。7月补差明细、滞纳金年化18.25%与110%核定风险、金税四期三条比对线、三数对齐自查清单。</p>
  </div>

  <div class="article-card">
    <h2><a href="/blog/20260822-us-tro-72hour-checklist.html">货款被美国法院冻结，72小时做对这5件事</a></h2>
    <div class="meta"><span class="tag">TRO</span><span class="tag">跨境电商</span><span class="tag">涉外维权</span> 2026年8月22日 · 纳杰知识产权</div>
    <p>2026年25天210件TRO案、1674家中国店铺被冻结。第七巡回法院新判例撕开管辖权抗辩窗口，《海牙送达公约》禁止电邮送达。72小时五件事清单+和解/应诉/弃店对比。</p>
  </div>
'''

pat = re.compile(r'<<<<<<< HEAD.*?>>>>>>> a4d1e2c \(siteops: 社保基数两篇\+美国TRO 精修上线\(blog\+najie双版本\) \+ 索引/sitemap/articles\.json \+ TRO注册db\)\n', re.S)
new_idx, n = pat.subn(head_cards + '\n', idx)
print(f"blog/index.html 冲突块替换: {n} 处")
with open(f'{BASE}/blog/index.html', 'w', encoding='utf-8') as f:
    f.write(new_idx)

# ---- 4. sitemap.xml: 合并 mili + blog, 去掉 najie ----
with open(f'{BASE}/sitemap.xml', encoding='utf-8') as f:
    sm = f.read()
# 取并发 HEAD 的 mili 3 条
mili_block = '''  <url>
    <loc>https://najieip.com/mili/blog/20260821-beijing-shebao-2026.html</loc>
    <lastmod>2026-08-21</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/mili/blog/20260821-beijing-shebao-tax.html</loc>
    <lastmod>2026-08-21</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/mili/blog/20260822-us-tro-72hour-checklist.html</loc>
    <lastmod>2026-08-21</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
blog_block = '''  <url>
    <loc>https://najieip.com/blog/20260821-beijing-shebao-2026.html</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/blog/20260821-beijing-shebao-tax.html</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/blog/20260822-us-tro-72hour-checklist.html</loc>
    <lastmod>2026-08-22</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''
pat_sm = re.compile(r'<<<<<<< HEAD.*?>>>>>>> a4d1e2c \(siteops: 社保基数两篇\+美国TRO 精修上线\(blog\+najie双版本\) \+ 索引/sitemap/articles\.json \+ TRO注册db\)\n', re.S)
new_sm, n2 = pat_sm.subn(mili_block + blog_block, sm)
print(f"sitemap.xml 冲突块替换: {n2} 处")
with open(f'{BASE}/sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(new_sm)

# ---- 5. 删除 najie/blog 3 个文件 + 回退 najie/blog/index.html ----
for s in SLUGS:
    p = f'{BASE}/najie/blog/{s}.html'
    if os.path.exists(p):
        os.remove(p)
        print(f"删除 najie/blog/{s}.html")
sh('git checkout --ours najie/blog/index.html')
print("najie/blog/index.html -> 回退并发版本")

# ---- 6. 检查残留冲突标记 ----
for f in ['blog/index.html', 'sitemap.xml', 'articles.json']:
    with open(f'{BASE}/{f}', encoding='utf-8') as fh:
        c = fh.read()
    if '<<<<<<<' in c:
        print(f"!! {f} 仍有冲突标记")
    else:
        print(f"{f} 无冲突标记 ✓")
