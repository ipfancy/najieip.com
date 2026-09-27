#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 deploy-log 追加第 80 条（indent=1，取 origin 版本做底，只 append）"""
import os, json, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
P = 'site-inbox/deploy-log.json'
APPLY = '--apply' in sys.argv

raw = subprocess.run(['git', 'show', 'origin/main:' + P], capture_output=True, text=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and 'deploys' in log, '结构必须是 {"deploys": [...]}'
before = len(log['deploys'])

entry = {
  "date": "2026-09-27",
  "time": "22:0x CST",
  "type": "daily-ops (cron)",
  "commit": "pending",
  "summary": (
    "22:00 日检：核心 6 页全 200（首页/mili/najie/blog/sitemap/llms）；articles.json 守卫 156/156 零违例、"
    "首页 slice(0,6) 六条页面四件齐备；近 4 天 12 个文章页「房屋四件」全 PASS（无第 5 例裸发布）；"
    "缺口扫描（品牌索引 173 卡 href 归一 vs 主索引）0 真实缺口（唯一候选 cnptes-three-layer-architecture-diagram 属"
    "架构图页，沿用 09-23 口径不入主索引）；sitemap 268 loc / lastmod 100%，看门测试 exit 0 且 loc 不变（无回灌）；"
    "线上字节：sitemap + 三索引 IDENTICAL，facts.html Δ233B = CF email-protection + beacon（逐行归因）。"
    "【发现并修复：09-27 口径对齐只做了 zh 页，EN/FR 语种页仍是旧口径】"
    "① llms.txt（AI 导航图，AI 最先读）仍写「觅理：专注知识产权法律保护」并把三主体概述写成「法律服务与诉讼」→ 改综合所口径，"
    "并新增 facts.html 条目 + 页首声明「主体关系以 facts.html 为准」；"
    "② en/mili、fr/mili 的 title/description/og 全是 IP-only 旧口径（AI 据此判断我们只做 IP）；"
    "③ 两页 description 混入 12 个中文字（机翻模板泄漏）；"
    "④ fr/mili og:description 因撇号未转义被截成字面量 \"Mili Cabinet d\"（属性断裂）；"
    "⑤ fr/mili title 裸撇号写入，HTML 属性风险；"
    "⑥ en/mili、fr/mili 零 JSON-LD（全站唯一无结构化数据的品牌页）→ 补 LegalService JSON-LD（@id 对齐 zh 页 /#org-mili、"
    "信用代码 31110000MD0262382F、knowsAbout 十项综合领域、knowsLanguage、memberOf 指向 #organization）；"
    "⑦ mili 三语页补 hreflang 四值（zh-CN/en/fr/x-default）；"
    "⑧ 4 个 EN/FR 页缺 twitter:title → 复用各自 og:title（不另编）；"
    "⑨ zh mili hero 文案仍写「专注知识产权诉讼与法律保护」+ 业务领域副题「全维度知识产权法律保护」→ 改「以知产诉讼为专长，"
    "覆盖综合法律事务」；"
    "⑩ EN/FR aipunajie「总部在朝阳」与今日已修的 zh 注册住所（东城崇文门外大街11号2层208）打架 → 统一为"
    "注册住所东城 + 共用办公地朝阳宝钢大厦1502。共 5 文件、31 处精确替换（每处断言匹配数==1）+ 5 处插入，"
    "终验 0 FAIL（JSON-LD 全部 json.loads 通过、div 配平 diff=0、EN/FR meta 中文残留 0、双房屋齐备）。"
  ),
  "files_changed": ["mili/index.html", "en/mili/index.html", "fr/mili/index.html",
                    "en/aipunajie/index.html", "fr/aipunajie/index.html", "llms.txt"],
  "verified": "local-structure PASS / live-pending",
  "notes": "修复依据 = 权威口径页 facts.html（今日 844d6e5/de4a62c 新增）；原则：只做口径一致性对齐，不新增论点。"
}
log['deploys'].append(entry)
print('条目数 %d → %d' % (before, len(log['deploys'])))

s = json.dumps(log, ensure_ascii=False, indent=1) + '\n'
if APPLY:
    open(P, 'w', encoding='utf-8').write(s)
    print('已写入 %s (%d B, indent=1)' % (P, len(s.encode('utf-8'))))
    # 自检：diff 只应有新增
    d = subprocess.run(['git', 'diff', '--numstat', '--', P], capture_output=True, text=True).stdout
    print('numstat(added deleted file):', d.strip())
else:
    print('[dry-run] 未写盘')
