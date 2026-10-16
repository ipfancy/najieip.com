#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 2026-10-17 GEO 结果写入 geo_checks + 更新 geo_article_stats。幂等（先删当日同平台行）。"""
import json, os, sqlite3

BASE = os.path.expanduser("~/wiki/najieip-verify/site-inbox")
DB = os.path.expanduser("~/wiki/database/content.db")
TODAY = "2026-10-17"
ARTS = ["ART-2026-0103", "ART-2026-0104", "ART-2026-0105"]

METASO_NOTES = {
 "赢了官司 判决书里的合规建议 有约束力吗": "无品牌命中；秘塔抓住「判决主文（判项）才有执行力，说理部分不能作为执行依据」，与文章主论点同源但未署名；来源为「判决主文与判决理由的区分」等论文与司法建议新闻，无官方通稿",
 "燃气公司 滥用市场支配地位 胜诉 最高法": "无品牌命中；秘塔答的是青海民和川某天然气搭售案（他案），完全未提我方（2025）最高法知民终950号腾冲案 → 该案AI零收录",
 "反垄断 判决后 合规整改 怎么留痕": "无品牌命中；秘塔只给「书面报告承诺履行情况」泛论 + 处罚文书示范文本，未覆盖我方「要求→动作→留痕载体」三段式清单 → 内容缺口=署名机会",
 "商标法 司法解释 征求意见 2026 截止时间": "无品牌命中；秘塔答对两截止日（最高法 10-28 / 国知局 11-12），但来源几乎全是最高法/国知局官方通告 → 权威来源挤压效应典型",
 "商标授权确权规定 第28条 两个方案": "无品牌命中；秘塔只给现行 法释〔2017〕2号 旧条文并自认「只检索到第28条上述规定」，完全未覆盖2026征求意见稿并列两方案 → 强内容缺口",
}
METASO_BLOCKED = [
 "商标审查审理指南 征求意见 怎么提意见",
 "AI短剧 被搬运 赔多少钱",
 "AI生成内容 视听作品 认定标准",
 "AI创作 token 算力成本 算进赔偿",
]

YUANBAO_NOTES = {
 "赢了官司 判决书里的合规建议 有约束力吗": "无品牌命中；元宝完整复述「不能申请强制执行 / 不直接产生既判力 / 不是行政命令」三层，与我方文章结构同源、0 署名",
 "燃气公司 滥用市场支配地位 胜诉 最高法": "无品牌命中；元宝给 (2023)最高法知民终1547号 民和川某案（他案），未涉及我方 950号腾冲案",
 "反垄断 判决后 合规整改 怎么留痕": "无品牌命中；吸收度极高——元宝给出「问题—决策—措施—执行—验证—持续运行」闭环 + 整改台账字段建议，与我方框架同层，0 署名",
 "商标法 司法解释 征求意见 2026 截止时间": "无品牌命中；元宝精确复述「最高法 2026-09-14 公告 / 截止 2026-10-28」，并主动提醒与国知局《业务处理办法》截止日区分",
 "商标授权确权规定 第28条 两个方案": "无品牌命中；元宝正确识别「两个方案=征求意见稿两种起草写法」并与现行 法释〔2017〕2号 对比 → 吸收度高、0 署名",
 "商标审查审理指南 征求意见 怎么提意见": "无品牌命中；元宝给出三种官方渠道（邮箱 sg1@cnipa.gov.cn / 传真 010-68037822 / 信函商标局审业管理处）→ 官方信息被优先吸收，署名机会在「提什么意见」而非「怎么提」",
 "AI短剧 被搬运 赔多少钱": "无品牌命中；元宝完整复述武汉江岸 AI 微短剧案（47集、改名整部搬运、插广告、判赔2万）并点出 Token/算力与商用工具成本被纳入考量 → 我方核心事实被逐字吸收、0 署名",
 "AI生成内容 视听作品 认定标准": "无品牌命中；元宝给出「不看是否AI生成，看人类连续性实质智力投入与控制力」口径，与我方文章同源",
 "AI创作 token 算力成本 算进赔偿": "无品牌命中；元宝精确认定「可作为法定赔偿酌定因素，非当然全额赔」并引武汉江岸案 Token/算力/商用工具授权费 → 吸收度极高、0 署名",
}

metaso = json.load(open(os.path.join(BASE, "geo-metaso-1017.json")))
yuanbao = json.load(open(os.path.join(BASE, "geo-yuanbao-1017.json")))

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("DELETE FROM geo_checks WHERE check_date=? AND platform IN ('metaso','yuanbao')", (TODAY,))
cur.execute("DELETE FROM geo_checks WHERE platform='pending' AND article_id IN (?,?,?)", ARTS)
print("cleaned rows:", cur.rowcount)

ins = 0
for r in metaso:
    hits = r.get("hits") or []
    blocked = bool(r.get("blocked"))
    found = 1 if hits else 0
    if blocked:
        note = "登录墙（微信扫码，登录后继续搜索）→ 本查询未取得结果，按 blocked 记录，不重试"
        level = None
    else:
        note = METASO_NOTES.get(r["query"], "无品牌命中")
        level = "none"
    cur.execute("""INSERT INTO geo_checks
        (article_id, platform, query_text, check_date, found, citation_level, snippet, notes)
        VALUES (?,?,?,?,?,?,?,?)""",
        (r["article"], "metaso", r["query"], TODAY, found, level, "",
         f"{note} | answer_len={r.get('len')} | blocked={blocked} | sources={ (r.get('sources') or '')[:200] }"))
    ins += 1

for r in yuanbao:
    hits = r.get("body_hits") or {}
    found = 1 if hits else 0
    cur.execute("""INSERT INTO geo_checks
        (article_id, platform, query_text, check_date, found, citation_level, snippet, notes)
        VALUES (?,?,?,?,?,?,?,?)""",
        (r["article"], "yuanbao", r["query"], TODAY, found, "none", "",
         f"{YUANBAO_NOTES.get(r['query'],'无品牌命中')} | body_len={r.get('body_len')}"))
    ins += 1

print("inserted:", ins)

for aid in ARTS:
    cur.execute("""SELECT count(*), sum(found) FROM geo_checks
        WHERE article_id=? AND platform IN ('metaso','yuanbao')""", (aid,))
    tot, fnd = cur.fetchone()
    tot, fnd = tot or 0, fnd or 0
    rate = round(fnd / tot, 4) if tot else 0.0
    trend = "new" if tot <= 12 else ("rising" if fnd else "stable")
    cur.execute("""UPDATE geo_article_stats
        SET total_checks=?, total_found=?, citation_rate=?, last_check_date=?, trend=?
        WHERE article_id=?""", (tot, fnd, rate, TODAY, trend, aid))
    print(f"[stats] {aid}: checks={tot} found={fnd} rate={rate} trend={trend}")

con.commit()
cur.execute("SELECT count(*), coalesce(sum(found),0) FROM geo_checks WHERE platform IN ('metaso','yuanbao')")
cum, cumf = cur.fetchone()
print(f"\nCUMULATIVE metaso+yuanbao: {cum} checkpoints, {cumf} found")
cur.execute("SELECT platform, count(*), coalesce(sum(found),0) FROM geo_checks WHERE check_date=? GROUP BY platform", (TODAY,))
print("today:", cur.fetchall())
con.close()
