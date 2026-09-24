#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 诊断：畸形页段落 vs md 源逐段比对 + 模板页字段提取"""
import os, re

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260924-malicious-litigation-supervision"
MD = os.path.expanduser("~/wiki/digital-employees/articles/%s.md" % SLUG)
TARGET = os.path.join(REPO, "mili/blog/%s.html" % SLUG)
INBOX = os.path.join(REPO, "site-inbox/%s.html" % SLUG)


def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


md = rd(MD)
body = md.split("---", 2)[2]
body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
md_paras = [p.strip() for p in body.split("\n\n") if p.strip()]
print("=== MD 源段落 (%d) ===" % len(md_paras))
for i, p in enumerate(md_paras):
    print("[%02d] (%d) %s" % (i, len(p), p[:110]))

cur = rd(TARGET)
ps = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<p[^>]*>(.*?)</p>", cur, re.S)]
ps = [p.replace("&#x27;", "'").replace("&amp;", "&").replace("&quot;", '"') for p in ps]
ps = [p for p in ps if p]
print("\n=== 畸形页段落 (%d) ===" % len(ps))
for i, p in enumerate(ps):
    print("[%02d] (%d) %s" % (i, len(p), p[:110]))

print("\n=== 逐段比对 ===")
n = min(len(ps), len(md_paras))
diffs = []
for i in range(n):
    a = ps[i].replace("&amp;", "&")
    b = md_paras[i].replace("&amp;", "&")
    b = re.sub(r"^\*|\*$", "", b).strip()
    if a != b:
        diffs.append(i)
        if len(diffs) <= 6:
            print("  [DIFF %d]\n    page: %s\n    md  : %s" % (i, a[:140], b[:140]))
print("  比对 %d 段，DIFF %d 段" % (n, len(diffs)))
print("  md 多出段:", [p[:60] for p in md_paras[n:]])
print("  页多出段:", [p[:60] for p in ps[n:]])

print("\n=== inbox 副本 vs 品牌目录副本 ===")
if os.path.exists(INBOX):
    ib = rd(INBOX)
    print("  inbox bytes", len(ib.encode()), "| target bytes", len(cur.encode()))
    print("  inbox h1", ib.count("<h1"), "| ld", ib.count("application/ld+json"), "| frontmatter leak", "title:" in ib[:1500])
    print("  identical:", ib == cur)
