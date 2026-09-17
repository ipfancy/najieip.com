#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sitemap-hygiene.py — 把 sitemap.xml 恢复为「口径三条全零」。

口径（2026-09-16 遗留项 1 回执 / skill siteops-seo-monitoring）：
    · 跳转/别名 loc  = 0     （应只收录 canonical 可索引页）
    · 重复登记 loc   = 0     （同一路径的中文原样 + %编码 只留与页面 canonical 一致者）
    · 非 200 loc     = 0     （页面不存在/不可访问者不得收录）

本脚本只从 sitemap.xml 摘除违规 <url>...</url> 块：
    · 不改动任何 HTML 文件
    · 不改动任何其它条目、不改动缩进与格式

用法：
    python3 sitemap-hygiene.py --dry-run     # 只报告（默认）
    python3 sitemap-hygiene.py --apply       # 写入
    python3 sitemap-hygiene.py --apply --live  # 非 200 判定改用线上 curl 实测（慢）
"""
import argparse
import os
import re
import subprocess
import sys
import urllib.parse

SITE = os.path.dirname(os.path.abspath(__file__))
SITEMAP = os.path.join(SITE, "sitemap.xml")
HOST = "https://najieip.com"
BLOCK_RE = re.compile(r"[ \t]*<url>\s*<loc>(https://najieip[.]com[^<]*)</loc>.*?</url>\n?", re.S)
LOC_RE = re.compile(r"<loc>(https://najieip[.]com[^<]*)</loc>")


def rel_of(url):
    """'https://najieip.com/blog/x.html' -> 'blog/x.html'（无前导斜杠）"""
    return url[len(HOST):].lstrip("/")


def canon_of(rel):
    p = os.path.join(SITE, rel)
    if not os.path.exists(p):
        return None
    try:
        h = open(p, encoding="utf-8", errors="ignore").read(8000)
    except Exception:
        return None
    m = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', h)
    return m.group(1) if m else None


def is_shell(rel):
    """meta refresh 跳转壳（不论有无 noindex）。"""
    p = os.path.join(SITE, rel)
    if not os.path.exists(p):
        return False
    try:
        low = open(p, encoding="utf-8", errors="ignore").read(4000).lower()
    except Exception:
        return False
    return 'http-equiv="refresh"' in low


def live_ok(rel):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                            "--max-time", "20", HOST + "/" + urllib.parse.quote(rel)],
                           capture_output=True, text=True, timeout=40)
        return r.stdout.strip() == "200"
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="（默认行为，显式给出亦可）")
    ap.add_argument("--live", action="store_true", help="非 200 用线上实测判定")
    args = ap.parse_args()

    content = open(SITEMAP, encoding="utf-8").read()
    locs = LOC_RE.findall(content)
    print(f"sitemap loc: {len(locs)}")

    drop = {}

    # A. 跳转/别名 loc
    for u in locs:
        if is_shell(rel_of(u)):
            drop[u] = "A-跳转/别名页"

    # B. 非 200 loc（本地无文件；--live 时以 curl 实测为准）
    for u in locs:
        rel = rel_of(u)
        if u in drop:
            continue
        if not os.path.exists(os.path.join(SITE, rel)):
            drop[u] = "B-页面不存在"
        elif args.live and not live_ok(rel):
            drop[u] = "B-线上非200"

    # C. 重复登记（中文原样 + %编码 并存 → 保留与 canonical 一致者）
    by_decoded = {}
    for u in locs:
        rel = rel_of(u)
        if urllib.parse.unquote(rel) != rel:      # 已编码登记
            partner = HOST + "/" + urllib.parse.unquote(rel)
            by_decoded.setdefault(partner, []).append(u)
    for raw_url, enc_urls in by_decoded.items():
        if raw_url not in locs:
            continue
        for enc in enc_urls:
            want = canon_of(rel_of(raw_url))
            keep = raw_url if (want is None or want == raw_url) else enc
            loser = enc if keep == raw_url else raw_url
            if loser != keep:
                drop[loser] = "C-重复登记"

    cats = {}
    for u, c in drop.items():
        cats.setdefault(c, []).append(u)
    print(f"\n待摘除 {len(drop)} 条：")
    for c in sorted(cats):
        print(f"  {c}: {len(cats[c])}")

    if not drop:
        print("✅ 口径已达标，无需处置")
        return 0

    if not args.apply:
        print("\n[dry-run] 未写入。加 --apply 执行。")
        return 0

    removed = []

    def _sub(m):
        if m.group(1) in drop:
            removed.append(m.group(1))
            return ""
        return m.group(0)

    new = BLOCK_RE.sub(_sub, content)
    if set(removed) != set(drop):
        print(f"⚠️ 摘除集合不一致（{len(removed)} vs {len(drop)}），已中止", file=sys.stderr)
        return 1
    after = LOC_RE.findall(new)
    if set(after) & set(drop):
        print("⚠️ 仍有残留，已中止", file=sys.stderr)
        return 1
    open(SITEMAP, "w", encoding="utf-8").write(new)
    print(f"\n✅ 已写入 sitemap.xml：loc {len(locs)} → {len(after)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
