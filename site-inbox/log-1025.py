import os,json,subprocess,collections
ROOT="/Users/ziganghe/wiki/najieip-verify"
p=os.path.join(ROOT,"site-inbox/deploy-log.json")
raw=subprocess.run(["git","-C",ROOT,"show","origin/main:site-inbox/deploy-log.json"],capture_output=True,text=True).stdout
log=json.loads(raw)
last=log["deploys"][-1]
print("last keys:",list(last.keys()))
print("indent check: first 40 chars ->",repr(raw[:40]))
new=collections.OrderedDict()
for k in last.keys():
    if k=="date": new[k]="2026-10-25"
    elif k=="time": new[k]="22:10"
    elif k=="agent": new[k]="SiteOps"
    elif k=="round": new[k]="每日运营（cron 4c121698279a）"
    elif k=="commit": new[k]="37313b9 + c6a396a"
    elif k=="action": new[k]="补建 2 篇「已发布但站点无页」文章 + 修 1 页缺 og:image + 主索引补 4 卡 + sitemap 纳入"
    elif k in ("files_changed","files"): new[k]=["mili/blog/20261025-mili-ai-label-service.html","mili/blog/20261024-mili-yetan-will.html","mili/blog/20261025-defendant-info-query-beijing.html","mili/blog/index.html","blog/index.html","articles.json","img/20261025-mili-ai-label-service.png","img/20261024-mili-yetan-will.png","img/20261025-defendant-info-query-beijing.png","sitemap.xml"]
    elif k=="cards_added": new[k]=4
    elif k=="verification": new[k]="本地 30 项断言 FAILS=0（两新页 body 与 md 源逐字相等 1501/1501、1739/1739）；线上 7/7 200（4 页 h1=1 ld>=2 og:image + 3 封面图）；/blog/ 235 卡、/mili/blog/ 131 卡线上 HIT；sitemap 333 loc"
    elif k=="defects_found": new[k]="①已发布但站点无页 2 篇（.published.json 有记录、品牌目录无文件，wechat-distribute site 渠道静默失败；10-20 同类第 2 批）②20261025 人口信息查询页缺 og:image/twitter:image（交互式会话新建页，无封面）③主索引漏 2 张今日卡（人口信息查询、najie 许可备案）"
    elif k=="notes": new[k]="新页沿用同日同品牌精修房屋（20261024 保护令页）正则取 head/nav/footer；md→HTML 保留原文落款（含电话）不替换统一三行；--- 分隔线丢弃、表格分隔行丢弃；人口信息查询页无封面 → PIL 生成 1200x630 品牌标题卡入库；articles.json 207 条 0 违例、首页 top6 全部有页面"
    elif k=="result": new[k]="PASS"
    else: new[k]=""
log["deploys"].append(new)
open(p,"w",encoding="utf-8").write(json.dumps(log,ensure_ascii=False,indent=2)+"\n")
print("deploys now",len(log["deploys"]))
print(subprocess.run(["git","-C",ROOT,"diff","--stat","--","site-inbox/deploy-log.json"],capture_output=True,text=True).stdout)
