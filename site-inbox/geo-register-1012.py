#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""注册 2026-10-12 周追踪文章 + 查询词到 geo 表。幂等。"""
import sqlite3, os

DB = os.path.expanduser("~/wiki/database/content.db")

ARTICLES = [
    ("ART-2026-0100", "2026-10-03", "有注册证也侵权：商标被判无效，法院顶格判赔500万", [
        "有注册证还被判侵权 怎么办",
        "商标被判无效 顶格判赔500万",
        "注册商标 能不能对抗在先商标权",
    ], "najie"),
    ("ART-2026-0101", "2026-10-04", "同一专利族，美国判赔2760万美元，欧洲驳回禁令", [
        "同一专利族 美国判赔 欧洲驳回禁令",
        "拓竹被Stratasys起诉 判赔多少钱",
        "FTO自由实施检索 怎么做 步骤",
    ], "mili"),
    ("ART-2026-0102", "2026-10-05", "前8年年费足缴，第9年专利作废！这5个信号最该自查", [
        "专利年费交了 为什么还被终止",
        "专利年费台账 怎么自查",
        "代理机构变更 没办著录事项变更 后果",
    ], "najie"),
]

TODAY = "2026-10-12"

con = sqlite3.connect(DB)
cur = con.cursor()

# 1) geo_article_stats: 只在不存在时建行（不覆盖历史统计）
for aid, pub, title, queries, brand in ARTICLES:
    cur.execute("SELECT count(*) FROM geo_article_stats WHERE article_id=?", (aid,))
    if cur.fetchone()[0] == 0:
        cur.execute("""INSERT INTO geo_article_stats
            (article_id, total_checks, total_found, citation_rate, best_platform,
             best_query, last_check_date, trend)
            VALUES (?,0,0,0.0,NULL,NULL,NULL,'new')""", (aid,))
        print(f"[stats] added {aid} ({brand})")
    else:
        print(f"[stats] exists {aid}")

# 2) geo_checks pending 占位：避免重复插（同 article+query+platform=pending）
for aid, pub, title, queries, brand in ARTICLES:
    for q in queries:
        cur.execute("""SELECT count(*) FROM geo_checks
            WHERE article_id=? AND query_text=? AND platform='pending'""", (aid, q))
        if cur.fetchone()[0] == 0:
            cur.execute("""INSERT INTO geo_checks
                (article_id, platform, query_text, check_date, found, citation_level, notes)
                VALUES (?,?,?,?,0,'none','待执行')""", (aid, 'pending', q, TODAY))
            print(f"[pending] {aid} | {q}")

con.commit()

# 3) 展示
print("\n=== geo_article_stats (本次 3 篇) ===")
for aid, pub, title, queries, brand in ARTICLES:
    cur.execute("SELECT article_id,total_checks,total_found,citation_rate,last_check_date,trend FROM geo_article_stats WHERE article_id=?", (aid,))
    print(cur.fetchone())
con.close()
