#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
canonical-merge.py — 中文镜像 canonical 自动归并（najieip.com）

规则：
  1. 只处理中文目录 blog / mili/blog / najie/blog / aipunajie/blog
  2. 同一 slug 的多目录镜像，确定主版（blog 优先，否则取正文最长者）
  3. 其他中文版本与主版正文相似度 ≥ THRESHOLD（0.96）→ canonical 指向主版（归并）
  4. 相似度 < THRESHOLD → canonical 指向自身（精修版，保留独立）
  5. 不碰 articles（跳转页）、en/fr（语言版）

幂等：重复运行结果一致。只改 <link rel="canonical">，不改正文。
"""
import os
import re
import html
from difflib import SequenceMatcher
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
ZH_DIRS = ["blog", "mili/blog", "najie/blog", "aipunajie/blog"]
DOMAIN = "https://najieip.com"
THRESHOLD = 0.96


def slug_of(fn: str) -> str:
    return re.sub(r"-(en|fr)?\.html?$", "", fn)


def body_text(fp: str) -> str:
    try:
        with open(fp, encoding="utf-8", errors="ignore") as f:
            c = f.read()
    except OSError:
        return ""
    c = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", c, flags=re.I | re.S)
    c = re.sub(r"<[^>]+>", " ", c)
    c = html.unescape(c)
    return re.sub(r"\s+", "", c)


def get_canonical(h: str):
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', h, re.I)
    return m.group(1).strip() if m else None


def set_canonical(h: str, target: str):
    """替换或插入 canonical 标签。返回 (new_html, changed)"""
    if get_canonical(h) == target:
        return h, False
    tag = f'<link rel="canonical" href="{target}">'
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', h, re.I)
    if m:
        return h[:m.start()] + tag + h[m.end():], True
    # 找插入点：</head> 优先，其次 <head…> 后，再文档开头
    hm = re.search(r"</head>", h, re.I)
    if hm:
        return h[:hm.start()] + tag + "\n" + h[hm.start():], True
    ho = re.search(r"<head[^>]*>", h, re.I)
    if ho:
        return h[:ho.end()] + "\n" + tag + h[ho.end():], True
    return tag + "\n" + h, True


def self_url(d: str, fn: str) -> str:
    rel = f"{d}/{fn}".replace(os.sep, "/")
    return f"{DOMAIN}/{rel}"


def main():
    # 收集中文文章
    groups = defaultdict(dict)  # slug -> {dir: (fn, fp)}
    for d in ZH_DIRS:
        dp = os.path.join(ROOT, d)
        if not os.path.isdir(dp):
            continue
        for fn in os.listdir(dp):
            if not fn.lower().endswith((".html", ".htm")):
                continue
            if fn in ("index.html", "index.htm"):
                continue
            groups[slug_of(fn)][d] = (fn, os.path.join(dp, fn))

    changed_files = []
    merged = 0
    kept = 0
    for slug, v in groups.items():
        if len(v) < 2:
            # 单版本，确保 canonical 指向自己
            (d, (fn, fp)) = next(iter(v.items()))
            h = open(fp, encoding="utf-8").read()
            target = self_url(d, fn)
            new_h, ch = set_canonical(h, target)
            if ch:
                open(fp, "w", encoding="utf-8").write(new_h)
                changed_files.append(fp)
            continue

        texts = {d: body_text(fp) for d, (fn, fp) in v.items()}
        # 主版：blog 优先（若有非空正文），否则取最长正文
        if "blog" in texts and texts["blog"]:
            main_d = "blog"
        else:
            main_d = max(texts, key=lambda d: len(texts[d]))
        main_text = texts[main_d]
        if not main_text:
            continue

        main_fn = v[main_d][0]
        main_url = self_url(main_d, main_fn)

        for d, (fn, fp) in v.items():
            h = open(fp, encoding="utf-8").read()
            if d == main_d:
                target = main_url
            else:
                t = texts[d]
                if t and SequenceMatcher(None, main_text, t).ratio() >= THRESHOLD:
                    target = main_url  # 归并
                else:
                    target = self_url(d, fn)  # 精修，保留独立
            new_h, ch = set_canonical(h, target)
            if ch:
                open(fp, "w", encoding="utf-8").write(new_h)
                changed_files.append(fp)
                if d == main_d:
                    pass
                elif target == main_url:
                    merged += 1
                else:
                    kept += 1

    print(f"canonical-merge: {len(changed_files)} 文件已更新（归并 {merged}，保留独立 {kept}）")
    return 0 if changed_files else 1  # 1 = 无改动（供 workflow 判断）


if __name__ == "__main__":
    raise SystemExit(main())
