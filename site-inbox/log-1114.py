import json, os

P = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
raw = open(P).read()
assert raw.rstrip().endswith("}\n ]\n}".replace("}", "}")) or True
r = raw.rstrip("\n")
TAIL = "\n  }\n ]\n}"
assert r.endswith(TAIL), repr(r[-30:])

entry = {
 "date": "2026-11-14",
 "time": "02:00",
 "agent": "SiteOps",
 "round": "每周 GEO 追踪 + 多语言同步（cron 44c490c5a742）",
 "commit": "b263044",
 "action": "第46周 GEO 18 检查点（秘塔 9 + 元宝 9）→ 入库 geo_checks/geo_article_stats + 周报；ART-2026-0129 荷兰突击搜查文 EN+FR 双语页上线",
 "files_changed": "en/blog/20261113-byd-netherlands-evidence-seizure-en.html（14,607B）、fr/blog/20261113-byd-netherlands-evidence-seizure-fr.html（16,903B）、en|fr/blog/index.html（各 25→26 卡）、mili/blog/20261113-byd-netherlands-evidence-seizure.html（补 hreflang 四值）、sitemap.xml（403→405 loc）",
 "cards_added": 2,
 "attribution": "选文按「涉外相关度 + 本周吸收时差最短」；GEO 数据源一体两用（同批 18 条结果既入 geo_checks，又做周报渠道覆盖与平台分化分析）",
 "verification": "线上 en/fr 页字节与本地严格一致（14,607B / 16,903B，delta 0），h1=1 / ld=2（BlogPosting+BreadcrumbList，各含 @context）/ og:image 313KB 200 / hreflang 4 / h2=5 / 表=1 / 零中文残留（仅语言条「中文」）/ **=0；en|fr 索引各 26 卡且 slug 命中 1；中文页 hreflang=4；sitemap 405 loc 且线上字节与本地 IDENTICAL（含 3 处 byd-netherlands）；Pages run 43480064254 completed/success",
 "defects_found": "① GEO 平台分化方向与上周相反：秘塔把新反法第29条答成 2019 版第24条（旧法），元宝答对；职务发明 5% 题秘塔答成「草案+实施细则2%」、元宝答对促进科技成果转化法第45条 → 「某平台强弱」结论不可跨周沿用；② 我方「镇江53万+500万两条责任」框架两平台均未采纳（元宝归给「淘宝/天猫一键搬家案500万」）→ 缺可检索锚点；③ 3 篇中 2 篇（0120/0129）0 命中，唯一命中来自 0124 的元宝「相关视频」卡",
 "notes": "★首次品牌命中（9 周 0 后破零）：元宝查询「公司说产品整体亏损 还要付发明人报酬吗」正文内挂出我方短视频卡《产品还在亏损-公司却被判付80万…》（署名 何自刚｜知识产权律师｜纳杰觅理），DOM 实证位于 .ybc-chat-videoBoxV2-bigCard（x=321/1200 聊天列），非登录头像区 → citation_level=indirect。累计检查点 232→250，累计命中 0→1。秘塔连续第 4 周 9/9 零墙；元宝 9/9。吸收时差缩短至 1 天（11-13 发布，11-14 两平台已复述 JLR/BYD Ti7 案撤销理由）。",
 "result": "PASS",
}

lines = []
for k, v in entry.items():
    lines.append(f'   "{k}": {json.dumps(v, ensure_ascii=False)}')
insert = ",\n  {\n" + ",\n".join(lines) + "\n  }"

head = r[:-len(TAIL)] + "\n  }"
new = head + insert + "\n ]\n}"

d = json.loads(new)
assert len(d["deploys"]) == 138
assert list(d["deploys"][-1].keys()) == list(d["deploys"][-2].keys()), "schema mismatch"
open(P, "w").write(new)
print("appended, entries =", len(d["deploys"]), "bytes", len(new))
