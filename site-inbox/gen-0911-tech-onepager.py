#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-11 发布 · TASK-SITE-PUBLISH-XISHUO-TECH-20260911 物料③
纳杰体系_技术能力一页纸_v2_AI增强_官网机构介绍版_20260911.html（md5 b34666f128）
  → najieip.com 机构介绍页  /about.html

幂等：若 /about.html 已存在则跳过正文写入（只校验），index.html 入口已存在则跳过。
红线：只新增本页与 1 个入口；不改动任何既有内容；正文与源件逐字一致（仅加外壳）。
"""
import os
import re
import sys
import hashlib

REPO = "/mnt/c/Users/zigan/najieip-site"
SRC = "/mnt/i/内省II耳目手足爪牙/文件存放/市场部/纳杰体系_技术能力一页纸_v2_AI增强_官网机构介绍版_20260911.html"
SRC_MD5_10 = "b34666f128"
ABOUT = os.path.join(REPO, "about.html")
INDEX = os.path.join(REPO, "index.html")

# ---------------- 源件校验（取件红线） ----------------
raw = open(SRC, "rb").read()
md5_10 = hashlib.md5(raw).hexdigest()[:10]
if md5_10 != SRC_MD5_10:
    print(f"🔴 源件 md5 不符：{md5_10} != {SRC_MD5_10} —— 停止，报如己")
    sys.exit(2)
src_html = raw.decode("utf-8")
print(f"✅ 源件 md5 {md5_10} 与执行单一致")

# 抽取 <article> 内部正文（原样保留，仅去除外层 article 标签）
m = re.search(r"<article>(.*?)</article>", src_html, re.DOTALL)
if not m:
    print("🔴 源件中未找到 <article> 正文块 —— 停止")
    sys.exit(2)
body = m.group(1).strip()

# 源件正文核验（标题/落款/邮箱）
for must in ["技术驱动的一体化知识产权服务", "纳杰体系：AI 增强 + 自研系统 + 专业团队 + 数据底座",
             "collection@najieip.com", "010-65150974 / 13911268604",
             "何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰"]:
    assert must in body, f"源件正文缺少必需串: {must}"
assert "本文仅代表作者个人观点" not in body, "官网版不应含个人观点免责句"
print("✅ 源件正文核验：标题/副题/邮箱/落款（电话行+署名行，无免责句）全部到位")

TITLE = "技术驱动的一体化知识产权服务 — 纳杰体系机构介绍"
DESC = ("纳杰体系机构介绍：北京纳杰知识产权（商标・著作权）、北京爱普纳杰专利代理事务所（专利）、"
        "北京觅理律师事务所（法律诉讼）三主体一体化。AI 增强的服务能力、自研业务系统 3 项软件著作权、"
        "66 国年费规则库数据底座、中/英/法/德四语团队，检索评估到维权诉讼一条链贯通。")
OG_DESC = ("三家机构一个体系：商标・专利・诉讼一体化。AI 负责效率，人负责判断与责任；"
           "自研知产有效期管理/年费提醒/案卷号系统 3 项软著，66 国年费规则库，中/英/法/德四语直接作业。")

JSONLD = """{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "纳杰体系（纳杰・爱普纳杰・觅理）",
  "url": "https://najieip.com/about.html",
  "email": "collection@najieip.com",
  "telephone": "+86-10-65150974",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "建国门外大街丙12-12号宝钢大厦1502室",
    "addressLocality": "北京市",
    "addressRegion": "朝阳区",
    "addressCountry": "CN"
  },
  "department": [
    {"@type": "Organization", "name": "北京纳杰知识产权代理有限公司", "description": "商标・著作权・涉外知识产权・项目非诉"},
    {"@type": "Organization", "name": "北京爱普纳杰专利代理事务所", "description": "专利新申请・OA答复・复审无效・检索分析"},
    {"@type": "Organization", "name": "北京觅理律师事务所", "description": "知识产权诉讼・商业秘密・争议解决・企业常法"}
  ]
}"""

PAGE = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{DESC}">
<title>{TITLE}</title>
<link rel="canonical" href="https://najieip.com/about.html">
<meta property="og:title" content="技术驱动的一体化知识产权服务 — 纳杰体系">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image" content="https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&amp;cs=tinysrgb&amp;w=1200">
<meta property="og:url" content="https://najieip.com/about.html">
<meta property="og:type" content="website">
<meta name="keywords" content="纳杰体系,知识产权一体化,商标代理,专利代理,知识产权诉讼,AI辅助检索,专利年费管理,涉外知识产权">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<style>
:root {{ --primary: #1F4E79; --accent: #C0A060; --text: #333; --text-light: #666; --bg: #F8F9FA; --white: #fff; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: 'Noto Sans SC', sans-serif; color: var(--text); line-height:1.9; background: var(--bg); }}
header {{ background: var(--primary); padding: 20px 48px; text-align:center; }}
header a {{ color: var(--white); text-decoration:none; font-size: 24px; font-weight: 900; letter-spacing:2px; }}
.lang-bar {{ background:#1a1a2e; padding:6px 48px; display:flex; justify-content:flex-end; gap:6px; font-size:12px; }}
.lang-bar a {{ color:rgba(255,255,255,0.5); text-decoration:none; padding:4px 12px; border-radius:14px; }}
.lang-bar a.active {{ color:var(--accent); background:rgba(192,160,96,0.15); font-weight:700; }}
.container {{ max-width: 900px; margin: 0 auto; padding: 48px 24px; }}
h1 {{ font-size: 32px; color: var(--primary); text-align:center; margin-bottom: 8px; }}
.subtitle {{ text-align:center; color: var(--text-light); font-size: 16px; margin-bottom: 40px; }}
h2 {{ font-size: 22px; color: var(--primary); margin: 40px 0 14px; padding-left: 12px; border-left: 4px solid var(--accent); }}
p {{ margin-bottom: 14px; font-size: 15px; }}
ul {{ margin: 0 0 16px 1.4em; }}
li {{ margin-bottom: 10px; font-size: 15px; }}
strong {{ color: var(--primary); }}
.card {{ background: var(--white); border-radius: 12px; padding: 28px 32px; box-shadow:0 2px 16px rgba(0,0,0,0.06); margin: 24px 0; }}
.card ul {{ margin-bottom: 0; }}
.loop {{ background: var(--primary); color: var(--white); border-radius: 12px; padding: 24px 32px; text-align:center; font-size: 16px; letter-spacing: 0.5px; margin: 24px 0; }}
.loop p {{ margin: 0; color: var(--white); }}
.closing {{ font-size: 15px; color: var(--text-light); }}
footer {{ background:#1a1a2e; color:rgba(255,255,255,0.6); padding:32px; text-align:center; font-size:13px; margin-top:60px; line-height:2; }}
footer a {{ color: var(--accent); text-decoration:none; }}
@media (max-width:640px) {{ header {{ padding:16px 20px; }} .container {{ padding: 32px 18px; }} h1 {{ font-size: 26px; }} }}
</style>
<script type="application/ld+json">
{JSONLD}
</script>
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
</head>
<body>
<div class="lang-bar">
  <a href="/about.html" class="active">中文</a>
  <a href="/en/">EN</a>
  <a href="/fr/">FR</a>
</div>
<header><a href="/">纳杰体系 · 机构介绍</a></header>
<div class="container">
{body}
</div>
<footer>
  <p>北京纳杰知识产权代理有限公司 &nbsp;|&nbsp; 北京爱普纳杰专利代理事务所 &nbsp;|&nbsp; 北京觅理律师事务所</p>
  <p>📞 <a href="tel:+861065150974">010-65150974</a> / <a href="tel:+8613911268604">13911268604</a> &nbsp;|&nbsp; ✉️ <a href="mailto:collection@najieip.com">collection@najieip.com</a></p>
  <p><a href="/">首页</a> · <a href="/najie/">纳杰</a> · <a href="/aipunajie/">爱普纳杰</a> · <a href="/mili/">觅理</a></p>
</footer>
</body>
</html>
"""

# ---------------- 写 about.html ----------------
if os.path.exists(ABOUT):
    old = open(ABOUT, encoding="utf-8").read()
    if old == PAGE:
        print("⏭  /about.html 已存在且内容一致，跳过写入")
    else:
        print("⚠️  /about.html 已存在但内容不同 —— 停止（避免覆盖）")
        sys.exit(3)
else:
    open(ABOUT, "w", encoding="utf-8").write(PAGE)
    print(f"✅ 已写入 /about.html（{len(PAGE)} 字符）")

# ---------------- index.html 加入口（幂等） ----------------
idx = open(INDEX, encoding="utf-8").read()
changed = False
if 'href="/about.html"' not in idx:
    nav_old = '    <li><a href="/mili/">觅理</a></li>\n'
    nav_new = '    <li><a href="/mili/">觅理</a></li>\n    <li><a href="/about.html">机构介绍</a></li>\n'
    if nav_old not in idx:
        print("🔴 index.html 导航锚点未找到 —— 停止")
        sys.exit(4)
    idx = idx.replace(nav_old, nav_new, 1)
    changed = True
    print("✅ index.html 导航 + 机构介绍 入口")

    foot_old = '  <p>📧 <a href="mailto:collection@najieip.com">collection@najieip.com</a></p>\n'
    foot_new = ('  <p>📧 <a href="mailto:collection@najieip.com">collection@najieip.com</a> '
                '&nbsp;|&nbsp; 🏛️ <a href="/about.html">机构介绍</a></p>\n')
    if foot_old in idx:
        idx = idx.replace(foot_old, foot_new, 1)
        print("✅ index.html footer + 机构介绍 入口")
    else:
        print("⚠️ footer 锚点未命中（导航入口已加，不阻断）")
else:
    print("⏭  index.html 已含 /about.html 入口，跳过")

if changed:
    open(INDEX, "w", encoding="utf-8").write(idx)

print("\n完成。下一步：git add/commit/push → 200 实测 → sitemap 刷新 → ping SE")
