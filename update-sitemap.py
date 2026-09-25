#!/usr/bin/env python3
"""update-sitemap.py — 增量合并 sitemap（只增不删，且只增「有效」URL）

从 articles.json 读取文章 URL，凡是 sitemap.xml 里还没有的，增量插入到
"文章"区块。绝不删除/替换 sitemap 中已有的任何 URL（含历史文章、多语言页、
旧路径跳转页）。

🔴 2026-09-17 加固（门丞）：本脚本此前无任何有效性校验，导致 sitemap 口径
   （见 siteops-seo-monitoring / 2026-09-16 遗留项回执）被反复回灌：
     · 61c39a2（09-16 15:40，Mac 端）一次加回 111 条，其中 96 条为根级
       /blog/ noindex 跳转壳 loc（已在 c1e3676、f94c3f7 清理过两次）
     · eb5dd3b（09-17 13:20）加回 47 条「无页面」死链 loc
       （siteops 于 6979c0f 明确「未被导入，待 go/no-go」，9 分钟后被覆盖）
   两条铁律：**目录里有文件才收录、是跳转壳不收录、同路径不重复登记。**
   跳过项会打印出来，便于人工复核（如需强制收录，用 --allow-missing）。

用法: python3 update-sitemap.py            # 增量合并
      python3 update-sitemap.py --check    # 只报告差异，不写文件
      python3 update-sitemap.py --allow-missing   # 关闭「文件存在」校验（慎用）
"""
import json, os, re, sys, urllib.parse
from datetime import datetime

SITE = os.environ.get("NAJIEIP_SITE", os.path.expanduser("~/wiki/najieip-verify"))
ARTICLES = os.path.join(SITE, "articles.json")
SITEMAP = os.path.join(SITE, "sitemap.xml")

ARTICLE_MARKER = "<!-- ========== 文章 ========== -->"
HOST = "https://najieip.com"


def get_existing_urls(content):
    """从 sitemap 文本提取已有全部 URL（含 <loc> 标签）"""
    return set(re.findall(r"<loc>(https://najieip\.com[^<]*)</loc>", content))


def is_redirect_shell(path):
    """跳转/别名页：含 meta refresh 的壳页（通常还带 noindex,follow）。"""
    try:
        low = open(path, encoding="utf-8", errors="ignore").read(4000).lower()
    except Exception:
        return False
    return 'http-equiv="refresh"' in low


def validate(url, existing_norm, allow_missing=False):
    """返回 None 表示可收录，否则返回跳过原因。"""
    rel = url[len(HOST):].lstrip("/")
    # 1) 同一路径不得重复登记（中文原样 vs %编码）
    if urllib.parse.unquote(url) in existing_norm:
        return "重复登记（同路径已以原样/%编码收录）"
    if not allow_missing:
        path = os.path.join(SITE, rel)
        # 2) 目录里没有这个文件 → 收录即产生 404 死链 loc
        if not os.path.exists(path):
            return "页面不存在（会变成非 200 loc）"
        # 3) 跳转壳 → 页面自身 noindex，收录与 noindex 指令矛盾
        if is_redirect_shell(path):
            return "跳转/别名页（noindex 壳，不应收录）"
    return None


def main():
    check_only = "--check" in sys.argv
    allow_missing = "--allow-missing" in sys.argv
    articles = json.load(open(ARTICLES, encoding="utf-8"))
    today = datetime.now().strftime("%Y-%m-%d")

    # 收集 articles.json 的文章 URL
    json_urls = {}
    seen = set()
    for a in articles:
        u = a.get("url", "")
        if not u:
            continue
        if "/blog/" not in u and "/articles/" not in u:
            continue
        if u in seen:
            continue
        seen.add(u)
        json_urls[f"{HOST}{u}"] = a.get("date", today)

    # 2026-09-25 加固（SiteOps）：除 articles.json 外，**同时扫描品牌博客目录**收录已落地文章页。
    # 根因：本守护原只从 articles.json 取数 → 上游写盘延迟 / 实体前缀错位（46 条「页面不存在」条目）
    # 时静默无产出；09-21~09-25 的 loc 全靠 08:0x 晨报人工补录，守护在窗口内仅成功一次（09-23 22:02）。
    # 判据（保守，仍走下方同一 validate()）：文件名 ^YYYYMMDD- 且非 index、页面存在、非跳转壳。
    SCAN_DIRS = ("blog", "mili/blog", "najie/blog", "aipunajie/blog", "en/blog", "fr/blog")
    scan_added = 0
    for _d in SCAN_DIRS:
        _full = os.path.join(SITE, _d)
        if not os.path.isdir(_full):
            continue
        for _fn in sorted(os.listdir(_full)):
            if _fn == "index.html" or not re.match(r"^\d{8}-.+\.html$", _fn):
                continue
            _u = f"{HOST}/{_d}/{_fn}"
            if _u in json_urls:
                continue
            try:
                _mtime = datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(_full, _fn))).strftime("%Y-%m-%d")
            except Exception:
                _mtime = today
            json_urls[_u] = _mtime
            scan_added += 1
    if scan_added:
        print(f"目录扫描补充候选: {scan_added} 条（articles.json 之外，仍需通过存在性/跳转壳校验）")

    # 读取现有 sitemap
    if not os.path.exists(SITEMAP):
        print(f"❌ sitemap 不存在: {SITEMAP}")
        sys.exit(1)
    with open(SITEMAP, encoding="utf-8") as f:
        content = f.read()

    existing = get_existing_urls(content)
    existing_norm = {urllib.parse.unquote(u) for u in existing}

    # 找出需要新增且「有效」的 URL
    to_add = []
    skipped = []
    for url, date in sorted(json_urls.items(), reverse=True):
        if url in existing:
            continue
        why = validate(url, existing_norm, allow_missing)
        if why:
            skipped.append((url, why))
            continue
        to_add.append((date, url))
        existing_norm.add(urllib.parse.unquote(url))

    print(f"articles.json: {len(json_urls)} 条 | sitemap 现有: {len(existing)} 条 | "
          f"有效待新增: {len(to_add)} 条 | 校验跳过: {len(skipped)} 条")

    if skipped:
        by = {}
        for url, why in skipped:
            by.setdefault(why, []).append(url)
        for why, urls in sorted(by.items()):
            print(f"  ⏭ 跳过 {len(urls)} 条 — {why}")
            for u in urls[:5]:
                print(f"       {u}")
            if len(urls) > 5:
                print(f"       …另 {len(urls) - 5} 条")

    if check_only:
        for date, url in sorted(to_add, reverse=True):
            print(f"  + {date} {url}")
        return

    if not to_add:
        print("✅ 无需更新，sitemap 已是最新（且口径达标）")
        return

    # 生成新增条目
    entries = []
    for date, url in sorted(to_add, reverse=True):
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
    block = "\n".join(entries) + "\n"

    # 在"文章"标记后插入（只插入，不替换任何内容）
    if ARTICLE_MARKER in content:
        content = content.replace(ARTICLE_MARKER, ARTICLE_MARKER + "\n" + block, 1)
    else:
        # 没有文章标记：在 </urlset> 前插入（保留全部现有内容）
        content = content.replace("</urlset>", block + "</urlset>", 1)

    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write(content)

    new_count = len(get_existing_urls(content))
    print(f"✅ 已新增 {len(to_add)} 条，sitemap 现有 {new_count} 条 URL（只增不删，已过滤无效项）")


if __name__ == "__main__":
    main()
