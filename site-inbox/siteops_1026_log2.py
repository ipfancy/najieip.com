#!/usr/bin/env python3
# 文本方式追加 deploy-log（保持原手工缩进风格，零删除）
import json, sys
BASE = "/Users/ziganghe/wiki/najieip-verify"
p = f"{BASE}/site-inbox/deploy-log.json"
raw = open(p, encoding="utf-8").read()
had_nl = raw.endswith("\n")
raw = raw.rstrip("\n")
MARKER = "\n  }\n ]\n}"
assert raw.endswith(MARKER), repr(raw[-30:])

entry = {
 "date": "2026-10-26",
 "time": "22:05",
 "agent": "SiteOps",
 "round": "每日运营（22:00 cron）",
 "commit": "(本提交)",
 "action": "主索引补 3 张 2026-10-26 缺卡 + articles.json 补 1 条（觅理技术秘密新文）",
 "files_changed": ["blog/index.html", "articles.json"],
 "cards_added": 3,
 "attribution": "上游发布只同步品牌索引，主索引需 SiteOps 补齐",
 "verification": "核心 6 页全部 200；主索引 235→238 卡（div 深度归零、无负深度、href 无重复）；articles.json 210→211（守卫 211/211 零违例，首页 slice(0,6) 六条全部有页面）；sitemap 看门 exit 0（338 loc 不变）；近 5 日 20 个品牌博客文章页六联判据全 OK（desc 无标题复读、stars=0、裸表=0）",
 "defects_found": [
   "10-26 三篇新文（mili 离婚后继承所得、najie 双11爆单、mili 技术秘密秘密点）只进品牌索引，主索引零卡",
   "觅理技术秘密文未写入 articles.json（首页曝光数据源缺该文）"
 ],
 "notes": "上游 9968a5d/81ca2c7 只改品牌索引；按日期降序插到首张 2026-10-25 卡之前，逐轮重扫位置法插入，卡计数+3/div 归零/href 唯一三项断言通过；articles.json 走原生 indent=2 插入条目",
 "result": "PASS",
}

lines = []
for k, v in entry.items():
    lines.append(f'   {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}')
new = "\n  },\n  {\n" + ",\n".join(lines) + "\n  }"
raw2 = raw[:-len(MARKER)] + new + "\n ]\n}"
json.loads(raw2)  # validate
open(p, "w", encoding="utf-8").write(raw2 + ("\n" if had_nl else ""))
print(f"OK deploys={len(json.loads(raw2)['deploys'])}")
