#!/usr/bin/env python3
# site-inbox/log-1123.py — 追加 11-23 每日运营 entry（keys 与上一条完全一致）
import json, os, subprocess
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
raw = open("site-inbox/deploy-log.json", encoding="utf-8").read()
cur = json.loads(raw)
last = cur["deploys"][-1]
keys = list(last.keys())
entry = {"date": "2026-11-23", "time": "05:33", "agent": "SiteOps", "round": "每日运营",
         "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
         "action": "巡检+精修：高企文补 h1/JSON-LD/og/摘要并清 frontmatter 泄漏；食品贴牌文补 JSON-LD/og；articles.json 隔离 52 条死链；najie 索引+主索引补卡",
         "files_changed": 7, "cards_added": 2,
         "attribution": "高企文→najie/blog（纳杰·高新认定线）；食品委托生产文→najie/blog；两篇均入 najie 品牌索引 + 主索引",
         "verification": "核心 6 页 200；线上 7 URL 200 + 双页 h1=1/ld=2/og:image 齐备 + 4 处索引卡 HIT + live articles.json=276；sitemap 看门 exit 0（433 loc）",
         "defects_found": "① 高企文（当日）零卡 + frontmatter 泄漏为可见文本 + h1=0/ld=0/无 og:image/摘要复读标题 ② 食品贴牌文 ld=0/无 og:image/摘要复读（部分裸发布）③ articles.json 上游复活至 328 条含 52 条死链",
         "notes": "首页 slice(0,6) 六条全部有页面；两处 MISMATCH 归因为归一化噪声（frontmatter 头 + h2 标题文字）非正文截断，机顶盒文（11-19）六项全达标零缺陷",
         "result": "PASS"}
assert list(entry.keys()) == keys, (list(entry.keys()), keys)
TAIL = "\n  }\n ]\n}"
assert raw.rstrip("\n").endswith(TAIL), repr(raw[-30:])
head = raw.rstrip("\n")[:-len(TAIL)] + "\n  }"
kv = ",\n".join(f'   "{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in entry.items())
new = head + ",\n  {\n" + kv + "\n  }" + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
chk = json.loads(new)
assert list(chk["deploys"][-1].keys()) == keys
open("site-inbox/deploy-log.json", "w", encoding="utf-8").write(new)
print("entries:", len(chk["deploys"]))
