#!/usr/bin/env python3
"""2026-11-28 deploy-log 文本手术追加（+15 行 / 0 删除）"""
import json

P = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
raw = open(P, encoding="utf-8").read()
r = raw.rstrip("\n")
TAIL = "\n  }\n ]\n}"
assert r.endswith(TAIL), repr(r[-30:])

prev = json.loads(raw)["deploys"][-1]
entry = {
    "date": "2026-11-28",
    "time": "02:00",
    "agent": "SiteOps",
    "round": "GEO 周追踪（第48周周六班）",
    "commit": "6db38c8",
    "action": "第48周 GEO 18 检查点（秘塔 9/9 零墙 + 元宝 9/9，0 命中）+ 多语言同步 ART-2026-0137《漏写请求，最高五倍没了》→ EN/FR 双语页（双索引卡 + 5 页 hreflang + sitemap 446→448）",
    "files_changed": 17,
    "cards_added": 2,
    "attribution": {"en": 1, "fr": 1},
    "verification": "本地 verify-1128-i18n.py 26 项 FAILURES=NONE（en/fr ld=2 h1=1 desc>120B og:image+hreflang 4 值/零 CJK、zh 页 hreflang 4 值、索引卡 36/36、sitemap 448 loc lastmod 2026-11-28）；DB geo_checks +18 行（286 累计 / 1 命中），geo_article_stats 三篇各 6 检查",
    "defects_found": "站点 0 缺陷；工具侧 browser_exec 云端 IPC Runtime.evaluate 超时（改本地 CDP 9225 匿名通道，9/9 零墙）",
    "notes": "秘塔连续第 6 周 9/9 零登录墙。三处 AI 事实错误取证：0134 秘塔把婚姻家庭编解释（二）第6条误挂游戏账号（本条只管直播打赏）、0136 秘塔复述中介『新规倒计时』而主文件仍为国科发火〔2016〕32号、0135 合同题秘塔 1338 字漏我方 6 个独有论点（商标法第55条解除权/30天时间差/实施问答情形7/情形8/去标义务/10工作日报告）。吸收时差 ≤5 天再现：0136 元宝逐字复述『上海沪科〔2026〕89号』（该文号只出现在我方 11-23 文中）。渠道覆盖 0 条 najieip.com（约 100 来源位），二手转载占案例题、中介话术占政策题。",
    "result": "PASS",
}
assert list(entry.keys()) == list(prev.keys()), (list(entry.keys()), list(prev.keys()))

lines = []
for k, v in entry.items():
    lines.append(f'   "{k}": {json.dumps(v, ensure_ascii=False)}')
insert = ",\n  {\n" + ",\n".join(lines) + "\n  }"
head = r[:-len(TAIL)] + "\n  }"
out = head + insert + "\n ]\n}"

d = json.loads(out)
assert len(d["deploys"]) == len(json.loads(raw)["deploys"]) + 1
assert list(d["deploys"][-1].keys()) == list(prev.keys())
open(P, "w", encoding="utf-8").write(out)
print("entries:", len(json.loads(raw)["deploys"]), "->", len(d["deploys"]))
print("bytes:", len(raw), "->", len(out))
