#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精修 site-inbox/trademark-compliance-selfcheck-20260810.html → 正式博客 HTML
处理: markdown残留(**/表格/>引用/[ ]/---/空<br>) → 干净HTML + 完整SEO头
输出: blog/trademark-compliance-selfcheck-20260810.html
      najie/blog/trademark-compliance-selfcheck-20260810.html
"""
import re, sys, html as html_mod

SRC = "/Users/ziganghe/wiki/najieip-verify/site-inbox/trademark-compliance-selfcheck-20260810.html"
OUT_MAIN = "/Users/ziganghe/wiki/najieip-verify/blog/trademark-compliance-selfcheck-20260810.html"
OUT_NAJIE = "/Users/ziganghe/wiki/najieip-verify/najie/blog/trademark-compliance-selfcheck-20260810.html"

TITLE = "你的商标这样做，可能被撤销——新商标法第56条自查清单"
DESC = "2027年1月1日起，新《商标法》第56条正式施行——即便商标已注册，只要\u201c以误导公众的方式使用\u201d，最高罚款25万，逾期不改直接撤销注册商标。15条企业IPR可直接打印使用的自查清单：形态一致、表述真实、管理闭环三个维度。"
KEYWORDS = "商标法,商标撤销,第56条,商标使用合规,误导性使用,商标自查清单,商标管理,何自刚"
CANONICAL_MAIN = "https://najieip.com/blog/trademark-compliance-selfcheck-20260810.html"
CANONICAL_NAJIE = "https://najieip.com/najie/blog/trademark-compliance-selfcheck-20260810.html"
DATE = "2026-08-10"

with open(SRC, encoding="utf-8") as f:
    raw = f.read()

# ---- 提取 body 内 <article> 内容 ----
m = re.search(r"<article>(.*?)</article>", raw, re.S)
body_inner = m.group(1) if m else raw

# ---- 1. 处理 markdown 表格：把连续的 <p>|...|</p> 合并成 <table> ----
def md_table_to_html(lines):
    """lines: list of <p>|...|</p> strings -> list with table html"""
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 检测表格行: <p>| ... |</p>
        if re.match(r"^\s*<p>\s*\|", line):
            rows = []
            while i < len(lines) and re.match(r"^\s*<p>\s*\|", lines[i]):
                cells_raw = re.sub(r"^\s*<p>\s*", "", lines[i])
                cells_raw = re.sub(r"\s*</p>\s*$", "", cells_raw)
                cells = [c.strip() for c in cells_raw.strip().strip("|").split("|")]
                # 跳过分隔行 |---|---|
                if all(re.fullmatch(r"-{2,}", c) for c in cells if c):
                    i += 1
                    continue
                rows.append(cells)
                i += 1
            if rows:
                header = rows[0]
                t = ["<table><thead><tr>"]
                for c in header:
                    t.append(f"<th>{c}</th>")
                t.append("</tr></thead><tbody>")
                for r in rows[1:]:
                    t.append("<tr>")
                    for c in r:
                        t.append(f"<td>{c}</td>")
                    t.append("</tr>")
                t.append("</tbody></table>")
                out.append("".join(t))
            continue
        out.append(line)
        i += 1
    return out

# ---- 2. 将 body 按 <br> 拆分为逻辑行，再处理 ----
# 先移除所有 <br> 标签（内容本身已有段落包裹）
body_inner = re.sub(r"<br\s*/?>", "", body_inner)
# 保持段落，拆分处理
# 表格: 表格行是 <p>|...|</p> 相邻出现，用上面函数处理需要按行处理。
# 简化：把 <p> 标签拆开处理表格，其余保留。
# 方法：先把每个 <p>...</p> 独立成一行
chunks = re.split(r"(<p>.*?</p>)", body_inner, flags=re.S)
lines = [c for c in chunks if c.strip()]
lines = md_table_to_html(lines)

def fix_bold(s):
    """**text** -> <strong>text</strong>"""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

def fix_quote(s):
    """&gt; xxx 引用 -> blockquote"""
    if s.startswith("<p>&gt;") or s.startswith("<p> &gt;") or re.match(r"^\s*<p>[&]gt;", s):
        inner = re.sub(r"^\s*<p>\s*&gt;\s*", "", s)
        inner = re.sub(r"\s*</p>\s*$", "", inner)
        return f"<blockquote><p>{inner}</p></blockquote>"
    return s

out_lines = []
for line in lines:
    line = fix_bold(line)
    line = fix_quote(line)
    # --- 分隔线
    if re.match(r"^\s*<p>\s*---\s*</p>\s*$", line):
        continue  # 删除分隔线（视觉噪音）
    # --- 原文斜体 *...* 行尾
    line = re.sub(r"<p>\s*\*(.+?)\*\s*</p>", r"<p><em>\1</em></p>", line)
    # [ ] 复选框 → ☐
    line = line.replace("[ ]", "☐")
    out_lines.append(line)

inner = "\n".join(out_lines)
# 清理多余空行
inner = re.sub(r"\n{3,}", "\n\n", inner)

# ---- 3. 组装完整 HTML ----
def build_html(canonical, brand_label):
    head = f"""<!DOCTYPE html>
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
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="纳杰知识产权">
<meta property="og:image" content="https://images.pexels.com/photos/3943716/pexels-photo-3943716.jpeg?auto=compress&cs=tinysrgb&w=1200">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<link rel="canonical" href="{canonical}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{TITLE}","description":"{DESC}","author":{{"@type":"Person","name":"何自刚"}},"publisher":{{"@type":"Organization","name":"纳杰知识产权"}},"datePublished":"{DATE}","dateModified":"{DATE}","mainEntityOfPage":"{canonical}","url":"{canonical}"}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"首页","item":"https://najieip.com/"}},{{"@type":"ListItem","position":2,"name":"博客","item":"{canonical.rsplit('/',1)[0]}/"}},{{"@type":"ListItem","position":3,"name":"{TITLE}"}}]}}
</script>
</head>
<body>
<nav><a href="/">← 首页</a></nav>
<article>
{inner}
</article>
<footer>
<p>© 2026 纳杰觅理 · 愛普納傑专利所 &amp; 觅理律所</p>
<p><a href="https://github.com/ipfancy/najieip.com">Open Source</a></p>
</footer>
</body>
</html>
"""
    return head

main_html = build_html(CANONICAL_MAIN, "爱普纳杰")
najie_html = build_html(CANONICAL_NAJIE, "纳杰")

with open(OUT_MAIN, "w", encoding="utf-8") as f:
    f.write(main_html)
with open(OUT_NAJIE, "w", encoding="utf-8") as f:
    f.write(najie_html)

# ---- 4. 验证：markdown 残留 = 0 ----
for p, name in [(OUT_MAIN, "main"), (OUT_NAJIE, "najie")]:
    with open(p, encoding="utf-8") as f:
        c = f.read()
    md_stars = len(re.findall(r"\*\*", c))
    md_table = len(re.findall(r"<p>\s*\|", c))
    md_gt = len(re.findall(r"&gt;", c))
    og_ok = c.count('property="og:') >= 4
    ld_ok = c.count('application/ld+json') >= 2
    print(f"{name}: size={len(c)}B, **残留={md_stars}, 表格残留={md_table}, &gt;残留={md_gt}, og={og_ok}, ld={ld_ok}")
    if md_stars or md_table or md_gt:
        sys.exit(1)
print("OK: 精修完成，markdown 残留为 0")
