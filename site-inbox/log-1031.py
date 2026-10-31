#!/usr/bin/env python3
"""Append entry to site-inbox/deploy-log.json (text surgery) + write daily report."""
import os, json, re, subprocess, datetime

REPO = os.path.expanduser("~/wiki/najieip-verify")
LOG = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(LOG, encoding="utf-8").read()
d = json.loads(raw)
last = d["deploys"][-1]
print("prev keys:", list(last.keys()))
print("prev last entry:", last.get("date"), last.get("commit"))
print("tail repr:", repr(raw[-60:]))

head_sha = subprocess.run("git rev-parse --short HEAD", shell=True, cwd=REPO, capture_output=True, text=True).stdout.strip()

entry = {
 "date": "2026-10-31",
 "time": "22:15",
 "agent": "siteops",
 "round": "每日运营",
 "commit": head_sha,
 "action": "精修「部分裸发布」页（工具中立／反不正当竞争法13条，正文被截断3段+2段声明）按 md 源重建并套同日 najie 房屋；三索引补卡（najie 96→98、mili 141→142、主索引 251→254）；articles.json 守卫第18次隔离 277→226；aipunajie 索引清理 5 张死链卡",
 "files_changed": 9,
 "cards_added": 6,
 "attribution": {"najie/blog/20261031-najie-specialized-sme-patent-screen.html": "najie",
                 "najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html": "najie",
                 "mili/blog/20261031-mili-mofcom-trade-secret-sanctions.html": "mili"},
 "verification": "线上 3 文章页 200 + h1=1/ld=2/og:image/desc>80/stars=0 全 OK；封面 img 200；三索引 6 处卡全 HIT；aipunajie 死链卡线上 GONE；live articles.json=226；sitemap 看门 exit 0（369 loc 已含三文，上游 5262e35 已补 /topics/）",
 "defects_found": "①「部分裸发布」1 篇：h1 有、外链样式有，但 ld+json=0、无 og:image、description 复读标题、正文截断（缺「一句话收口」+欢迎评论+两条免责声明）、ASCII 直引号未转；②三篇当日文全部未进品牌索引与主索引（上游 commit 只发布页面）；③articles.json 51 条无页面条目（首页 slice(0,6) 前 3 位是新文，隔离后仍全命中）；④aipunajie 索引 5 张卡指向已不存在的文件（线上 404/000）",
 "notes": "SITEMAP 无需改动（三文已在 357→359 那次纳入）；aipunajie 五张死链卡均无同名文件落在 mili/najie 目录，故直接移除卡片而非改指向；裸发布页 canonical/og:url 已正确指向 najie 目录，无需纠正",
 "result": "PASS",
}

assert list(entry.keys()) == list(last.keys()), ("schema mismatch", list(entry.keys()), list(last.keys()))

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), repr(r[-40:])
head = r[:-len(TAIL)] + "\n  }"
lines = []
for k, v in entry.items():
    lines.append(f'   "{k}": ' + json.dumps(v, ensure_ascii=False))
body = ",\n".join(lines)
new = head + ",\n  {\n" + body + "\n  }\n ]\n}"
json.loads(new)  # self check
open(LOG, "w", encoding="utf-8").write(new)
print("appended. deploys:", len(json.loads(new)["deploys"]))

# daily report
rep = os.path.expanduser("~/wiki/digital-employees/reports")
os.makedirs(rep, exist_ok=True)
rp = os.path.join(rep, "siteops-daily-20261031.md")
open(rp, "w", encoding="utf-8").write(f"""# SiteOps 日报 — 2026-10-31（周六）

## ✅ 站点状态
- 核心 6 页全部 200：`/`、`/mili/`、`/najie/`、`/blog/`、`/sitemap.xml`、`/llms.txt`（本轮零瞬断）
- sitemap 369 loc / 369 lastmod（上游 5262e35 补 /topics/ 十条）；看门脚本 exit 0 静默，无回灌

## 🔧 本轮修复
1. **精修「部分裸发布」1 篇**：`najie/blog/20261031-mili-ai-product-image-review-tool-neutrality.html`
   （「工具中立」还能用多久／反不正当竞争法第13条）
   - 缺陷：ld+json=0、无 og:image、description 复读标题、**正文被截断**（缺收口段 + 欢迎评论 + 两条免责声明）、直引号未转
   - 处理：按 md 源重建（6,262B → **10,810B**），套同日 najie 精修页房屋，Article+BreadcrumbList 双 JSON-LD、og/twitter/keywords/真摘要 185 字、封面 `img/<slug>.png` 入库
   - 断言：md 正文（剥标记/空白）**完整包含于页面正文**；h1=1、ld=2、schema.org≥2、canonical 指向落脚目录、无 `https://***`
2. **三索引补卡 6 张**（当日 3 篇全缺品牌卡与主索引卡）：najie 96→98、mili 141→142、主索引 251→254，日期降序插位
3. **articles.json 守卫（第 18 次）**：277 → **226** 条（隔离 51 条无页面条目），首页 slice(0,6) 六条全部有页面且即本文三篇
4. **aipunajie 索引清 5 张死链卡**（对应文件已不存在，线上 404/000）

## 📊 验证
- 3 文章页线上 200 + 六项判据全 OK；封面图 200；三索引 6 处卡全 HIT；死链卡线上 GONE；live articles.json = 226
- **FAILURES: NONE**

## ⚠️ 观察
- 上游 `2e4815d` 只发布页面（写 articles.json、sitemap、img），未写任何索引卡 → 当日新文「双索引零卡」已成常态，每日必须逐 slug `grep -c`
- 「部分裸发布」本轮回退到带**正文截断**的一档：md 有 19 段、页面只落 15 段，说明上游 md→HTML 生成器在长文上有截断风险，建议每条正文比对按「md 全包含于页面」而非仅段落数
""")
print("report:", rp)
