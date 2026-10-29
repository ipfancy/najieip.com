import subprocess, time, re, json
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36'
BASE = 'https://najieip.com'
SLUG = '20261029-mili-ai-seeding-notes-case'
fails = []

def get(url, binary=False):
    for i in range(3):
        cmd = ['curl', '-sS', '--max-time', '25', '-A', UA, url]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout if binary else r.stdout.decode('utf-8', 'ignore')
        time.sleep(3)
    return b'' if binary else ''

def status(url):
    for i in range(3):
        r = subprocess.run(['curl', '-sI', '--max-time', '20', '-A', UA, '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True)
        code = r.stdout.strip()
        if code.startswith('2'):
            return code
        time.sleep(3)
    return code

cb = int(time.time())
# 1 page
code = status(BASE + '/mili/blog/%s.html' % SLUG)
print('page status', code)
html = get(BASE + '/mili/blog/%s.html?cb=%d' % (SLUG, cb))
if code != '200':
    fails.append('page not 200: ' + code)
checks = {
    'h1': html.count('<h1') == 1,
    'ld==2': html.count('application/ld+json') == 2,
    'og:image': 'og:image' in html,
    'desc_no_dup': '种草笔记' in html,
    'no_stars': html.count('**') == 0,
    'schema': html.count('https://schema.org') >= 2,
    'len>8000': len(html) > 8000,
}
print('page', json.dumps(checks, ensure_ascii=False), 'len', len(html))
for k, v in checks.items():
    if not v:
        fails.append('page check ' + k)

# 2 img
code = status(BASE + '/img/%s.png' % SLUG)
print('img status', code)
if code != '200':
    fails.append('img ' + code)

# 3 indexes contract
for path, key in [('/mili/blog/', '/%s.html' % SLUG), ('/blog/', '/mili/blog/%s.html' % SLUG)]:
    t = get(BASE + path + '?cb=%d' % cb)
    hit = key in t or SLUG in t
    print('index', path, 'hit', hit, 'cards', t.count('<div class="article-card">'))
    if not hit:
        fails.append('index ' + path)

# 4 sitemap + articles.json live
sm = get(BASE + '/sitemap.xml?cb=%d' % cb)
print('sitemap loc', sm.count('<loc>'), 'has new', SLUG in sm)
if SLUG not in sm:
    fails.append('sitemap missing')
aj = get(BASE + '/articles.json?cb=%d' % cb)
print('live articles.json', len(json.loads(aj)) if aj.startswith('[') else 'ERR')
if SLUG not in aj:
    fails.append('articles.json live missing')

print('FAILS =', fails if fails else 'NONE')
