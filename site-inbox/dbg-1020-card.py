import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
key = "customs-ip-detention-30-day-timeline-20261018.html"
print("found at", t.find(key), "cards", t.count('<div class="article-card">'))
idx = t.find(key)
start = t.rfind('<div class="article-card">', 0, idx)
print("start", start)
i = start + len('<div class="article-card">')
depth = 1
ends = []
for m in re.finditer(r"<div\b|</div>", t[i:]):
    depth += 1 if m.group(0).startswith("<div") else -1
    if depth == 0:
        ends.append(i + m.end())
        break
print("end", ends[:1], "final depth", depth)
print(repr(t[start:start+120]))
