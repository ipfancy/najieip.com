#!/usr/bin/env python3
"""Corrected containment: only strip ordered-list markers followed by whitespace."""
import re, os, glob, json, unicodedata

REPO = "/Users/ziganghe/wiki/najieip-verify"
ART = "/Users/ziganghe/wiki/digital-employees/articles"
BYLINES = ["北京纳杰知识产权代理有限公司何自刚", "何自刚", "何自刚知识产权律师爱普纳杰·觅理·纳杰",
           "何自刚｜知识产权律师｜纳杰觅理", "纳杰觅理", "爱普纳杰·觅理·纳杰"]

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r'[\s“”"\'’‘「」『』【】\[\]>:：\-—…、,，.。!！?？*|]', '', s)

def strip_fm(md):
    lines = md.split("\n"); i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith("<!--") or s == "---" or re.match(
                r'^(title|date|slug|brand|style|voice|end|ai_smell|tags|author|category|cover|desc|description)\s*[:：]', s):
            i += 1; continue
        break
    return "\n".join(lines[i:])

def mdn_of(path):
    md = strip_fm(open(path, encoding="utf-8").read()); keep = []
    for ln in md.split("\n"):
        s = ln.strip()
        if not s or s.startswith("<!--") or s.startswith("#"): continue
        if re.match(r'^\*\*[^*\n]{1,32}\*\*$', s) or re.match(r'^[一二三四五六七八九十]、', s): continue
        if s.startswith("|"):
            if re.match(r'^\|[\s:|-]+\|$', s): continue
            s = re.sub(r'[|\-:]', '', s)
        s = re.sub(r'^\d+\.\s+', '', s)   # FIX: require whitespace after marker
        if "lt;!--" in s: continue
        keep.append(s)
    o = norm("".join(keep))
    for b in BYLINES: o = o.replace(norm(b), "")
    return o

def pg_of(hp):
    t = open(hp, encoding="utf-8").read()
    m = re.search(r'<article.*?</article>', t, re.S)
    seg = m.group(0) if m else t[t.find("<body"):]
    seg = re.sub(r'<script.*?</script>', ' ', seg, flags=re.S)
    seg = re.sub(r'<h[1-6].*?</h[1-6]>', ' ', seg, flags=re.S)
    pg = norm(re.sub(r'<[^>]+>', '\n', seg))
    for b in BYLINES: pg = pg.replace(norm(b), "")
    return pg

for slug, brand in [("20261123-mili-gaoqi-2026-no-new-standard", "najie"),
                    ("mili-food-oem-trademark-113-order-20261122", "najie"),
                    ("20261121-mili-divorce-game-account-88w", "mili")]:
    md = mdn_of(glob.glob(os.path.join(ART, slug + ".md"))[0])
    pg = pg_of(os.path.join(REPO, brand, "blog", slug + ".html"))
    r = {"slug": slug, "md_len": len(md), "pg_len": len(pg), "contained": md in pg, "equal": len(md) == len(pg)}
    if not r["contained"]:
        i = 0
        while i < min(len(md), len(pg)) and md[i] == pg[i]: i += 1
        r["diff_at"] = i
        r["md_ctx"] = md[max(0, i-25):i+45]
        r["pg_ctx"] = pg[max(0, i-25):i+45]
        # tail diff
        if len(md) > len(pg):
            r["md_tail"] = md[-60:]
        else:
            r["pg_tail"] = pg[-60:]
    print(json.dumps(r, ensure_ascii=False))
