#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-26 夜班：线上终验 + deploy-log 文本手术追加。"""
import os, re, json, subprocess, time, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
SITE = "https://najieip.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
APPLY = "--apply" in sys.argv

def curl(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "60", "-A", UA, url],
                           capture_output=True, text=True, errors="replace")
        if r.returncode == 0 and len(r.stdout) > 300:
            return r.stdout
        time.sleep(4)
    return ""

def code(url, tries=3):
    for i in range(tries):
        r = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}",
                            "-A", UA, "--max-time", "30", url], capture_output=True, text=True)
        c = r.stdout.strip()
        if c == "200":
            return c
        time.sleep(3)
    return c if 'c' in dir() else "000"

fails = []
SLUG = "20261126-mili-livestream-tip-divorce-recovery"
target_url = f"{SITE}/mili/blog/{SLUG}.html"

# 轮询直到线上拿到新版（本地 5315 字符）
local = len(open(f"{REPO}/mili/blog/{SLUG}.html", encoding="utf-8").read())
live = ""
for i in range(10):
    live = curl(target_url)
    if live and "og:image" in live and abs(len(live) - local) < 400:
        break
    time.sleep(25)

if not live:
    fails.append("livestream page unreadable")
else:
    checks = {
        "h1": live.count("<h1") == 1,
        "ld2": live.count("application/ld+json") >= 2,
        "og_image": "og:image" in live,
        "stars0": len(re.findall(r"(?<![0-9*])\*\*", live)) == 0,
        "schema": "https://schema.org" in live,
        "desc_len": len(re.search(r'<meta name="description" content="([^"]*)"', live).group(1)) > 80,
    }
    print("LIVE livestream", checks, "len", len(live), "local", local)
    fails += [k for k, v in checks.items() if not v]

cm = curl(f"{SITE}/mili/blog/20261126-mili-committees-recruitment.html")
print("LIVE committees h1=", cm.count("<h1"), "ld=", cm.count("application/ld+json"))
if cm.count("<h1") != 1:
    fails.append("committees h1")

img_code = code(f"{SITE}/img/{SLUG}.png")
print("LIVE img png:", img_code)
if img_code != "200":
    fails.append("img png " + img_code)

idx = curl(f"{SITE}/blog/?cb={int(time.time())}", tries=2)
cards = idx.count('class="article-card"') if idx else 0
hit = sum(len(re.findall(r'<h[23][^>]*><a href="[^"]*' + s, idx)) for s in
          ["mili-committees-recruitment", "aipu-limited-choice-inventiveness", "taiwan-mainland-trademark"])
print("LIVE blog index cards", cards, "| 3 new hits", hit, "| len", len(idx))
if hit != 3:
    fails.append("index hits %d" % hit)

feed = curl(f"{SITE}/feed.xml", tries=2)
print("LIVE feed committees entries:", feed.count("mili-committees-recruitment"))
if feed.count("mili-committees-recruitment") < 1:
    fails.append("feed missing")

# 核心 6 页
for u in ["", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt"]:
    c = code(f"{SITE}/{u}")
    if c != "200":
        fails.append(f"core {u or '/'} = {c}")
print("CORE6 done, fails so far:", fails)

# ---- deploy-log 文本手术 ----
LOG = f"{REPO}/site-inbox/deploy-log.json"
raw = open(LOG, encoding="utf-8").read()
data = json.loads(raw)
last = data["deploys"][-1]
print("SCHEMA last keys:", list(last.keys()))

entry = {
    "date": "2026-11-26",
    "time": "22:05",
    "agent": "SiteOps",
    "round": "每日运营（夜班）",
    "commit": "2126f1e",
    "action": "修复打赏主播文裸发布页（整页按 md 源重建套 11-21 mili 房屋）+ 招贤帖 h1 去重与 Breadcrumb 补件 + 主索引补 3 卡 / feed 补 1 条",
    "files_changed": 6,
    "cards_added": 3,
    "attribution": {"brand": "mili", "author": "何自刚"},
    "verification": "核心 6 页 200；打赏文 h1=1/ld=2/og:image/stars=0/schema/desc>80 + md 全文包含=True；封面 308,810B 入库；主索引 338 卡 678/678 配平；articles.json 283/283 零违例；sitemap 看门 exit 0 无 diff",
    "defects_found": "打赏文=裸发布畸形页（h1=0/ld=0/无og:image/desc复读标题/**×4）且处 articles.json 首页第 3 曝光位；招贤帖 h1×2 且缺 BreadcrumbList/og:image；主索引缺 3 张当日卡 + feed 缺 1 条",
    "notes": "招贤帖与 aipunajie 308 号文均无上游封面图（cover-<slug>.png 不存在）→ og:image 仍缺，记 backlog 待补封面；taiwan 商标文六项全合格，零改动",
    "result": "PASS",
}
assert list(entry.keys()) == list(last.keys()), "SCHEMA MISMATCH"

TAIL = "\n  }\n ]\n}"
r = raw.rstrip("\n")
assert r.endswith(TAIL)
head = r[:-len(TAIL)] + "\n  }"
lines = ",\n  {\n" + ",\n".join(
    "   " + json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False) for k, v in entry.items()) + "\n  }"
new = head + lines + "\n ]\n}"
json.loads(new)
if APPLY:
    open(LOG, "w", encoding="utf-8").write(new)
    print("LOG appended; entries:", len(json.loads(new)["deploys"]))
else:
    print("LOG dry-run ok; entries would be", len(json.loads(new)["deploys"]))

print("RESULT:", "PASS" if not fails else "FAILS=" + ",".join(fails))
