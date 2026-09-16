#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-0916-seo-meta-backfill.py — 交接单遗留项 3：历史规范页批量补齐 SEO 头部

范围：非跳转桩、非 noindex、非 dashboard/site-inbox/archive 的规范页；
      只补「已经能从严不编造的信息」——
        canonical / og:url  ← 页面自身路径
        og:title            ← 既有 <title>（去尾部署名）
        description / og:description ← 既有 meta description，否则正文首个 ≥20 字段落（≤150 字）
        og:image / og:type / twitter:card ← 机构默认资源 + 页面类型
幂等：逐标签判存在即跳过；缺正文摘要的页面只补 URL/标题类标签，不编造描述。
用法：python3 site-inbox/fix-0916-seo-meta-backfill.py [--apply]
"""
import argparse, glob, html, os, re, sys

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)
SITE = "https://najieip.com"
IMG = {"mili": "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200",
       "_default": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200"}
EXCLUDE_DIRS = ("site-inbox/", "archive/", "dashboard/", "node_modules/")

def read(p):
    return open(p, encoding="utf-8", errors="ignore").read()

def page_url(path):
    if os.path.basename(path) == "index.html":
        return SITE + "/" + os.path.dirname(path).replace("\\", "/").rstrip("/") + "/"
    return SITE + "/" + path.replace("\\", "/")

def first_paragraph(h, limit=150):
    body = re.sub(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", h, flags=re.I | re.S)
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", body, re.S):
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        t = re.sub(r"\s+", " ", t).replace("**", "").strip()
        t = re.sub(r"^[>》\s]+", "", t).strip()          # 去 blockquote 前导标记
        if len(t) >= 20:
            if len(t) > limit:
                cut = t[:limit]
                for sep in ("。", "！", "？", "；", ". "):
                    i = cut.rfind(sep)
                    if i >= 40:
                        cut = cut[:i + 1]
                        break
                t = cut
            return t
    return ""

def esc(s):
    return html.escape(s, quote=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = not args.apply

    files = sorted(f.replace("\\", "/") for f in glob.glob("**/*.html", recursive=True))
    targets, no_desc, skipped = [], [], []
    for p in files:
        if any(s in p for s in EXCLUDE_DIRS):
            continue
        if os.path.basename(p) == "404.html" or "verify" in p.lower():
            continue
        h = read(p)
        head = h.split("</head>")[0]
        if "</head>" not in h:
            skipped.append((p, "无 </head>（结构异常，跳过）"))
            continue
        if re.search(r'http-equiv=["\']refresh', h, re.I):
            continue
        if re.search(r'name=["\']robots["\'][^>]*noindex', head, re.I):
            continue
        need = []
        if not re.search(r'rel=["\']canonical["\']', head, re.I):
            need.append("canonical")
        for tag in ("og:title", "og:description", "og:image", "og:url", "og:type"):
            if not re.search(r'property=["\']' + tag + r'["\']', head, re.I):
                need.append(tag)
        if not re.search(r'name=["\']twitter:card["\']', head, re.I):
            need.append("twitter:card")
        if not re.search(r'name=["\']description["\']', head, re.I):
            need.append("description")
        if not need:
            continue
        title = ""
        mt = re.search(r"<title>(.*?)</title>", h, re.S)
        if mt:
            title = re.split(r"\s+[—|·]\s+", html.unescape(mt.group(1).strip()))[0]
        md = re.search(r'name=["\']description["\'][^>]*content=["\']([^"\']*)', head, re.I)
        desc = html.unescape(md.group(1)) if md else first_paragraph(h)
        if "description" in need and not desc:
            need.remove("description")
            need = [x for x in need if x != "og:description"]
            no_desc.append(p)
        if not title:
            skipped.append((p, "无 <title>"))
            continue
        org = "mili" if p.startswith("mili/") or re.match(r"^(en|fr)/mili/", p) else "_default"
        tags = []
        url = page_url(p)
        for t in need:
            if t == "canonical":
                tags.append(f'<link rel="canonical" href="{url}">')
            elif t == "og:url":
                tags.append(f'<meta property="og:url" content="{url}">')
            elif t == "og:title":
                tags.append(f'<meta property="og:title" content="{esc(title)}">')
            elif t in ("description", "og:description"):
                tags.append(f'<meta {"name" if t == "description" else "property"}="{t}" content="{esc(desc)}">')
            elif t == "og:image":
                tags.append(f'<meta property="og:image" content="{IMG[org]}">')
            elif t == "og:type":
                tags.append('<meta property="og:type" content="%s">' %
                            ("website" if os.path.basename(p) == "index.html" else "article"))
            elif t == "twitter:card":
                tags.append('<meta name="twitter:card" content="summary_large_image">')
        targets.append((p, need, tags))

    print(f"待补页面 {len(targets)} 个；其中无法从正文取到摘要（只补其他标签）{len(no_desc)} 个")
    for p, need, tags in targets:
        print(f"\n  {p}\n    补 {len(need)} 项: {','.join(need)}")
        for t in tags:
            print("      ", t[:110])
    if no_desc:
        print("\n无正文摘要（不编造 description）:", no_desc)
    if skipped:
        print("跳过:", skipped)

    if dry:
        print("\n[dry-run] 未写盘")
        return 0
    for p, need, tags in targets:
        h = read(p)
        i = re.search(r"</head>", h, re.I).start()
        block = "".join(t + "\n" for t in tags)
        open(p, "w", encoding="utf-8").write(h[:i] + block + h[i:])
        got = read(p).split("</head>")[0]
        for t in need:
            key = ('rel="canonical"' if t == "canonical" else
                   f'property="{t}"' if t.startswith("og:") else f'name="{t}"')
            assert key in got, f"{p} 补 {t} 失败"
    print(f"\n✅ 已写入 {len(targets)} 个页面")
    return 0

if __name__ == "__main__":
    sys.exit(main())
