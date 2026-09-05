#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-05: ART-2026-0078 开源数据别乱用 精修版生成
原始版只在旧路径 articles/ (有 ** 残留、无 JSON-LD/OG)
→ 生成 blog/ + mili/blog/ 精修版, articles/ 改跳转页, 主blog+mili索引+sitemap+articles.json+deploy-log更新
品牌归属: 商业秘密/反不正当竞争+AI数据合规 → 觅理 (mili/blog), 同时进主博客 blog/
"""
import re, os, json, datetime

ROOT = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260905-ai-training-data-compliance.html"
TITLE = "开源数据别乱用！5条线帮你避坑，有人已赔10万"
DESC = ("全国首例《数据知识产权登记证》司法效力案：数据堂诉隐某，同一中文语音数据集一审认定商业秘密、二审改判不构成，"
        "被告仍因不正当竞争赔偿10万元＋2300元合理开支。数据集可有三重身份：汇编作品/商业秘密/反不正当竞争法第2条竞争性权益；"
        "登记证是“初步证据”护身符；开源≠放弃权利（CC非商业条款是红线）。附五条AI训练数据输入合规自检线"
        "（来源合法/在先权利/开源协议/登记确权/防输出泄密）＋“输入→模型→人”三层防护。数据堂凭登记证2024年数据交易约9558万元，"
        "全国已发证超4.8万张。")
KEYWORDS = "数据知识产权登记证,商业秘密,AI训练数据,开源协议,反不正当竞争,数据合规,数据堂案,AI数据合规"
OG_DESC = ("全国首例《数据知识产权登记证》司法效力案：同一中文语音数据集一审判商业秘密、二审改判不构成，被告仍赔10万＋2300元。"
           "数据集三重身份、登记证当护身符、开源≠放弃权利——五条输入合规自检线，AI企业今天就能做。")
DATE = "2026-09-05"
TAGS = ["数据合规", "AI训练", "商业秘密", "开源协议", "数据知识产权"]
CARD_SUMMARY = ("全国首例《数据知识产权登记证》司法效力案：同一中文语音数据集一审认定商业秘密、二审改判不构成，被告仍因不正当竞争赔偿10万元＋2300元合理开支。"
                "一个数据集的三重身份（汇编作品/商业秘密/竞争性权益）、登记证为何是“初步证据”护身符、开源≠放弃权利——"
                "附五条AI训练数据输入合规自检线（来源合法/在先权利/开源协议/登记确权/防输出泄密）和“输入→模型→人”三层防护，今天就能做。")
PEXELS_IMG = "https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=1200"

BODY = [
    ("blockquote", "本文作者何自刚，执业20年知识产权律师，以“一人公司（OPC）＋AI数字员工”运营爱普纳杰专利所、觅理律所、纳杰公司三个主体。今天拆解全国首例《数据知识产权登记证》司法效力案：数据集为什么能有三重身份、登记证怎么当“初步证据”护身符、开源为什么不等于放弃权利——最后附五条输入合规自检线，逐条给自己打勾。"),
    ("p", "同一个中文语音数据集，一审法院判它是商业秘密，二审却说不是——但被告该赔的钱一分没少，10万元照付，外加2300元合理开支。"),
    ("p", "这就是全国首例《数据知识产权登记证》司法效力案：数据堂（北京）诉隐某（上海）。数据堂2021年9月发布“1505小时中文普通话语音数据”开源计划，2023年拿到北京市首批数据知识产权登记证。被告把其中200小时的子集，放到自家官网当数据产品对外披露、诱导注册下载，被判构成不正当竞争。"),
    ("p", "这个案子把三件事说透了，每件都直接关系到你的AI项目。"),
    ("h2", "一个数据集，可以有三重身份"),
    ("p", "法院确立了“分类保护、阶梯适用”的三阶梯："),
    ("ul", [
        "内容选择、编排有独创性的，是<strong>汇编作品</strong>；",
        "不为相关领域人员容易获取的，是<strong>商业秘密</strong>；",
        "公开了、又缺独创性、但你花了真金白银投入整理的，是<strong>反不正当竞争法第2条保护的竞争性权益</strong>。",
    ]),
    ("p", "数据堂的语音库就是第三种——虽然公开了不能算商业秘密，但人家实打实的投入，别人不能白嫖。"),
    ("h2", "登记证是一张“初步证据”护身符"),
    ("p", "没有相反证据时，登记证＝你对数据享有财产性利益＋收集行为来源合法的初步证明。"),
    ("p", "注意“初步”两个字——它能被反证推翻，但关键在：<strong>它能帮你把举证责任先顶过去</strong>。对方想否认，得自己掏证据来翻。在诉讼里，这就是一个巨大的先手。"),
    ("h2", "开源 ≠ 放弃权利"),
    ("p", "数据堂用了CC开源协议，被告以为“开源＝随便商用”。法院说得明白：是否遵循开源协议（尤其非商业用途条款），是衡量数据服务领域商业道德的重要考量。未经许可、不劳而获地商用，就是不正当竞争。"),
    ("blockquote", "<strong>“输入端登记确权、输出端留痕保密，AI企业的数据护城河，是拿动作堆出来的，不是拿口号喊出来的。”</strong> —— 何自刚 | 知识产权律师 | 爱普纳杰·觅理·纳杰（执业20年，以OPC＋AI数字员工运营三主体）"),
    ("h2", "五条输入合规自检线，逐条给自己打勾"),
    ("p", "<strong>① 来源合法</strong> —— 训练数据的授权链条完整吗？公共数据走了授权运营吗？从第三方买的数据做尽调了吗？留痕了吗？"),
    ("p", "<strong>② 在先权利</strong> —— 数据里有没有别人的著作权、商业秘密、个人信息？《生成式AI服务管理暂行办法》第7条是强制项，不得侵害他人合法权益。"),
    ("p", "<strong>③ 开源协议</strong> —— 你引用的开源数据集，逐条读过CC协议了吗？商用条款是红线，很多“免费”数据集，其实只是“免费非商用”。"),
    ("p", "<strong>④ 登记确权</strong> —— 自建的数据集，去试点省市申请登记证了吗？截至2025年底，全国已发出超4.8万张证、融资增信近150亿元。数据堂凭一张证，2024年数据交易卖了约9558万元，比前一年涨了76%。"),
    ("p", "<strong>⑤ 防输出泄密</strong> —— 这条最容易被忽视。市场监管总局2026年8月20日刚公布：杭州一位算法专家离职后，把原单位的AI模型专属提示词模板、审查规则、标注规范外发，被罚35万元。官方定性很硬：自然语言类的集成方案、非标运营规则，也能独立构成商业秘密。"),
    ("h2", "三层都得防：输入 → 模型 → 人"),
    ("p", "抖音诉亿睿科“B612咔叽”案，全国首例AI模型结构和参数受反法保护案——对方照搬漫画特效模型的结构与参数，单案判赔160万元，安卓加iOS两案合计约320万元。"),
    ("p", "从输入数据（登记证）、到中间模型（商业秘密/竞争性权益）、再到离职员工（保密管理），漏一层就是真金白银的代价。"),
    ("h2", "三条建议，今天就能做"),
    ("ol", [
        "马上把在用的开源数据集清单拉出来，逐个核对CC协议的商用条款；",
        "立即查一查自建数据集所在省市开没开数据知识产权登记试点，能登记就登记；",
        "把提示词模板、模型参数、审查规则纳入保密清单，签好保密协议、做好离职管理。",
    ]),
    ("p", "数据合规这件事，早做是护城河，晚做是学费。别等收到起诉状，才想起去看开源协议。"),
    ("p", "在数据合规上踩过坑的，欢迎在评论区聊聊。关注公众号「纳杰觅理」，下一篇讲：AI模型被抄了，160万判赔是怎么算出来的——模型资产的双轨保护打法。"),
    ("p", "何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰"),
    ("p", "座机：010-65150974 | 手机：15321374076 / 13911268604"),
    ("p_em", "本文仅代表作者个人观点，不构成法律意见。如需具体案件分析，欢迎联系我们。"),
]

def render_body():
    out = []
    for item in BODY:
        tag, content = item[0], item[1]
        if tag == "p":
            out.append(f"<p>{content}</p>")
        elif tag == "p_em":
            out.append(f"<p><em>{content}</em></p>")
        elif tag == "h2":
            out.append(f"<h2>{content}</h2>")
        elif tag == "blockquote":
            out.append(f"<blockquote><p>{content}</p></blockquote>")
        elif tag in ("ul", "ol"):
            lis = "".join(f"<li>{li}</li>" for li in content)
            out.append(f"<{tag}>\n{lis}\n</{tag}>")
    return "\n".join(out)

def gen_article(url_abs, site_name, breadcrumb_blog_url):
    article_json = (
        '{"@context": "https://schema.org", "@type": "Article", "headline": "%s", '
        '"description": "%s", "author": {"@type": "Person", "name": "何自刚"}, '
        '"publisher": {"@type": "Organization", "name": "%s"}, '
        '"datePublished": "%s", "dateModified": "%s", '
        '"mainEntityOfPage": "%s", "url": "%s"}'
    ) % (TITLE, DESC, site_name, DATE, DATE, url_abs, url_abs)
    breadcrumb_json = (
        '{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['
        '{"@type": "ListItem", "position": 1, "name": "首页", "item": "https://najieip.com/"}, '
        '{"@type": "ListItem", "position": 2, "name": "博客", "item": "%s"}, '
        '{"@type": "ListItem", "position": 3, "name": "%s"}]}'
    ) % (breadcrumb_blog_url, TITLE)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — 纳杰觅理</title>
<link rel="stylesheet" href="/style.css">
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "c80241f3caa4e708a12ed93baec1bde"}}'></script>
<meta name="description" content="{DESC}">
<meta name="keywords" content="{KEYWORDS}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url_abs}">
<meta property="og:site_name" content="{site_name}">
<meta property="og:image" content="{PEXELS_IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{OG_DESC}">
<link rel="canonical" href="{url_abs}">
<script type="application/ld+json">
{article_json}
</script>
<script type="application/ld+json">
{breadcrumb_json}
</script>
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
<h1>{TITLE}</h1>
{render_body()}
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
"""
    return html

def redirect_page(target_url):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={target_url}">
<link rel="canonical" href="https://najieip.com{target_url}">
<title>{TITLE}</title>
</head>
<body>
<p>文章已迁移：<a href="{target_url}">{TITLE}</a></p>
</body>
</html>
"""

def card_html(href, org):
    tag_spans = "".join(f'<span class="tag">{t}</span>' for t in TAGS[:3])
    return f"""  <div class="article-card">
    <h2><a href="{href}">{TITLE}</a></h2>
    <div class="meta">{tag_spans} {DATE} · {org}</div>
    <p>{CARD_SUMMARY}</p>
  </div>"""

def main():
    # 1. blog/ 精修版 (主博客)
    blog_url = f"https://najieip.com/blog/{SLUG}"
    with open(os.path.join(ROOT, f"blog/{SLUG}"), "w", encoding="utf-8") as f:
        f.write(gen_article(blog_url, "爱普纳杰专利所", "https://najieip.com/blog/"))
    # 2. mili/blog/ 精修版 (觅理)
    mili_url = f"https://najieip.com/mili/blog/{SLUG}"
    with open(os.path.join(ROOT, f"mili/blog/{SLUG}"), "w", encoding="utf-8") as f:
        f.write(gen_article(mili_url, "觅理律师事务所", "https://najieip.com/mili/blog/"))
    # 3. articles/ 旧路径 → 跳转页
    with open(os.path.join(ROOT, f"articles/{SLUG}"), "w", encoding="utf-8") as f:
        f.write(redirect_page(f"/blog/{SLUG}"))
    # 4. 主博客索引卡片 (插到 <div class="container"> 之后)
    idx = os.path.join(ROOT, "blog/index.html")
    s = open(idx, encoding="utf-8").read()
    assert f"/blog/{SLUG}" not in s, "blog index 已有该文章!"
    card = card_html(f"/blog/{SLUG}", "纳杰知识产权")
    s2 = s.replace('<div class="container">\n', '<div class="container">\n' + card + "\n", 1)
    assert s2 != s, "blog index 找不到 container 锚点"
    open(idx, "w", encoding="utf-8").write(s2)
    # 5. mili 博客索引卡片
    midx = os.path.join(ROOT, "mili/blog/index.html")
    m = open(midx, encoding="utf-8").read()
    assert f"./{SLUG}" not in m, "mili index 已有该文章!"
    mcard = card_html(f"./{SLUG}", "觅理律师事务所")
    m2 = m.replace('<div class="container">\n', '<div class="container">\n' + mcard + "\n", 1)
    assert m2 != m, "mili index 找不到 container 锚点"
    open(midx, "w", encoding="utf-8").write(m2)
    # 6. sitemap 增加两条
    sp = os.path.join(ROOT, "sitemap.xml")
    sm = open(sp, encoding="utf-8").read()
    assert SLUG not in sm, "sitemap 已有该文章!"
    entries = []
    for u in (blog_url, mili_url):
        entries.append(f"""  <url>
    <loc>{u}</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")
    sm2 = sm.replace("</urlset>", "\n".join(entries) + "\n</urlset>", 1)
    assert sm2 != sm
    open(sp, "w", encoding="utf-8").write(sm2)
    # 7. articles.json: 把 /articles/20260905 单条 → 三条 (blog/mili/articles)
    ap = os.path.join(ROOT, "articles.json")
    data = json.load(open(ap, encoding="utf-8"))
    data = [a for a in data if SLUG not in a["url"]]
    new_entries = [
        {"url": f"/blog/{SLUG}", "title": TITLE, "date": DATE, "site": "najie"},
        {"url": f"/mili/blog/{SLUG}", "title": TITLE, "date": DATE, "site": "mili"},
        {"url": f"/articles/{SLUG}", "title": TITLE, "date": DATE, "site": "najie"},
    ]
    data = new_entries + data
    json.dump(data, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 8. deploy-log
    lp = os.path.join(ROOT, "site-inbox/deploy-log.json")
    log = json.load(open(lp, encoding="utf-8"))
    if isinstance(log, dict):
        deploys = log["deploys"]
    else:
        deploys = log
    deploys.append({
        "date": "2026-09-05", "time": "22:10",
        "url": blog_url,
        "status": "deployed",
        "note": "ART-0078开源数据别乱用精修归位 blog+mili/blog(JSON-LD/OG/canonical补全,**转strong), articles旧路径改跳转, 主blog+mili索引+sitemap+articles.json更新",
    })
    json.dump(log, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DEPLOY GENERATED OK")

if __name__ == "__main__":
    main()
