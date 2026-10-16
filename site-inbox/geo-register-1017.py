#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""注册 2026-10-17 周追踪文章 + 查询词到 geo 表。幂等。"""
import sqlite3, os

DB = os.path.expanduser("~/wiki/database/content.db")
TODAY = "2026-10-17"

ARTICLES = [
    ("ART-2026-0103", "2026-10-06", "赢了官司还被点名6条：这份合规清单抄了就能用", [
        "赢了官司 判决书里的合规建议 有约束力吗",
        "燃气公司 滥用市场支配地位 胜诉 最高法",
        "反垄断 判决后 合规整改 怎么留痕",
    ], "mili"),
    ("ART-2026-0104", "2026-10-07", "商标新规征求意见只剩21天：这3条意见，不提你就亏了", [
        "商标法 司法解释 征求意见 2026 截止时间",
        "商标授权确权规定 第28条 两个方案",
        "商标审查审理指南 征求意见 怎么提意见",
    ], "mili"),
    ("ART-2026-0105", "2026-10-09", "AI短剧被整部搬走只赔2万，这3样证据你留了吗", [
        "AI短剧 被搬运 赔多少钱",
        "AI生成内容 视听作品 认定标准",
        "AI创作 token 算力成本 算进赔偿",
    ], "mili"),
]

con = sqlite3.connect(DB)
cur = con.cursor()

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
print("\n=== stats ===")
for aid, pub, title, queries, brand in ARTICLES:
    cur.execute("SELECT article_id,total_checks,total_found,citation_rate,last_check_date,trend FROM geo_article_stats WHERE article_id=?", (aid,))
    print(cur.fetchone())
cur.execute("SELECT count(*) FROM geo_checks WHERE platform='pending'")
print("pending rows total:", cur.fetchone()[0])
con.close()
