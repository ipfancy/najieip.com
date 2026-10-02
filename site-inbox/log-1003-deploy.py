#!/usr/bin/env python3
# 追加 deploy-log 第 85 条 — 2026-10-03 第39周
import json, os, subprocess

R = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(R, "site-inbox/deploy-log.json")

# 取 origin 版本做底
raw = subprocess.run(["git", "-C", R, "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True)
base = raw.stdout if raw.returncode == 0 else open(P, encoding="utf-8").read()
d = json.loads(base)
n = len(d["deploys"])

ind = None
for cand in (2, 1, 4):
    if json.dumps(d, ensure_ascii=False, indent=cand) in (base, base.rstrip("\n")):
        ind = cand
        break
ind = ind or 2

entry = {
  "date": "2026-10-03",
  "time": "02:40",
  "agent": "SiteOps",
  "round": "weekly-0200 第39周（GEO 双平台追踪 + 多语言同步）",
  "commit": "7a46dfc + a14e6e7",
  "action": "多语言同步：20260928 德国实用新型文 → EN/FR 双页 + 双索引卡 + sitemap 275→277；3 篇新页 QA 补件（JSON-LD×2 / og:image / description 去标题复读）与 Markdown 残留修复",
  "files_changed": [
    "en/blog/20260928-german-utility-model-offense-en.html (new, 16033B)",
    "fr/blog/20260928-german-utility-model-offense-fr.html (new, 18032B)",
    "en/blog/index.html", "fr/blog/index.html", "sitemap.xml",
    "mili/blog/20260928-german-utility-model-offense.html",
    "mili/blog/20261001-ai-voice-clone-shanghai-first-case-evidence-shift.html",
    "najie/blog/20261002-ai-patent-reply-evidence.html"
  ],
  "cards_added": [
    "/en/blog/20260928-german-utility-model-offense-en.html",
    "/fr/blog/20260928-german-utility-model-offense-fr.html"
  ],
  "verification": {
    "sitemap_before": 275,
    "sitemap_after": 277,
    "duplicates": 0,
    "index_cards": "en 17->18 / fr 17->18；depth_end=0；每卡 depth==1；'**'=0",
    "i18n_pages": "en/fr：h1=1 / ld=1 / og:image✓ / canonical✓ / hreflang=4 / schema.org=1 / masked=0 / table=2",
    "page_repair": "german：table 0->2、md残留 6->0；voice：h1 0->1、table 0->1；patent：h1 0->1、'**' 4->0",
    "jsonld_parse": "5 页 8 个 ld+json 块全部 json.loads 通过（修复 20261002 中文直引号导致的 JSON 破损）",
    "live_check": "en 页 200 / fr 页 200（首轮 404 = Pages 构建延迟 ~2min，重试 3 次全 200）；EN 索引线上命中新卡",
    "raw_repo": "首轮 raw 000 = 网络瞬断，非故障（线上终态 200 为准）",
    "geo_week39": "18 检查点（秘塔 9/9 全通、元宝 9/9），命中 0；累计 142 检查点 / 0 命中"
  },
  "defects_found": [
    "三篇新文页面模板侧缺陷未修（10-02 当班已记录，本轮由 SiteOps 补齐）：20260928 缺 JSON-LD 且 2 张表格以 <p>|...|</p> 裸文本发布；20261001 缺 <h1>+JSON-LD+og:image 且 1 张表格未渲染；20261002 缺 <h1>+JSON-LD 且正文 4 处 ** 未转 <strong>",
    "meta description 三篇均为标题复读（已按原文事实重写，长度 134-166 字）",
    "20261002 补件时中文直引号 \"没有技术启示\" 直接写入 JSON-LD/属性 → JSON 破损；已改中文引号 “”",
    "上游发布流水线仍未做页面模板合规（本轮为第 5-7 例同源缺陷，累计已多次复发）"
  ],
  "notes": "GEO 侧选文口径：citation_rate 全 0 时按“内容吸收度 + 涉外相关度”选（本轮 = AI写专利答复 / AI声音案 / 最高检恶意诉讼 5 案，均属案例复盘型赛道）。两篇 1-2 日内新文属基线建立，非“未被引用”结论。秘塔连续第 3 周全通（9/9），元宝 9/9。",
  "result": "PASS（i18n 与页面修复均已线上验证；GEO 0 命中为实测结论）"
}

d["deploys"].append(entry)
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=ind))
print("deploy-log entries:", n, "->", len(d["deploys"]), "| indent:", ind)
