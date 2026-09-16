#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-0916-legacy-urls.py — 处置 Mac 端交接单遗留项 1（/articles/ 旧路径）

做四件事（幂等，先 --dry-run 后 --apply）：
  A. articles.json：/articles/ 旧条目 → 三主体规范路径；纯重复条目删除；site 字段校正
  B. 两篇「仅存 /articles/ 副本」的孤儿页迁入 najie/blog（复制 + 索引卡片 + JSON-LD）
  C. /articles/*.html 真内容副本 → 统一跳转桩（canonical + refresh + noindex,follow）
  D. sitemap.xml：剔除全部跳转/别名 loc（/articles/、根级 /blog/ 桩、org 目录桩）、
     非 200 死链 loc、空 loc、中文原样/%编码重复登记 → 并补入迁移页 loc

不写盘时只打印计划；--apply 写盘并输出前后 md5 / 条数。
"""
import argparse, collections, glob, hashlib, html, json, os, re, shutil, sys
import urllib.parse
import xml.dom.minidom as minidom

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)
SITE = "https://najieip.com"
ORGS = ("najie", "aipunajie", "mili")
INS = {"najie": "北京纳杰知识产权代理有限公司",
       "aipunajie": "北京爱普纳杰专利代理事务所",
       "mili": "北京觅理律师事务所"}
OG_IMG = {"najie": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200",
          "aipunajie": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200",
          "mili": "https://images.pexels.com/photos/5669602/pexels-photo-5669602.jpeg?auto=compress&cs=tinysrgb&w=1200"}
# 孤儿页归属：案件性质优先；与本族群既有归位一致（中国专利奖申报策略篇已在 najie/blog）
ORPHAN_ORG = {"20260829-micromovie-regulation-ip-checklist.html": "najie",
              "20260829-patent-award-quota-tightening.html": "najie"}

def read(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""

def title_of(p):
    m = re.search(r"<title>(.*?)</title>", read(p), re.S)
    return html.unescape(m.group(1).strip()) if m else ""

def canonical_of(p):
    h = read(p)
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', h, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r'http-equiv=["\']refresh["\'][^>]*url=([^"\'>\s]+)', h, re.I)
    return m.group(1).strip() if m else None

def rel(url):
    """绝对/相对 → 站内相对路径（含前导 /）"""
    u = urllib.parse.unquote(url.strip())
    if u.startswith(SITE):
        u = u[len(SITE):]
    return u if u.startswith("/") else "/" + u

# ---------------------------------------------------------------- 索引
org_files = set()
org_by_base = collections.defaultdict(list)
org_by_title = collections.defaultdict(list)
for org in ORGS:
    for f in glob.glob(f"{org}/blog/*.html"):
        p = f.replace("\\", "/")
        if os.path.basename(p) == "index.html":
            continue
        org_files.add("/" + p)
        org_by_base[os.path.basename(p)].append("/" + p)
        t = title_of(p)
        if t:
            org_by_title[t].append("/" + p)

def resolve_target(u, title):
    """返回 (target_or_None, how)"""
    base = u.rsplit("/", 1)[-1]
    if base in org_by_base:
        return org_by_base[base][0], "same-basename"
    if os.path.exists(u.lstrip("/")):
        c = canonical_of(u.lstrip("/"))
        if c:
            t = rel(c)
            if t in org_files:
                return t, "canonical/refresh-target"
    t = title_of(u.lstrip("/")) if os.path.exists(u.lstrip("/")) else ""
    cand = org_by_title.get(t) or org_by_title.get(title)
    if cand:
        return cand[0], "title-match"
    if base in ORPHAN_ORG:
        return f"/{ORPHAN_ORG[base]}/blog/{base}", "migrate-orphan"
    return None, "no-target"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = not args.apply
    print("=" * 78)
    print("模式:", "DRY-RUN（不写盘）" if dry else "APPLY（写盘）")

    arts = json.load(open("articles.json", encoding="utf-8"))
    raw_sitemap = open("sitemap.xml", encoding="utf-8").read()
    locs = re.findall(r"<loc>([^<]*)</loc>", raw_sitemap)

    # ============================================================ A. articles.json
    redirect_map = {}          # /articles/旧路径 → 三主体规范路径（供 CF Bulk Redirects）
    canon_urls = [a["url"] for a in arts if not a["url"].startswith("/articles/")]
    canon_set = set(canon_urls)
    plan_a, dropped, migrated = [], [], []
    seen_new = set()
    for a in arts:
        u = a["url"]
        if not u.startswith("/articles/"):
            a["site"] = org_of(u) or a.get("site")
            plan_a.append(a)
            continue
        t, how = resolve_target(u, a.get("title", ""))
        if t is None:
            dropped.append((u, a.get("title", ""), "无规范目标（站点从未上线）"))
            continue
        redirect_map[u] = t
        if t in canon_set or t in seen_new:
            dropped.append((u, a.get("title", ""), f"重复条目 → 已在 {t}"))
            continue
        new = dict(a)
        new["url"] = t
        new["site"] = org_of(t)
        seen_new.add(t)
        plan_a.append(new)
        if how == "migrate-orphan":
            migrated.append((u, t))
    # 排序（日期倒序，稳定）+ 唯一校验
    plan_a.sort(key=lambda x: x.get("date") or "", reverse=True)
    urls = [a["url"] for a in plan_a]
    assert len(urls) == len(set(urls)), "articles.json 出现重复 URL"
    assert all(org_of(u) for u in urls), "articles.json 存在非三主体 URL"
    print(f"\n[A] articles.json: {len(arts)} → {len(plan_a)} 条 "
          f"（删除旧条目 {len(dropped)}，含迁移 {len(migrated)}）")
    for u, t, why in dropped:
        print(f"     - {u}\n         {why}")
    for u, t in migrated:
        print(f"     ↻ {u} → {t}")

    # ============================================================ B. 孤儿页迁移
    for u, t in migrated:
        src, dst = u.lstrip("/"), t.lstrip("/")
        org = (org_of(t) or "najie").strip("/")
        h = read(src)
        body_first = first_paragraph(h)
        h2 = h
        if 'name="description"' not in h2:
            h2 = h2.replace("</head>", f'<meta name="description" content="{esc(body_first)}">\n'
                                      f'<link rel="canonical" href="{SITE}{t}">\n'
                                      f'<meta property="og:title" content="{esc(title_of(src))}">\n'
                                      f'<meta property="og:description" content="{esc(body_first)}">\n'
                                      f'<meta property="og:image" content="{OG_IMG[org]}">\n'
                                      f'<meta property="og:url" content="{SITE}{t}">\n'
                                      f'<meta property="og:type" content="article">\n'
                                      f'<meta name="twitter:card" content="summary_large_image">\n'
                                      "</head>", 1)
        else:
            h2 = re.sub(r'(<link[^>]+rel=["\']canonical["\'][^>]*href=["\'])[^"\']*',
                        r"\g<1>" + SITE + t, h2, count=1, flags=re.I)
        print(f"\n[B] 迁移 {src} → {dst}（文件复制 + SEO 头部）")
        if not dry:
            open(dst, "w", encoding="utf-8").write(h2)
        # 索引卡片 + JSON-LD
        idx = f"{org}/blog/index.html"
        adate = next((a.get("date") or "" for a in arts if a["url"] == u), "")
        card_fn = add_index_card if org == "aipunajie" else add_index_card_std
        print(f"     索引 {idx}: 卡片 + JSON-LD blogPost  {'(dry-run 跳过)' if dry else ''}")
        if not dry:
            card_fn(idx, t, title_of(dst), body_first, adate)

    # ============================================================ C. /articles/ 真内容副本 → 跳转桩
    stubs = []
    for f in sorted(glob.glob("articles/*.html")):
        p = f.replace("\\", "/")
        h = read(p)
        if re.search(r'http-equiv=["\']refresh', h, re.I):
            continue                                    # 已是桩
        u = "/" + p
        t, how = resolve_target(u, title_of(p))
        if not t:
            print(f"     ⚠️ 无目标，保留原样: {p}")
            continue
        if os.path.abspath(t.lstrip("/")) == os.path.abspath(p):
            continue                                    # 目标即自身
        stubs.append((p, t, title_of(p)))
        redirect_map.setdefault(u, t)
    print(f"\n[C] 真内容副本 → 跳转桩: {len(stubs)} 个")
    for p, t, ti in stubs:
        print(f"     {p} → {t}")
        if not dry:
            write_stub(p, ti, t)

    # CF Bulk Redirects 素材（旧路径 → 规范路径，301）
    csv_path = "site-inbox/cf-redirects-articles-20260916.csv"
    with open(csv_path, "w", encoding="utf-8") as fh:
        fh.write("source,target,status,preserve_query_string,preserve_path_suffix\n")
        for u in sorted(redirect_map):
            t = redirect_map[u]
            fh.write(f"{SITE}{urllib.parse.quote(u)},{SITE}{urllib.parse.quote(t)},301,true,false\n")
    print(f"\n[CF] 301 映射素材 → {csv_path}（{len(redirect_map)} 条）")

    # ============================================================ D. sitemap 清理
    # 默认「保留」，只有拿到证据才删（避免误删首页/robots/llms 等合法 loc）
    remove, keep_notes = [], collections.Counter()
    loc_set = set(locs)
    seen_paths = set()
    for l in locs:
        path = urllib.parse.unquote(l[len(SITE):]) if l.startswith(SITE) else l
        if path == "":
            continue                                          # 首页，保留
        # ① 同一 URL 的两种写法（中文原样 / %编码）→ 只留一种
        if path in seen_paths:
            remove.append(l); keep_notes["重复登记（同 URL 两种写法）"] += 1; continue
        raw_loc, enc_loc = SITE + path, SITE + urllib.parse.quote(path)
        if raw_loc != enc_loc:                            # 路径含中文 → 可能有两种写法
            pref = unicode_pref(path)
            keep_one, drop_one = ((raw_loc, enc_loc) if pref == "keep-raw" else (enc_loc, raw_loc))
            if l == drop_one and drop_one in loc_set and keep_one in loc_set:
                remove.append(l)
                keep_notes["重复登记（保留中文原样形式）" if pref == "keep-raw"
                           else "重复登记（保留 %编码 形式）"] += 1
                continue
        # ② /articles/ 旧路径：一律不再登记（handoff 遗留项 1）
        if path.startswith("/articles/"):
            reason = "非 200 死链 loc" if not local_exists(path) else "/articles/ 旧路径（跳转/别名）"
            remove.append(l); keep_notes[reason] += 1; seen_paths.add(path); continue
        # ③ 文件不存在 → 死链 loc
        if not local_exists(path):
            remove.append(l); keep_notes["非 200 死链 loc"] += 1; seen_paths.add(path); continue
        # ④ 跳转/别名页
        fp = local_file(path)
        h = read(fp)
        refresh = bool(re.search(r'http-equiv=["\']refresh', h, re.I))
        noindex = "noindex" in h.lower()
        canon = canonical_of(fp)
        if refresh and noindex:
            remove.append(l); keep_notes["跳转/别名页（noindex+refresh）"] += 1; seen_paths.add(path); continue
        if refresh and canon and canonical_targets_other(path.lstrip("/"), canon):
            remove.append(l); keep_notes["跳转/别名页（refresh+canonical 他指）"] += 1; seen_paths.add(path); continue
        seen_paths.add(path)
    # 迁移页 loc 补入
    add = [SITE + t for _, t in migrated]
    print(f"\n[D] sitemap: {len(locs)} loc → 删除 {len(remove)} → 剩余 {len(locs) - len(remove)}"
          f" + 新增 {len(add)}")
    for k, v in keep_notes.most_common():
        print(f"     {k}: {v}")
    print("     删除清单（前 8）:", [urllib.parse.unquote(r) for r in remove[:8]])

    # [D1] 别名 loc 的目标必须在保留集中（否则等于丢了索引入口）
    kept = [l for l in locs if l not in set(remove)] + add
    kept_set = set(kept)
    lost_targets = []
    for l in remove:
        path = urllib.parse.unquote(l[len(SITE):]) if l.startswith(SITE) else l
        fp = local_file(path)
        if not path or not os.path.exists(fp):
            continue
        c = canonical_of(fp)
        if c:
            tgt = c if c.startswith("http") else SITE + rel(c)
            if tgt not in kept_set and tgt not in (SITE + path,):
                lost_targets.append((path, tgt))
    print(f"\n[D1] 被删别名 loc 的目标是否仍在 sitemap: 失联 {len(lost_targets)}")
    for a, b in lost_targets[:10]:
        print("     ⚠️", a, "→", b)

    print("\n[D2] 交叉校验：articles.json 每个 URL 是否有 sitemap loc")
    remain = [l for l in locs if l not in remove] + add
    remain_paths = set(urllib.parse.unquote(l.replace(SITE, "")) for l in remain)
    gap = [u for u in urls if u not in remain_paths]
    print("     缺失:", len(gap), gap[:5])

    # ============================================================ E. 写盘
    if dry:
        print("\n[dry-run] 未写盘。")
        return 0
    # 备份
    ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    for f in ("articles.json", "sitemap.xml"):
        shutil.copy2(f, f"{f}.bak_{ts}")
    json.dump(plan_a, open("articles.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open("articles.json", "a").write("\n")

    remove_set = set(remove)

    def drop(m):
        mm = re.search(r"<loc>([^<]*)</loc>", m.group(0))
        if mm and mm.group(1) in remove_set:
            return ""
        return m.group(0)
    new_sm = re.sub(r"[ \t]*<url>.*?</url>\n?", drop, raw_sitemap, flags=re.S)
    if add:
        block = "".join(f"  <url>\n    <loc>{a}</loc>\n    <changefreq>monthly</changefreq>\n"
                        f"    <priority>0.7</priority>\n  </url>\n" for a in add)
        new_sm = new_sm.replace("</urlset>", block + "</urlset>")
    minidom.parseString(new_sm)                          # XML 合法性校验
    if not new_sm.endswith("\n"):
        new_sm += "\n"
    open("sitemap.xml", "w", encoding="utf-8").write(new_sm)
    print(f"\n[E] 已写盘 | 备份后缀 .bak_{ts} | sitemap loc {len(locs)} → "
          f"{len(re.findall(r'<loc>', new_sm))}")
    return 0

# ---------------------------------------------------------------- helpers
def local_exists(path):
    p = path.lstrip("/")
    if p == "":
        return True
    return os.path.exists(p) or os.path.exists(p.rstrip("/") + "/index.html")

def local_file(path):
    p = path.lstrip("/")
    if os.path.isdir(p):
        return p.rstrip("/") + "/index.html"
    return p

def unicode_pref(path):
    """中文原样 / %编码 重复登记时保哪一种：与页面 canonical 写法一致者优先，无 canonical 保 %编码"""
    fp = local_file(path)
    c = canonical_of(fp) if os.path.exists(fp) else None
    if c:
        c_raw = c[len(SITE):] if c.startswith(SITE) else c
        if "%" in c_raw and urllib.parse.unquote(c_raw) == path:
            return "keep-encoded"
        return "keep-raw"
    return "keep-encoded"

def org_of(u):
    m = re.match(r"^/(najie|aipunajie|mili)/", u)
    return m.group(1) if m else None

def esc(s):
    return html.escape(s or "", quote=True)

def first_paragraph(h):
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.I | re.S)
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", body, re.S):
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        t = re.sub(r"\s+", "", t).replace("**", "")
        if len(t) >= 30:
            return t[:150]
    return html.unescape(title_of_str(h))[:150]

def title_of_str(h):
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    return html.unescape(m.group(1).strip()) if m else ""

def canonical_targets_other(p, canon):
    c = rel(canon)
    return c.rstrip("/") != "/" + p.rstrip("/")

def write_stub(path, title, target):
    open(path, "w", encoding="utf-8").write(
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        f"<title>{html.escape(title)}</title>\n"
        f'<meta name="robots" content="noindex, follow">\n'
        f'<meta http-equiv="refresh" content="0; url={target}">\n'
        f'<link rel="canonical" href="{SITE}{target}">\n'
        "</head>\n<body>\n"
        f'<p>本文已迁移至 <a href="{target}">{html.escape(title)}</a></p>\n'
        "</body>\n</html>\n")

def add_index_card_std(idx, url, title, desc, date=""):
    """najie/blog、mili/blog 模板：<div class="container"> 锚点 + .article-card / h2>a / .meta / p"""
    h = read(idx)
    slug = url.rsplit("/", 1)[-1]
    if slug in h:
        print(f"     （已存在卡片，跳过）{slug}")
        return
    org = idx.split("/")[0]
    name = INS[org]
    card = (f'  <div class="article-card">\n'
            f'    <h2><a href="./{slug}">{html.escape(title.split(" — ")[0])}</a></h2>\n'
            f'    <div class="meta">{esc(date)} · {name}</div>\n'
            f'    <p>{esc(desc)}</p>\n  </div>\n')
    anchor = '<div class="container">\n'
    assert h.count(anchor) == 1, f"{idx} 锚点不唯一"
    h = h.replace(anchor, anchor + card, 1)
    h = add_jsonld(idx, h, slug, title, desc, date)
    open(idx, "w", encoding="utf-8").write(h)

def add_jsonld(idx, h, slug, title, desc, date):
    """向 Blog.blogPost 数组头部插入一条 BlogPosting
    幂等判据只看 JSON-LD 块本身：卡片先插入会让整文件包含 slug，用整文件判据会漏插（2026-09-16 实测）"""
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    if not m or '"blogPost"' not in m.group(1):
        print(f"     ⚠️ {idx} 未找到 blogPost 数组，跳过 JSON-LD")
        return h
    d = json.loads(m.group(1))
    posts = d.get("blogPost", [])
    if any(p.get("url", "").rsplit("/", 1)[-1] == slug for p in posts):
        return h
    entry = {"@type": "BlogPosting", "headline": title.split(" — ")[0],
             "url": f"{SITE}/{idx.split('/')[0]}/blog/{slug}", "description": desc}
    if date:
        entry["datePublished"] = date
    d["blogPost"] = [entry] + posts
    return h[:m.start(1)] + json.dumps(d, ensure_ascii=False) + h[m.end(1):]

def add_index_card(idx, url, title, desc, date=""):
    """aipunajie/blog 模板：<div class="articles"> 锚点 + .date / h3>a / .excerpt"""
    h = read(idx)
    slug = url.rsplit("/", 1)[-1]
    if slug in h:
        return
    card = (f'  <div class="date">{esc(date)}</div>\n'
            f'  <h3><a href="./{slug}">{esc(title.split(" — ")[0])}</a></h3>\n'
            f'  <p class="excerpt">{esc(desc)}</p>\n')
    anchor = '<div class="articles">\n'
    assert h.count(anchor) == 1, f"{idx} 锚点不唯一"
    h = h.replace(anchor, anchor + card, 1)
    h = add_jsonld(idx, h, slug, title, desc, date)
    open(idx, "w", encoding="utf-8").write(h)

if __name__ == "__main__":
    sys.exit(main())
