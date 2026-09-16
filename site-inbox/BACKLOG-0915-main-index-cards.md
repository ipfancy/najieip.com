# Backlog：主 blog/index.html 缺失卡片 —— **2026-09-16 已清零，本文件归档**

## 状态（2026-09-16 22:00 更新）
- 余 37 张 + 09-15/09-16 新增漏卡，已由 `site-inbox/gen-0916-index-cards-v4.py` 一次性补齐 48 张，主索引 109 → **157 卡**
- 校验全通过（卡数/配平/深度/重复/单调/格式），线上字节一致
- 6 张非文章页（跳转壳/图页）经核实不入索引；3 项假缺口已用权威路径收录
- 复跑方式：`gen-0916-gather-missing.py`（生成候选）→ `gen-0916-index-cards-v4.py --apply`（幂等补卡）→ `verify-0916-final-structure.py`（结构双份校验）

## 背景（历史）
主 `blog/index.html` 长期滞后于品牌索引（mili/najie/aipunajie 由发布脚本同步，主索引常漏卡）。
2026-09-15 22:00 巡检逐 slug 比对：52 张真实文章卡缺失 → 已补最近 15 张（09-01~09-14），**余 37 张待补**。

## 已建好的机制（可直接复用，勿重写）
- 脚本：`site-inbox/gen-0915-index-cards-v3.py`（幂等；每次插入后重扫卡片位置，避免偏移过期撕标签）
- 输入：JSON 数组 `[{slug,brand,path,date,h1,ogtitle,desc,kw,canonical}]`
- 复跑：生成新的 input JSON → 改脚本第 19 行路径 → `python3 site-inbox/gen-0915-index-cards-v3.py --apply`
- 校验项：卡片数 =原数+N、`<div>`/`</div>` 配平、每个 href 恰 1 次、malformed=0、带日期卡降序单调

## 待补清单（37 张）
- 带日期前缀 8 张（日期可用，可直接按日期降序插入）
- 无日期前缀 29 张（需从文章页 JSON-LD `datePublished` 取日期，或统一插到已收录无日期卡块之后）

- /mili/blog/20260815-punitive-damages-guide.html  (10205B)
- /mili/blog/20260817-trade-name-collision-3-remedies.html  (14796B)
- /mili/blog/20260825-tax-invoice-redline.html  (20803B)
- /najie/blog/20260804-ic-layout-design-regulations.html  (9419B)
- /najie/blog/20260817-trademark-nonuse-cancellation-rescue.html  (15751B)
- /aipunajie/blog/20260824-annual-fee-6month-lapse.html  (10895B)
- /aipunajie/blog/20260824-patent-agent-3-step-rescue.html  (10411B)
- /aipunajie/blog/20260825-patent-agent-qualification-redline.html  (11800B)
- /mili/blog/ai-generated-content-copyright-en.html  (7861B)
- /mili/blog/ai-music-copyright-boundary.html  (9597B)
- /mili/blog/ai-training-copyright-boundary.html  (10330B)
- /mili/blog/ai-training-copyright-fair-use-2026.html  (5244B)
- /mili/blog/beiruqin-sancha-20260831.html  (11152B)
- /mili/blog/franchise-supreme-court-7cases-20260814.html  (5943B)
- /mili/blog/fuyi-fanpei-yiwanjiu-20260831.html  (12580B)
- /mili/blog/geely-wm-trade-secret-20260814.html  (8343B)
- /mili/blog/trade-secret-three-lessons-20260813.html  (9206B)
- /mili/blog/trademark-law-2026-revision.html  (9379B)
- /mili/blog/trademark-squatting-guide-en.html  (7719B)
- /mili/blog/uspto-foreign-representation-rule-2026.html  (4313B)
- /mili/blog/uspto-tbmp-2026-ttab-center-estta-update.html  (13630B)
- /mili/blog/uspto-tbmp-2026-update.html  (18833B)
- /mili/blog/yanglao-will-white-paper.html  (12186B)
- /najie/blog/cnptes-three-layer-architecture-diagram.html  (12833B)
- /najie/blog/enterprise-ip-compliance-system.html  (8790B)
- /najie/blog/ip-content-selection-methodology-202608.html  (10058B)
- /najie/blog/ipms-certification-new-rules-2026.html  (20136B)
- /najie/blog/lawyer-law-amendment-2026.html  (6510B)
- /najie/blog/overseas-ip-selfcheck-2026.html  (5710B)
- /najie/blog/overseas-trademark-madrid-2026.html  (5568B)
- /najie/blog/overseas-trademark-strategy.html  (9601B)
- /najie/blog/trademark-law-countdown-20260808.html  (14601B)
- /aipunajie/blog/ip-xiuxian-003.html  (6798B)
- /aipunajie/blog/patent-agency-license-redline-20260825.html  (9501B)
- /aipunajie/blog/patent-early-warning-system-20260802.html  (6859B)
- /aipunajie/blog/shuiwu-shuishou-kaipiao-redline-20260825.html  (22364B)
- /aipunajie/blog/utility-model-fast-grant-20260813.html  (11616B)
