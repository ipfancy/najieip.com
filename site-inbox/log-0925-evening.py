#!/usr/bin/env python3
"""0925 收尾留档：deploy-log 追加修复条目（以 origin 版本为底、原生 indent=1）+ 站点日报"""
import json
import os
import subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
LOG = f"{REPO}/site-inbox/deploy-log.json"

# ---- 1. deploy-log：取 origin 版做底再 append（严禁整档重写） ----
base = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                      cwd=REPO, capture_output=True, text=True, check=True).stdout
d = json.loads(base)
n0 = len(d["deploys"])
if any(e.get("commit", "").startswith("8c6e692") for e in d["deploys"]):
    print("⏭ deploy-log 已有本条目，跳过")
else:
    d["deploys"].append({
        "date": "2026-09-25",
        "time": "13:30 CST",
        "type": "repair-4th-bare-publish + index-cards + guard-hardening",
        "commit": "8c6e692 / 5c7caa3（SiteOps 交互式会话修复）",
        "summary": "闭环晨报移交的 3 项 P1：（1）第 4 例「裸发布畸形页」——今日新文 mili/blog/20260925-… 原 8,294B、h1=0/h2=0/JSON-LD=0/无 og:image/keywords、description 复读标题 → 按同日同品牌精修页（09-24）房屋模板重建，正文与 md 源逐段 0 差异，补 h1 + 8 条描述性 h2 路标 + Article/BreadcrumbList JSON-LD + og/twitter/keywords/canonical，上线 11,941B（本地 11,574 + CF beacon 367）。（2）索引补卡：mili 栏目索引 96→97（BlogPosting JSON-LD 88→89）、主索引 182→183。（3）sitemap 守护根因加固：update-sitemap.py 原只从 articles.json 取数，46 条「页面不存在」条目致静默无产出（09-21~09-25 的 loc 全靠 08:0x 晨报人工补录）→ 双副本同改，新增品牌博客目录扫描数据源。另修复生成器层 frontmatter 泄漏（wechat-distribute 全 6 渠道导出件）。",
        "changes": [
            "mili/blog/20260925-policy-cash-value-execution-2024-instance.html：重建（8,294 → 11,574 B 本地；线上 11,941 B），正文 0 字改动",
            "mili/blog/index.html：+1 卡（97）+ blogPost JSON-LD 88→89",
            "blog/index.html：+1 卡（182→183）",
            "update-sitemap.py（仓库 + ~/.hermes/scripts 双副本）：新增目录扫描数据源",
            "site-inbox/：diag-0925-coverage.py / fix-0925-page.py / gen-0925-index-cards.py / verify-0925-live.py 留档",
            "未改动：sitemap.xml（267 loc 不变，看门测试静默 exit 0）/ articles.json / CNAME / DNS",
        ],
        "verify": {
            "article_live": "h1=1 / h2=8 / ld+json=2 / og:image ✓ / keywords ✓（curl ?cb= 实抓，2 次轮询收敛）",
            "byte_compare": "本地 11,574B vs 线上 11,941B，Δ=367B 全部为 Cloudflare beacon（既有判据）",
            "index_cards": "mili 索引卡计数 97、主索引 183，新卡均位于 body 首卡；每卡以 <h2><a href= 起、malformed=0、div 深度归零、markdown 星号 0",
            "sitemap": "267 loc，线上含该文；加固后 --check 有效待新增 0 条（51 条目录候选全为已收录或 noindex 壳，未误加）；看门测试 rc=0 静默",
            "generator_fix": "wechat-distribute：read_article_body() 统一剥离 frontmatter + 微博链接改按主体目录；6 渠道导出件重跑实测 ALL PASS，单测 5/5，残留未修读取点 0",
            "root_cause_sitemap": "守护窗口（01/04/10/16/22 时）与发布窗（05:0x）错位 + articles.json 46 条无页面条目 → 守护静默；loc 增量实证：09-21~09-25 均由晨报人工补录，窗口内守护仅成功 1 次（09-23 22:02 +7）",
        },
    })
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"✅ deploy-log: {n0} → {len(d['deploys'])} 条")

# ---- 2. 站点日报 ----
report = f"""# SiteOps 日报 — 2026-09-25（周五）

> 生成：SiteOps（交互式会话，应何律「继续做，别等着」）
> 触发：BOSS 晨报移交的 3 项 P1（09-25 新文无 h1/JSON-LD + 2 处静态索引缺卡）

## 一、今日修复（全部线上验证）

| # | 问题 | 级别 | 状态 |
|:--|:--|:--:|:--|
| 1 | **第 4 例「裸发布畸形页」**：今日新文 h1=0 / h2=0 / JSON-LD=0 / 无 og:image、无 keywords、description 复读标题（8,294B） | 🔴 P0 | ✅ 已修（线上 11,941B，四件齐备） |
| 2 | 今日新文在 mili 栏目索引 + 主索引 **零卡片** | 🔴 P0 | ✅ 已补（96→97 / 182→183） |
| 3 | **生成器层 frontmatter 泄漏**：`_cms.html`/`_zhihu.md`/`_bilibili.md`/`_toutiao.md`/`_163.md` 首部渲染出 `title/date/ai_smell` | 🔴 P0（客户可见面） | ✅ 已根治（生成时剥离，6 渠道复跑 ALL PASS） |
| 4 | sitemap 守护「窗口内静默无产出」根因 | 🟠 P1 | ✅ 已加固（新增目录扫描数据源，双副本同改） |
| 5 | 微博导出件链接指向旧扁平 `/blog/`（外发即死链） | 🟠 P1 | ✅ 已修（改按主体目录） |

## 二、根因（sitemap 守护）

实证：`loc` 增量全部来自「晨报人工补录」——09-21 07:02 / 09-22 07:01 / 09-23 08:01 / 09-24 08:03 / 09-25 08:03 各 +1，
守护（每 6h）在窗口内**只成功过一次**（09-23 22:02，+7）。两条原因：

1. **时序错位**：守护跑 01:0x/04:0x/10:0x/16:0x/22:0x，文章多在 05:0x 发布 → 04:0x 那班看不到，10:0x 那班之前 08:0x 晨报已手工补上 → 守护永远"无新增"。
2. **数据源单一**：`update-sitemap.py` 只从 `articles.json` 取数，而该文件长期有 **46 条「页面不存在」**条目（实体前缀错位/无页面）→ `validate()` 静默跳过。

修法：保留 `articles.json` 为主源，**新增品牌博客目录扫描**（`^YYYYMMDD-*.html`、非 index、存在、非跳转壳，仍走同一校验）。
加固后 `--check`：51 条目录候选全为已收录或 noindex 壳 → 有效待新增 0 条（未误加）。

## 三、验证证据

- 文章页线上实抓：`h1=1 / h2=8 / ld+json=2 / og:image ✓ / keywords ✓`；本地 11,574B vs 线上 11,941B，**Δ=367B 全部为 CF beacon**（既有判据）
- 索引：mili 97 卡 / 主索引 183 卡，新卡均在 body 首卡；`malformed=0`、div 深度归零、markdown 星号 0、日期降序
- JSON-LD：`blogPost` 88→89，`json.loads` 自检 PASS
- sitemap：267 loc，线上含该文；看门测试 `sitemap-auto.sh` **rc=0 静默**（无回灌）
- 生成器：`python3 scripts/regen-0925-exports.py` → 6 件产物 **ALL PASS**，单测 5/5，残留未修读取点 0

## 四、待跟进（未擅动）

| 项 | 说明 |
|:--|:--|
| `articles.json` 46 条「页面不存在」条目 | 上游自动发布持续复活；守卫脚本 `guard-0918-articles-json.py --check` 可检出，本次未隔离（避免与并发写方冲突） |
| GEO 抓取层（CF robots 屏蔽 GPTBot 等） | 第 17 日，仍在待何律确认清单（唯一有引用胜算的赛道） |
| 裸发布畸形页的**上游根治** | 已连续 4 例（09-21/09-22/09-24/09-25）；本机只能每次事后精修，需上游发布流水线补房屋模板 |
"""
p = f"{REPO}/../digital-employees/reports/siteops-daily-20260925.md"
open(p, "w", encoding="utf-8").write(report)
print("✅ 日报已写:", p, len(report.encode()), "B")
