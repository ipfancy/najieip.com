#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-14 当日新文六项 + 索引 + 正文包含"""
import os, re, json, glob, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
IDX = {"main": os.path.join(REPO, "blog/index.html"),
       "mili": os.path.join(REPO, "mili/blog/index.html"),
       "najie": os.path.join(REPO, "najie/blog/index.html"),
       "aipunajie": os.path.join(REPO, "aipunajie/blog/index.html")}

# 当日 git 新增文章页（修正：无前导斜杠）
out = subprocess.run(["git", "-C", REPO, "log", "--since=3.days", "--name-only",
                      "--diff-filter=AM", "--pretty=format:"], capture_output=True, text=True).stdout
newpages = sorted({l.strip() for l in out.splitlines()
                   if re.match(r"^(mili|najie|aipunajie)/blog/", l.strip())
                   and l.strip().endswith(".html") and not l.strip().endswith("index.html")})
print(f"=== 近3日 git 新增/修改文章页: {len(newpages)} ===")
for p in newpages:
    print("  ", p)

def textify(html):
    b = html
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<(h1|h2)[^>]*>.*?</\1>", " ", b, flags=re.S)
    b = re.sub(r"<figure.*?</figure>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    b = b.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'")
    b = re.sub(r"[“”\"'’「」『』【】:：\s|*\-]", "", b)
    return b

BYLINES = ["何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "北京纳杰知识产权代理有限公司 何自刚",
           "何自刚｜知识产权律师｜纳杰觅理", "何自刚 | 知识产权律师 | 纳杰觅理"]

print("\n=== 当日新文逐页六项 + 正文包含 ===")
for p in newpages:
    fp = os.path.join(REPO, p)
    if not os.path.exists(fp):
        print(f"  {p}: MISSING FILE"); continue
    t = open(fp, encoding="utf-8", errors="ignore").read()
    slug = os.path.basename(p).replace(".html", "")
    h1 = len(re.findall(r"<h1[ >]", t))
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ldok = 0
    types = []
    for l in lds:
        try:
            o = json.loads(l); ldok += 1
            types.append(o.get("@type") if isinstance(o, dict) else "?")
        except Exception as e:
            types.append("BAD:" + str(e)[:30])
    ogimg = "og:image" in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    mtitle = re.search(r"<title>(.*?)</title>", t, re.S)
    title = mtitle.group(1) if mtitle else ""
    rep = desc.strip().rstrip(" —") in title or title.split(" —")[0].strip() in desc
    stars = len(re.findall(r"[0-9*]\*{2}[0-9.]*", t))
    stars_all = t.count("**")
    baretab = len(re.findall(r"<p>\s*\|", t))
    style = ("<style>" in t) or ("/style.css" in t)
    ctx = t.count("https://schema.org")
    cano = re.search(r'<link rel="canonical" href="([^"]*)"', t)
    cano_v = cano.group(1) if cano else ""
    cano_ok = cano_v.endswith(p)
    # 正文包含
    md = os.path.expanduser("~/wiki/digital-employees/articles/" + p.split("/")[1].replace(".html", ".md"))
    cont = "n/a"
    if os.path.exists(md):
        mdt = open(md, encoding="utf-8").read()
        mdt = re.sub(r"^---.*?---\s*", "", mdt, flags=re.S)
        mlines = []
        for line in mdt.splitlines():
            s = line.strip()
            if not s or s.startswith("<!--") or s.startswith("!["):
                continue
            if re.match(r"^#{1,6}\s", s):
                continue
            if re.fullmatch(r"\*\*[^*\n]{1,30}\*\*", s) and not s.endswith(("。", "！", "？")):
                continue
            if re.match(r"^[一二三四五六七八九十]、", s):
                continue
            if "|" in s and re.fullmatch(r"[\s|:\-]+", s):
                continue
            l = re.sub(r"^\d+\.\s*", "", s)
            l = re.sub(r"^[-*]\s+", "", l)
            l = l.replace("**", "").replace("*", "")
            mlines.append(l)
        mdn = textify("\n".join("".join(mlines).split("\n")))
        for b in BYLINES:
            mdn = mdn.replace(textify(b), "")
        art = re.search(r"<article.*?</article>", t, re.S)
        seg = art.group(0) if art else t[t.find("<body"):]
        pgn = textify(seg)
        for b in BYLINES:
            pgn = pgn.replace(textify(b), "")
        cont = (mdn in pgn)
        if not cont:
            # 找差异位置
            d = 0
            while d < min(len(mdn), len(pgn)) and mdn[d] == pgn[d]:
                d += 1
            cont = f"FALSE diff_at={d} len_md={len(mdn)} len_pg={len(pgn)} md[{d}:{d+40}]={mdn[d:d+40]!r} pg={pgn[d:d+40]!r}"
    hits = {}
    for k, f in IDX.items():
        if os.path.exists(f):
            c = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), open(f, encoding="utf-8", errors="ignore").read()))
            if c: hits[k] = c
    print(f"\n  --- {p} ({os.path.getsize(fp)}B) ---")
    print(f"    h1={h1} ld={ldok}/{len(lds)} types={types} schema_ctx={ctx}")
    print(f"    og:image={ogimg} style={style} desc复读={rep} desc_len={len(desc)}")
    print(f"    stars={stars}/{stars_all} bare_table_p={baretab} canonical_ok={cano_ok} ({cano_v})")
    print(f"    md包含={cont}")
    print(f"    idx={hits if hits else 'NONE'}")
