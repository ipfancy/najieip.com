# NOTE 2026-09-17 — sitemap「摘除→加回」乒乓根因：cron 跑的是未加固副本

**发现者**：SiteOps 22:00 日检（对 09-17 三次同题提交的复盘）
**症状**：`sitemap: 自动纳入新文章URL (已新增 N 条)` 与 siteops 的「摘除违规 loc」交替出现，
一天内 4 次（13:20 +47、15:42 +151、21:43 +151，siteops 各摘除一次），最后 HEAD 停在「已加回 151 条」。

## 根因（实测）

| 路径 | 行数 | 校验 | 谁在用 |
|------|:----:|------|--------|
| `~/wiki/najieip-verify/update-sitemap.py` | 155 | 有（文件存在/跳转壳/重复登记三条） | 人类/agent 手工调用 |
| `~/.hermes/scripts/update-sitemap.py` | 112 | **无任何校验** | **cron `2ddb76c2dd9a` → `~/.hermes/scripts/sitemap-auto.sh` 每 6h** |

09-17 的加固（c265124）只改了**仓库副本**，cron 实际执行的副本没动 → 每 6 小时把 siteops 刚摘掉的
跳转壳/无页面 loc 原样加回。**修复：已把加固版覆盖到 cron 路径（旧版备份 `.bak-20260917`），
并实跑 `bash ~/.hermes/scripts/sitemap-auto.sh` 验证 exit 0 且 loc 不变。**

## 口径（沿用 2026-09-16 三条全零）

跳转/别名 loc = 0；重复登记 loc = 0；非 200 loc = 0。当前 **391 → 240**，全唯一。

## 给下一轮巡检的口径

1. 见到 `sitemap: 自动纳入新文章URL (已新增 N 条)` 提交 → 先 diff 新增 loc 是否含跳转壳/无页面，
   若有 → 说明加固又被覆盖（检查是否有人从别处拷回旧脚本），**不要只做摘除，先修副本**。
2. 巡检收尾必跑 `bash ~/.hermes/scripts/sitemap-auto.sh`（应为静默 no-op）——这是防回灌的看门测试。
3. 仓库副本与 `~/.hermes/scripts/` 副本是**两套**，任何 sitemap 脚本改动必须双写。
