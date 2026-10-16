#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 2026-10-17 GEO 周任务 deploy-log 条目（以 origin/main 版本为底，indent=1，只 append）"""
import json, os, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
P = f"{REPO}/site-inbox/deploy-log.json"

raw = subprocess.run(["git", "-C", REPO, "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True, check=True).stdout
log = json.loads(raw)
before = len(log["deploys"])

entry = {
    "date": "2026-10-17",
    "time": "02:3x CST",
    "agent": "SiteOps",
    "round": "geo-weekly-week42",
    "commit": "68d6c53",
    "action": "第42周 GEO 追踪（3 篇 × 3 查询词 × 秘塔/元宝）+ 多语言同步 ART-2026-0105 AI短剧/Token 成本入赔 → EN+FR 页 + 双索引卡 + 中文页 hreflang + sitemap loc + 封面图入库",
    "files_changed": [
        "en/blog/20261009-mili-ai-short-drama-token-evidence-en.html",
        "fr/blog/20261009-mili-ai-short-drama-token-evidence-fr.html",
        "en/blog/index.html",
        "fr/blog/index.html",
        "mili/blog/20261009-mili-ai-short-drama-token-evidence.html",
        "img/20261009-mili-ai-short-drama-token-evidence.png",
        "sitemap.xml",
        "site-inbox/geo-*.py/json（register/ingest/batch/结果档）",
        "site-inbox/gen-1017-i18n-*.py、install-1017-i18n.py、verify-1017-i18n.py、live-1017.py",
    ],
    "cards_added": 2,
    "verification": "本地结构终验 33 项 FAILURES=0；线上终验 32 项 FAILURES=0（11/11 核心页 200；EN 13,531B / FR 14,288B 线上字节与本地严格一致；双索引卡 HIT；封面图 200；sitemap 311 loc；articles.json 190）；sitemap 看门测试 exit 0 静默、loc 不变",
    "defects_found": [
        "秘塔 4/9 查询撞登录墙（微信扫码，登录后继续搜索）→ 按行规停止重试标 blocked（第 6 条起）：0104×1、0105×3",
        "GEO 引用率 0/18（有效判定 0/14）——连续第 10 个有效执行周期 0 命中；累计 178 检查点 0 命中",
        "我方独家案件 (2025)最高法知民终950号（腾冲燃气案）在秘塔/元宝均零收录，AI 同题只答他案 (2023)最高法知民终1547号",
    ],
    "notes": "秘塔来源面板本周以「官方通告 + 学术论文」为主（10+7 条），门户转载少见，najieip.com 与品牌名 0 占位。元宝 9/9 无来源面板（内化复述），吸收度极高：逐字复述武汉江岸 AI 短剧案 47 集/赔 2 万/Token 与算力成本入赔。新识别缺口题：「商标新稿第28条两方案」秘塔只会背 2017 旧法释、元宝答对 → 两平台分化=真实内容缺口。多语言数字保真按语言分别核（EN 20,000 / FR 20 000；EN 1,700 / FR 1 700），0 FAIL。articles.json 守卫 190/190 0 违例（第 17 次隔离未复活）。",
    "result": "success",
}

log["deploys"].append(entry)
with open(P, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print(f"deploys {before} -> {len(log['deploys'])}")
print("file bytes:", os.path.getsize(P))

# 校验：JSON 可解析 + 历史条目未变
d2 = json.load(open(P, encoding="utf-8"))
assert len(d2["deploys"]) == before + 1
assert d2["deploys"][0] == log["deploys"][0]
print("OK")
