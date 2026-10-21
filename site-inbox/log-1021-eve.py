#!/usr/bin/env python3
"""SiteOps 1021晚：deploy-log 追加 + 日报落盘"""
import os, json, subprocess, datetime

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
now = datetime.datetime.now()
date_s, time_s = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

# --- deploy-log：取远端版本做底，append + indent=1 ---
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and "deploys" in log
n_before = len(log["deploys"])
entry = {
    "date": date_s,
    "time": time_s,
    "agent": "siteops",
    "round": "每日运营 22:00",
    "commit": "6ec2a24",
    "action": "主索引补3卡(judge/3gpp/goods) 220->223 + judge页补og:image/twitter:image + articles.json补judge条目 195->196",
    "files_changed": ["blog/index.html", "mili/blog/20261022-judge-liability-verdict-reversed.html", "articles.json"],
    "cards_added": {"main": 3, "mili": 0, "najie": 0},
    "verification": "核心6页200；三新页线上h1=1/ld=3/og:image+twitter:image/无markdown泄漏；主索引线上223卡且3条HIT；articles.json线上196条top1=10-22；sitemap 318 loc不变；guard 196/196零违例",
    "defects_found": [
        "主索引滞后：3篇新页(10-22/10-21×2)品牌索引有卡、主索引无卡",
        "mili 20261022-judge 页缺 og:image + twitter:image",
        "articles.json 缺 judge(10-22) 条目 = 首页第1曝光位空缺",
    ],
    "notes": "3gpp 页 ** 为专利号掩码 20088000****.4，非 markdown 泄漏（判据需排除数字紧邻星号）；judge 页无自托管封面资产，暂用觅理品牌页同款 Pexels 法律图（200），自托管封面列为 backlog",
    "result": "success",
}
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print(f"deploy-log: {n_before} -> {len(log['deploys'])}")

# --- 日报 ---
rep = f"""# SiteOps 日报 — {date_s}

## 状态
- 核心 6 页（/ /mili/ /najie/ /blog/ /sitemap.xml /llms.txt）：**6/6 = 200**
- articles.json 守卫：**196/196 合格，0 违例**；首页 slice(0,6) 六条全部有落地页
- sitemap 看门：exit 0，**318 loc 不变**（3 篇新页已在内、lastmod 完整 0 缺）
- 工作树 clean，与 origin/main 同步（起点 159910a → 收尾 6ec2a24）

## 本轮修复（3 项）
1. **主索引补 3 卡**：220 → **223**
   - /mili/blog/20261022-judge-liability-verdict-reversed.html（2026-10-22）
   - /mili/blog/20261021-3gpp-proposal-prior-art-date.html（2026-10-21）
   - /najie/blog/20261021-goods-names-acceptable-list-q4.html（2026-10-21）
   - 日期降序插位（首卡仍为 10-22）、div 深度配平 0、malformed=0、href 无重复
2. **judge 页补 og:image + twitter:image**（原 twitter:card=summary → summary_large_image）；body 逐字未改
3. **articles.json 补 judge 条目**：195 → 196，该文占据首页第 1 曝光位

## 判据澄清（防误报）
- 3gpp 页 `**` 仅 1 处 = 专利号掩码 `20088000****.4`，**不是** markdown 泄漏，未改
- judge 页无自托管封面（cover 候选缺失）→ 暂用觅理品牌页同款 Pexels 图（实测 200），**backlog：需 Agent-visual 出 cover-20261022-judge-*.png 并入库 img/**

## 线上终验
- 3/3 新页：200 + h1=1 + ld=3 + og:image + twitter:image
- 主索引线上 223 卡、3 条新卡全部 HIT
- 线上 articles.json = 196，top1 = 2026-10-22
- FAILURES = NONE（首轮读到旧缓存属 CF 传播，150s 后收敛）
"""
p = os.path.expanduser(f"~/wiki/digital-employees/reports/siteops-daily-{now.strftime('%Y%m%d')}.md")
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p, "w", encoding="utf-8").write(rep)
print("report:", p)

# --- commit+push（deploy-log + 脚本）---
for cmd in (["git", "add", "-A"],
            ["git", "commit", "-m", "siteops(1021晚): deploy-log 记录主索引补3卡+judge页og图+articles.json条目"],
            ["git", "push", "origin", "main"]):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("$", cmd[1], "->", r.returncode, (r.stdout or r.stderr).strip()[-200:])
