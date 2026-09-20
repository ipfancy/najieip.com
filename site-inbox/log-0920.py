#!/usr/bin/env python3
# 0920 deploy-log 追加（origin 版本做底 · indent=1）+ 日报
import os, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
subprocess.run(["git", "fetch", "origin", "-q"], cwd=REPO, check=False)
raw = subprocess.run(["git", "show", "origin/main:site-inbox/deploy-log.json"],
                     cwd=REPO, capture_output=True, text=True).stdout
log = json.loads(raw)
print("baseline deploys:", len(log["deploys"]))

entry = {
    "date": "2026-09-20",
    "run": "22:00 每日运营",
    "commit": "e11b023",
    "checks": {
        "core_pages_http": {"najieip.com": 200, "/mili/": 200, "/najie/": 200, "/blog/": 200,
                            "sitemap.xml": 200, "llms.txt": 200},
        "content_db_recent": ["ART-2026-0091", "ART-2026-0090", "ART-2026-0089", "ART-2026-0088"],
        "brand_index_coverage": "4/4 全部在对应品牌索引",
        "main_index_gap": "1 处（0920 新文）→ 已补卡 162→163",
        "structure_verify": "11 项全 PASS（depth=0 / depth=2 卡片 163 / malformed=0 / dup=0 / md_leak=0 / 日期降序）",
        "live_bytes": ["/blog/ 103207B IDENTICAL", "/mili/blog/ 104999B IDENTICAL",
                       "/najie/blog/ 66025B IDENTICAL"],
        "sitemap": "247 loc · lastmod 100% · 含 0920 新文",
        "articles_json_guard": "136/136 零违例 · 首页 top6 全部落地",
        "seocheck": "全部通过（4 段）",
    },
    "fixes": ["主索引补卡《家族信托被存款扣走4143万》(mili/20260920-family-wealth-isolation-three-firewalls)",
              "补卡脚本首版漏 </div>，被结构终验（div 深度归零 + depth=2 卡片计数）拦下后修正"],
    "verdict": "healthy",
}
log["deploys"].append(entry)
with open(os.path.join(REPO, "site-inbox/deploy-log.json"), "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("appended ->", len(log["deploys"]), "entries")

# 日报
report = """# SiteOps 日报 — 2026-09-20（22:00 每日运营）

## ✅ 站点核心页面（6/6 全 200）
najieip.com / /mili/ / /najie/ / /blog/ / sitemap.xml / llms.txt — 全部 200

## ✅ 内容同步
- content.db 近 3 天已发布 4 篇，全部在对应品牌索引：
  ART-2026-0091 家族信托（mili）· ART-2026-0090 许诺销售（mili）
  ART-2026-0089 欧盟外观设计（najie）· ART-2026-0088 UPC 禁令反打（mili）
- 缺口扫描（品牌索引 href 归一比对 148 卡）：发现 **1 处缺口** → 0920 新文《家族信托被当存款扣走4143万》未进主索引
- ⚠️→✅ 已修复：主索引补卡 162→**163**，日期降序置顶

## ✅ 结构终验（11 项全 PASS）
卡片计数 163 · div 深度归零 · depth=2 卡片 163 · malformed 0 · 重复 href 0 · 新卡为首卡 ·
前缀日期降序 [09-20, 09-19, 09-19] · markdown 泄漏 0 · 描述无污染
（首版补卡脚本漏写 `</div>`，被「div 深度归零 + depth=2 计数」两项断言当场拦下后修正 —— 校验清单再次生效）

## ✅ 部署验证（字节口径，非 grep 计数）
/blog/ 103207B · /mili/blog/ 104999B · /najie/blog/ 66025B —— 线上与本地**全部 IDENTICAL**
线上主索引首卡即新文，163 卡；新文详情页 200（8,988B）

## ✅ SEO / 数据卫生
- najie-seocheck 4 段全通过；sitemap 247 loc，lastmod **100%**（0 缺失），含 0920 新文
- articles.json 守卫：136/136 零违例；首页 slice(0,6) 六个位次全部有落地页（无 404 曝光风险）

## 结论
站点健康。今日唯一动作 = 主索引补 1 张缺卡并上线，已字节级确认。无待办遗留。
"""
rp = os.path.expanduser("~/wiki/digital-employees/reports/siteops-daily-20260920.md")
os.makedirs(os.path.dirname(rp), exist_ok=True)
open(rp, "w", encoding="utf-8").write(report)
print("report ->", rp)
