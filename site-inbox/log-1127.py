import json, os, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
os.chdir(REPO)
DL = "site-inbox/deploy-log.json"

entry = {
    "date": "2026-11-27",
    "time": "22:00",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "7d10ab6",
    "action": "11-27 两篇新文质检修复（孕妇血走私：补 h1/og:image/twitter/去重复 BreadcrumbList；欧盟商标：补 BreadcrumbList/og:image/twitter/清 ** 残留）+ 主索引补 1 张卡 + feed 补 1 条",
    "files_changed": 8,
    "cards_added": 1,
    "attribution": {"mili": 1, "main": 1},
    "verification": "核心 6 页 6/6=200；线上两页 h1=1/ld=2/og:image/twitter/`**`=0；封面 200；主索引 348 卡（两张新卡各 1）；mili 索引 213 卡；feed 两条目 HIT；Pages run success",
    "defects_found": "孕妇血文 h1=0 缺 og:image/twitter 且 BreadcrumbList 重复 2 次；欧盟商标文 ld=1 缺 BreadcrumbList、缺 og:image/twitter、`**` 2 处未转；欧盟商标文主索引零卡、feed 缺条；articles.json 2 条 description 键与标题重复（indent 误用 2 已回退为 1）",
    "notes": "articles.json 守卫余 2 条「/blog/ 路径不在白名单」系主博客有效老文（文件均存在、非首页 top6），不隔离；两篇新文分列首页曝光位 1、2 位",
    "result": "PASS",
}

raw = open(DL, encoding="utf-8").read()
d0 = json.loads(raw)
last = d0["deploys"][-1]
print("LAST KEYS:", list(last.keys()))
print("ENTRY KEYS:", list(entry.keys()))
assert list(entry.keys()) == list(last.keys()), "SCHEMA MISMATCH"

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), repr(r[-30:])
head = r[:-len(TAIL)] + "\n  }"
body = ",\n  {\n" + ",\n".join(
    '   "%s": %s' % (k, json.dumps(v, ensure_ascii=False)) for k, v in entry.items()
) + "\n  }"
new = head + body + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
json.loads(new)
open(DL, "w", encoding="utf-8").write(new)
print("deploy-log entries:", len(json.loads(new)["deploys"]))

# daily report
rep = "/Users/ziganghe/wiki/digital-employees/reports/siteops-daily-20261127.md"
os.makedirs(os.path.dirname(rep), exist_ok=True)
open(rep, "w", encoding="utf-8").write("""# SiteOps 日报 — 2026-11-27（夜班 22:00）

## 一、核心页面状态
✅ 6/6 = 200（https://najieip.com、/mili/、/najie/、/blog/、/sitemap.xml、/llms.txt），零瞬断。

## 二、今日新文（2 篇，均由上游 18:44 落地，均在首页曝光位）
| 文章 | 页面 | 修复前 | 修复后 |
|------|------|--------|--------|
| 3.8万份孕妇血走私出境，最高判7年 | mili/blog/20261127-mili-pregnant-blood-smuggling.html | h1=0、无 og:image/twitter、BreadcrumbList 重复 2 份 | 8,407B：h1=1、ld=2、og:image+twitter 四卡、封面入库 200 |
| 850 欧元，买不下欧盟 27 国商标 | mili/blog/20261127-mili-eu-trademark-real-cost.html | ld=1（缺 BreadcrumbList）、无 og:image/twitter、`**` 2 处未转 | 9,510B：h1=1、ld=2、og:image+twitter、`**`=0 |

两篇「正文剥标签后逐字未改」断言通过。

## 三、索引 / feed 对账
- 主索引：347 → **348 卡**，欧盟商标文补卡（此前主场零卡）。
- mili 索引：213 卡，两篇各 1 张（上游已同步）。
- feed.xml：补欧盟商标文条目（site-index-sync --apply）。
- sitemap：446 loc，两条新文各 1 条（上游已纳入）。

## 四、articles.json
- 修正 2 条 description 键（与标题重复，违反四键 schema）；误用 indent=2 已回退为 indent=1，净 diff 仅 2+/4-。
- 守卫：285/287 合格；余 2 条「/blog/ 路径不在白名单」为主博客有效老文（文件均存在、非 top6），判为白名单正则缺陷，**不隔离**。
- 首页 slice(0,6) 六条全部有页面（含两篇新文，位次 1、2）。

## 五、部署验证
✅ Pages run `7d10ab6` completed/success；线上两页六项全达标、封面 200、主/mili 索引卡各 1、feed HIT。

## 结论
✅ 站点健康；2 篇今日新文已按房屋标准精修上线，索引与 feed 已对齐。唯一遗留为 articles.json 白名单正则不含 /blog/（建议上游修脚本，非本站缺陷）。
""")
print("report written:", rep)
