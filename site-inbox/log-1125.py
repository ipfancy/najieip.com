#!/usr/bin/env python3
"""11-25 夜班 deploy-log 文本手术追加（+15 行 / 0 删除形状）"""
import json, re, subprocess, os

REPO = "/Users/ziganghe/wiki/najieip-verify"
P = os.path.join(REPO, "site-inbox/deploy-log.json")
raw = open(P, encoding="utf-8").read()

d = json.loads(raw)
last = d["deploys"][-1]
KEYS = ["date", "time", "agent", "round", "commit", "action", "files_changed",
        "cards_added", "attribution", "verification", "defects_found", "notes", "result"]
assert list(last.keys()) == KEYS, f"schema drift: {list(last.keys())}"
print("last entry keys OK, count =", len(d["deploys"]))

entry = {
    "date": "2026-11-25",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "de0cda5",
    "action": "每日巡检：核心页 200；11-25 mili AI融脸页补 og:image/og:site_name/keywords/twitter 四卡 + 真摘要（去标题复读）；主索引补 2 张 najie 11-25 卡（植物新品种赔偿基数、专利密集型产品备案）；sitemap 看门 exit 0",
    "files_changed": [
        "mili/blog/20261125-mili-ai-face-blend-portrait-1019.html",
        "img/20261125-mili-ai-face-blend-portrait-1019.png",
        "blog/index.html",
    ],
    "cards_added": 2,
    "attribution": {"najie": 2, "mili": 0, "aipunajie": 0},
    "verification": {
        "core_pages": "7/7 200（含封面 PNG）",
        "structure": "主索引 310 卡 +4/+4 div、depth delta {0:2}、malformed 0、dups 0、stars 0",
        "page_six": "h1=1 ld=2 og:image=True twitter=summary_large_image desc_len=108 正文未改一字",
        "live": "主索引 206,077B / 页面 9,603B 与本地字节一致",
        "feed": "40 条，3 篇新文 RFC822 格式正确",
        "sitemap": "438 loc，看门 exit 0 无回灌",
    },
    "defects_found": [
        "mili 11-25 页缺 og:image 且 description 复读标题（上游 morning 修复只补了 h1/JSON-LD）",
        "两篇 najie 11-25 文有品牌卡但主索引零卡",
    ],
    "notes": "articles.json 守卫 279/279 零违例，首页 top6 六条均有页面；feed 已在 18d3b83 重建，无需补",
    "result": "PASS",
}
assert list(entry.keys()) == KEYS

TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith(TAIL), repr(raw[-40:])
head = raw.rstrip("\n")[:-len(TAIL)] + "\n  }"
lines = []
for k, v in entry.items():
    lines.append("   " + json.dumps(k, ensure_ascii=False) + ": " + json.dumps(v, ensure_ascii=False))
ins = ",\n  {\n" + ",\n".join(lines) + "\n  }"
out = head + ins + "\n ]\n}"
d2 = json.loads(out)
assert len(d2["deploys"]) == len(d["deploys"]) + 1
assert list(d2["deploys"][-1].keys()) == KEYS
open(P, "w", encoding="utf-8").write(out)
print("appended, total entries =", len(d2["deploys"]))

# sitemap 新文覆盖检查
sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
for s in ["20261125-mili-ai-face-blend-portrait-1019",
          "20261125-najie-plant-variety-punitive-damages",
          "20261125-najie-patent-intensive-product-filing"]:
    print("  sitemap", s, sm.count(s))
