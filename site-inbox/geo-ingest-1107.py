#!/usr/bin/env python3
"""第45周 GEO 数据入库：geo_checks + geo_article_stats"""
import json, os, sqlite3

DB = os.path.expanduser("~/wiki/database/content.db")
DATE = "2026-11-07"
SCRATCH = "/Users/ziganghe/.hermes/cache/scratch"

# ---- 秘塔 9 条（8 条来自 jsonl + 首条来自首次人工捕获）----
metaso = []
mpath = "/Users/ziganghe/.hermes/cache/browser-use/workspace/cron_44c490c5a742_95b2f3b9479e42bcb45a208cec0bac6a/metaso_1107.jsonl"
for line in open(mpath, encoding="utf-8"):
    metaso.append(json.loads(line))

first = {
    "article_id": "ART-2026-0117",
    "query": "帮商家刷好评的软件 服务商 违法吗",
    "answer_len": 756, "blocked": False, "brand_hits": [], "najieip_url": False,
    "answer_head": "是的，为商家刷好评的软件及其服务商，相关行为是违法的，且可能面临多重法律责任。一、违法性质 刷好评本质上是弄虚作假、虚假交易…二、服务商可能承担的法律责任 行政责任（反不正当竞争法第二十条，20万至300万元罚款）、民事责任（民法典1165条）、刑事责任（刑法286条）",
    "src_tail": "",
}
metaso.insert(0, first)
assert len(metaso) == 9, len(metaso)

yuanbao = [json.loads(l) for l in open(os.path.join(SCRATCH, "yuanbao_1107.jsonl"), encoding="utf-8")]
print("metaso:", len(metaso), "yuanbao:", len(yuanbao))

con = sqlite3.connect(DB)
cur = con.cursor()

rows = 0
for r in metaso:
    found = 1 if (r["brand_hits"] or r.get("najieip_url")) else 0
    level = "direct" if r.get("najieip_url") else ("indirect" if r["brand_hits"] else "none")
    note = "秘塔匿名 ?q= 直链 + innerText 轮询（>300字符且连续2次不变）"
    if r.get("blocked"):
        level = None
        note = "登录墙，未取得回答（不计入引用率分母）"
    cur.execute(
        "INSERT INTO geo_checks (article_id, platform, query_text, check_date, found, source_url, rank_position, snippet, citation_level, competitor_found, notes)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (r["article_id"], "metaso", r["query"], DATE, found, None, None,
         (r.get("answer_head") or "")[:600], level,
         json.dumps({"src_panel": (r.get("src_tail") or "")[:400]}, ensure_ascii=False), note))
    rows += 1

for r in yuanbao:
    if r.get("error"):
        cur.execute(
            "INSERT INTO geo_checks (article_id, platform, query_text, check_date, found, source_url, rank_position, snippet, citation_level, competitor_found, notes)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (r["article_id"], "yuanbao", r["query"], DATE, 0, None, None, None, None, None,
             "脚本异常：" + str(r["error"])))
        rows += 1
        continue
    hits = r.get("body_hits") or {}
    found = 1 if hits else 0
    cur.execute(
        "INSERT INTO geo_checks (article_id, platform, query_text, check_date, found, source_url, rank_position, snippet, citation_level, competitor_found, notes)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (r["article_id"], "yuanbao", r["query"], DATE, found, None, None,
         (r.get("body_head") or "")[:600], "indirect" if found else "none",
         json.dumps({"body_len": r.get("body_len"), "hits": list(hits.keys())}, ensure_ascii=False),
         "元宝 CDP 9224 登录态，geo-check-yuanbao-verify 查询词回显定位正文"))
    rows += 1

con.commit()
print("geo_checks inserted:", rows)

# ---- 更新 geo_article_stats ----
for aid in ("ART-2026-0117", "ART-2026-0118", "ART-2026-0119"):
    cur.execute("SELECT count(*), coalesce(sum(found),0) FROM geo_checks WHERE article_id=? AND platform IN ('metaso','yuanbao')", (aid,))
    total, found = cur.fetchone()
    rate = round(found / total, 4) if total else 0.0
    cur.execute("SELECT article_id FROM geo_article_stats WHERE article_id=?", (aid,))
    exists = cur.fetchone()
    if exists:
        cur.execute("UPDATE geo_article_stats SET total_checks=?, total_found=?, citation_rate=?, last_check_date=?, trend=? WHERE article_id=?",
                    (total, found, rate, DATE, "new", aid))
    else:
        cur.execute("INSERT INTO geo_article_stats (article_id, total_checks, total_found, citation_rate, best_platform, best_query, last_check_date, trend)"
                    " VALUES (?,?,?,?,?,?,?,?)", (aid, total, found, rate, None, None, DATE, "new"))
con.commit()

cur.execute("SELECT article_id, total_checks, total_found, citation_rate, last_check_date FROM geo_article_stats WHERE last_check_date=? ORDER BY article_id", (DATE,))
for r in cur.fetchall():
    print("STAT", r)

cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')")
print("累计检查点:", cur.fetchone()[0])
cur.execute("SELECT platform, count(*), sum(found) FROM geo_checks WHERE check_date=? GROUP BY platform", (DATE,))
print("本周:", cur.fetchall())
con.close()
