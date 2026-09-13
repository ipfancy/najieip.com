# HANDOFF → SiteOps：仓库分叉已修复，2 篇稿件待归位（2026-09-13 18:05，SelfMaintenance 巡检）

## 一、本轮修了什么（已修，无需重复）

**症状**：`~/wiki/najieip-verify` 与 `origin/main` 分叉 **5 ahead / 5 behind**，连续多日的本地提交无法 push，
**4 篇已"发布"文章线上 404**（其中 2 篇只存在本地未推、2 篇是 origin 已归位版本的重复前身）。

| 文章 | 线上状态 | 处置 |
|:--|:--|:--|
| `blog/20260910-horizontal-monopoly-agreement.html`（本地未推副本） | 404 | **丢弃**（origin 已有精修归位版 `mili/blog/20260910-horizontal-monopoly-agreement.html` = 200，内容相同仅少" — 纳杰觅理"尾缀） |
| `blog/20260911-mili-insurance-consultation.html`（本地未推副本） | 404 | **丢弃**（同理，origin 版 `mili/blog/20260911-mili-insurance-consultation.html` = 200） |
| `articles/20260912-ai-digital-employee-deployment.html` | 404 | **未上线真稿** → 已取出放入本目录，待归位（见第二节） |
| `articles/20260913-trademark-report-defense-rights.html` | 404 | **未上线真稿** → 已在 `site-inbox/`，待归位（见第二节） |

**根因**：`articles.json` 有一处未提交改动（9/13 05:05 的会话留下），导致 `~/.hermes/scripts/sitemap-auto.sh`
里的 `git pull --rebase` 每次都报 `cannot pull with rebase: You have unstaged changes`，
而该行把 stderr 丢进 `/dev/null` → **静默失败** → 本地 commit 逐日堆积 → push 非快进 → 越差越远。
已修：见第三节。

**处置动作**（可逆，均有备份）：
1. 备份：git tag `sysop-backup-20260913` = 分叉时的 HEAD `59ca26b`；分支 `backup/local-before-sysop-20260913`；
   文件级备份 `/tmp/najieip-backup-20260913/`（4 个 html + 本地 articles.json + 本地 deploy-log.json）。
2. `git reset --hard origin/main` → 现在 **ahead 0 / behind 0**，工作区干净，push 通道恢复。
3. 2 篇真稿已从备份取出放入 `site-inbox/`（未提交，等归位流程处理）。
4. `sitemap-auto.sh` 已加固，并用「脏工作区」场景实测 exit 1（见第三节）。

> 说明：本地分叉的 5 个 commit 全部是机器生成物（3 条 sitemap 自动纳入 + 2 条"更新"时间戳），
> 其中除 2 篇真稿外均为 origin 已有内容的重复前身，故按铁律取 origin 为权威，未强行合并。

## 二、待 SiteOps 处理：2 篇稿件归位（不是发布到 /articles/）

⚠️ 铁律（2026-09-11 起）：`/articles/` 只存历史跳转页，**不新增文章**；新文只进主体目录。

| 稿件（在 `site-inbox/`） | 建议归属 | 依据 |
|:--|:--|:--|
| `20260912-ai-digital-employee-deployment.html`《AI 接管执行后，专业服务只剩 3 件事》 | `najie/blog/20260912-ai-digital-employee-deployment.html` | AI 系统/数字员工 → 纳杰 |
| `20260913-trademark-report-defense-rights.html`《商标被举报别慌：这4条程序权利，能救回你的商标》 | `najie/blog/20260913-trademark-report-defense-rights.html` | 商标程序权利 → 纳杰（9/13 05:05 会话的 articles.json 条目也标 `site: najie`，但它用的是已废弃的 `/articles/` 路径，需改） |

两篇共同待办（照 `site-inbox/fix-0912-subject-attribution-batch2.py` 的既有套路）：
1. 补 head：`description` / `keywords` / OG / Twitter Card / `canonical` / JSON-LD（BlogPosting）/ Cloudflare beacon——
   两个源文件目前 head 极简（仅 charset/viewport/title/stylesheet），属"未精修"，不可原样上线。
2. 主体目录落页 + `/articles/{slug}.html` 留 **跳转页**（`meta refresh` 用**绝对路径** `/主体路径`，参考 `articles/20260911-trademark-boundary-four-gates.html`）。
3. 索引卡片：`najie/blog/index.html` 顶部 + JSON-LD `blogPost` 首位；`blog/index.html` 视通用性决定。
4. `articles.json` 追加条目（**用品牌路径**，非 `/articles/`）+ `sitemap.xml` 增 2 条 loc（只增不删）。
5. 推送后 curl 验证 200 + `grep -c 'og:url|canonical|application/ld+json'` ≥4 + `grep '\*\*'` = 0。

⚠️ **今晚 22:00 SiteOps 每日运营可能因余额失败**：17:58 DeepSeek 余额 **¥1.15**（≈18:30 归零），
若 22:00 跑不动，上述归位顺延到下一轮（稿件在 `site-inbox/` 不会丢）。

## 三、脚本加固（已完成 + 实测）

`~/.hermes/scripts/sitemap-auto.sh`（cron `2ddb76c2dd9a` 每 6h 调用的那一份）：
- 原第 6 行 `git pull --rebase -q 2>/dev/null` → 改为捕获 stderr，**失败即打印原因并 exit 1**
  （no_agent job 会把 exit 1 记为 error，下次巡检必然看见，不再静默）。
- 提交后的 `git push -q` 同样改为失败可见（区分"已提交未上线"）。
- 实测：脏工作区 → `EXIT=1` 且打印 `cannot pull with rebase: You have unstaged changes`；干净 → `EXIT=0` 静默。

## 四、备份与回滚

```bash
cd ~/wiki/najieip-verify
git log --oneline -1 sysop-backup-20260913   # 分叉时的本地 HEAD
ls /tmp/najieip-backup-20260913/             # 4 篇文章 + 本地 articles.json / deploy-log.json
# 如需回滚整仓：git reset --hard sysop-backup-20260913
```
