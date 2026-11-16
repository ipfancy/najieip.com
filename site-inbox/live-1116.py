#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 1116 线上终验"""
import subprocess, json, time, re, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SLUG = "20261116-mili-protection-order-72hours"
NAJ = "20261116-najie-ai-image-copyright-three-layers"
fails = []

def curl(url, head=False, tries=3):
    for _ in range(tries):
        cmd = ["curl", "-s", "-A", UA, "--max-time", "60"]
        if head:
            cmd += ["-I", "-o", "/dev/null", "-w", "%{http_code}"]
        cmd.append(url)
        r = subprocess.run(cmd, capture_output=True)
        out = r.stdout.decode("utf-8", "replace")
        if head:
            if out.strip() in ("200", "301", "302"):
                return out.strip()
        else:
            if len(out) > 500:
                return out
        time.sleep(4)
    return out if not head else out.strip()

def chk(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + str(detail) if detail else ""))
    if not cond:
        fails.append(name)

# 1 页面 HTTP
for u in [f"https://najieip.com/mili/blog/{SLUG}.html",
          f"https://najieip.com/najie/blog/{NAJ}.html",
          f"https://najieip.com/img/{SLUG}.png",
          "https://najieip.com/blog/", "https://najieip.com/mili/blog/",
          "https://najieip.com/najie/blog/", "https://najieip.com/sitemap.xml",
          "https://najieip.com/llms.txt"]:
    c = curl(u, head=True)
    chk("HTTP " + u.split("najieip.com")[1], c == "200", c)

# 2 保护令页六项
t = curl(f"https://najieip.com/mili/blog/{SLUG}.html?cb={int(time.time())}")
chk("保护令页 h1==1", len(re.findall(r'<h1[\s>]', t)) == 1, len(t.encode()))
chk("保护令页 og:image", 'og:image" content="https://najieip.com/img/' in t or 'og:image" content="https:' in t)
chk("保护令页 tw summary_large_image", "summary_large_image" in t)
chk("保护令页 ld==2", t.count("application/ld+json") == 2, t.count("application/ld+json"))
chk("保护令页 schema.org x2", t.count("https://schema.org") >= 2, t.count("https://schema.org"))
chk("保护令页 无 **", t.count("**") == 0)
chk("保护令页 无 ***", "https://***" not in t)

# 3 主索引卡 HIT
mi = curl(f"https://najieip.com/blog/?cb={int(time.time())}")
chk("主索引 najie AI图卡 HIT", NAJ in mi)
chk("主索引 卡片数>=310", mi.count('<div class="article-card">') >= 310, mi.count('<div class="article-card">'))

# 4 najie 品牌索引卡 HIT
ni = curl(f"https://najieip.com/najie/blog/?cb={int(time.time())}")
chk("najie 索引卡 HIT", NAJ in ni)

# 5 live articles.json
aj = curl(f"https://najieip.com/articles.json?cb={int(time.time())}")
try:
    d = json.loads(aj)
    chk("live articles.json 条数==306", len(d) == 306, len(d))
    chk("live articles.json 含 najie AI图", any(i.get("url", "").endswith(NAJ + ".html") for i in d))
    top6 = [i.get("url") for i in d[:6]]
    chk("live top6 首页曝光位", len(top6) == 6, top6[:2])
except Exception as e:
    chk("live articles.json 可解析", False, str(e))

# 6 sitemap 含两篇
sm = curl(f"https://najieip.com/sitemap.xml?cb={int(time.time())}")
chk("sitemap 含保护令", SLUG in sm)
chk("sitemap 含 najie AI图", NAJ in sm)

print("\nFAILURES:", "NONE" if not fails else fails)
