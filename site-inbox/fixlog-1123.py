#!/usr/bin/env python3
# site-inbox/fixlog-1123.py — 给刚追加的 entry 补 attribution 键（保持 schema 一致）
import json, os, subprocess
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
raw = open("site-inbox/deploy-log.json", encoding="utf-8").read()
cur = json.loads(raw)
last = cur["deploys"][-1]
if "attribution" in last:
    print("already has attribution"); raise SystemExit
marker = '"cards_added": %s,' % json.dumps(last["cards_added"])
i = raw.rfind(marker)
assert i > 0, "marker not found"
ins = '\n   "attribution": "高企文→najie/blog（纳杰·高新认定线）；食品委托生产文→najie/blog；均入 najie 索引 + 主索引"'
new = raw[:i + len(marker)] + ins + raw[i + len(marker):]
chk = json.loads(new)
print("entries", len(chk["deploys"]), "keys", list(chk["deploys"][-1].keys()) == list(chk["deploys"][-2].keys()))
open("site-inbox/deploy-log.json", "w", encoding="utf-8").write(new)
print("OK")
