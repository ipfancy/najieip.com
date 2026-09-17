# NOTE 2026-09-17 — articles.json 混入 50 条「无页面」条目（其中 47 条会变成 sitemap 死链）

**发现者**：门丞（siteops）· 2026-09-17 13:0x（sitemap 刷新+ping 例行巡检）
**触发**：`siteops_sitemap_refresh.py --check` 报「缺失文章 URL: 47」
**根因提交**：`db22bd2`（2026-09-17 09:09，提交信息为自动生成的「更新: 2026-09-17 09:09」）
—— 该提交把 `articles.json` 从 130 条扩到 180 条（**+50 条，0 条删除**），同时上线 `mili/blog/20260917-upc-injunction-counterattack.html`。

## 证据（全部实测）

| 项 | 实测值 |
|----|--------|
| articles.json 现存条目 | 180（唯一 180，`/articles/` 前缀 0） |
| 其中**指向文件的路径不存在** | **50 条**：47 条 `{机构}/blog/...` + 3 条 `/site-inbox/...` |
| 47 条 `{机构}/blog/...` 线上状态 | **47/47 = HTTP 404**（CF 与 `ipfancy.github.io/najieip.com` 直连双路径一致；含 5 条中文 slug 已按 %编码复测） |
| 同 basename 的 `/articles/<base>` 老路径 | 45/47 仍 HTTP 200（内容在旧路径，规范路径从未建页）；2 条全站无页面（幽灵：opc-policy-real-ledger、child-touch-accusation-parents-guide） |
| 3 条 `/site-inbox/...` | 线上 **404**，仓库内也无该文件（工作区路径被写进数据源） |
| 站内引用面 | 47 条**仅 articles.json 引用**（0 个 HTML 卡片/JSON-LD/sitemap 引用）→ 当前无客户可见断链 |
| 首页可见性 | `index.html` 用 `articles.slice(0, 6)`；47 条最小下标 = 8 → **当前不可见，但再上线 3 篇即会被推入首页卡片区**（第 8 位那条 = 幽灵 opc-policy） |

## 已做动作（本机，未越权）

1. **未执行** sitemap 刷新脚本的「照单补录」——它会把这 47 条 404 加进 sitemap 并随后 ping IndexNow。sitemap 保持 `非 200 loc = 0`。
2. 补录唯一合法缺项：`https://najieip.com/mili/blog/20260917-upc-injunction-counterattack.html`（线上 200、self-canonical、本日上线）→ sitemap 347 → **348** loc（XML 校验通过、loc 全唯一），commit `6979c0f` 已推送。
3. IndexNow 提交：该新页 + 常规 5 条，均 **HTTP 200**（Google/Bing 传统端点 404/410 属已停用，非故障）。
4. 证据 JSON：`/tmp/dead_probe.json`、`/tmp/dead_refs.json`（本机）。

## 待 go/no-go（数据源修正，门丞不自裁）

- **推荐 A（立即）**：把上述 50 条从 `articles.json` 摘除（= 复现 2026-09-16 `fix-0916-legacy-urls.py` 的既定口径：删纯重复/幽灵条目）。首页不受影响（均在 slice(0,6) 之外）；sitemap 无需变动。
- **B（排期）**：若这 47 篇确需以 `{机构}/blog/` 为规范址，则把 `/articles/` 老路径内容**回填**到规范路径（含 canonical/JSON-LD/索引卡片），再由 siteops 补 loc + IndexNow。
- **同时需修生成方**：`db22bd2` 的自动化把「无对应页面」甚至 `site-inbox/` 工作区路径写进 articles.json——生成器必须加「文件存在性 + 路径白名单（仅三机构 blog/）」校验，否则每次运行都会复活被清理的条目。

## 给下一轮巡检的口径

`sitemap 刷新 + ping` 例行任务在数据源修正前，**只补线上 200 的规范页，其余一律悬停并回报**；`--check` 报「缺失文章 URL: 47」在修好数据源前属**已知状态**，不是新故障。
