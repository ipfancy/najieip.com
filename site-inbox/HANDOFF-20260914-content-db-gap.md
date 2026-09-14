# HANDOFF — content.db 缺 09-14 两篇已上线文章记录

**日期**：2026-09-14 22:00（SiteOps 每日巡检发现）
**处理者**：SiteOps Agent

## 现象

以下两篇文章已于 2026-09-14 上线 najieip.com（线上 curl 200、已入 articles.json、已入 sitemap、品牌博客索引卡片齐备），**但 `~/wiki/database/content.db` 的 `articles` 表中没有对应记录**：

| 文章 | 线上 URL | publish_date |
|------|---------|:----:|
| 商标被驳回的6个原因：六类驳回情形与收到驳回通知后的三步 | `/najie/blog/20260914-trademark-rejection-six-reasons.html` | 2026-09-14 |
| 专利选错，白等2年：发明与实用新型怎么选 | `/aipunajie/blog/20260914-patent-invention-vs-utility-model.html` | 2026-09-14 |

核对命令：
```bash
sqlite3 ~/wiki/database/content.db "SELECT article_id,title FROM articles WHERE title LIKE '%驳回的6个原因%' OR title LIKE '%白等2年%';"
# → 空
```

## 影响

1. **GEO 周追踪池漏检**：周六 GEO 作业从 `content.db articles` 取待检文章，这两篇不会被纳入（新文章上线 3 天首检的规则失效）
2. **发布去重防线变弱**：`dedup-publishing` 依赖 DB 记录判断"同文同渠道是否已发"
3. 每日巡检若以 DB 为准，这两篇会长期"隐形"

## 为什么 SiteOps 没有直接补写

`articles.article_id` 为主键且管线按 `ART-2026-NNNN` 顺序编号（当前最新 published 为 `ART-2026-0085`，但库内已存在到 `ART-2026-0330` 的历史号段）。**擅自猜号写入有与管线后续插入撞主键的风险**（title 上有 UNIQUE 索引，冲突会直接报错中断管线）。故按"不猜、不破坏"原则只报告。

## 建议修复（管线/Outreach 侧，一条命令级）

```sql
-- 建议由管线按自身编号规则插入（示例，article_id 请用管线实际下一个号）
INSERT INTO articles (article_id,title,summary,author,source_file,status,publish_date,tags)
VALUES
 ('ART-2026-0086','商标被驳回的6个原因：六类驳回情形与收到驳回通知后的三步','', '何自刚',
  '~/wiki/najieip-verify/najie/blog/20260914-trademark-rejection-six-reasons.html','published','2026-09-14',
  '["商标驳回","驳回复审","商标检索"]'),
 ('ART-2026-0087','专利选错，白等2年：发明与实用新型怎么选，一条被低估的同日双申请路','', '何自刚',
  '~/wiki/najieip-verify/aipunajie/blog/20260914-patent-invention-vs-utility-model.html','published','2026-09-14',
  '["专利选型","实用新型","同日双申请"]');
```

## 根因提示

09-14 这一批是 SiteOps 从 `site-inbox/` 草稿（`gen-0914-place-2-drafts.py` / `gen-0914-publish-2.py`）归位上线的，**没有走 Agent5 Outreach 的发布链路 → content.db 写入被跳过**。建议：SiteOps 归位脚本上线后统一调用管线的 DB 登记步骤，或由 Outreach 每日本地核对"线上新增文章 vs DB"。
