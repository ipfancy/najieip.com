#!/usr/bin/env python3
"""追加 deploy-log（文本手术，+15 行 / 0 删除）"""
import json, subprocess, os

P = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     cwd="/Users/ziganghe/wiki/najieip-verify", capture_output=True, text=True).stdout
if not raw:
    raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
last_keys = list(d["deploys"][-1].keys())

entry = {
    "date": "2026-11-21",
    "time": "02:00",
    "agent": "SiteOps",
    "round": "GEO 周班（第47周：GEO 追踪 + 多语言同步）",
    "commit": "0492f74",
    "action": "第47周 GEO 双平台 18 检查点（秘塔 9/9 零登录墙连续第 5 周 + 元宝 9/9）0 命中，累计 250→268；多语言同步 ART-2026-0128 马尔代夫商标法 → EN 12,193B + FR 13,000B（各 2 个 h2 路标、逐语言单独请求、零中文残留），en/fr 索引 34→35 卡，中文页补 hreflang 四值，sitemap 426→428",
    "files_changed": 6,
    "cards_added": 2,
    "attribution": {"en": 1, "fr": 1},
    "verification": "线上 3 页 HTTP 200（首查 en/zh 各 1 次 000 瞬断，重试即 200）；EN/FR/ZH 均 ld=2 且 json.loads 全通、og:image 自托管、hreflang 四值、h1=1、article 区 CJK=0（en/fr）、**=0；en|fr 索引卡 HIT（len=23292/24648 字符）；封面 img 200；sitemap loc=428 且含 EN/FR 两条 loc；Pages run 0492f74 completed/success（18:07Z）；本地终验 FAILURES=0，线上终验 FAILURES=0",
    "defects_found": "中文页此前 hreflang 为 0 条（本次补四值）；GEO 侧本周 0 命中：上周唯一命中（元宝相关视频卡）同题材未复现；秘塔把 802 号令逾期利息答成 728 号令第 15 条（旧条号），元宝条号对但施行日错写 2020-09-01",
    "notes": "本周新增行规：① 视频卡是「可触发的概率曝光」而非「词命中即出」——上周命中绑定的是一条特定短视频，未做同题视频即不复现，需文章+短视频成对投放；② 「权威源真空」是新选题判据（查人脸信息存设备还是上云，秘塔 15 条来源全是设备厂商软文，无对手占位）；③ 元宝侧出现「条号对、施行日错」的新错法，说明「新法条号+施行日」是最可争夺的组合锚点；④ i18n 描述须按句边界裁到 140-250 字符（首版 EN 485 / FR 293 字符过长）；⑤ 秒级 curl 探活串行会拖过 300s，改后台跑 + 轮询",
    "result": "PASS",
}
assert list(entry.keys()) == last_keys, f"schema drift: {list(entry.keys())} vs {last_keys}"

TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith(TAIL), "tail mismatch"
r = raw.rstrip("\n")
head = r[: -len(TAIL)] + "\n  }"
lines = "".join(f'   "{k}": {json.dumps(v, ensure_ascii=False)},\n' for k, v in entry.items())
lines = lines.rstrip(",\n")
new = head + ",\n  {\n" + lines + "\n  }" + "\n ]\n}"

parsed = json.loads(new)
assert len(parsed["deploys"]) == len(d["deploys"]) + 1
open(P, "w", encoding="utf-8").write(new)
print("entries:", len(d["deploys"]), "->", len(parsed["deploys"]))
print("OK")
