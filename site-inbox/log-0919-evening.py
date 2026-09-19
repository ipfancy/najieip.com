#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-19 晚间日报 + deploy-log 追加（indent=1，原生格式）"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, 'site-inbox/deploy-log.json')
REPORT = os.path.expanduser('~/wiki/digital-employees/reports/siteops-daily-20260919.md')

entry = {
    "date": "2026-09-19",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "daily-evening-2200",
    "commit": "9c03dfd（主索引补卡）",
    "action": "晚间运营检查：核心 6 页全 200；主索引补 3 张 09-19 缺卡（159→162）；新页 og:image 补全 3 处；SEO/OG 巡检通过；articles.json 守卫 135/135 零违例",
    "scope": "① 主索引缺口：mili/wangluo-jishu-zhichi-kaishe-duchangzui-2026、mili/20260919-offer-to-sell-three-rules、najie/nongye-pinpai-ip-buju-2026 三张卡已在品牌索引但未进 blog/index.html（gather-0919-v5.py 按 href 归一扫出，stub 2 张剔除：cnptes-three-layer-architecture-diagram 图页 14165B、uspto-tbmp-2026-update 跳转壳 529B）；② 插位按「第一张日期 < 新卡日期 之前」规则落在 09-18 卡前，终验 9 项全 PASS（卡数/div 深度归零/直子节点 162/malformed 0/无重复 href/前缀降序/无 ** 泄漏/schema.org 完整）；③ 线上 blog/ 字节一致（102617B，162 卡）——13a8aa0 的 gaoqi-selfcheck 工具页 + 当日 3 篇新文均 200；④ 新页质检（qa-0919-evening.py）发现 2 篇文章 + 1 工具页缺 og:image，按 house-style 补齐（mili 用 5669602 / najie 用 3183150），工具页另补 twitter:card+title+description+og:site_name；⑤ articles.json 守卫 135/135 零违例，首页 slice(0,6) 6 条全部有页面",
    "verify": {
        "core_pages": "6/6 200（首页/mili/najie/blog/sitemap/llms.txt）",
        "live_blog_index": "字节一致 102617B · 162 卡 · 新卡 grep 各 1 次",
        "new_pages_200": 5,
        "seocheck": "通过（sitemap 246 loc · lastmod 246/246 · JSON-LD 6/6）",
        "ogcheck": "核心 4 页 0 issue",
        "articles_json_guard": "135/135 零违例"
    },
    "files": [
        "blog/index.html",
        "site-inbox/missing-cards-20260919.json",
        "mili/blog/wangluo-jishu-zhichi-kaishe-duchangzui-2026.html",
        "najie/blog/nongye-pinpai-ip-buju-2026.html",
        "najie/gaoqi-selfcheck.html"
    ]
}

log = json.load(open(LOG, encoding='utf-8'))
if not any(e.get('round') == 'daily-evening-2200' and e.get('date') == '2026-09-19' for e in log['deploys']):
    log['deploys'].append(entry)
    json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('deploy-log appended, n =', len(log['deploys']))
else:
    print('deploy-log already has this round, skip')

md = """# SiteOps 日报 — 2026-09-19（晚间 22:00）

## 结论
站点健康 ✅ 全绿。核心 6 页全 200；主索引补齐 3 张当日缺卡（159→162）并线上字节验证通过；
新页 og:image 缺 3 处已补齐；sitemap 246 loc 零缺 lastmod；articles.json 守卫 135/135 零违例。

## 1. 核心页面 HTTP（6/6 200）
najieip.com / mili/ / najie/ / blog/ / sitemap.xml / llms.txt → 200

## 2. content.db 近期文章 vs 索引
- ART-2026-0090《没卖一件也赔3万！许诺销售这4个坑》09-19 → mili 索引 + 主索引 ✅（今晚入主索引）
- ART-2026-0089《游戏界面中国不给专利，欧盟7月1日起能注册》09-18 → najie 索引 + 主索引 ✅
- 另两篇当日发布（非 content.db 源）：mili/wangluo-jishu-zhichi-kaishe-duchangzui-2026、
  najie/nongye-pinpai-ip-buju-2026 → 品牌索引已有，**主索引缺** → 本轮补卡

## 3. 主索引补卡（159 → 162）
gather-0919-v5.py 按 href 归一比对三索引 body 卡，3 张真缺口；插入按日期降序（落 09-18 卡前）。
终验 9 项全 PASS：卡数 162 / div 深度归零 / 直子节点 162 / malformed 0 / 无重复 href /
前缀日期降序 / 无 `**` 泄漏 / `https://schema.org` 完整（无 `https://***`）。
stub 剔除 2：`cnptes-three-layer-architecture-diagram`（14KB 图页）、`uspto-tbmp-2026-update`（529B 跳转壳）。

## 4. 部署验证（不信任 git push exit 0）
- push 13a8aa0 → 9c03dfd ✅
- 线上 https://najieip.com/blog/ 与本地字节一致 102,617 B、162 卡、3 张新卡各命中 1 次
- 当日新页 5 个 URL 全 200（含 13a8aa0 的 /najie/gaoqi-selfcheck.html 工具页）

## 5. 新页质检（qa-0919-evening.py）
| 页面 | 结果 |
|---|---|
| wangluo-jishu-zhichi-kaishe-duchangzui-2026 | 修 og:image（5669602） |
| nongye-pinpai-ip-buju-2026 | 修 og:image（3183150） |
| gaoqi-selfcheck（工具页·未公开） | 补 og:image + twitter:card/title/description + og:site_name |
| 其余 6 页 | og/twitter/canonical/JSON-LD 齐备，`**` 泄漏 0 |

## 6. SEO / OG 巡检
- najie-seocheck：所有检查通过；sitemap 246 URL、lastmod 246/246、博客页 215、lastmod 最新 2026-09-19
- najie-ogcheck：核心 4 页 0 issue
- articles.json 守卫 --check：总 135 / 合格 135 / 违例 0；首页 slice(0,6) 6 条全有页面

## 7. 待办 / 风险
- gaoqi 工具页为「仅链接分发」未公开页：已在 sitemap 外（未加 loc），符合预期
- 上游 auto-publish 仍会复活 articles.json 无页面条目（连续 3 次），守卫脚本已可每日复跑
- GEO：今日凌晨已跑第 38 周双平台 12 检查点（0 命中，累计 124 点）；下周六 02:00 继续
"""

open(REPORT, 'w', encoding='utf-8').write(md)
print('report written', REPORT, os.path.getsize(REPORT), 'bytes')
