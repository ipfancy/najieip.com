#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append a deploy-log entry by text surgery (matches existing mixed indentation)."""
import json, os, sys

P = os.path.expanduser("~/wiki/najieip-verify/site-inbox/deploy-log.json")
entry = {
    "date": "2026-10-27",
    "time": "22:10",
    "agent": "SiteOps",
    "round": "每日运营（22:00 cron）",
    "commit": "60c789b",
    "action": "主索引补 2 张爱普纳杰缺卡（10-27 OA 电话答复 / 10-26 发布会前申请专利）+ articles.json 补今日条目",
    "files_changed": ["blog/index.html", "articles.json"],
    "cards_added": 2,
    "attribution": "上游发布只同步品牌索引（aipunajie/blog/index.html），主索引与 articles.json 需 SiteOps 补齐",
    "verification": "核心 6 页全部 200（llms.txt 首轮 000 瞬断，重试即 200）；今日 aipunajie 新页六联判据 OK（h1=1 / h2=10 / ld=2 / og:image / stars=0 / 裸表=0，15,251B）；主索引 238→240 卡（div 深度归零、无异常闭合、每卡以 h2 起、日期降序置顶）；articles.json 211→212（守卫 212/212 零违例，首页 slice(0,6) 六条全部有页面）；sitemap 看门 exit 0（339 loc 不变）；近 3 日 8 个品牌博客文章页六联判据 8/8 OK；线上主索引 240 卡 + 两张新卡 HIT + articles.json 212 条 + 索引字节一致（165,256B）",
    "defects_found": [
        "10-27 aipunajie 新文与 10-26 aipunajie 发布会文均只进品牌索引，主索引零卡",
        "今日新文未写入 articles.json（首页 slice(0,6) 曝光数据源缺该文）",
        "Pages 构建排队约 7 分钟（queued→in_progress→success），期间线上仍为旧版"
    ],
    "notes": "品牌索引 aipunajie 卡模板为 h3+href ./x.html，缺口扫描正则须 <h[23][^>]*><a href=，只写 <h2> 会把 aipunajie 全量漏判；主索引卡按主索引房屋样式重建（h2 绝对路径 + meta 带 tag/日期/主体署名 + p 摘要）。插入用逐轮重扫位置法，硬断言 t2.replace(card+'\\n  ','',1)==t 通过。cnptes-three-layer-architecture-diagram.html 属架构图页，按既有口径不入主索引。线上首轮读旧缓存（238 卡/211 条），Pages 构建 success 后 45s 内全部收敛。",
    "result": "PASS",
}

raw = open(P, encoding="utf-8").read()
tail = "\n ]\n}\n"
assert raw.endswith("\n  }\n ]\n}") or raw.endswith("\n  }\n ]\n}\n"), repr(raw[-30:])

lines = []
for k, v in entry.items():
    lines.append('   %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)))
block = "\n  {\n" + ",\n".join(lines) + "\n  }"

new = raw.rstrip("\n")
assert new.endswith("\n  }\n ]\n}")
new = new[: -len("\n ]\n}")] + ",\n" + block.lstrip("\n") + "\n ]\n}"
new += "\n"

d = json.loads(new)
assert len(d["deploys"]) == 119, len(d["deploys"])
assert d["deploys"][-1]["date"] == "2026-10-27"
print("entries:", len(d["deploys"]), "| keys:", list(d["deploys"][-1].keys()))
if "--apply" in sys.argv:
    open(P, "w", encoding="utf-8").write(new)
    print("WRITTEN")
else:
    print("DRY-RUN")
