import re, os
p = '/Users/ziganghe/wiki/najieip-verify/mili/blog/20261111-mili-fake-patent-marking-line.html'
t = open(p, encoding='utf-8').read()
print('--- NAV ---')
print(t[t.find('<nav'):t.find('</nav>') + 6])
print('--- ARTICLE HEAD 600 ---')
print(t[3038:3640])
print('--- TAIL 5560-END ---')
print(t[5560:])
print('--- IMG DIR (recent) ---')
d = '/Users/ziganghe/wiki/najieip-verify/img'
files = sorted(os.listdir(d), key=lambda f: os.path.getmtime(os.path.join(d, f)), reverse=True)[:8]
for f in files:
    print(os.path.getsize(os.path.join(d, f)), f)
