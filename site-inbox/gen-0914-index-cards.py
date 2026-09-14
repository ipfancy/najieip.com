#!/usr/bin/env python3
"""SiteOps 0914 补卡：把缺失的最近文章卡片插入 blog/index.html 顶部（幂等）。"""
import re
import sys

IDX = 'blog/index.html'
t = open(IDX, encoding='utf-8').read()

CARDS = [
    # (slug_path, title, tags_html, date, brand_label, excerpt)
    ("/najie/blog/20260914-trademark-rejection-six-reasons.html",
     "商标被驳回的6个原因：六类驳回情形与收到驳回通知后的三步",
     '<span class="tag">商标驳回</span><span class="tag">驳回复审</span><span class="tag">商标检索</span>',
     "2026-09-14", "纳杰知识产权",
     "商标驳回绝大多数不是运气不好，申请之前就能看出来。六类常见驳回情形逐个拆解：缺显著特征（商标法11条）、与在先商标近似（30条）、碰禁用条款（10条）、损害在先权利或抢注（32条）、图样与商品项目选错、主体材料瑕疵。附收到驳回通知书后先做的三件事——算清15天复审期限（34条）、分清全部驳回与部分驳回并考虑分割申请、按使用证据/逐条论证不近似/清除障碍三条路定策略，以及复审不成向北京知识产权法院起诉的30日司法救济。"),
    ("/aipunajie/blog/20260914-patent-invention-vs-utility-model.html",
     "专利选错，白等2年：发明与实用新型怎么选，一条被低估的同日双申请路",
     '<span class="tag">专利选型</span><span class="tag">实用新型</span><span class="tag">同日双申请</span>',
     "2026-09-14", "爱普纳杰专利代理",
     "发明与实用新型选错，是中小企业专利布局里最贵的一个决定：结构改良只报发明，两年后产品迭代两轮、手里一件授权专利都没有。六项差别（保护对象/保护期限/审查方式/创造性标准/授权速度/官费与稳定性）一次讲清，三条选型依据（技术生命周期、是不是命门、要这件专利干什么），以及同日双申请（专利法9条1款）换时间又换稳定性的打法与三个最常见的坑。"),
    ("/najie/blog/20260913-trademark-report-defense-rights.html",
     "商标被举报别慌：这4条程序权利，能救回你的商标",
     '<span class="tag">心机商标</span><span class="tag">商标法第70条</span><span class="tag">程序权利</span>',
     "2026-09-13", "纳杰知识产权",
     "国知局「心机商标」治理专栏累计公示 1782 件依职权宣告无效的商标——注册年限救不了你。被举报后你手里有四条程序权利：申辩、听证、不得因申辩加重处罚、未告知未听取申辩不得下处罚决定。监管时钟：15 个工作日核查、立案后 90 日内决定，真正致命的是「限期改正」逾期不改→撤销注册商标。另附合规举报竞品的三条红线。"),
    ("/najie/blog/20260912-trademark-certificate-not-shield.html",
     "注册证不是挡箭牌！包装一句话，最高罚5倍",
     '<span class="tag">商标使用合规</span><span class="tag">新商标法第56条</span><span class="tag">闲置商标清理</span>',
     "2026-09-12", "纳杰知识产权",
     "新《商标法》第56条把监管重心从\"注册\"搬到\"使用\"：包装、详情页、直播话术里的一句话，最高罚经营额5倍或25万，逾期不改直接撤销商标。今麦郎主动注销10件 vs 壹号土猪复审抗辩——两条路怎么选，附闲置商标清点四问与今天就能做的三件事。"),
    ("/najie/blog/20260912-ai-digital-employee-deployment.html",
     "AI 接管执行后，专业服务只剩 3 件事",
     '<span class="tag">AI原生组织</span><span class="tag">数字员工</span><span class="tag">人机分工</span>',
     "2026-09-12", "纳杰知识产权",
     "凌晨 1:30 余额归零，10 个定时任务同时欠费失败，2 小时后系统自己爬起来补齐当天主文——全程无人碰键盘。把当天所有需要人的节点摊开，只剩五类：出钱、担责、在场、裁量、定义，收敛成 3 件事：当主体、当出资人、当提问者。附「流程按能不能担责分三类」的落地三步法，与三条今天就能做的判断。"),
]

anchor = '<div class="container">\n'
pos = t.find(anchor)
if pos < 0:
    sys.exit('ERROR: container anchor not found')
insert_at = pos + len(anchor)

blocks = []
added = []
for path, title, tags, date, brand, excerpt in CARDS:
    if path in t:
        print('SKIP (already present):', path)
        continue
    blocks.append(
        '  <div class="article-card">\n'
        f'    <h2><a href="{path}">{title}</a></h2>\n'
        f'    <div class="meta">{tags} {date} · {brand}</div>\n'
        f'    <p>{excerpt}</p>\n'
        '  </div>\n'
    )
    added.append(path)

if not blocks:
    print('nothing to add')
    sys.exit(0)

t = t[:insert_at] + ''.join(blocks) + t[insert_at:]
open(IDX, 'w', encoding='utf-8').write(t)

# verify: no duplicate slugs, each added exactly once
for p in added:
    c = t.count(f'href="{p}"')
    print(f'{"OK " if c == 1 else "DUP"} x{c}  {p}')
print('total cards now:', t.count('class="article-card"'))
