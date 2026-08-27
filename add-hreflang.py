#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hreflang 标签生成脚本（najieip.com）
====================================

给中/英/法三语版本页面互相标注 hreflang，让搜索引擎正确识别
同一内容的多语言关系（SEO 多语言优化）。

规则：
  1. en/fr 文件名去掉 -en/-fr 后缀 = 中文 slug。
  2. 中文主版：优先 /blog/，其次 /articles/。
  3. 三版（zh/en/fr）都写入同一组 hreflang 标签，互相指向 + x-default 指向中文。

用法：
    python add-hreflang.py          # dry-run
    python add-hreflang.py --apply  # 实际写入
"""

import os
import re
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://najieip.com"
APPLY = "--apply" in sys.argv


def read(fp):
    try:
        with open(fp, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def url_of(rel):
    return DOMAIN + quote(rel, safe="/")


def zh_slug_of(fn):
    s = re.sub(r"\.html?$", "", fn)
    return re.sub(r"-(en|fr)$", "", s)


def find_zh_file(zh_slug):
    """在 blog/ 或 articles/ 里找中文主版文件，返回 (目录, 文件名) 或 None。"""
    for d in ["blog", "articles"]:
        fp = os.path.join(ROOT, d, zh_slug + ".html")
        if os.path.isfile(fp):
            return d, zh_slug + ".html"
    return None


def build_hreflang(zh_url, en_url, fr_url):
    return "\n".join([
        f'<link rel="alternate" hreflang="zh-CN" href="{zh_url}">',
        f'<link rel="alternate" hreflang="en" href="{en_url}">',
        f'<link rel="alternate" hreflang="fr" href="{fr_url}">',
        f'<link rel="alternate" hreflang="x-default" href="{zh_url}">',
    ])


def insert_hreflang(html, tags):
    """移除已有 hreflang，插入新的一组（在 </head> 前或 <head> 后）。"""
    html = re.sub(r'<link[^>]+rel=["\']alternate["\'][^>]+hreflang=["\'][^"\']*["\'][^>]*>\s*',
                  '', html, flags=re.I)
    hm = re.search(r'</head>', html, re.I)
    if hm:
        return html[:hm.start()] + tags + "\n" + html[hm.start():], True
    ho = re.search(r'<head[^>]*>', html, re.I)
    if ho:
        return html[:ho.end()] + "\n" + tags + html[ho.end():], True
    return tags + "\n" + html, True


def main():
    # 扫描 en/fr
    groups = {}  # zh_slug -> {"zh": (dir,fn), "en": (dir,fn), "fr": (dir,fn)}
    for lang in ["en", "fr"]:
        dp = os.path.join(ROOT, lang, "blog")
        if not os.path.isdir(dp):
            continue
        for fn in os.listdir(dp):
            if not fn.lower().endswith((".html", ".htm")):
                continue
            if fn == "index.html":
                continue
            zh_slug = zh_slug_of(fn)
            g = groups.setdefault(zh_slug, {})
            g[lang] = (f"{lang}/blog", fn)

    # 补中文主版
    for zh_slug in groups:
        zh = find_zh_file(zh_slug)
        if zh:
            groups[zh_slug]["zh"] = zh

    changes = []
    for zh_slug, g in sorted(groups.items()):
        if "zh" not in g:
            print(f"⚠️ 跳过（无中文对应）: {zh_slug}")
            continue
        zh_d, zh_fn = g["zh"]
        zh_url = url_of(f"/{zh_d}/{zh_fn}")
        en_url = url_of(f"/{g['en'][0]}/{g['en'][1]}") if "en" in g else None
        fr_url = url_of(f"/{g['fr'][0]}/{g['fr'][1]}") if "fr" in g else None

        # 只有 en 或 fr 不全时，缺的指向 x-default（中文）
        en_url = en_url or zh_url
        fr_url = fr_url or zh_url

        tags = build_hreflang(zh_url, en_url, fr_url)

        for target_d, target_fn in [("zh", (zh_d, zh_fn))] + \
                                   ([("en", g["en"])] if "en" in g else []) + \
                                   ([("fr", g["fr"])] if "fr" in g else []):
            d, fn = target_fn
            fp = os.path.join(ROOT, d, fn)
            h = read(fp)
            new_h, changed = insert_hreflang(h, tags)
            if changed:
                changes.append((fp, tags))

    print(f"共 {len(groups)} 个语言组，需写 {len(changes)} 个文件\n")
    if APPLY:
        # 按文件最后一次写入
        final = {}
        for fp, tags in changes:
            final[fp] = tags
        for fp, tags in final.items():
            h = read(fp)
            new_h, _ = insert_hreflang(h, tags)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_h)
        print(f"已写入 {len(final)} 个文件")
        # 打印示例
        if final:
            sample_fp = list(final)[0]
            print(f"\n示例（{os.path.relpath(sample_fp, ROOT)}）:")
            print(final[sample_fp])
    else:
        # dry-run 打印示例
        if changes:
            sample_fp, sample_tags = changes[0]
            print(f"示例（{os.path.relpath(sample_fp, ROOT)}）:")
            print(sample_tags)
        print("\n（dry-run 模式，未写入。加 --apply 实际执行）")


if __name__ == "__main__":
    main()
