import json, os, subprocess, sys
REPO = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
data = json.loads(raw)
last = data["deploys"][-1]
keys = list(last.keys())
print("LAST KEYS:", keys, "| entries:", len(data["deploys"]))

vals = {
 "date": "2026-11-03", "time": "22:20", "agent": "SiteOps", "round": "每日运营（22:00）",
 "commit": "b706a68",
 "action": "精修当日新文「抓一次数据：罚53万，再赔500万」(mili) head 面 + 主/品牌索引补卡 + articles.json 守卫隔离",
 "files_changed": ["mili/blog/20261103-mili-unfair-competition-data-scraping.html",
                   "img/20261103-mili-unfair-competition-data-scraping.png",
                   "blog/index.html", "mili/blog/index.html", "articles.json",
                   "articles-quarantine-20261103.json"],
 "cards_added": 3,
 "attribution": "mili（上游 2516361 落地 mili/blog，canonical/og:url 一致，不改路径）",
 "verification": "核心 6 页 6/6=200；两页 ld=2 / og:image 自托管 / h1=1 / **=0 / desc 198+170 字；封面 303KB curl 200；主索引 257→259 卡、mili 索引 143→144；live articles.json=231；线上 24/24 PASS",
 "defects_found": "① 爬虫文「部分裸发布」：ld=0、无 og:image/twitter/keywords/og:site_name、description 仅 17 字复读标题（正文完整无截断）→ 按同日同品牌房屋重建 head，6,675→10,899B，正文逐字不变；② 两篇 11-03 文主索引均零卡、mili 索引漏爬虫文 → 补 3 卡；③ articles.json 51 条无页面条目（第 21 次隔离，282→231），首页 top6 全有页面；④ 上游 site-inbox 冗余副本（与精修前同源）已删",
 "notes": "sitemap 看门 exit 0 静默（374 loc，无回灌）；推送遇远端并发提交 69ede7e(feed.xml) → rebase 后正常；Pages run completed/success 后线上收敛。新行规：depth 直方图统计全部 div，单卡贡献 depth0+1/depth1+1，断言不能写成「delta 之和==新增卡数」。",
 "result": "PASS",
}
entry = {k: vals.get(k, last[k]) for k in keys}

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), "unexpected tail"
body = r[:-len(TAIL)]
lines = ",".join("\n" + "   " + json.dumps(k, ensure_ascii=False) + ": " + json.dumps(entry[k], ensure_ascii=False) for k in keys)
new = body + "\n  },\n  {" + lines + "\n  }" + "\n ]\n}" + "\n"
d2 = json.loads(new)
assert len(d2["deploys"]) == len(data["deploys"]) + 1
assert list(d2["deploys"][-1].keys()) == keys
open(P, "w", encoding="utf-8").write(new)
print("APPENDED; entries:", len(d2["deploys"]))
print(subprocess.run(["git", "diff", "--stat", "site-inbox/deploy-log.json"], cwd=REPO,
                     capture_output=True, text=True).stdout.strip())
