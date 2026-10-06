#!/usr/bin/env python3
"""Append deploy-log entry (base = origin/main version, native indent=1) + write daily report."""
import subprocess, json, os, datetime

ROOT = "/Users/ziganghe/wiki/najieip-verify"
os.chdir(ROOT)
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     capture_output=True, text=True).stdout
log = json.loads(raw)
print("existing entries:", len(log["deploys"]))
print("last entry keys:", list(log["deploys"][-1].keys()))

entry = {
    "date": "2026-10-06",
    "time": "22:0x",
    "agent": "SiteOps",
    "round": "每日运营（夜间）",
    "commit": "c26c146",
    "action": ("核心 8 页 200；精修诺奖×专利文（上游部分裸发布：缺 JSON-LD/og:image、og:title 属性内直引号致截断、"
               "** 未转 strong、description 复读标题、HTML 注释被转义为可见文本）7315→10861B，正文 32 段零改动；"
               "mili 索引补卡 108→109、主索引 201→202（日期降序插位）；articles.json 守卫第 11 次隔离 225→175；"
               "sitemap 看门 exit 0（292 loc 不变）"),
    "files_changed": ["mili/blog/20261006-nobel-icecube-patent-four-rules.html",
                      "mili/blog/index.html", "blog/index.html", "articles.json",
                      "articles-quarantine-20261006.json"],
    "cards_added": {"mili/blog/index.html": "108→109", "blog/index.html": "201→202"},
    "verification": "核心页 8/8 200；线上 11/11 PASS（直连+cache-buster）；结构终验 cards/depth1/dup/date-desc 全 PASS；首页 top6 全部有页面；sitemap 看门 exit 0",
    "defects_found": ["诺奖×专利文部分裸发布（缺 JSON-LD/og:image/og:title 截断/** 未转/描述复读标题），且处首页 slice(0,6) 第 2 曝光位",
                      "content.db articles 表无诺奖文记录（上游发布未登记）",
                      "articles.json 上游第 11 次复活 50 条无页面条目"],
    "notes": ("首次线上校验读到 CF 旧缓存（3860 字符=旧版），等 150s 后 11/11 全通 → push 后 CF 传播需等待，勿提前判故障；"
              "20261006-工程结算-最终结算条款-二审改判 仅有 md 源、无 HTML 页，未上线"),
    "result": "PASS",
}
log["deploys"].append(entry)
with open("site-inbox/deploy-log.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("appended; entries now:", len(log["deploys"]))

report = """# SiteOps 日报 — 2026-10-06（夜间 22:00）

## 一、站点核心页 HTTP 状态
✅ 8/8 返回 200：`/`、`/mili/`、`/najie/`、`/blog/`、`/sitemap.xml`、`/llms.txt`、`/en/`、`/fr/`

## 二、近 2 日文章 × 索引一致性
| 文章 | 文件 | 品牌索引 | 主索引 |
|------|:----:|:--------:|:------:|
| 20261006-诺奖×专利（IceCube） | ✅ | ⚠️→✅ 已补 | ⚠️→✅ 已补 |
| 20261006 赢了官司还被点名6条 | ✅ | ✅ | ✅ |
| 20261005 前8年年费足缴 | ✅ | ✅ | ✅ |
| 20261005 商标法2027实施条例 | ✅ | ✅ | ✅ |
| 20261005 商标被抢注3招 | ✅ | ✅ | ✅ |
| 20261004 同一专利族美国判赔 | ✅ | ✅ | ✅ |
| 20261003 有注册证也侵权 | ✅ | ✅ | ✅ |

## 三、异常与修复（1 项）
⚠️ **诺奖×专利文为「部分裸发布」**（今日 18:31 上游提交，仅在 mili/blog 落页、两索引零卡，且正处 articles.json 首页 slice(0,6) **第 2 曝光位**）
- 缺陷：无 JSON-LD、无 og:image、`og:title` 属性内直引号致属性被截断、`**` 未转 `<strong>`、description 复读标题、HTML 注释被转义为可见文本
- 修复：房屋样式补齐（Article + BreadcrumbList JSON-LD、og/twitter 全套、keywords/author）、description 按原文事实重写（133 字）、引号规范为中文引号、注释转真注释
- 尺寸：7,315 → 10,861 B；**正文 32 段零改动**（逐段断言通过）

## 四、索引补卡
✅ mili 索引 108 → 109；主索引 201 → 202（按日期降序插位）
✅ 结构终验：卡片数 / depth1 直接子节点 / 无重复 href / 插入点前缀降序 全 PASS

## 五、articles.json 守卫（第 11 次）
✅ 隔离 225 → 175（违例 50：文件不存在 50 + 非白名单路径 4）；复查 175/175 零违例
✅ 首页 slice(0,6) 全部有落地页

## 六、sitemap 看门测试
✅ `sitemap-auto.sh` exit 0，loc 292 不变（诺奖文 loc 已由上游 18:31 提交补入）

## 七、线上部署验证（直连 + cache-buster）
✅ 11/11 PASS：文章页 ld+json×2、og:image、h1=1、`**`=0、描述非标题复读、og:title 未截断；两索引卡 HIT；articles.json=175；线上与磁盘差异仅 CF beacon（8 行）
⚠️ 首次校验读到旧缓存（3,860 字符），等待 150s 后全通 —— push→CF 传播确需等待

## 八、待办 / 移交
- 上游发布流水线仍会产出「裸发布页」并占据首页曝光位（连续第 5 日）→ 建议在发布侧强制套用房屋模板
- `20261006-工程结算-最终结算条款-二审改判.md` 已有 md 源但无 HTML 页，未上线，本周内关注
"""
os.makedirs(os.path.join(ROOT, "..", "digital-employees/reports"), exist_ok=True)
rp = "/Users/ziganghe/wiki/digital-employees/reports/siteops-daily-20261006.md"
open(rp, "w", encoding="utf-8").write(report)
print("report ->", rp, os.path.getsize(rp), "B")
