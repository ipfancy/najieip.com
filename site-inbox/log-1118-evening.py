#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy-log 文本手术追加（现行手工混排缩进，禁止 json.dump 重写）"""
import json, subprocess, os

P = os.path.expanduser("~/wiki/najieip-verify/site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()
TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith(TAIL), "TAIL 不匹配，中止"

entry = {
    "date": "2026-11-18",
    "time": "22:05",
    "agent": "SiteOps",
    "round": "每日运营（周三夜班）",
    "commit": "7703312",
    "action": "精修 20261118 芬兰出海用工裸发布页（h1=0 / h2=0 / ld=0 / 无 og:image / description 20 字复读标题）→ 按 md 源整页重建 3246→11314B（7 个 h2 路标、Article+BreadcrumbList、真摘要 123 字、封面 285KB 入库）；当日 5 篇文双索引补卡 6 张；articles.json 守卫第 25 次隔离 26 条",
    "files_changed": [
        "mili/blog/20261118-mili-finland-labor-four-gates.html (3246→11314B)",
        "img/20261118-mili-finland-labor-four-gates.png (285854B 新增)",
        "blog/index.html (334→338 卡)",
        "mili/blog/index.html (197→198 卡)",
        "najie/blog/index.html (149→150 卡)",
        "articles.json (290→264，隔离 26 条无页面条目)",
        "articles-quarantine-20261118.json (累计 26 条)",
    ],
    "cards_added": 6,
    "attribution": "mili 4 篇（芬兰出海用工/药链九案/拒执五案/AI商业秘密）+ najie 1 篇（地理标志十五五）",
    "verification": "核心 6 页 6/6=200（零瞬断）；5 篇当日文六项判据全 PASS（h1=1 / ld≥2 / og:image / 真摘要 / **=0 / 无裸表）；品牌卡+主卡逐 slug 各 1 张；md 全文包含=True（1905 字，正文未改一字）；articles.json 前 6 位 6/6 有页面、违例 0/264；sitemap 看门 exit 0（420 loc 不变）",
    "defects_found": [
        "芬兰用工文为裸发布档（无 h1/h2/JSON-LD/og:image，描述复读标题）",
        "当日 5 篇文中 4 篇缺主索引卡、2 篇缺品牌索引卡（上游只写页面/sitemap/feed）",
        "articles.json 复活 26 条无页面条目（第 25 次隔离）",
    ],
    "notes": "新增行规：上游当日 5 篇的 md 源可能改名/改日期落盘（拒执五案 md 实为 20261120-*），md_contained 仅对同期文件可判，其余走六项 head 判据；索引卡摘要应取页面 meta description 而非标题（芬兰卡原为标题复读，已修 2 处）",
    "result": "PASS",
}

last = json.loads(raw)["deploys"][-1]
assert list(entry.keys()) == list(last.keys()), "schema 键序不一致"

head = raw.rstrip("\n")[:-len(TAIL)] + "\n  }"
lines = []
for k, v in entry.items():
    lines.append(f'   "{k}": {json.dumps(v, ensure_ascii=False)}')
body = ",\n".join(lines)
new = head + ",\n  {\n" + body + "\n  }" + "\n ]\n}"
d = json.loads(new)
assert len(d["deploys"]) == len(json.loads(raw)["deploys"]) + 1
open(P, "w", encoding="utf-8").write(new)
print("appended, entries =", len(d["deploys"]))
print(subprocess.run(["git", "diff", "--stat", "site-inbox/deploy-log.json"],
                     cwd=os.path.expanduser("~/wiki/najieip-verify"), capture_output=True, text=True).stdout)
