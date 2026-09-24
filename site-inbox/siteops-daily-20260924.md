# SiteOps 日报 — 2026-09-24（周四 22:00 档）

**结论：核心 8 页全 200；修复今日裸发布畸形页（正处首页第 1 曝光位）+ 双索引补卡；零缺口。**

## 1. HTTP 状态（8/8 = 200）
| 页面 | 状态 |
|------|:----:|
| najieip.com / /mili/ / /najie/ / /blog/ / /mili/blog/ | 200 |
| sitemap.xml (266 loc) / llms.txt | 200 |
| mili/blog/20260924-malicious-litigation-supervision.html | 200 |

`najie-seocheck` 首轮把 `/fr/` 报 0 → 按行规 curl 重试 3/3 全 200 = **网络瞬断误报，非故障**。

## 2. 今日新文：裸发布畸形页（已修复）
`ART-2026-0095 被碰瓷式维权告了？最高检6月29日5案` → `mili/blog/20260924-malicious-litigation-supervision.html`

| 缺陷 | 修前 | 修后 |
|------|------|------|
| `<h1>` | 0 | 1 |
| `<h2>` 路标 | 0 | 6 |
| JSON-LD | 0 | 2（Article + BreadcrumbList） |
| og:image / keywords | 无／无 | 有／有 |
| meta description | 28 字（复读标题） | 130 字（原文事实重写） |
| 体积 | 7,716 B | 10,420 B |

- 房屋模板取**同日同品牌精修页** `mili/blog/20260922-caichan-shouhu-07.html`（外链 `/style.css` 版）
- **正文与 md 源逐段比对 30/30 段 0 差异**（不加一字、不加 h2 论点、仅补描述性路标）
- 该文同时处 `articles.json` 首页 `slice(0,6)` **第 1 曝光位**，且**两索引都无卡**（零卡 + 最高曝光 + 零样式三重故障齐发，与 09-21/09-22 同一模式）

## 3. 索引补卡
| 索引 | 卡片数 | blogPost JSON-LD | 插入位 |
|------|:------:|:----------------:|--------|
| `mili/blog/index.html` | 95 → **96** | 87 → 88 | 首位（09-24 > 首卡 09-22） |
| `blog/index.html` | 181 → **182** | — | 首位（09-24 > 首卡 09-23） |

终验 11 项全 PASS：卡片数 +N、div 深度归零、malformed=0、重复 href=0、插入点前缀日期降序、新卡为首卡、`**`=0。
> 深度判据先对 `origin/main` 基线校准：实测 `article-card` 位于 **depth==1**（勿沿用旧记录的 depth==2）。

## 4. 近 2 日已发布文章全链路（3 篇，0 缺口）
| 文章 | 主索引 | 品牌索引 | articles.json | sitemap | 线上 |
|------|:------:|:--------:|:-------------:|:-------:|:----:|
| ART-0095 恶意诉讼监督（mili） | ✓ | ✓ | ✓ | ✓ | 200 |
| ART-0094 AI 造谣维权（najie） | ✓ | ✓ | ✓ | ✓ | 200 |
| ART-0093 美商标自查（najie） | ✓ | ✓ | ✓ | ✓ | 200 |

三篇房屋样式四件（h1 / h2 / ld≥2 / og:image）全合格。

## 5. 其他守卫
- **articles.json**：155/155 合格，**0 违例**（上游本次未复活被隔离条目）；首页 top6 六条全部有实体页面
- **OG/Twitter**：核心 4 页 0 issues
- **sitemap 看门测试**：`sitemap-auto.sh` 静默 exit 0、loc 266 不变 = 无回灌
- **部署字节核验**：文章页线上与本地唯一差异 = Cloudflare 注入 `beacon.min.js`（Δ367 B，已 difflib 归因）；两索引 Δ367 B 同因，新卡 HIT + 卡数一致

## 6. 待办 / 观察
- 该文为 09-21、09-22 之后**第 3 次**「上游裸发布畸形页」且越来越靠前（rank3 → rank1）→ 建议上游发布流水线加「房屋样式四件」自检（本机已每日必查前 6 条）
- 秘塔/元宝 GEO 追踪为周六 02:00 档，本日未跑

---
*SiteOps Agent｜脚本留档：site-inbox/{diag,fix,gen,verify,diff,gapscan,log}-0924*.py*
