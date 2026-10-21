#!/usr/bin/env python3
"""修正 deploy-log 缩进口径：restore indent=2 原档 + 追加本轮条目，amend 上一提交"""
import os, json, subprocess

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))

def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    print("$", " ".join(a[:2]), "->", r.returncode, (r.stdout or r.stderr).strip()[-160:])
    return r

sh("git", "fetch", "origin")
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
om = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True, text=True).stdout.strip()
assert head == om, f"HEAD {head} != origin {om}, abort (concurrent push)"

# 1) 回到第一个提交（含主索引/页面/articles.json 修复，不含 deploy-log 改动）
sh("git", "reset", "--soft", "HEAD~1")

# 2) 用原档（indent=2）重建 deploy-log
raw = subprocess.run(["git", "show", "HEAD:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
n0 = len(log["deploys"])
entry = {
    "date": "2026-10-21",
    "time": "22:40",
    "agent": "siteops",
    "round": "SiteOps 每日运营 22:00",
    "commit": "6ec2a24",
    "action": "主索引补 3 卡（10-22 judge / 10-21 3gpp / 10-21 goods）220->223；judge 页补 og:image + twitter:image（card 升 summary_large_image）；articles.json 补 judge 条目 195->196",
    "files_changed": ["blog/index.html",
                      "mili/blog/20261022-judge-liability-verdict-reversed.html",
                      "articles.json"],
    "cards_added": "主索引 +3（mili 品牌索引已有卡，未重复新增）",
    "verification": "核心 6 页 200；三新页 live 200 且 h1=1 / ld=3 / og:image+twitter:image 齐备 / 无 markdown 泄漏；主索引 live 223 卡且 3 条新卡全 HIT；live articles.json=196 且 top1=2026-10-22；sitemap 看门 exit 0（318 loc 不变，lastmod 0 缺）；articles.json 守卫 196/196 零违例，首页 slice(0,6) 六条全部有落地页",
    "defects_found": "3 项：①主索引滞后（3 篇新页品牌索引有卡、主索引无卡）②judge 页缺 og:image/twitter:image ③articles.json 缺 judge(10-22) 条目（该文为首页第 1 曝光位）",
    "notes": "3gpp 页 `**` 仅 1 处为专利号掩码 20088000****.4，非 markdown 泄漏，未改（星号判据须排除数字紧邻情形）；judge 页无自托管封面资产，暂用觅理品牌页同款 Pexels 法律图（实测 200），backlog=需 Agent-visual 出 cover 并入库 img/；脚本 site-inbox/{ops,fix,verify,commit,log,live2}-1021-eve.py",
    "result": "PASS",
}
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"deploy-log: {n0} -> {len(log['deploys'])} (indent=2)")

sh("git", "add", "-A")
print(subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True).stdout)
sh("git", "commit", "-m",
   "siteops(1021晚): 主索引补3卡(judge/3gpp/goods) 220->223 + judge页og/twitter图 + articles.json 195->196 + deploy-log")
sh("git", "push", "origin", "main")
