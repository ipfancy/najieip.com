#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1024 GEO 结果入库：geo_checks + geo_article_stats（幂等，先删当日再写）"""
import json, os, sqlite3

BASE = os.path.expanduser("~/wiki/najieip-verify/site-inbox")
DB = os.path.expanduser("~/wiki/database/content.db")
D = "2026-10-24"

mes = json.load(open(os.path.join(BASE, "geo-metaso-1024.json"), encoding="utf-8"))
yb = json.load(open(os.path.join(BASE, "geo-yuanbao-1024.json"), encoding="utf-8"))

PLAN = [
    ("ART-2026-0103", "赢了官司 判决书里的合规建议 有约束力吗"),
    ("ART-2026-0103", "燃气公司 滥用市场支配地位 胜诉 最高法"),
    ("ART-2026-0103", "反垄断 判决后 合规整改 怎么留痕"),
    ("ART-2026-0104", "商标法 司法解释 征求意见 2026 截止时间"),
    ("ART-2026-0104", "商标授权确权规定 第28条 两个方案"),
    ("ART-2026-0104", "商标审查审理指南 征求意见 怎么提意见"),
    ("ART-2026-0105", "AI短剧 被搬运 赔多少钱"),
    ("ART-2026-0105", "AI生成内容 视听作品 认定标准"),
    ("ART-2026-0105", "AI创作 token 算力成本 算进赔偿"),
]

# 吸收度归因（人工阅读答案后写入 notes）
ABSORB = {
    ("ART-2026-0103", "赢了官司 判决书里的合规建议 有约束力吗"):
        "吸收度高：秘塔区分判项/司法建议两性质；元宝给判项·本院认为·法官后语三层效力。未覆盖我方'六条清单+留痕载体'。0署名",
    ("ART-2026-0103", "燃气公司 滥用市场支配地位 胜诉 最高法"):
        "★变化：秘塔本周首次检索到腾冲昆某燃气公司案（上周期零收录），准确答出'提前申报用气计划+偏差结算机制不构成附加不合理交易条件'；但来源为官方/媒体案例摘要×4，0署名。元宝仍只答他案(2023)最高法知民终1547号青海民和川某案 → 平台分化",
    ("ART-2026-0103", "反垄断 判决后 合规整改 怎么留痕"):
        "内容缺口：秘塔给'书面化/台账/承诺履行报告/信用记录'5点泛论；元宝给出整改台账字段清单（编号·对应条款·风险点·责任部门·措施·完成时间）比我方'要求→动作→留痕'三段式更细 → 我方需补台账字段级内容",
    ("ART-2026-0104", "商标法 司法解释 征求意见 2026 截止时间"):
        "高：秘塔答对两截止日（最高法10-28/国知局11-12）并区分法律草案；元宝精确复述'最高法2026-09-14公告'。官方通稿挤压，0署名",
    ("ART-2026-0104", "商标授权确权规定 第28条 两个方案"):
        "★连续第2周平台分化：秘塔仍只给法释〔2017〕2号旧条文并自认'未找到两个方案的官方出处'；元宝正确识别为2026-09-14征求意见稿对原第28条的两种备选写法 → 秘塔侧强内容缺口，可争夺引用位",
    ("ART-2026-0104", "商标审查审理指南 征求意见 怎么提意见"):
        "高：两平台均给出三渠道（sg1@cnipa.gov.cn/传真010-68037822/信函商标局审业管理处100055）→ 官方信息优先，0署名",
    ("ART-2026-0105", "AI短剧 被搬运 赔多少钱"):
        "极高：秘塔逐字复述武汉江岸47集、改名搬运、判赔2万、首次将词元消耗纳入赔偿；元宝另给《著作权法》54条三层计算+法定赔偿500元-500万+1-5倍惩罚性 → 事实被完整吸收，0署名",
    ("ART-2026-0105", "AI生成内容 视听作品 认定标准"):
        "高：秘塔给'完整预见性+实质性控制+连续性实质性智力投入'三标准（与我方文章同源）；元宝给作品四要件+视听要件两段式。0署名",
    ("ART-2026-0105", "AI创作 token 算力成本 算进赔偿"):
        "极高：元宝精确认定'可作酌定因素、非当然全额赔'并引江岸案 Token/算力/商用工具授权费；秘塔先反问澄清后仍答对。0署名",
}

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("DELETE FROM geo_checks WHERE check_date=?", (D,))
print("deleted existing rows for", D, "->", cur.rowcount)

rows = 0
for platform, data in (("metaso", mes), ("yuanbao", yb)):
    for r in data:
        q = r["query"]
        aid = next((a for a, qq in PLAN if qq == q), None)
        if aid is None:
            print("!! 未匹配查询词:", q); continue
        if platform == "metaso":
            found = 1 if r.get("brand_hits") else 0
            ans = r.get("answer", "")
            src = r.get("sources_raw", "")
            note = ABSORB.get((aid, q), "")
            if src:
                note += " | 秘塔来源面板: " + " / ".join(
                    [s.strip() for s in src.replace("来源", "").split("\n") if s.strip()][:6])[:400]
            snippet = ans[:300].replace("\n", " ")
        else:
            found = 1 if r.get("body_hits") else 0
            snippet = (r.get("body_head") or "")[:300]
            note = ABSORB.get((aid, q), "") + " | 元宝无来源面板（模型内化复述）"
        level = "none" if not found else "indirect"
        cur.execute("""INSERT INTO geo_checks
            (article_id, platform, query_text, check_date, found, source_url, rank_position,
             snippet, citation_level, competitor_found, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (aid, platform, q, D, found, None, None, snippet, level, None, note))
        rows += 1

# 更新 stats（按 DB 全量重算）
for aid in sorted(set(a for a, _ in PLAN)):
    cur.execute("SELECT count(*), sum(found) FROM geo_checks WHERE article_id=? AND platform IN ('metaso','yuanbao')", (aid,))
    total, found = cur.fetchone()
    found = found or 0
    rate = round(found / total, 4) if total else 0.0
    cur.execute("SELECT platform, query_text FROM geo_checks WHERE article_id=? AND found=1 LIMIT 1", (aid,))
    bp = cur.fetchone()
    cur.execute("""INSERT INTO geo_article_stats
        (article_id, total_checks, total_found, citation_rate, best_platform, best_query, last_check_date, trend)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(article_id) DO UPDATE SET
          total_checks=excluded.total_checks, total_found=excluded.total_found,
          citation_rate=excluded.citation_rate, last_check_date=excluded.last_check_date,
          trend=excluded.trend""",
        (aid, total, found, rate, bp[0] if bp else None, bp[1] if bp else None, D, "new"))
    print(f"{aid}: total={total} found={found} rate={rate}")

con.commit()
cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')")
print("累计双平台检查点:", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM geo_checks WHERE check_date=? AND platform IN ('metaso','yuanbao')", (D,))
print("本周检查点:", cur.fetchone()[0])
con.close()
print("inserted rows:", rows)
