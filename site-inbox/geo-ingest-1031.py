#!/usr/bin/env python3
"""GEO 2026-10-31 ingest: 18 checkpoints (metaso 9 + yuanbao 9) → geo_checks + geo_article_stats"""
import json, os, re, sqlite3, datetime

DB = os.path.expanduser("~/wiki/database/content.db")
TODAY = "2026-10-31"
yb = {r["query"]: r for r in json.load(open("/tmp/geo_yuanbao_1031.json"))}

# 秘塔实测证据（来自本轮 browser 输出的回答正文/来源面板）
METASO = [
 ("ART-2026-0114", "人身安全保护令 能证明家暴吗",
  "保护令不能直接、单独地证明家暴；保护令标准为「较大可能性」，离婚赔偿认定需「高度可能性」，须结合其他证据综合认定。",
  ["顺法一分钟丨国际反家暴日", "人身安全保护令能直接证明家暴吗？来看这对房山离婚夫妻的经历"]),
 ("ART-2026-0114", "人身安全保护令 与 离婚损害赔偿 证据标准 区别",
  "以表格给出「较大可能性 vs 高度可能性」双重标准；引《办理人身安全保护令案件规定》第9条，并说明保护令裁定无查明事实部分、证据未经质证。",
  ["民商事审判实务（第4册）", "人身安全保护令中的证据问题研究", "人身安全保护令证据制度之构建", "以案释法：家庭暴力认定中的法律适用"]),
 ("ART-2026-0114", "家暴证据 清单 怎么收集 报警回执 告诫书",
  "按公安机关文书/医疗/求助记录/证人四类给出清单，强调报警时明确说「家庭暴力」并索要回执、告诫书证明力极强。",
  ["家庭暴力受害人证据收集指引（全国妇联）", "向家暴说'不'！收好这篇超全维权指南", "网信普法 转扩！遭受家暴如何收集证据"]),
 ("ART-2026-0115", "离婚后 发现 对方婚内继承房产卖房款 还能分吗",
  "完整复现北京三中院「婚内继承母亲房产份额并出售得款400余万元」案，认定售房款属夫妻共同财产、支持分割；要点含1062条/1063条第3项、遗产未实际分割的处理。",
  ["离婚后意外发现前夫婚内继承400余万房款，还能分割吗？", "女子离婚后，意外发现前夫婚内继承了400多万元房款", "婚内继承的房产，离婚时配偶竟能分走？法院判了"]),
 ("ART-2026-0115", "遗嘱只写 给儿子 没写 只归个人 儿媳 能不能分",
  "明确「给儿子」只解决谁来继承，「只归儿子个人」才解决是否夫妻共同财产；建议遗嘱写明「不作为其夫妻共同财产」。",
  ["遗嘱只写'房子给儿子'，儿媳能分吗？", "想要遗产不给儿媳的话，老人遗嘱写\"遗产归儿子\"就够了？"]),
 ("ART-2026-0115", "离婚时没处理的夫妻共同财产 离婚后 起诉 民法典1092条",
  "浅答：直接称依据1092条（隐藏转移）可再诉分割，未区分「漏分」与「隐藏转移」两条路径，未提婚姻家庭编解释（一）第83条。",
  ["婚姻家庭领域常见法律问题汇总", "《中华人民共和国民法典》第1092条", "《民法典》实施后夫妻共同财产分割相关法律问题"]),
 ("ART-2026-0116", "怀孕了不知道 签了自愿离职协议 还能撤销吗",
  "结论「一般无法撤销」，依据为劳动争议司法解释（三）第10条与「不知怀孕不构成重大误解」的判例口径；未提北京京高法发〔2024〕534号第69条地方口径。",
  ["离职一周发现怀孕 解聘协议能否撤销?", "签完离职协议还未离职时发现怀孕了，能否反悔？", "劳动争议典型案例汇编"]),
 ("ART-2026-0116", "孕期被辞退 要2N 还是 要求继续履行 哪个划算",
  "按劳动合同法第48条说明劳动者享有选择权，分别列出继续履行与2N的优劣，但未给出量化差额与决策清单。",
  ["违法解除劳动合同的赔偿标准", "公司辞退孕妇，要求继续履行会被得到支持吗？", "中国法院2025年度案例·劳动纠纷"]),
 ("ART-2026-0116", "变相辞退孕妇 证据怎么留 调岗降薪 旷工",
  "给出证据留存指南：调岗需满足生产经营需要/工资相当/无侮辱性，主张保留调岗通知、工资流水、考勤与沟通记录。",
  ["孕妇被变相辞退怎么办？", "孕期被调岗，薪资从1万4降到4千，接着被辞退！法院终于判了！", "口头辞退的法律风险与应对策略"]),
]

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT count(*) FROM geo_checks WHERE article_id=?", ("ART-2026-0103",))
print("ART-0103 rows:", cur.fetchone()[0])

rows = []
for aid, q, snip, srcs in METASO:
    rows.append((aid, "metaso", q, snip, json.dumps({"sources": srcs, "note": "来源面板无本域"}, ensure_ascii=False)))
    y = yb.get(q, {})
    head = re.sub(r"\s*\|\s*", " ", str(y.get("body_head", ""))).strip()
    ysnip = (head[:150] + "…") if head else ""
    rows.append((aid, "yuanbao", q, ysnip, json.dumps({"sources": [], "note": "元宝无来源面板"}, ensure_ascii=False)))

new = 0
for aid, plat, q, snip, comp in rows:
    cur.execute("SELECT count(*) FROM geo_checks WHERE article_id=? AND platform=? AND query_text=? AND check_date=?",
                (aid, plat, q, TODAY))
    if cur.fetchone()[0]:
        continue
    cur.execute("""INSERT INTO geo_checks (article_id, platform, query_text, check_date, found, source_url,
                   rank_position, snippet, citation_level, competitor_found, notes)
                   VALUES (?,?,?,?,0,NULL,NULL,?,?,?,?)""",
                (aid, plat, q, TODAY, snip, "none", comp, "2026-10-31 周六 双平台实测；零品牌命中"))
    new += 1
conn.commit()
print("inserted geo_checks:", new)

# 更新 geo_article_stats（以本表实际行数为口径）
for aid in ("ART-2026-0114", "ART-2026-0115", "ART-2026-0116"):
    cur.execute("SELECT count(*), coalesce(sum(found),0) FROM geo_checks WHERE article_id=? AND platform IN ('metaso','yuanbao')", (aid,))
    total, found = cur.fetchone()
    rate = round(found / total, 4) if total else 0.0
    cur.execute("""INSERT INTO geo_article_stats (article_id,total_checks,total_found,citation_rate,best_platform,
                   best_query,last_check_date,trend) VALUES (?,?,?,?,NULL,NULL,?, 'new')
                   ON CONFLICT(article_id) DO UPDATE SET total_checks=excluded.total_checks,
                   total_found=excluded.total_found, citation_rate=excluded.citation_rate,
                   last_check_date=excluded.last_check_date, trend=excluded.trend""",
                (aid, total, found, rate, TODAY))
    print(aid, "total", total, "found", found, "rate", rate)
conn.commit()

cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')")
print("cumulative checkpoints (metaso+yuanbao):", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao') AND found=1")
print("cumulative found:", cur.fetchone()[0])
conn.close()
