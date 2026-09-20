import re
t = open('blog/index.html', encoding='utf-8').read()
b = t.find('<body')
i = t.find('<div class="article-card"', b)
print("=== FIRST CARD BLOCK (main) ===")
print(repr(t[i:i+700]))
print()
print("=== 首卡前 200 字符 ===")
print(repr(t[b:b+400]))
print()
# 日期序列前 16
body = t[b:]
dates = re.findall(r'<span class="tag">[^<]*</span>(?:\s*<span class="tag">[^<]*</span>)*\s*(\d{4}-\d{2}-\d{2})', body)
print("dates[:16] =", dates[:16])
