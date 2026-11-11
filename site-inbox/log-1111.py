#!/usr/bin/env python3
"""deploy-log 文本手术追加（+15 行 / 0 删除）"""
import json, os, re

P = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
raw = open(P, encoding="utf-8").read()
r = raw.rstrip("\n")
TAIL = "\n  }\n ]\n}"
assert r.endswith(TAIL), repr(r[-30:])
head = r[:-len(TAIL)] + "\n  }"
log = json.loads(raw)
last = log["deploys"][-1]
print("last keys:", list(last.keys()), "| result:", last.get("result"), "| count:", len(log["deploys"]))

entry = {
    "date": "2026-11-11",
    "time": "22:00-22:40",
    "agent": "SiteOps",
    "round": "每日运营（夜检）",
    "commit": "ec44bf6",
    "action": "补建「已发布无页」定金20%上限页 + 精修「部分裸发布」年终奖页 + 双索引补卡6张 + articles.json四守卫第25次隔离",
    "files_changed": [
        "mili/blog/20261111-mili-earnest-money-cap.html（新建 6,111B）",
        "mili/blog/20261112-mili-year-end-bonus-cancel.html（3,938→6,441B 重建）",
        "img/20261111-mili-earnest-money-cap.png（310,668B）",
        "img/20261112-mili-year-end-bonus-cancel.png（48,665B）",
        "mili/blog/index.html 178→180",
        "najie/blog/index.html 132→133",
        "blog/index.html 301→304",
        "articles.json 300→301（补缺条目）→ 250（隔离51条）",
        "sitemap.xml 400→401",
    ],
    "cards_added": 6,
    "attribution": "mili×2（定金/假冒专利）+ najie×1（同日双申）进品牌索引与主索引；两篇 11-11 文上游两侧零卡，定金文且无页面、articles.json 无条目",
    "verification": "线上 4 页 200（h1=1 / ld=2-3 / og:image / **=0 / 裸表=0）+ 封面 2/2 200 + 三索引卡数 180/133/304 精确命中 + live articles.json=250 + 守卫首页 top6 六条全有页面",
    "defects_found": "①「已发布但站点无页」：earnest-money-cap 在 .published.json 有记录、articles.json/sitemap/索引全无；②「部分裸发布」：year-end-bonus h1=0/h2=0/ld=0/无 og:image/描述复读标题/**×12；③两篇 11-11 文品牌与主索引全零卡",
    "notes": "新建页以同日 mili「假冒专利」精修页做房屋（外链 style.css + nav/footer/CTA），ld 只留 Article+BreadcrumbList（剔除模板 FAQPage）；year-end 页 md 小标题为独立 **加粗行** 而非 ## → 转换按「≤30字且不以句号结尾」判 h2（5 个）；两页正文 md 全文包含=True（1541/1653、1689/1801）一字未改；封面自托管入库后线上 200",
    "result": "PASS",
}
assert list(entry.keys()) == list(last.keys()), (list(entry.keys()), list(last.keys()))

lines = []
for k, v in entry.items():
    lines.append('   "%s": %s' % (k, json.dumps(v, ensure_ascii=False)))
body = ",\n".join(lines)
new = head + ",\n  {\n" + body + "\n  }" + "\n ]\n}"
json.loads(new)
open(P, "w", encoding="utf-8").write(new)
print("entry count now:", len(json.loads(new)["deploys"]))
