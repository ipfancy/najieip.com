#!/usr/bin/env python3
# 0923 部署日志追加（origin 版本做底, indent=1）
import json, os, subprocess

os.chdir(os.path.expanduser('~/wiki/najieip-verify'))
P = 'site-inbox/deploy-log.json'
base = open(P, encoding='utf-8').read()
log = json.loads(base)
assert isinstance(log, dict) and 'deploys' in log, type(log)

entry = {
  "date": "2026-09-23",
  "time": "22:0x CST",
  "type": "daily-operations",
  "commit": "d579735 + 8c70774",
  "summary": "每日运营：核心 6 页 200；主索引补 9 张卡（mili 财产守护系列 7 期 + najie 商标驳回复审/AAA 评价 2 篇）172→181；articles.json 守卫第 7 次隔离（204→154）；sitemap 回补 7 条 mili 系列 loc（258→265）",
  "changes": [
    "blog/index.html：补 9 张卡 —— /mili/blog/20260922-caichan-shouhu-01..07（财产守护系列）与 /najie/blog/shangbiao-bohuifushen-2026.html、/najie/blog/zhiming-shangbiao-pinpai-pingjia-2026.html；v3 法每次插入后重扫位置，插到「第一张日期 < 新卡日期」的卡之前，卡片 172→181、div 配平 0、depth==1 卡片数 181、malformed 0、插入点前缀降序 9/9 无违例",
    "articles.json：守卫第 7 次隔离（204→154），违例 50 条移入 articles-quarantine-20260923.json（原生 indent=2，diff 仅 -300 行 0 新增）；首页 slice(0,6) 六条全部有页面，无 404 曝光位",
    "sitemap.xml：跑 ~/.hermes/scripts/sitemap-auto.sh（看门测试）自动纳入 7 条 mili 系列 loc，258→265 条，只增不删；线上字节一致 51,634B",
    "上游产出核验：mili 财产守护系列 7 篇（外部样式表房屋样式 + h1 + JSON-LD 2 + og:image 齐备）、najie 商标驳回复审 16,007B / AAA 知名商标品牌评价 15,065B（内联样式 + JSON-LD 3）—— 均合格，无需重建",
    "排除项：najie/blog/cnptes-three-layer-architecture-diagram.html（架构图页非文章，沿用 09-16 口径不补主索引；已在 sitemap）、najie/blog/uspto-tbmp-2026-update.html（529B 跳转壳）"
  ],
  "verification": {
    "core_pages_http200": "6/6（首页 / mili / najie / blog / sitemap.xml / llms.txt）",
    "main_index_cards": "172 → 181（线上 181 一致）",
    "new_cards_live": "9/9 HIT（curl 线上 blog/ 索引）",
    "sitemap_locs": "258 → 265（线上 265 条，字节 IDENTICAL 51,634B）",
    "index_byte_diff": "Δ367B = Cloudflare 自动注入 beacon.min.js（三个品牌索引同幅，属正常）",
    "article_pages_seo": "3 抽检：og:url/canonical 齐备、ld+json 2~3、schema.org 未脱敏、`**` 泄漏 0、h1==1",
    "articles_json_guard": "204 → 154，违例 0（--check 复跑应为 154/154）"
  },
  "notes": "cron 会话内 git push 曾两次报 Permission denied (publickey)（ssh-agent 无 identity）；用 GIT_SSH_COMMAND='ssh -i /Users/ziganghe/.ssh/id_ed25519 -o IdentitiesOnly=yes' 即成功，随后裸 ssh 亦恢复 —— 属瞬时 ssh-agent/网络问题，非密钥失效"
}
log['deploys'].append(entry)
out = json.dumps(log, ensure_ascii=False, indent=1)
open(P, 'w', encoding='utf-8').write(out)
# diff 规模自检：应仅 +34 行左右
diff = subprocess.run(['git', 'diff', '--numstat', P], capture_output=True, text=True).stdout
print("entries:", len(log['deploys']), "| diff:", diff.strip())
print("json reload ok:", isinstance(json.loads(open(P, encoding='utf-8').read()), dict))
