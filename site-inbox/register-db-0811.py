#!/usr/bin/env python3
"""SiteOps 2026-08-11: 注册 ART-2026-0044/0045 到 content.db + GEO 追踪池"""
import sqlite3

db = sqlite3.connect('/Users/ziganghe/wiki/database/content.db')
cur = db.cursor()

articles = [
    ('ART-2026-0044', '专利无效攻防：一场没有硝烟的「华山论剑」',
     '专利无效宣告是知识产权界最刺激的"约架"——请求人三把刀：新颖性、创造性、公开不充分；专利权人只有一个月应战。戏说IP系列用「华山论剑」拆解无效攻防全流程。',
     'published', '2026-08-10', '["专利无效","无效宣告","戏说IP"]', '戏说IP', None),
    ('ART-2026-0045', '中美AI版权"冰火两重天"：你的AI生成内容，出海怎么办？',
     '美国最高法院拒审Thaler案——纯AI生成在美国不受版权保护；中国法院却认定AI图片可构成作品。幻之翼案输20万 vs 春风案赢500元，区别只有四个字：创作留痕。拆解中美路径差异，附6个出海实操动作。',
     'published', '2026-08-11', '["AI版权","著作权","出海","Thaler案"]', 'AI系列', None),
]

for aid, title, summary, status, pdate, tags, series, cover in articles:
    cur.execute("""INSERT OR REPLACE INTO articles
        (article_id, title, summary, author, status, publish_date, tags, series, cover_image, created_at, updated_at)
        VALUES (?,?,?, '何自刚', ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
        (aid, title, summary, status, pdate, tags, series, cover))

# GEO 追踪池（带查询词，pending 待下周六）
geo_articles = [
    ('ART-2026-0044',
     ['专利无效宣告 怎么应对', '专利被请求无效 一个月怎么答复', '专利无效 新颖性 创造性 区别', '无效掉一个专利 有多难', '专利质量 权利要求 怎么写']),
    ('ART-2026-0045',
     ['AI生成图片 有版权吗 2026', '美国AI作品 不受版权保护 Thaler', 'AI生成内容 出海 版权怎么办', '春风案 幻之翼案 AI版权 区别', 'AI创作 留痕 证明独创性']),
]
for aid, queries in geo_articles:
    cur.execute("""INSERT OR REPLACE INTO geo_article_stats
        (article_id, total_checks, total_found, citation_rate, best_platform, best_query, last_check_date, trend)
        VALUES (?, 0, 0, 0.0, NULL, NULL, NULL, 'new')""", (aid,))
    for q in queries:
        cur.execute("""INSERT OR REPLACE INTO geo_checks
            (article_id, platform, query_text, check_date, found, source_url, rank_position, snippet, citation_level, competitor_found, notes)
            VALUES (?, 'pending', ?, date('now'), 0, NULL, NULL, NULL, 'none', NULL, '待下周六执行')""",
            (aid, q))

db.commit()
print("articles 0044/0045 注册完成")
print("geo_article_stats:", db.execute("SELECT COUNT(*) FROM geo_article_stats WHERE article_id LIKE 'ART-2026-004%'").fetchone()[0])
print("geo_checks pending:", db.execute("SELECT COUNT(*) FROM geo_checks WHERE platform='pending' AND article_id LIKE 'ART-2026-004%'").fetchone()[0])
db.close()
