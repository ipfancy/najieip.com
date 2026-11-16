#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断 md 包含断言差异位置"""
import os, re, difflib

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"

CASES = [("mili", "20261116-mili-protection-order-72hours"),
         ("mili", "20261115-mili-payment-60days-b2b"),
         ("mili", "20261114-mili-face-recognition-compliance")]

def norm(s):
    s = s.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "")
    s = s.replace("北京纳杰知识产权代理有限公司 何自刚", "")
    s = re.sub(r'[“”"\'’「」『』【】]', '', s)
    s = re.sub(r'[*>`|:\-\s]', '', s)
    return s

for brand, slug in CASES:
    md_path = os.path.join(ART, slug + ".md")
    if not os.path.exists(md_path):
        print(slug, "NO MD", md_path)
        continue
    md = open(md_path, encoding="utf-8").read()
    md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
    md = re.sub(r'<!--.*?-->', ' ', md, flags=re.S)
    lines = []
    for ln in md.split("\n"):
        s = ln.strip()
        if not s: continue
        if s.startswith("#"): continue
        if re.match(r'^\*\*([^*\n]{1,30})\*\*$', s): continue
        if re.match(r'^[一二三四五六七八九十]、', s): continue
        if re.match(r'^\|?[\s:|-]+\|?$', s): continue
        lines.append(s)
    mdt = " ".join(lines)
    t = open(os.path.join(REPO, brand, "blog", slug + ".html"), encoding="utf-8").read()
    seg = re.search(r'<article[^>]*>(.*?)</article>', t, re.S)
    b = seg.group(1) if seg else t[t.find("<body"):]
    b = re.sub(r'<script.*?</script>', ' ', b, flags=re.S)
    b = re.sub(r'<h[123]>.*?</h[123]>', ' ', b, flags=re.S)
    btxt = re.sub(r'<[^>]+>', ' ', b)
    mn, bn = norm(mdt), norm(btxt)
    ok = mn in bn
    print(f"--- {slug} contained={ok} md_len={len(mn)} page_len={len(bn)}")
    if not ok:
        sm = difflib.SequenceMatcher(None, mn, bn)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                print("   ", tag, repr(mn[i1:i2][:80]), "||", repr(bn[j1:j2][:80]))
                break
