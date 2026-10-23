#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 1024 GEO 周报 + 渠道覆盖统计"""
import json, os, datetime, sqlite3, re
from collections import Counter

BASE = os.path.expanduser("~/wiki/najieip-verify/site-inbox")
DB = os.path.expanduser("~/wiki/database/content.db")
OUT = os.path.expanduser("~/wiki/digital-employees/reports/geo-weekly-20261024.md")

mes = json.load(open(os.path.join(BASE, "geo-metaso-1024.json"), encoding="utf-8"))

iso = datetime.date(2026, 10, 24).isocalendar()
print("ISO week:", iso)

# 来源面板统计：取 rfind("来源") 之后的标题行
NOISE = {"来源", "脑图", "大纲", "深度研究", "互动网页", "内容由AI生成，请仔细甄别", "文本", "好看", "生成幻灯片", "展示海报", ""}
srcs = []
for r in mes:
    raw = r.get("sources_raw", "")
    cut = raw.rfind("深度研究")
    if cut > 0:
        raw = raw[:cut]
    for line in raw.split("\n"):
        s = line.strip()
        if s and s not in NOISE and not s.startswith("来源"):
            srcs.append(s)

def kind(s):
    if "cnipa" in s or "国家知识产权局" in s or "最高人民法院" in s or "公开征求意见" in s or "行政处罚文书示范文本" in s or "反垄断合规指引" in s or "通知" in s or "典型案例" in s:
        return "官方/机构（法院·国知局·监管）"
    if "论" in s or "研究" in s or "初探" in s or "以《" in s or "视角" in s:
        return "学术论文/专业文献"
    if any(k in s for k in ["律师事务所", "环球律师"]):
        return "律所解读"
    return "媒体/门户转载"

tally = Counter(kind(s) for s in srcs)
print("来源条目总数:", len(srcs))
for k, v in tally.most_common():
    print(f"  {k}: {v}")
print("\n最难判的条目：")
for s in srcs:
    print("  -", kind(s), "|", s[:70])

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')")
cum = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM geo_checks WHERE found=1")
found_cum = cur.fetchone()[0]
con.close()
print("\n累计:", cum, "命中:", found_cum)
