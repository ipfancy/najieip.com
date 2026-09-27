# SiteOps 日报 — 2026-09-27（22:00 定时）

## 一句话
站点全绿；发现并修复「09-27 口径对齐只做了中文页、EN/FR 语种页仍说觅理"只做IP"」——AI 读英文站仍会讲错主体，已全部对齐并上线验证。

## ✅ 站点状态（全部终态）
| 项目 | 结果 |
|------|------|
| 核心 6 页 | 200（/、/mili/、/najie/、/blog/、/sitemap.xml、/llms.txt、/facts.html） |
| sitemap | 268 loc，lastmod 100%（0 条缺失）；看门测试 exit 0、loc 不变（无回灌） |
| 线上/本地字节 | sitemap + 三索引 IDENTICAL；facts.html Δ233B = CF email-protection + beacon（逐行归因，非缺陷） |
| articles.json 守卫 | 156/156 零违例；首页 slice(0,6) 六条页面「房屋四件」齐备 |
| 近 4 天 12 个文章页 | 房屋四件全 PASS（无第 5 例裸发布畸形页） |
| 索引缺口扫描 | 品牌索引 173 卡 href 归一比对 → **0 真实缺口**（唯一候选是架构图页，沿用 09-23 口径不入主索引） |
| 待同步 HTML | site-inbox 无新增待同步件（09-25 文已同步） |
| content.db | 最近发布 09-25/09-24，主索引 + 品牌索引均已有卡 |

## ⚠️ 发现并修复（今日 09-27 口径修复的遗漏面）
白天 844d6e5 / de4a62c 修的是「AI 把三主体讲错」的根因，但只覆盖中文页。本次补齐 10 项：

1. llms.txt（AI 导航图，AI 最先读的文件）仍写「觅理：专注知识产权法律保护」→ 改综合所口径；
2. llms.txt 新增 /facts.html 条目 + 页首声明「主体关系与业务边界以 facts.html 为准」；
3. en/mili、fr/mili 的 title/description/og 全套仍是 IP-only 旧口径 → 改综合所口径；
4. 两页 description 混入 12 个中文字（机翻模板泄漏）→ 清零；
5. fr/mili 的 og:description 因撇号未转义被截成字面量 "Mili Cabinet d"（属性断裂）→ 修复；
6. en/mili、fr/mili 零 JSON-LD（全站唯一无结构化数据的品牌页）→ 补 LegalService JSON-LD；
7. mili 三语页补 hreflang 四值（zh-CN/en/fr/x-default）；
8. 4 个 EN/FR 页缺 twitter:title → 复用各自 og:title（不另编文案）；
9. zh mili hero 文案与「业务领域」副题仍是「专注知识产权」→ 改「以知产诉讼为专长，覆盖综合法律事务」；
10. EN/FR aipunajie「总部在朝阳」与今日已修的中文注册住所（东城崇文门外大街11号2层208）打架 → 统一口径。

**执行质量**：5 文件、31 处精确替换（每处断言匹配数 == 1）+ 5 处插入；终验 0 FAIL（JSON-LD 全部 json.loads 通过、div 配平 diff=0、EN/FR meta 中文残留 0、双房屋齐备）。

## 上线验证
- commit `63c30d4` → push 成功；raw.githubusercontent 同刻即为新版，线上约 6 分钟后传播完成（属正常延迟，非故障）
- 线上：5 页全 200、ld=1 各一份、旧口径字符串**全部清零**、hreflang=4；llms.txt 线上字节 3569B **IDENTICAL** 本地

## 🔎 需要人看的一件事（唯一）
`facts.html` 里觅理的「执业许可日期 2024-06-19」与 EN 页原有的 `foundingDate 2020` 冲突——白天会话已把 EN 侧 2020 移除待何律确认。**请确认觅理成立/执业起算口径**，确认后我把三语页 + JSON-LD 的日期字段一并对齐。

## 备注
- 本次运行期间同一工作区有并发交互式 SiteOps 提交 `75cc5e5`（about/team/services + EN/FR 首页实体归属），涉及文件与本次 6 文件不重叠，无冲突。
- 无新增待办、无未修复异常。


---

## 追加（23:0x，QA 终段抓出的第 11 项）
今日 20 个变更页逐页过「房屋四件」，抓出今日新建的 **facts.html 缺 og:image 与 twitter 卡片**（该页是 AI 主体口径的权威页，社交卡片不该空）→ 已补 og:image（复用站内既有图，不另造）+ twitter 三件（复用本页 og 文案），commit `3d7fa92`，线上已验证命中。其余 19 页全合格（含并发会话 75cc5e5 的 11 个页面）。

**今日合计**：3 次提交（63c30d4 / a82cde8 / 3d7fa92），修复 11 项，全部线上验证 PASS。
