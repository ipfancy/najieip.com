#!/usr/bin/env python3
"""从 origin/main 版本重建 deploy-log.json 并追加本轮 22:00 条目（保持 indent=1 原格式）。"""
import json
import subprocess
import os

REPO = os.path.expanduser('~/wiki/najieip-verify')
subprocess.run(['git', 'fetch', 'origin'], cwd=REPO, check=True)
raw = subprocess.run(['git', 'show', 'origin/main:site-inbox/deploy-log.json'],
                     cwd=REPO, capture_output=True, text=True, check=True).stdout
log = json.loads(raw)
assert isinstance(log, dict) and isinstance(log.get('deploys'), list)

entry = {
    "date": "2026-09-14",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "daily-2200",
    "commit": "f5b5d97",
    "action": "主 blog/index.html 补 5 张缺失文章卡片（0912-0914）",
    "cards_added": [
        "/najie/blog/20260914-trademark-rejection-six-reasons.html",
        "/aipunajie/blog/20260914-patent-invention-vs-utility-model.html",
        "/najie/blog/20260913-trademark-report-defense-rights.html",
        "/najie/blog/20260912-trademark-certificate-not-shield.html",
        "/najie/blog/20260912-ai-digital-employee-deployment.html",
    ],
    "verification": {
        "core_pages_http": {"najieip.com": 200, "/mili/": 200, "/najie/": 200,
                            "/blog/": 200, "/sitemap.xml": 200, "/llms.txt": 200},
        "articles_http_200": "5/5",
        "live_index_cards": "5/5 出现于 https://najieip.com/blog/",
        "seocheck": "全部通过（sitemap 419 URL 全带 lastmod / 核心页 JSON-LD 齐备）",
        "commit_deletion_scan": "最近 5 commit 无 D 条目",
    },
    "defects_found": [
        "主 blog/index.html 缺失 0912-0914 共 5 张卡片（已修复）",
        "content.db 缺 09-14 两篇已上线文章记录 → 已出 HANDOFF-20260914-content-db-gap.md，未擅自编号写入",
    ],
    "result": "PASS",
}

# 幂等：已有同 round 条目则跳过
if any(e.get('round') == 'daily-2200' and e.get('date') == '2026-09-14' for e in log['deploys']):
    print('已在 origin 中，跳过追加')
else:
    log['deploys'].append(entry)

out = json.dumps(log, ensure_ascii=False, indent=1)
open(os.path.join(REPO, 'site-inbox/deploy-log.json'), 'w', encoding='utf-8').write(out)
print('deploys total:', len(log['deploys']))
print('last entry commit/result:', log['deploys'][-1].get('commit'), log['deploys'][-1].get('result'))
print('formatted bytes:', len(out.encode()))
