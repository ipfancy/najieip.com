import json, os, subprocess
REPO = os.path.expanduser('~/wiki/najieip-verify')
PATH = os.path.join(REPO, 'site-inbox/deploy-log.json')
raw = open(PATH, encoding='utf-8').read()
d = json.loads(raw)
last = d['deploys'][-1]
KEYS = list(last.keys())
commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip()

entry = {
    'date': '2026-10-29',
    'time': '22:05',
    'agent': 'SiteOps',
    'round': 'daily-20261029',
    'commit': commit,
    'action': '每日运营：核心 6 页 200；补建「已发布但站点无页」文章 mili/blog/20261029-mili-ai-seeding-notes-case.html（AI代写种草笔记不正当竞争案，.published.json 已发布、三品牌目录零页）——按 10-28 同日同品牌精修页取房屋（外链 /style.css）+ md→HTML（6 h2 路标 + 1 表 + 1 blockquote + **→strong + 中文引号），补 Article+BreadcrumbList JSON-LD、og/twitter 全量、真摘要 127 字、封面 94KB 入库；mili 索引 136→137、主索引 244→245（10-29 置顶）；articles.json 264→265（首页第 1 曝光位）；清理 site-inbox 上游陈旧副本 1 件；articles.json 守卫 265/217（48 条 /articles/ 301 重定向页为昨日刻意整改，白名单未覆盖，不隔离）',
    'files_changed': ['mili/blog/20261029-mili-ai-seeding-notes-case.html', 'img/20261029-mili-ai-seeding-notes-case.png', 'mili/blog/index.html', 'blog/index.html', 'articles.json', 'sitemap.xml', 'site-inbox/gen-1029-page.py', 'site-inbox/verify-1029-structure.py', 'site-inbox/deploy-log.json'],
    'cards_added': 2,
    'attribution': {'mili': 1, 'main': 1},
    'verification': {'core_pages_200': '6/6', 'h1': 1, 'ld_json': 2, 'og_image': True, 'desc_len': 127, 'desc_dup_title': False, 'stars': 0, 'index_hits': 2, 'div_balance': 'OK', 'sitemap_loc': None, 'live_check': None},
    'defects_found': ['upstream: 文章已发布但三品牌目录零页（wechat-distribute site 渠道静默失败）', 'articles.json 48 条 /articles/ 301 重定向条目不在守卫白名单（昨日刻意整改，非死链）'],
    'notes': '房屋模板 = mili/blog/20261028-mili-pregnancy-disguised-dismissal-evidence.html；md 源逐段核验仅 3 处结构性差异（h1 行/表格/blockquote 渲染）；insert_card 保留 div 配平断言',
    'result': 'PASS',
}
assert list(entry.keys()) == KEYS, (list(entry.keys()), KEYS)

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL), repr(r[-20:])
head = r[:-len(TAIL)] + "\n  }"
lines = ",\n  {\n" + ",\n".join('   %s: %s' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in entry.items()) + "\n  }"
out = head + lines + "\n ]\n}"
json.loads(out)
open(PATH, 'w', encoding='utf-8').write(out)
print('appended, entries', len(json.loads(out)['deploys']))
