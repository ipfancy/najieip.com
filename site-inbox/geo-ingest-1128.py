#!/usr/bin/env python3
"""2026-11-28 GEO 入库：读 metaso/yuanbao 两个 JSON → geo_checks + geo_article_stats"""
import json, re, sqlite3, os

DB = "/Users/ziganghe/.hermes/../wiki/database/content.db"
DB = os.path.expanduser("~/wiki/database/content.db")
SI = "/Users/ziganghe/wiki/najieip-verify/site-inbox"
DATE = "2026-11-28"
BRANDS = ["najieip.com", "纳杰觅理", "何自刚", "爱普纳杰", "觅理", "纳杰"]


def level_of(hits):
    if not hits:
        return "none"
    if "najieip.com" in hits:
        return "direct"
    return "indirect"


def clean(s, n=230):
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s[:n]


rows = []
for fn in ("geo-metaso-1128.json", "geo-yuanbao-1128.json"):
    p = os.path.join(SI, fn)
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    for r in json.load(open(p)):
        plat = r.get("platform")
        hits = r.get("body_hits") or {}
        wall = r.get("login_wall")
        found = 1 if hits else 0
        if wall:
            lvl = None
            note = "秘塔登录墙，标 blocked，不计入引用率分母"
        else:
            lvl = level_of(hits)
            if plat == "metaso":
                src = clean(r.get("sources_tail", ""), 150)
                note = f"秘塔正文 {r.get('body_len')} 字；来源面板：{src}"
            else:
                note = f"元宝正文 {r.get('body_len')} 字（无来源面板）"
            if hits:
                note = "命中：" + "; ".join(f"{k}×{v['count']}" for k, v in hits.items()) + " | " + note
        snippet = clean(r.get("body_head", ""))
        if hits:
            snippet = clean(" || ".join(v["ctx"] for v in hits.values()))
        rows.append((r["article_id"], plat, r["query"], DATE, found, snippet, lvl, note, bool(wall)))

con = sqlite3.connect(DB)
cur = con.cursor()
n_ins = 0
for aid, plat, q, d, found, snip, lvl, note, wall in rows:
    ex = cur.execute("SELECT count(*) FROM geo_checks WHERE article_id=? AND platform=? AND query_text=? AND check_date=?",
                     (aid, plat, q, d)).fetchone()[0]
    if ex:
        continue
    cur.execute("""INSERT INTO geo_checks (article_id, platform, query_text, check_date, found, source_url,
                   rank_position, snippet, citation_level, competitor_found, notes)
                   VALUES (?,?,?,?,?,NULL,NULL,?,?,NULL,?)""",
                (aid, plat, q, d, found, snip, lvl, note))
    n_ins += 1

# 重算 stats
aids = sorted({r[0] for r in rows})
for aid in aids:
    tot = cur.execute("SELECT count(*) FROM geo_checks WHERE article_id=? AND citation_level IS NOT NULL", (aid,)).fetchone()[0]
    hit = cur.execute("SELECT count(*) FROM geo_checks WHERE article_id=? AND found=1", (aid,)).fetchone()[0]
    rate = round(hit / tot, 4) if tot else 0.0
    best_plat = cur.execute("SELECT platform FROM geo_checks WHERE article_id=? AND found=1 LIMIT 1", (aid,)).fetchone()
    best_q = cur.execute("SELECT query_text FROM geo_checks WHERE article_id=? AND found=1 LIMIT 1", (aid,)).fetchone()
    last = cur.execute("SELECT max(check_date) FROM geo_checks WHERE article_id=?", (aid,)).fetchone()[0]
    trend = "rising" if hit else "stable"
    cur.execute("""INSERT INTO geo_article_stats (article_id, total_checks, total_found, citation_rate,
                   best_platform, best_query, last_check_date, trend)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(article_id) DO UPDATE SET
                     total_checks=excluded.total_checks, total_found=excluded.total_found,
                     citation_rate=excluded.citation_rate, best_platform=excluded.best_platform,
                     best_query=excluded.best_query, last_check_date=excluded.last_check_date,
                     trend=excluded.trend""",
                (aid, tot, hit, rate, best_plat[0] if best_plat else None,
                 best_q[0] if best_q else None, last, trend))
    print(f"STATS {aid}: checks={tot} found={hit} rate={rate}")

con.commit()
tot_all = cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')").fetchone()[0]
tot_hit = cur.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao') AND found=1").fetchone()[0]
print(f"INSERTED {n_ins} rows | cumulative metaso+yuanbao checks={tot_all} hits={tot_hit}")
con.close()
