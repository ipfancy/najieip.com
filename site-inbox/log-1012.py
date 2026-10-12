#!/usr/bin/env python3
# 追加 deploy-log（取 origin/main 版本做底，indent=1）
import json, subprocess, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
PATH = "site-inbox/deploy-log.json"

raw = subprocess.run(["git", "show", f"origin/main:{PATH}"], cwd=REPO,
                     capture_output=True, text=True, check=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and "deploys" in log, "schema drift"

entry = {
    "date": "2026-10-12",
    "round": "第41周 GEO 追踪 + 多语言同步（cron 44c490c5a742）",
    "action": (
        "GEO：新文 ART-2026-0100/0101/0102（发布 7–9 日，首次有效引用判定点）入库追踪池，"
        "秘塔匿名 9/9 + 元宝本地 CDP 9/9 = 18 检查点，0 命中，累计 160/0。"
        "i18n：ART-2026-0101 拓竹×Stratasys 双语化 → EN 14,579B（4 条描述性 h2）/ FR 16,138B（5 条），"
        "中文权威页 hreflang 四值，en/fr 索引卡 19→20，sitemap 302→304。"
        "并行：articles.json 守卫第 15 次隔离 234→184。"
    ),
    "files_changed": [
        "en/blog/bambu-stratasys-fto-decision-tree-20261004-en.html",
        "fr/blog/bambu-stratasys-fto-decision-tree-20261004-fr.html",
        "en/blog/index.html",
        "fr/blog/index.html",
        "mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
        "sitemap.xml",
        "articles.json",
    ],
    "verification": (
        "线上终验 FAILURES=0：11/11 URL 200（6 核心页 + 3 文章页 + sitemap + articles.json）；"
        "新页线上字节与本地严格一致（EN 14,579 / FR 16,138）；两页 h1=1 / ld+json=1 且 json.loads 通过 / "
        "og:image=1 / `**`=0 / hreflang=4 / h2=4 与 5 / table=1；双索引卡 HIT=True 且卡数 20；"
        "sitemap 线上 304 loc 且 EN+FR loc 均命中；本地结构终验 42 项断言全 PASS。"
    ),
    "defects_found": (
        "① 上游 articles.json 违例条目第 15 次整体复活（234 条，50 条无页面）——已幂等隔离；"
        "② 译文初版 0 个 <h2>（中文源本就无小标题）：加「描述性 h2 路标」后正文逐字不变断言校验；"
        "③ 数字保真校验器口径过严会把 EN/FR 语言化写法（27.6 million / 27,6 millions）误报为丢数字——已按语言分别核；"
        "④ 第 39 周（09-26）与第 40 周（10-10）GEO 任务零产出，本次周报如实标注缺档、不做连续拼接。"
    ),
    "notes": (
        "第 41 周 GEO 18 检查点 0 命中；累计 160 检查点 / 0 命中（口径 metaso+yuanbao）。"
        "新洞察：门户/行业媒体首发占位持续；「内容缺口=署名机会」（AI 答案比我方文章浅的题目才可争夺）；"
        "元宝无来源面板（纯内化复述）与秘塔（检索+来源面板）性质不同，署名策略需分开。"
        "正文零改动（h2 插入经逐字断言）。"
    ),
    "result": "PASS",
}

log["deploys"].append(entry)
out = json.dumps(log, ensure_ascii=False, indent=1)
with open(os.path.join(REPO, PATH), "w", encoding="utf-8") as f:
    f.write(out)
print("deploys now:", len(log["deploys"]))
print("bytes:", len(out.encode()))
