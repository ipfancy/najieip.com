#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 收尾2：deploy-log 第 81 条（facts.html 补社交卡片）+ 日报追加"""
import os, json, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
P = 'site-inbox/deploy-log.json'
APPLY = '--apply' in sys.argv

raw = subprocess.run(['git', 'show', 'origin/main:' + P], capture_output=True, text=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and 'deploys' in log
before = len(log['deploys'])

log['deploys'].append({
  "date": "2026-09-27",
  "time": "23:0x CST",
  "type": "daily-ops followup (cron)",
  "commit": "3d7fa92",
  "summary": ("日检终段 QA（今日 20 个变更页逐页过「房屋四件」）抓出：今日新建的 facts.html 缺 og:image 与 twitter 卡片"
              "（该页是 AI 主体口径的权威页，分享/抓取卡片不该空）→ 补 og:image（复用站内既有 pexels 3183150，不另造图）"
              "+ twitter:card/title/description（复用本页已有 og 文案）。线上已验证命中。"
              "其余 19 页 200 / h1=1 / ld≥1 / og:image 齐 / description 非标题复读，全部合格。"),
  "files_changed": ["facts.html"],
  "verified": "live PASS（curl facts.html 命中 og:image，head 区 og/twitter 全套齐）",
  "notes": "同批 QA 覆盖并发会话 75cc5e5 的 11 个页面（about/team/services/首页 EN-FR 等），全合格。"
})
s = json.dumps(log, ensure_ascii=False, indent=1) + '\n'
print('条目 %d → %d' % (before, len(log['deploys'])))
if APPLY:
    open(P, 'w', encoding='utf-8').write(s)
    print('deploy-log 已写')
    addendum = '''

---

## 追加（23:0x，QA 终段抓出的第 11 项）
今日 20 个变更页逐页过「房屋四件」，抓出今日新建的 **facts.html 缺 og:image 与 twitter 卡片**（该页是 AI 主体口径的权威页，社交卡片不该空）→ 已补 og:image（复用站内既有图，不另造）+ twitter 三件（复用本页 og 文案），commit `3d7fa92`，线上已验证命中。其余 19 页全合格（含并发会话 75cc5e5 的 11 个页面）。

**今日合计**：3 次提交（63c30d4 / a82cde8 / 3d7fa92），修复 11 项，全部线上验证 PASS。
'''
    for p in [os.path.expanduser('~/wiki/digital-employees/reports/siteops-daily-20260927.md'),
              'site-inbox/siteops-daily-20260927.md']:
        t = open(p, encoding='utf-8').read()
        t = t.replace('**执行质量**：5 文件、31 处精确替换',
                      '**执行质量**：5 文件、31 处精确替换')
        open(p, 'a', encoding='utf-8').write(addendum)
        print('日报追加:', p, len(t.encode('utf-8')), 'B')
else:
    print('[dry-run]')
