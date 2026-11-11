import re
for p in ('mili/blog/index.html', 'najie/blog/index.html', 'blog/index.html'):
    t = open('/Users/ziganghe/wiki/najieip-verify/' + p, encoding='utf-8').read()
    sts = [m.start() for m in re.finditer(r'<div class="article-card">', t)]
    print('=' * 40, p, 'cards', len(sts))
    print('SAMPLE1:', repr(t[sts[0]:sts[0] + 420]))
    print('SAMPLE2_date_meta:', repr(t[sts[1]:sts[1] + 200]))
    # first 3 hrefs
    for s in sts[:3]:
        m = re.search(r'href="([^"]+)"', t[s:s + 400])
        print('  href', m.group(1) if m else None)
