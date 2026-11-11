import re, json
p = '/Users/ziganghe/wiki/najieip-verify/mili/blog/20261111-mili-fake-patent-marking-line.html'
t = open(p, encoding='utf-8').read()
print('len', len(t))
for pat in ['<head', '</head>', '<body', '<nav', '</nav>', '<header', '</header>', '<article', '</article>', '<footer', '</footer>', '<style', 'stylesheet', 'ld+json', '<h1', 'class="container', 'beacon']:
    print(pat, [m.start() for m in re.finditer(re.escape(pat), t)][:6])
print('--- LD TYPES ---')
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    try:
        d = json.loads(m.group(1))
        print(type(d).__name__, d.get('@type') if isinstance(d, dict) else [x.get('@type') for x in d])
    except Exception as e:
        print('PARSE FAIL', e)
print('--- HEAD ---')
print(t[:t.find('</head>')])
