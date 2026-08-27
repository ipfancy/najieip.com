#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
canonical 归并修复脚本 v2（najieip.com）
========================================

规则（SEO 最优解，且绝不破坏已有正确归并）：
  1. 每篇文章（同 slug）分类：
     - 跳转页（meta-refresh）：canonical 指向其跳转目标
     - 已归并镜像（canonical 已指向其他 URL）：保持不动
     - 主版候选（无 canonical，或 canonical 指向自己）：参与归并
  2. 主版候选里按优先级选主版：blog > mili/najie/aipunajie > articles。
  3. 主版补 canonical 指向自己；其余主版候选 canonical 指向主版。
  4. en/、fr/ 语言版不参与（保持独立）。

用法：
    python fix-canonical.py          # dry-run
    python fix-canonical.py --apply  # 实际写入
"""

import os
import re
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://najieip.com"
DIRS = ["blog", "articles", "mili/blog", "najie/blog", "aipunajie/blog"]
PRIORITY = {"blog": 0, "mili/blog": 1, "najie/blog": 1, "aipunajie/blog": 1, "articles": 2}

APPLY = "--apply" in sys.argv


def read(fp):
    try:
        with open(fp, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def is_meta_refresh(html):
    return bool(re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', html, re.I))


def get_canonical(html):
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', html, re.I)
    if not m:
        return None
    h = re.search(r'href=["\']([^"\']+)["\']', m.group(0), re.I)
    return h.group(1) if h else None


def get_refresh_target(html):
    m = re.search(
        r'<meta[^>]+http-equiv=["\']refresh["\'][^>]+content=["\'][^"\']*url=([^"\';]+)',
        html, re.I)
    return m.group(1) if m else None


def self_url(fp):
    rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
    return DOMAIN + "/" + quote(rel, safe="/")


def normalize(u):
    """把 canonical href 归一化成绝对 URL。"""
    if not u:
        return None
    u = u.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u.rstrip("/") if u.endswith("/") and len(u) > 10 else u
    if u.startswith("/"):
        return (DOMAIN + u).rstrip("/")
    return (DOMAIN + "/" + u).rstrip("/")


def set_canonical(html, target):
    if normalize(get_canonical(html)) == normalize(target):
        return html, False
    tag = f'<link rel="canonical" href="{target}">'
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', html, re.I)
    if m:
        return html[:m.start()] + tag + html[m.end():], True
    # 找插入点：</head> 优先；否则 <head…> 后；再 <html…> 后；最后文档开头
    hm = re.search(r'</head>', html, re.I)
    if hm:
        return html[:hm.start()] + tag + "\n" + html[hm.start():], True
    ho = re.search(r'<head[^>]*>', html, re.I)
    if ho:
        return html[:ho.end()] + "\n" + tag + html[ho.end():], True
    ht = re.search(r'<html[^>]*>', html, re.I)
    if ht:
        return html[:ht.end()] + "\n" + tag + html[ht.end():], True
    return tag + "\n" + html, True


def main():
    files = {}
    for d in DIRS:
        dp = os.path.join(ROOT, d)
        if not os.path.isdir(dp):
            continue
        for fn in os.listdir(dp):
            if not fn.lower().endswith((".html", ".htm")):
                continue
            if fn in ("index.html", "index.htm"):
                continue
            files[(d, re.sub(r"\.html?$", "", fn))] = os.path.join(dp, fn)

    groups = {}
    for (d, slug), fp in files.items():
        groups.setdefault(slug, []).append((d, fp))

    changes = []  # (fp, old_canonical, new_canonical, reason)

    for slug, items in sorted(groups.items()):
        redirects, mirrors, candidates = [], [], []
        info = {}
        for d, fp in items:
            h = read(fp)
            canon = get_canonical(h)
            info[fp] = {"h": h, "refresh": is_meta_refresh(h),
                        "canonical": canon, "target": get_refresh_target(h)}
            if info[fp]["refresh"]:
                redirects.append((d, fp))
            elif canon and normalize(canon) != normalize(self_url(fp)):
                mirrors.append((d, fp))      # 已正确归并，不动
            else:
                candidates.append((d, fp))  # 裸奔 或 自指

        # 无主版候选 → 全部是跳转/已归并，跳过
        if not candidates:
            continue

        candidates.sort(key=lambda x: PRIORITY.get(x[0], 9))
        main_d, main_fp = candidates[0]
        main_url = self_url(main_fp)

        # 主版 → 指向自己
        h = info[main_fp]["h"]
        new_h, ch = set_canonical(h, main_url)
        if ch:
            changes.append((main_fp, info[main_fp]["canonical"], main_url, "主版补canonical"))

        # 其余候选 → 归并到主版
        for d, fp in candidates[1:]:
            h = info[fp]["h"]
            new_h, ch = set_canonical(h, main_url)
            if ch:
                changes.append((fp, info[fp]["canonical"], main_url, "镜像副本归并→主版"))

        # 跳转页 → canonical 指向跳转目标（若目标在站内）
        for d, fp in redirects:
            tgt = info[fp]["target"]
            tgt_url = None
            if tgt:
                if tgt.startswith("http"):
                    tgt_url = normalize(tgt)
                elif tgt.startswith("/"):
                    tgt_url = DOMAIN + tgt
            if tgt_url:
                h = info[fp]["h"]
                new_h, ch = set_canonical(h, tgt_url)
                if ch:
                    changes.append((fp, info[fp]["canonical"], tgt_url, "跳转页canonical→跳转目标"))

        # mirrors 不动

    print(f"共 {len(groups)} 个 slug，{len(changes)} 处需要改动\n")
    for fp, old, new, reason in changes:
        rel = os.path.relpath(fp, ROOT)
        print(f"[{reason}] {rel}")
        print(f"      {old or '(无)'}  ->  {new}")

    if APPLY:
        # 按文件取最后一次目标写入
        final = {}
        for fp, old, new, reason in changes:
            final[fp] = new
        for fp, target in final.items():
            h = read(fp)
            new_h, _ = set_canonical(h, target)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_h)
        print(f"\n已写入 {len(final)} 个文件")
    else:
        print("\n（dry-run 模式，未写入。加 --apply 实际执行）")


if __name__ == "__main__":
    main()
