import os, json, subprocess
R = os.path.expanduser("~/wiki/najieip-verify")
P = os.path.join(R, "site-inbox/deploy-log.json")
entry = {
 "date": "2026-11-07",
 "time": "22:25",
 "agent": "siteops",
 "round": "daily",
 "commit": "824469b",
 "action": "修当日「试岗期」文部分裸发布（ld=0→2 / 无 og:image / description 复读标题 / 正文 ASCII 直引号 / <p>---</p> 泄漏）5727→8266B；三索引补卡 5 张（mili+najie 品牌卡各 1、主索引 3）；articles.json 守卫第 23 次隔离 293→242",
 "files_changed": ["mili/blog/20261107-mili-unpaid-trial-shigang.html", "img/20261107-mili-unpaid-trial-shigang.png", "mili/blog/index.html", "najie/blog/index.html", "blog/index.html", "articles.json", "articles-quarantine-20261107.json"],
 "cards_added": 5,
 "attribution": "3 篇当日文落地 mili/blog/（试岗/过渡办法/不当得利）与 najie/blog/（专利许可 6 条），canonical 与落地目录一致，未改路径",
 "verification": "核心 6 页 6/6 200；4 页线上 h1=1 / ld≥2 / og:image / **=0 全 PASS（8266/12470/12398/11684B）；封面 img 200；7 处索引卡 HIT；live articles.json=242；结构终验 div 配平 + dups=0 + md 全文包含=True；Pages run 824469b success",
 "defects_found": ["上游当日 3 篇文品牌索引与主索引漏卡（mili 过渡办法 / najie 专利许可双索引零卡，不当得利仅缺主索引）", "上游「试岗期」文部分裸发布：ld=0、无 og:image/og:site_name/keywords/twitter、description 复读标题、正文 ASCII 直引号、裸 --- 分隔行", "articles.json 仍含 51 条无页面条目（守卫第 23 次隔离）", "mili/blog/index.html 存在历史遗留 unclosed div（改动前后同为 332/331，非本次引入）"],
 "notes": "试岗文正文本身完整（md 全文包含=True），只修 head 面，正文一字未改仅做引号归一与 <p>---</p>→<hr>；品牌索引卡 href 用相对 ./slug.html、主索引用绝对路径；索引补卡走 div 深度配对模板 + 按日期降序插位；sitemap 看门 exit 0 无 diff（392 loc）",
 "result": "PASS",
}
raw = open(P, encoding="utf-8").read()
TAIL = "\n  }\n ]\n}"
assert raw.endswith(TAIL) or raw.rstrip("\n").endswith("}\n ]\n}"), repr(raw[-40:])
r = raw.rstrip("\n")
if r.endswith(TAIL):
    head = r[:-len(TAIL)] + "\n  }"
else:
    head = r[:r.rfind("\n ]\n}")] + "\n  }"
lines = []
for k, v in entry.items():
    lines.append("   %s: %s" % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)))
block = ",\n  {\n" + ",\n".join(lines) + "\n  }"
new = head + block + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
d = json.loads(new)
assert len(d["deploys"]) == 131, len(d["deploys"])
assert list(d["deploys"][-1].keys()) == list(d["deploys"][-2].keys()), "schema mismatch"
open(P, "w", encoding="utf-8").write(new)
print("OK entries", len(d["deploys"]), "bytes", len(new), "last", d["deploys"][-1]["result"])
