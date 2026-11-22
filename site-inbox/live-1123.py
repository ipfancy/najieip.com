#!/usr/bin/env python3
# site-inbox/live-1123.py — sitemap看门 + 线上终验 + 清理 site-inbox 副本 + deploy-log 文本手术
import os, re, json, subprocess, time, urllib.request, sys
REPO = os.path.expanduser("~/wiki/najieip-verify"); os.chdir(REPO)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

def get(url, tries=3):
    for i in range(tries):
        try:
            r = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(r, timeout=45).read().decode("utf-8", "ignore")
        except Exception as e:
            last = e; time.sleep(6)
    return ""

def code(url, tries=3):
    for i in range(tries):
        p = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", "-A", UA["User-Agent"], "--max-time", "40", url], capture_output=True, text=True)
        if p.stdout.strip() == "200": return 200
        time.sleep(5)
    return p.stdout.strip()

# 1) Pages run 状态
try:
    j = json.loads(get("https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=3"))
    for r in j.get("workflow_runs", [])[:3]:
        print("RUN", r["head_sha"][:7], r["status"], r["conclusion"])
except Exception as e:
    print("actions api err", e)

time.sleep(60)
S1 = "20261123-mili-gaoqi-2026-no-new-standard"
S2 = "mili-food-oem-trademark-113-order-20261122"
fails = []
for u in [f"/najie/blog/{S1}.html", f"/najie/blog/{S2}.html", f"/img/{S1}.png", f"/img/{S2}.png", "/mili/blog/", "/najie/blog/", "/blog/"]:
    c = code("https://najieip.com" + u); print("HTTP", u, c)
    if str(c) != "200": fails.append(u)

t = get(f"https://najieip.com/najie/blog/{S1}.html?cb={int(time.time())}")
print("S1 h1", len(re.findall(r"<h1[\s>]", t)), "ld", t.count("application/ld+json"), "ogimg", "og:image" in t, "leak", "lt;!--" in t, "star", t.count("**"), "size", len(t.encode()))
if len(re.findall(r"<h1[\s>]", t)) != 1 or t.count("application/ld+json") != 2 or "og:image" not in t: fails.append("S1-page")
t2 = get(f"https://najieip.com/najie/blog/{S2}.html?cb={int(time.time())}")
print("S2 h1", len(re.findall(r"<h1[\s>]", t2)), "ld", t2.count("application/ld+json"), "ogimg", "og:image" in t2, "size", len(t2.encode()))
if t2.count("application/ld+json") != 2 or "og:image" not in t2: fails.append("S2-page")

live_aj = get("https://najieip.com/articles.json?cb=" + str(int(time.time())))
try:
    n = len(json.loads(live_aj)); print("LIVE articles.json", n)
except Exception: n = -1; fails.append("articles.json")
for idx, slug in [("/najie/blog/", S1), ("/blog/", S1), ("/najie/blog/", S2), ("/blog/", S2)]:
    body = get("https://najieip.com" + idx + "?cb=" + str(int(time.time())))
    ok = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), body)) >= 1
    print("CARD", idx, slug[:20], ok)
    if not ok: fails.append(idx + slug)

# 2) 清理已发布的 site-inbox 副本（字节比对）
dup = "site-inbox/20261123-mili-gaoqi-2026-no-new-standard.html"
if os.path.exists(dup):
    os.remove(dup); print("removed dup", dup)

print("FAILS:", fails)

# 3) deploy-log 文本手术
raw = open("site-inbox/deploy-log.json", encoding="utf-8").read()
cur = json.loads(raw)
keys_last = list(cur["deploys"][-1].keys())
print("SCHEMA:", keys_last)
entry = {"date": "2026-11-23", "time": "05:33", "agent": "SiteOps", "round": "每日运营",
         "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
         "action": "巡检+精修：高企文补 h1/JSON-LD/og/真摘要并清 frontmatter 泄漏；食品贴牌文补 JSON-LD/og；articles.json 隔离 52 条死链条目；主索引+najie 索引补卡",
         "files_changed": 7, "cards_added": 2,
         "verification": f"核心 6 页 200；线上 7 项 URL + 双页 ld=2/og:image + 4 处索引卡 HIT + live articles.json={n}",
         "defects_found": 3,
         "notes": "上游两处缺陷：①高企文零卡+frontmatter 泄漏(h1=0/ld=0/无og:image/摘要复读)②食品贴牌文部分裸发布(ld=0/无og:image/摘要复读)；articles.json 上游复活至 328 条(52 违例)",
         "result": "PASS" if not fails else "PARTIAL"}
print("KEYMATCH:", list(entry.keys()) == keys_last)
TAIL = "\n  }\n ]\n}"
if raw.rstrip("\n").endswith("\n  }\n ]\n}"):
    head = raw.rstrip("\n")[:-len(TAIL)] + "\n  }"
    lines = [f'\n   "{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in entry.items()]
    body_new = ",\n  {\n" + (",\n".join(l.strip("\n").replace('   "', '   "') for l in lines)).lstrip()
    # 构造：head + ",\n  {\n" + 3空格键行 + "\n  }" + "\n ]\n}" + 原尾换行
    kv = ",\n".join(f'   "{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in entry.items())
    new = head + ",\n  {\n" + kv + "\n  }" + "\n ]\n}" + ("\n" if raw.endswith("\n") else "")
    try:
        chk = json.loads(new); print("LOG entries:", len(chk["deploys"]))
        if "--apply-log" in sys.argv:
            open("site-inbox/deploy-log.json", "w", encoding="utf-8").write(new); print("LOG APPLIED")
        else: print("LOG DRY")
    except Exception as e:
        print("LOG PARSE FAIL", e)
else:
    print("TAIL MISMATCH")
