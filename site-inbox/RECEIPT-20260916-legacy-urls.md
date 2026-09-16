# 回执：najieip.com 站点遗留问题（Mac 端交接单 2026-09-16）

**处理方**：Windows 端 · 门丞（siteops profile）
**处理时间**：2026-09-16 14:40–14:50 CST
**提交**：`f94c3f7`（遗留项 1）、`2471f47`（遗留项 3），均已 push 并核对远程 HEAD

> 交接单回执行（供 Mac 端追加）：
> `2026-09-16 已处理 by Windows端(siteops/门丞) — 提交 f94c3f7、2471f47`

---

## 遗留项 1：sitemap 与索引里的旧路径 —— ✅ 已闭环

实测（处理前）：sitemap 432 loc，其中 `/articles/` **94**；articles.json 170 条，其中 `/articles/` **78**。
94 条拆开是：68 条跳转页 + 22 条"真内容副本"（19 条机构目录另有正版）+ **4 条死链 loc**（文件不存在，curl 404）。

| 动作 | 结果 |
|------|------|
| `articles.json` | 170 → **123** 条：删 45 条纯重复 + 2 条幽灵条目；29 条 url 归位三主体；`site` 字段与 URL 前缀强制一致；URL 唯一 |
| `sitemap.xml` | 432 → **231** loc：剔 `/articles/` 94 条、根级/机构内跳转桩 loc 102 条、死链 4 条、中文原样/%编码重复登记 10 条（保与页面 canonical 一致者） |
| /articles/ 真内容副本 | 18 个 → 统一跳转桩（canonical + meta refresh + `noindex,follow`） |
| 孤儿页迁移 | 2 篇"仅存 /articles/ 副本"迁入 `najie/blog/`（复制 + description/canonical/og 五件套 + 索引卡片 + JSON-LD BlogPosting），`/articles/` 原址留跳转桩 |
| 幽灵条目 | 2 条（《工信部点名"一人公司"…真账本》《孩子被指"摸臀"…》）全仓仅 articles.json 引用，页面从未上线 → 摘链并在此回报，**未造链** |

判定口径：同 basename 命中 → canonical/refresh 目标 → 标题匹配 → 孤儿页按**案件性质优先**（微短剧 IP 清单、中国专利奖名额收紧均归 najie，与同族群《中国专利奖申报策略》既有归位一致）。

**验证（线上实测，非本地推断）**：

- sitemap 线上 231 loc / `/articles/` 0；articles.json 线上 123 条 / `/articles/` 0
- 本地 loc = 线上 loc（local-only 0、live-only 0）
- 跳转/别名页 loc 0、重复登记 0、非 200 loc 0（`sitemap_loc_audit.py` 全绿）
- 首页 `slice(0,6)` 六张卡片全部 200（处理前第 3、4 张是重复跳转卡，第 6 张是 404 死链卡）
- 旧 `/articles/` 桩仍 200（老链接不断），2 篇迁入页 200
- 别名 loc 目标失联 0、articles.json 每个 URL 均有 loc

## 遗留项 2：跳转非 301 —— ⏸ 待 CF 侧授权（素材已备）

GitHub Pages 无法真 301；站点无 `_config.yml`+`.nojekyll`，Jekyll `redirect_from` 不可用 → 只能走 Cloudflare。

- 已生成 **`site-inbox/cf-redirects-articles-20260916.csv`**（76 条：`source,target,status=301,preserve_query_string=true,preserve_path_suffix=false`），可直接导入 CF **Bulk Redirects**；每条 target 已校验有对应文件
- **本机无 CF API token**，无法代配。所需权限：Zone → **Redirect Rules / Bulk Redirects: Edit**（+ Zone:Read）。Analytics read 权限不足以改重定向
- 页面内 meta refresh 保留作兜底；`noindex,follow` 已补，即使 CF 未配也不产生重复内容信号

## 遗留项 3（非必须）：历史页 SEO 要素 —— ✅ 已批量补齐

规范页（排除跳转桩）**224** 个，补齐前后：

| 标签 | 处理前 | 处理后 |
|------|:--:|:--:|
| description | 192/225 | **224/224** |
| canonical | 181/225 | **222/224** |
| og:title / og:url / og:type / og:image / twitter:card | 96–136/225 | **221/224** |

取值规则：全部来自页面**既有** `<title>`/meta 或**正文首段真实摘要**（≤150 字，句末截断），未编造；无正文摘要的页面只补 URL/标题类标签。128 个文件改动后结构校验：canonical 恰 1 个、插入点在 `</head>` 前、`</html>` 完整 —— 异常 0。

## 处理中发现、交接单未列的问题（需裁定，非门丞自行处置范围）

1. 🔴 **三所联合页是空壳**：`mili/blog/najie-apnajie-mili-collaboration.html`（+ en/fr 镜像）只有 `<head>` 与 CSS，**无 `</head>`、无 `<body>`、正文 0–86 字**；git 全历史（2026-07-25 起 5 个版本）均如此，即从未有过正文。但它被 3 条 sitemap loc、`mili|najie|en|fr/blog/index.html` 卡片、`najie/blog/index.html` 的 JSON-LD blogPost、`llms.txt` 与根 `blog/` 跳转桩指为规范页。建议二选一：① 由扬声/仪观补正文 ② 撤页并同步清 3 条 loc + 卡片 + JSON-LD + llms.txt（**推荐先补正文**，该页是三所协同的对外主打页）。
2. 处理前根级 `/blog/` 有 96 条 noindex 跳转桩 loc、机构目录内 8 条，此前已于 `c1e3676`（09-11）清理过一次，09-12 被非 cron 的外部脚本加回。本次一并剔除，建议**加一道回归检查**（见下）。
3. 本次额外剔除的 `articles.json` 幽灵条目对应文章若确有价值，需扬声排期重新发布。

## 复现工具（均为幂等，默认 dry-run）

| 脚本 | 用途 |
|------|------|
| `site-inbox/fix-0916-legacy-urls.py` | 遗留项 1 全流程（articles.json 归位去重 + 孤儿迁移 + 跳转桩 + sitemap 清理 + CF 素材） |
| `site-inbox/fix-0916-seo-meta-backfill.py` | 遗留项 3：规范页 SEO 头部补齐 |
| `site-inbox/cf-redirects-articles-20260916.csv` | CF Bulk Redirects 导入素材（76 条） |
| skill `siteops-seo-monitoring` → `scripts/sitemap_loc_audit.py` | 日常口径：跳转/别名 loc、重复登记、非 200 loc 应为 0 |

备份：`~/.hermes/logs/backup-20260916/{articles.json,sitemap.xml}.bak_20260916_143950`
