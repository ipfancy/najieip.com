#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 2026-10-12 GEO 结果写入 geo_checks + 更新 geo_article_stats。幂等（先删当日同平台同查询）。"""
import json, os, sqlite3

BASE = os.path.expanduser("~/wiki/najieip-verify/site-inbox")
DB = os.path.expanduser("~/wiki/database/content.db")
TODAY = "2026-10-12"
ARTS = ["ART-2026-0100", "ART-2026-0101", "ART-2026-0102"]

metaso = json.load(open(os.path.join(BASE, "geo-metaso-1012.json")))
yuanbao = json.load(open(os.path.join(BASE, "geo-yuanbao-1012.json")))

con = sqlite3.connect(DB)
cur = con.cursor()

# 清理当日重复 + pending 占位
cur.execute("DELETE FROM geo_checks WHERE check_date=? AND platform IN ('metaso','yuanbao')", (TODAY,))
cur.execute("DELETE FROM geo_checks WHERE platform='pending' AND article_id IN (?,?,?)", ARTS)
print("cleaned:", cur.rowcount, "pending rows removed")

ins = 0
for r in metaso:
    hits = r.get("hits") or {}
    found = 1 if hits else 0
    cur.execute("""INSERT INTO geo_checks
        (article_id, platform, query_text, check_date, found, citation_level, snippet, notes)
        VALUES (?,?,?,?,?,?,?,?)""",
        (r["article"], "metaso", r["query"], TODAY, found, "none", "",
         f"{r.get('note','无品牌命中')} | answer_len={r.get('len')} | blocked={r.get('blocked')}"))
    ins += 1

for r in yuanbao:
    hits = r.get("body_hits") or {}
    found = 1 if hits else 0
    cur.execute("""INSERT INTO geo_checks
        (article_id, platform, query_text, check_date, found, citation_level, snippet, notes)
        VALUES (?,?,?,?,?,?,?,?)""",
        (r["article"], "yuanbao", r["query"], TODAY, found, "none", "",
         f"无品牌命中；元宝完整吸收话题事实 | body_len={r.get('body_len')}"))
    ins += 1

print("inserted:", ins)

# 更新 geo_article_stats
for aid in ARTS:
    cur.execute("""SELECT count(*), sum(found) FROM geo_checks
        WHERE article_id=? AND platform IN ('metaso','yuanbao')""", (aid,))
    tot, fnd = cur.fetchone()
    tot, fnd = tot or 0, fnd or 0
    rate = round(fnd / tot, 4) if tot else 0.0
    trend = "new" if tot <= 9 else ("rising" if fnd else "stable")
    cur.execute("""UPDATE geo_article_stats
        SET total_checks=?, total_found=?, citation_rate=?, last_check_date=?, trend=?
        WHERE article_id=?""", (tot, fnd, rate, TODAY, trend, aid))
    print(f"[stats] {aid}: checks={tot} found={fnd} rate={rate} trend={trend}")

con.commit()

# 累计口径（技能规定：只算 metaso+yuanbao）
cur.execute("SELECT count(*), coalesce(sum(found),0) FROM geo_checks WHERE platform IN ('metaso','yuanbao')")
cum, cumf = cur.fetchone()
print(f"\nCUMULATIVE metaso+yuanbao: {cum} checkpoints, {cumf} found")
cur.execute("SELECT platform, count(*) FROM geo_checks WHERE check_date=? GROUP BY platform", (TODAY,))
print("today:", cur.fetchall())
con.close()
