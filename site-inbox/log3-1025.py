import os,json,subprocess,collections
ROOT="/Users/ziganghe/wiki/najieip-verify"
p=os.path.join(ROOT,"site-inbox/deploy-log.json")
raw=open(p,encoding="utf-8").read()
log=json.loads(raw)
d=log["deploys"]
tpl=None
for e in reversed(d):
    if "agent" in e and "round" in e:
        tpl=e; break
print("template keys:",list(tpl.keys()),"date",tpl.get("date"))
vals={
 "date":"2026-10-25",
 "time":"22:05-22:25",
 "agent":"SiteOps",
 "round":"每日运营（cron 4c121698279a）",
 "commit":"37313b9 + c6a396a",
 "action":"补建 2 篇「已发布但站点无页」文章（mili AI内容标识 / mili 叶檀遗嘱）+ 修 1 页缺 og:image（人口信息查询）+ 主索引补 4 卡 + sitemap 纳入 2 条",
 "files_changed":["mili/blog/20261025-mili-ai-label-service.html","mili/blog/20261024-mili-yetan-will.html","mili/blog/20261025-defendant-info-query-beijing.html","mili/blog/index.html","blog/index.html","articles.json","img/20261025-mili-ai-label-service.png","img/20261024-mili-yetan-will.png","img/20261025-defendant-info-query-beijing.png","sitemap.xml"],
 "cards_added":4,
 "attribution":"", 
 "verification":"本地 30 项断言 FAILS=0（两新页 body 与 md 源逐字相等 1501/1501、1739/1739，div 配平，ld json 全通）；线上 7/7 200（4 页 h1=1 / ld>=2 / og:image + 3 封面图 200）；/blog/ 235 卡、/mili/blog/ 131 卡线上 HIT；sitemap 333 loc；articles.json 207 条 0 违例",
 "defects_found":"①「已发布但站点无页」2 篇（.published.json 有记录、品牌目录无文件 → wechat-distribute site 渠道静默失败；10-20 同类之后第 2 批）②今日人口信息查询页缺 og:image/twitter:image（交互式会话新建、无封面）③主索引漏 2 张今日卡（人口信息查询、najie 许可备案）",
 "notes":"新页沿用同日同品牌精修房屋（20261024 保护令页）正则取 head/nav/footer + deepcopy 覆写 JSON-LD；md→HTML 保留原文落款含电话、丢弃 --- 分隔线与表格分隔行；无封面页用 PIL 生成 1200x630 品牌标题卡入库；六联判据复跑：pharma 页 stars 属专利号掩码（2005******329.6）非 markdown 泄漏，en/fr i18n 页 ld=1 为 i18n 房屋常态，均非缺陷",
 "result":"PASS",
}
new=collections.OrderedDict()
for k in tpl.keys():
    new[k]=vals.get(k, tpl.get(k,""))
d.append(new)
open(p,"w",encoding="utf-8").write(json.dumps(log,ensure_ascii=False,indent=1)+"\n")
print("deploys",len(d))
print(subprocess.run(["git","-C",ROOT,"diff","--stat","--","site-inbox/deploy-log.json"],capture_output=True,text=True).stdout)
