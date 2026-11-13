#!/usr/bin/env python3
# 追加 deploy-log（文本手术，+15 行 / 0 删除）
import json, subprocess, sys

P = "/Users/ziganghe/wiki/najieip-verify/site-inbox/deploy-log.json"
raw = open(P, encoding="utf-8").read()
if raw.endswith("\n"):
    raw = raw.rstrip("\n")
d = json.loads(raw)
last = d["deploys"][-1]
KEYS = list(last.keys())

entry = {
    "date": "2026-11-13",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（cron 4c121698279a）",
    "commit": "1552ef7",
    "action": "精修当日 mili「荷兰突击搜查撤销」部分裸发布页；六项判据体检 + 双索引卡复核 + articles.json 守卫 + sitemap 看门 + 线上终验",
    "files_changed": "mili/blog/20261113-byd-netherlands-evidence-seizure.html（5,862→10,037B）、img/20261113-byd-netherlands-evidence-seizure.png（313KB 入库）",
    "cards_added": 0,
    "attribution": "上游 05:02 自动发布已写双索引卡（mili + 主各 1 张），本轮零补卡；品牌归属按落地目录 /mili/blog/",
    "verification": "核心 6 页 6/6=200（零瞬断）；文章页 h1=1 / ld=2（Article+BreadcrumbList，含 @context）/ og:image 200 / description 138 字非标题复读 / **=0 / 裸表=0；正文 md 全文归一包含=True（1328 字一字未改，新增 5 个 h2 路标）；封面 curl 200；双索引卡 HIT 各 1；线上 articles.json=251 含当日文；sitemap 403 loc 已含本文，看门 exit 0 无新增提交",
    "defects_found": "① 部分裸发布：ld=0 / 无 og:image / 无 twitter:title / 无 keywords / description 25 字复读标题 / **×10 / 裸 markdown 表 6 行（正处 articles.json 首页 slice(0,6) 第 1 曝光位）② 管线产出未确认发布：20261113-mili-registered-capital-deadline publish_id 为空、站点无页——未自动建页（避免草稿上线），转人工确认",
    "notes": "行规复用：房屋取同品牌近期精修页（20261112-mili-year-end-bonus-cancel）；ld 两块 deepcopy 后显式加 @context（najie/mili 房屋普遍缺 @context）；md 无 ## 时按段落前缀注入 5 个描述性 h2 路标、正文不改一字；单次 run 工具调用 20 次（成本纪律 ≤25）。",
    "result": "PASS",
}
assert list(entry.keys()) == KEYS, f"schema mismatch: {list(entry.keys())} vs {KEYS}"

TAIL = "\n  }\n ]\n}"
assert raw.endswith(TAIL), "tail mismatch"
head = raw[:-len(TAIL)] + "\n  }"   # TAIL 开头的 "  }" 是上一条 entry 的闭括号，必须补回
lines = []
for k, v in entry.items():
    lines.append('   "%s": %s' % (k, json.dumps(v, ensure_ascii=False)))
new = head + ',\n  {\n' + ",\n".join(lines) + '\n  }' + "\n ]\n}"
d2 = json.loads(new)
assert len(d2["deploys"]) == len(d["deploys"]) + 1, "count mismatch"
assert list(d2["deploys"][-1].keys()) == KEYS

if "--apply" in sys.argv:
    open(P, "w", encoding="utf-8").write(new)
    print("APPENDED entries", len(d2["deploys"]))
else:
    print("DRY ok entries would be", len(d2["deploys"]))
