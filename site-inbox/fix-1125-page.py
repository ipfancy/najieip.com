#!/usr/bin/env python3
"""修复 11-25 mili AI融脸页：补 og:image / og:site_name / keywords / twitter 四卡 + 真摘要（去标题复读）"""
import re, os, shutil

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261125-mili-ai-face-blend-portrait-1019"
PAGE = os.path.join(REPO, "mili/blog", SLUG + ".html")
URL = "https://najieip.com/mili/blog/" + SLUG + ".html"
IMG = "https://najieip.com/img/" + SLUG + ".png"
DESC = ("AI融脸与AI换脸，法院判的结论为什么相反？北京互联网法院首例AI换脸案驳回肖像权主张，只认定个人信息权益，"
        "判赔500元与1500元；而融脸保留辨识度，稳稳落进民法典第1019条。尺子只有一把：普通公众能不能认出你。")

src = os.path.join("/Users/ziganghe/wiki/digital-employees/articles", "cover-" + SLUG + ".png")
dst = os.path.join(REPO, "img", SLUG + ".png")
if os.path.exists(src):
    shutil.copyfile(src, dst)
    print("cover copied:", os.path.getsize(dst), "bytes")
else:
    print("WARN cover not found:", src)

t = open(PAGE, encoding="utf-8").read()
head_end = t.find("</head>")
head, body = t[:head_end], t[head_end:]

# 1) description 换成真摘要
head2 = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="%s">' % DESC, head, count=1)
assert head2 != head, "description not replaced"

# 2) og:description 同步真摘要
head2 = re.sub(r'<meta property="og:description" content="[^"]*">',
               '<meta property="og:description" content="%s">' % DESC, head2, count=1)

# 3) og:image + og:site_name 插到 og:url 之后
anchor = '<meta property="og:url" content="%s">' % URL
assert anchor in head2, "og:url anchor missing"
add = (anchor + '\n'
       '<meta property="og:site_name" content="纳杰觅理">\n'
       '<meta property="og:image" content="%s">\n'
       '<meta property="og:image:width" content="1200">\n'
       '<meta property="og:image:height" content="630">\n'
       '<meta name="keywords" content="AI融脸,AI换脸,民法典第1019条,肖像权,个人信息权益">') % IMG
head2 = head2.replace(anchor, add, 1)

# 4) twitter 四卡（card 升 summary_large_image）
tw_old = '<meta name="twitter:card" content="summary">'
assert tw_old in head2, "twitter:card missing"
tw_new = ('<meta name="twitter:card" content="summary_large_image">\n'
          '<meta name="twitter:title" content="民法典第1019条：AI融脸不是换脸，照样侵权">\n'
          '<meta name="twitter:description" content="%s">\n'
          '<meta name="twitter:image" content="%s">') % (DESC, IMG)
head2 = head2.replace(tw_old, tw_new, 1)

new = head2 + body
open(PAGE, "w", encoding="utf-8").write(new)

# 终验
t2 = open(PAGE, encoding="utf-8").read()
h1 = len(re.findall(r"<h1[\s>]", t2))
ld = len(re.findall(r"application/ld\+json", t2))
desc = re.search(r'<meta name="description" content="([^"]*)"', t2).group(1)
print("h1=%d ld=%d ogimg=%s twitter=%s desc_len=%d desc_eq_title=%s size=%d"
      % (h1, ld, 'property="og:image"' in t2, "summary_large_image" in t2,
         len(desc), desc == "民法典第1019条：AI融脸不是换脸，照样侵权", os.path.getsize(PAGE)))
# 正文文本未改（剥标签后比较）
def txt(s):
    b = s[s.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", " ", b))
print("BODY_UNCHANGED:", txt(t) == txt(t2))
# JSON-LD 自检
import json
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
    json.loads(m)
print("JSONLD_OK")
