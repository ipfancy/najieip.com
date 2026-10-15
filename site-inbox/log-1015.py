#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy-log 追加（取 origin 版本做底，indent=1）+ 日报 + 提交推送"""
import os, subprocess, json, time

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
REPORTS = os.path.expanduser("~/wiki/digital-employees/reports")
os.makedirs(REPORTS, exist_ok=True)

# --- deploy-log: 以 origin 版本做底 ---
p = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"], capture_output=True, text=True)
log = json.loads(p.stdout)
print("origin deploy-log entries:", len(log["deploys"]))

entry = {
    "date": "2026-10-15",
    "time": "22:0x",
    "agent": "siteops",
    "round": "每日运营（1015）",
    "commit": "19d64d4",
    "action": "核心页 HTTP 巡检 + 精修 mili 新页（部分裸发布：补 Article/BreadcrumbList JSON-LD、og:image、og:site_name、twitter 卡、keywords、真摘要去标题复读）+ 双索引补卡 + articles.json 守卫隔离 + sitemap 看门",
    "files_changed": ["mili/blog/20261015-ip-4-hard-deadlines-buju-revision.html",
                      "mili/blog/index.html", "blog/index.html",
                      "img/20261015-ip-4-hard-deadlines-buju-revision.png",
                      "articles.json", "articles-quarantine-20261015.json"],
    "cards_added": {"mili/blog/index.html": [117, 118], "blog/index.html": [214, 215]},
    "verification": {"http_core": "6/6 200", "new_page_online_bytes": 11759,
                     "live_checks": "8 项 PASS（h1/ld>=2/og:image/twitter:image/keywords/desc>120/**==0/schema.org>=2）",
                     "index_live_cards": "mili 118 / main 215（均与新页 HIT）",
                     "cover_image": "200", "articles_json_live": 189,
                     "sitemap_loc": 308, "watchdog": "sitemap-auto.sh exit 0 且 loc 不变"},
    "defects_found": ["mili 新页部分裸发布（无 JSON-LD / 无 og:image / description 复读标题）",
                      "新页未进任何索引（主索引与 mili 索引均零卡）",
                      "articles.json 50 条无页面条目（第 16 次复活）"],
    "notes": "上游 431d8a5 已修 markdown 渲染（**→strong、竖线表→table 8 行、斜体→em），本轮只补 head 与索引面；正文 body 归一后逐字不变。行规沉淀：head 重建后必须用「原始 </head> 偏移」切 body，用 len(改后 head) 会吞掉正文开头（本轮实测 h1 计数掉落）。",
    "result": "PASS"
}
log["deploys"].append(entry)
open("site-inbox/deploy-log.json", "w", encoding="utf-8").write(
    json.dumps(log, ensure_ascii=False, indent=1))
print("deploy-log entries now:", len(log["deploys"]))

# --- 日报 ---
report = """# SiteOps 每日运营日报 — 2026-10-15

## 一句话
✅ 核心 6 页全 200；修复 mili 今日新页「部分裸发布」（补 JSON-LD/OG/Twitter/关键词/真摘要，7,308→11,759B，正文逐字未改）并补双索引卡；articles.json 守卫第 16 次隔离（239→189）。

## 1. 站点健康
- 核心页 curl：`/` `/mili/` `/najie/` `/blog/` `/sitemap.xml` `/llms.txt` = **6/6 200**（无瞬断）
- 站点页面：`/mili/blog/` 200、新页 200、封面图 200
- sitemap 看门 `sitemap-auto.sh`：exit 0，loc **308** 不变（无回灌；上游 bad2214 已把新页 loc 自动纳入）

## 2. 内容同步（近 2 日文章）
| 文章 | publish_date | 落地页 | 索引状态 |
|------|--------------|--------|----------|
| ART-2026-0107 4个知识产权硬时限速查 | 2026-10-15 | /mili/blog/20261015-...html | 修复后 mili 118 / 主 215 均 HIT |
| ART-2026-0106 AI团队最容易漏的2个泄密口子 | 2026-10-14 | /mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html | 主索引 + mili 索引均已有卡 |

## 3. 本轮修复
- **mili 新页「部分裸发布」**（有 h1 + 外链 /style.css，缺 JSON-LD / og:image / og:site_name / twitter 标题图像 / keywords，`description` 复读标题 22 字）：
  - 按同日同品牌精修页 `patent-vs-trade-secret-layering-2026.html` 取房屋，`copy.deepcopy` 其 Article + BreadcrumbList JSON-LD 后覆写字段（绕开 format/占位符两代坑）
  - 真摘要 252 字（4 个硬时限起算点 + 法条依据 + 842 号条例 + 商标法 2026 修订提示），去标题复读
  - 封面图入库 `img/20261015-ip-4-hard-deadlines-buju-revision.png`（296KB）
  - **正文 body 归一后逐字不变 = True**；ld+json 2 块 json.loads 通过；div 深度归零
- **索引补卡**：mili 117→118、主 214→215（日期 2026-10-15 降序置首位）；每卡以 `<h2><a href=` 起、depth 直方图 {2: N} 与卡片数一致、`t2.replace(card+"\\n  ", "", 1) == t` 断言通过
- **articles.json 守卫**：239 条中 50 条无页面（第 16 次复活），`--apply` 隔离 → 189/189 零违例；复跑确认；隔离档 `articles-quarantine-20261015.json` 入库
- 未发现其他缺口：近 4 日 6 个文章页逐一对三索引 href 归一比对，除本轮新页外全部已在位

## 4. 线上终验（push 后 180s 复读）
- 新页 11,759B：h1==1 / ld>=2 / og:image / twitter:image / keywords / desc 252 字 / `**`==0 / schema.org>=2 —— **8/8 PASS**
- 索引页线上卡片数 = 本地（mili 118、主 215），新页 HIT=True
- `articles.json` 线上 189 条；sitemap 线上 308 loc 含新页

## 5. 遗留 / 待观察
- articles.json 无页面条目会被上游自动发布整体复活（第 16 次）→ 根治需上游发布流水线按落地页生成数据源，本机继续每日守卫
- 全站普查遗留（老页无 JSON-LD / h1=2 / 早期机翻页裸表）仍按 backlog 量化处理，不批量改写
"""
rp = os.path.join(REPORTS, "siteops-daily-20261015.md")
open(rp, "w", encoding="utf-8").write(report)
print("report:", rp)

def run(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, capture_output=True, text=True, env=e)
    print("$ " + " ".join(cmd), "->", p.returncode, (p.stdout or "").strip()[:200], (p.stderr or "").strip()[:200])
    return p

run(["git", "add", "-A"])
run(["git", "commit", "-m", "siteops(1015): deploy-log + 日报（核心 6 页 200 / 新页精修 + 双索引补卡 / articles.json 第16次隔离）"])
p = run(["git", "push", "origin", "main"])
if p.returncode != 0 or "publickey" in (p.stderr or ""):
    run(["git", "push", "origin", "main"],
        env={"GIT_SSH_COMMAND": "ssh -i /Users/ziganghe/.ssh/id_ed25519 -o IdentitiesOnly=yes"})
run(["git", "log", "origin/main", "--oneline", "-3"])
run(["git", "status", "--porcelain"])
