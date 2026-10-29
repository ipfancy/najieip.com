import re, os, json, subprocess
REPO = os.path.expanduser('~/wiki/najieip-verify')
SLUG = '20261029-mili-ai-seeding-notes-case'
page = open(os.path.join(REPO, 'mili/blog/%s.html' % SLUG), encoding='utf-8').read()
md = open(os.path.expanduser('~/wiki/digital-employees/articles/%s.md' % SLUG), encoding='utf-8').read()

def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"')
    s = s.replace('*', '').replace('“', '"').replace('”', '"').replace('「', '"').replace('」', '"')
    s = re.sub(r'\|', '', s)
    s = re.sub(r'^\s*#+\s*', '', s, flags=re.M)
    s = re.sub(r'\s+', '', s)
    return s

body = page[page.find('<body'):]
art = body[body.find('<article>'):body.find('</article>')]
art = re.sub(r'<h1>.*?</h1>', ' ', art, flags=re.S)
pcn = norm(art)

mdcut = md.split('\n---\n')[0]
mdn = norm(mdcut)
# md 正文最后一个段落 vs page：逐段对比
md_paras = [p for p in re.split(r'\n(?=## )|\n\n', mdcut) if p.strip()]
print('md paras', len(md_paras), 'page norm len', len(pcn), 'md norm len', len(mdn))
missing = [p[:40] for p in md_paras if norm(p) and norm(p) not in pcn]
print('missing segments:', len(missing))
for x in missing[:6]:
    print('  MISS', x)

# 六联判据
head = page[:page.find('<body')]
desc = re.search(r'<meta name="description" content="([^"]*)"', head).group(1)
title = re.search(r'<title>(.*?)</title>', head, re.S).group(1)
print('h1', art.count('<h1') + page.count('<h1'), 'ld', page.count('application/ld+json'),
      'og:image', 'og:image' in head, 'desc len', len(desc), 'desc_dup_title', desc in title,
      'stars', page.count('**'), 'raw_table', page.count('<p>|'))

# 卡片/索引核验
for f, key in [('mili/blog/index.html', './%s.html' % SLUG), ('blog/index.html', '/mili/blog/%s.html' % SLUG)]:
    t = open(os.path.join(REPO, f), encoding='utf-8').read()
    print(f, 'card occurrences:', t.count(key), 'total cards:', t.count('<div class="article-card">'))

arr = json.load(open(os.path.join(REPO, 'articles.json'), encoding='utf-8'))
print('articles.json', len(arr), 'first:', arr[0]['url'], arr[0]['date'])

# 清理 stale site-inbox 上游副本（页面已精修，副本为发布前原件）
stale = os.path.join(REPO, 'site-inbox/20261028-mili-pregnancy-disguised-dismissal-evidence.html')
if os.path.exists(stale):
    os.remove(stale)
    print('REMOVED stale', os.path.basename(stale))
