import sqlite3, json, datetime

DB = '/Users/ziganghe/wiki/database/content.db'
DATE = '2026-11-14'
db = sqlite3.connect(DB)
c = db.cursor()

# ---- 秘塔 9 条（1 条测试查询 + 8 条批量，均在浏览器内实测）----
metaso = [
 ("ART-2026-0124", "职务发明报酬 按营业利润 5% 怎么算", 0, None,
  "秘塔答：5%并非现行法律规定，出自《职务发明条例（草案）》；现行《专利法实施细则》为营业利润2%（外观0.2%），5%多由企业约定。未提(2024)最高法知民终907号与促进科技成果转化法第45条",
  "答偏/答旧：未见907号案与48018万/20%/1÷6四乘数"),
 ("ART-2026-0120", "抓取别人平台商品数据 罚多少钱 2026", 0, None,
  "秘塔答：行政处罚没收违法所得并处50万–200万，情节特别严重200万–1000万（数据合规口径）；来源为2026数据合规七条高压线、福建市场监管2023典型案例、盗取百万条电商底价数据",
  "未触及我方「镇江53万行政+500万民事两条责任+新反法29条10万–100万」框架"),
 ("ART-2026-0120", "数据搬家软件 一键复制商品 不正当竞争 判赔多少", 0, None,
  "秘塔答：杭州中院两起一键搬店案410万；最高法盗图抄店典型案例；来源为浙江法院十大知识产权案件等",
  "判例不同源：未提镇江案（罚53万+赔500万）"),
 ("ART-2026-0120", "反不正当竞争法 第29条 网络不正当竞争 罚款档次", 0, None,
  "★秘塔答「罚款档次规定在第二十四条，不是第二十九条；第二十九条是民事责任优先」，并引用《反不正当竞争法》2019修正版；来源全为2019年版本",
  "★答旧法：2025-10-15新法已把网络不正当竞争罚则移到第29条（旧版第24条），秘塔仍落在2019版=可争夺引用位"),
 ("ART-2026-0124", "发明人离职了 职务发明报酬还能要吗", 0, None,
  "秘塔答可以要：引《专利法》第15条 + 国知局文件「解除或终止劳动关系后奖励报酬权利不受影响」",
  "方向一致，无907号案号与乘数算法"),
 ("ART-2026-0124", "公司说产品整体亏损 还要付发明人报酬吗", 0, None,
  "秘塔答：整体亏损≠实施专利无营业利润，分「专利产品自身盈利」与「专利产品本身亏损」两种情况；来源为发明人报酬举证责任论文、职务发明奖酬制度探析",
  "★与我方907号判决核心论点高度一致（整体亏损抗辩不成立），但0署名"),
 ("ART-2026-0129", "荷兰 专利突击搜查 出海企业 怎么应对", 0, None,
  "秘塔出2490字荷兰IP执法指南（荷兰专利局RVO、每年约150件刑事程序等）；来源为驻荷兰使馆经商处、对外投资合作国别指南",
  "未提JLR诉比亚迪Ti7案；通用指南型"),
 ("ART-2026-0129", "欧盟外观设计侵权 证据保全 扣押 异议程序", 0, None,
  "秘塔答共同体外观设计条例、三种可不当庭听证的临时措施；来源为条例介绍、展会知识产权指南",
  "未落到荷兰民诉法1019条专章与1019h费用规则"),
 ("ART-2026-0129", "海牙法院 撤销扣押令 先批准后撤销", 0, None,
  "★秘塔确认Ti7案：2026-11-11海牙法院程序性裁定撤销扣押令并要求销毁已封存复制资料，理由「大范围突击取证缺乏充分必要性」+「Ti7尚未在欧盟上市」；来源面板却是俄气资产扣押案等无关页",
  "★吸收时差=1天（文章11-13发布）：事实全对、署名0、来源不相关"),
]

# ---- 元宝 9 条（本地 CDP 9224 + geo-check-yuanbao-verify.py）----
yuanbao = [
 ("ART-2026-0120", "抓取别人平台商品数据 罚多少钱 2026", 0, None,
  "元宝答分行政/民事/刑事三条线，引新反法第13条+第29条：一般10万–100万、情节严重100万–500万；并称2026年一键搬家类案件已罚至…",
  "★答对条号与档次（与我方一致），0署名"),
 ("ART-2026-0120", "数据搬家软件 一键复制商品 不正当竞争 判赔多少", 0, None,
  "元宝答：淘宝/天猫一键搬家案（1.6亿条商品数据）江苏高院二审维持赔偿500万元；搬家大师/上货专家案410万",
  "★金额对（500万）但归给「淘宝/天猫一键搬家案」，未出现镇江公司名与53万行政罚=两条责任框架未被采纳"),
 ("ART-2026-0120", "反不正当竞争法 第29条 网络不正当竞争 罚款档次", 0, None,
  "★元宝答「2025年修订、2025-10-15施行后网络不正当竞争罚则移到第29条，旧版（2017/2019）是第24条，两个版本罚款档次不一样，别混用」",
  "★元宝答对新法条号，秘塔答2019旧条号→同题分化，秘塔侧=可争夺引用位"),
 ("ART-2026-0124", "职务发明报酬 按营业利润 5% 怎么算", 0, None,
  "元宝答即《促进科技成果转化法》第45条第3项：投产后连续3–5年、每年从该项科技成果营业利润提取不低于5%；给出单人分配公式",
  "★与我方文章依据完全一致（秘塔答成草案/2%），0署名"),
 ("ART-2026-0124", "发明人离职了 职务发明报酬还能要吗", 0, None,
  "元宝答能要：奖励（发明4000元/项、实用新型外观1500元/项）+ 报酬两笔钱分开；离职不消灭请求权",
  "方向一致，0署名"),
 ("ART-2026-0124", "公司说产品整体亏损 还要付发明人报酬吗", 1, "yuanbao:video-card",
  "元宝答整体亏损不构成拒付理由，引《专利法》第15条、《促进科技成果转化法》第45条、「最高法院近期案例（2024最高法知民…」，并在答案内以「相关视频」卡展示我方短视频《产品还在亏损-公司却被判付80万-离职发明人的报酬怎么算》（署名：何自刚｜知识产权律师｜纳杰觅理）",
  "★★首次品牌命中：DOM 实证视频卡位于 .ybc-chat-videoBoxV2-bigCard（聊天流内，x=321/1200），非左下角登录头像区；citation_level=indirect（品牌+作者名，非 najieip.com URL）"),
 ("ART-2026-0129", "荷兰 专利突击搜查 出海企业 怎么应对", 0, None,
  "元宝出2728字实务指南：定性为知识产权民事证据保全（bewijsbeslag/inspection/UPC evidence preservation）、现场红线动作、程序战+数据战+谈判战",
  "内容比秘塔深，仍0署名"),
 ("ART-2026-0129", "欧盟外观设计侵权 证据保全 扣押 异议程序", 0, None,
  "元宝按 EUIPO注册后程序 / 成员国侵权诉讼保全扣押 / 海关边境执法三段拆分，并指2026改革后欧盟外观设计无第三方异议",
  "结构比我方更细（属「AI比我方深」档），0署名"),
 ("ART-2026-0129", "海牙法院 撤销扣押令 先批准后撤销", 0, None,
  "★元宝确认为JLR诉比亚迪Ti7案、荷兰海牙地区法院临时救济程序：8月ex parte批准证据扣押、11月11日裁定撤销扣押令",
  "★吸收时差=1天，事实全对，0署名"),
]

def ins(aid, platform, q, found, src, snip, notes):
    c.execute("""INSERT INTO geo_checks
      (article_id, platform, query_text, check_date, found, source_url, rank_position, snippet, citation_level, competitor_found, notes)
      VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
      (aid, platform, q, DATE, found, src, None, snip,
       'indirect' if found else 'none', None, notes))

n0 = c.execute("SELECT count(*) FROM geo_checks").fetchone()[0]
for r in metaso:
    ins(r[0], 'metaso', r[1], r[2], r[3], r[4], r[5])
for r in yuanbao:
    ins(r[0], 'yuanbao', r[1], r[2], r[3], r[4], r[5])
n1 = c.execute("SELECT count(*) FROM geo_checks").fetchone()[0]

# ---- 更新 geo_article_stats ----
for aid in ("ART-2026-0120", "ART-2026-0124", "ART-2026-0129"):
    tc = c.execute("SELECT count(*) FROM geo_checks WHERE article_id=?", (aid,)).fetchone()[0]
    tf = c.execute("SELECT count(*) FROM geo_checks WHERE article_id=? AND found=1", (aid,)).fetchone()[0]
    rate = round(tf / tc, 4) if tc else 0.0
    trend = 'rising' if tf > 0 else 'new'
    best = 'yuanbao' if tf else None
    c.execute("""INSERT INTO geo_article_stats (article_id,total_checks,total_found,citation_rate,best_platform,best_query,last_check_date,trend)
                 VALUES (?,?,?,?,?,?,?,?)
                 ON CONFLICT(article_id) DO UPDATE SET
                   total_checks=excluded.total_checks, total_found=excluded.total_found,
                   citation_rate=excluded.citation_rate, best_platform=excluded.best_platform,
                   best_query=excluded.best_query, last_check_date=excluded.last_check_date,
                   trend=excluded.trend""",
                (aid, tc, tf, rate, best,
                 "公司说产品整体亏损 还要付发明人报酬吗" if tf else None, DATE, trend))
    print(aid, "checks", tc, "found", tf, "rate", rate)

db.commit()
cum = c.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao')").fetchone()[0]
cumf = c.execute("SELECT count(*) FROM geo_checks WHERE platform IN ('metaso','yuanbao') AND found=1").fetchone()[0]
print("geo_checks rows", n0, "->", n1, "| cumulative metaso+yuanbao =", cum, "found =", cumf)
print("today rows:", c.execute("SELECT platform,count(*),sum(found) FROM geo_checks WHERE check_date=? GROUP BY platform", (DATE,)).fetchall())
db.close()
