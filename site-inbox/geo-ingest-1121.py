#!/usr/bin/env python3
"""2026-11-21 第47周 GEO 结果入库：geo_checks + geo_article_stats"""
import json, sqlite3, datetime

DB = "/Users/ziganghe/wiki/database/content.db"
DATE = "2026-11-21"
RAW = "/Users/ziganghe/wiki/digital-employees/reports/_geo-yuanbao-raw-20261121.json"

# 秘塔（metaso）9 条 —— 全部 0 命中，notes 记录吸收度与分化
METASO = [
    ("ART-2026-0130", "刷脸考勤 员工不同意 必须给别的验证方式吗",
     "答对《人脸识别技术应用安全管理办法》第10条+个保法第29条单独同意；来源=汉盛律所百问百答/河南省交通运输厅。我方'双通道'与'673件公安处罚vs3件网信'框架未被采纳"),
    ("ART-2026-0130", "人脸识别 数据存在设备里还是传到云上 合规吗",
     "答对'本地为原则、上云为例外'(第8条)，但来源面板 15 条全是设备/SDK 厂商软文（澜极美颜SDK、ZUU中优门禁、虹软），零权威源——该题权威源真空=可争夺位"),
    ("ART-2026-0130", "刷脸考勤 被罚 是网信办还是公安",
     "★答旧版本：援引《人脸识别技术应用安全管理规定（试行）》而非 2025-06-01 施行的《人脸识别技术应用安全管理办法》；靠'合肥某公司罚3万'个案撑论，未答出673件/3件的部门分布"),
    ("ART-2026-0131", "合同写收到上家款再付 有效吗 2026",
     "答'背靠背原则上有效、仅大型企业→中小企业无效'，方向对；但只给裁判观点未给《条例》第9条第二款行政法规本体，也未提批复条号错位（批复第6/8条=现行第7/9条二款）——我方独家对照未被采纳"),
    ("ART-2026-0131", "大型企业欠款 逾期利息 万分之五还是LPR",
     "★答旧条号：《条例》第十五条（=2020年728号令条号；802号令现行第17条，已核中国政府网/人民网全文）；18.25%年化与LPR冲突、地区判例分化等判断与我方一致"),
    ("ART-2026-0131", "中小企业 怎么认定 工业 1000人 4亿",
     "答对工信部联企业〔2011〕300号'或'关系+中型/小型/微型细分，并给出 sme.miit.gov.cn 自测入口——比我方文章细（我方未给自测网址）"),
    ("ART-2026-0129", "荷兰 知识产权案件 败诉方要赔对方律师费吗",
     "★AI 比我方深：1019h + 律师费上限（简单禁令约6000欧/实质审理约25000欧；2020-09-01起专利诉讼1万–25万欧）+ 纯无效之诉只按固定费率——我方仅写'赔实际合理费用'"),
    ("ART-2026-0129", "公司被外国法院突击搜查 数据被拷走 怎么应对",
     "给通用跨境调查框架（legal hold/电子取证/特权材料/司法救济）并自认'以美英法律环境为主'；未出现荷兰1019 Rv、未出现比亚迪案、未出现'先批准后撤销'——我方差异化完全未被采纳=可争夺引用位"),
    ("ART-2026-0129", "证据保全 被申请人 提异议 法院能不能解除",
     "答对《知产证据规定》第17条（异议成立可变更/终止/解除）+ 解除条件与担保路径；来源=知产证据规定/人民法院案例库，与我方文章一致无新增"),
]

yb = {r["query"]: r for r in json.load(open(RAW, encoding="utf-8"))}

def level(hits):
    return "none"

con = sqlite3.connect(DB)
cur = con.cursor()
before = cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')").fetchone()[0]

rows = []
for aid, q, note in METASO:
    rows.append((aid, "metaso", q, 0, None, None, None, "none", "{}", note))
for aid, q, note in METASO:
    r = yb.get(q)
    if not r:
        rows.append((aid, "yuanbao", q, 0, None, None, None, None, "{}", "元宝本轮无返回（采集缺失）"))
        continue
    hits = r.get("body_hits") or {}
    found = 1 if hits else 0
    lvl = "indirect" if found else "none"
    snip = (r.get("body_head") or "")[:200]
    note2 = ("元宝正文命中: " + json.dumps({k: v.get("count") for k, v in hits.items()}, ensure_ascii=False)) if found else \
        f"元宝答题 {r.get('body_len')} 字，正文零品牌命中；{'/'.join([])}"
    rows.append((r.get("article_id", aid), "yuanbao", q, found, None, None, snip, lvl, "{}", note2))

for (aid, plat, q, found, url, rank, snip, lvl, comp, note) in rows:
    cur.execute("""INSERT INTO geo_checks
        (article_id, platform, query_text, check_date, found, source_url, rank_position, snippet, citation_level, competitor_found, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (aid, plat, q, DATE, found, url, rank, snip, lvl, comp, note))

# 更新 stats（全量重算）
for aid in sorted({r[0] for r in rows}):
    tot, fnd = cur.execute("SELECT count(*), sum(found) FROM geo_checks WHERE article_id=? AND platform IN ('metaso','yuanbao')", (aid,)).fetchone()
    rate = (fnd or 0) / tot if tot else 0.0
    best = cur.execute("""SELECT platform FROM geo_checks WHERE article_id=? AND found=1
                          GROUP BY platform ORDER BY count(*) DESC LIMIT 1""", (aid,)).fetchone()
    bq = cur.execute("""SELECT query_text FROM geo_checks WHERE article_id=? AND found=1 LIMIT 1""", (aid,)).fetchone()
    trend = "rising" if rate > 0 else "stable"
    cur.execute("""INSERT INTO geo_article_stats (article_id,total_checks,total_found,citation_rate,best_platform,best_query,last_check_date,trend)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(article_id) DO UPDATE SET total_checks=?,total_found=?,citation_rate=?,best_platform=?,best_query=?,last_check_date=?,trend=?""",
                (aid, tot, fnd or 0, rate, best[0] if best else None, bq[0] if bq else None, DATE, trend,
                 tot, fnd or 0, rate, best[0] if best else None, bq[0] if bq else None, DATE, trend))
    print(f"{aid}: total={tot} found={fnd} rate={rate:.3f}")

con.commit()
after = cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')").fetchone()[0]
tot_found = cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao') AND found=1").fetchone()[0]
print(f"geo_checks (metaso+yuanbao): {before} -> {after}  (+{after-before})")
print(f"累计命中: {tot_found} / {after} = {tot_found/after*100:.1f}%")
con.close()
