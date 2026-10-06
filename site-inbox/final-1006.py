#!/usr/bin/env python3
"""1006 终验：curl 线上验证 + deploy-log 修正 + 日报"""
import os, json, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def curl(args):
    r = subprocess.run(["curl"] + args, capture_output=True, text=True, timeout=60)
    return r.stdout

def status(url):
    return curl(["-sI", "-L", "-A", UA, "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "25", url]).strip()

PAGES = [
    "/", "/mili/", "/najie/", "/blog/", "/sitemap.xml", "/llms.txt",
    "/mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
    "/mili/blog/20261005-mili-gas-supply-cutoff-justification.html",
    "/mili/blog/20261004-mili-gas-deviation-settlement-account.html",
    "/mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
    "/najie/blog/20261005-patent-annual-fee-ledger-5-signals.html",
    "/najie/blog/20261005-trademark-law-2027-implementing-rules.html",
    "/najie/blog/20261003-trademark-invalidated-500w.html",
    "/mili/blog/", 
]
print("=== 线上 HTTP ===")
bad = []
for rel in PAGES:
    c = status("https://najieip.com" + rel)
    if c != "200":
        c = status("https://najieip.com" + rel)
    print(f"  {c}  {rel}")
    if c != "200":
        bad.append(rel)

print("\n=== 精修页内容核验（raw，绕 CF 缓存） ===")
raw_bad = []
for rel in PAGES[6:]:
    d = curl(["-s", "-A", UA, "--max-time", "30", "https://raw.githubusercontent.com/ipfancy/najieip.com/main" + rel])
    ld = d.count("application/ld+json")
    og = "og:image" in d
    st = d.count("**")
    ok = (ld >= 2 and og and st == 0) if rel.endswith(".html") and "blog/" in rel else True
    if rel.endswith(".html") and "blog/" in rel and not ok:
        raw_bad.append(rel)
    print(f"  ld={ld} og:image={og} **={st} bytes={len(d.encode())} {'OK' if ok else 'FAIL'} {rel}")

# 索引卡线上确认
for rel, needle in [("/mili/blog/", "20261006-mili-gas-post-judgment-six-checklist"),
                    ("/blog/", "shuju-chanquan-dengji-2026"),
                    ("/blog/", "jishu-hetong-zhuanli-guishu-2026"),
                    ("/blog/", "20261006-mili-gas-post-judgment-six-checklist")]:
    d = curl(["-s", "-A", UA, "--cache", "no-cache", "--max-time", "30", "https://raw.githubusercontent.com/ipfancy/najieip.com/main" + rel + "index.html"])
    print(f"  索引 {rel} 含 {needle}: {needle in d}")

# deploy-log entry 91 修正
p = "site-inbox/deploy-log.json"
log = json.load(open(p, encoding="utf-8"))
e = log["deploys"][-1]
e["agent"] = "Hermes Agent(SiteOps)·每日运营"
e["round"] = "每日运营（10-06）：上游裸发布页精修 + 索引补卡 + articles.json 守卫"
e["action"] = ("7 篇上游裸发布页精修（补 JSON-LD Article/BreadcrumbList、og:image/og:site_name、"
               "description 去标题复读、裸 markdown 表格转 table、** 转 strong、缺 h1 回填）；"
               "索引补卡：mili/blog/index 1 张 + 主索引 3 张（20261006 新文、shuju-chanquan-dengji-2026、"
               "jishu-hetong-zhuanli-guishu-2026）；articles.json 守卫第 10 次隔离 224→174；"
               "结构终验 11/11 PASS，push 2540072..67c89d6")
json.dump(log, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\ndeploy-log entry 91 已修正")

# 日报
rep = os.path.expanduser("~/wiki/digital-employees/reports")
os.makedirs(rep, exist_ok=True)
rp = f"{rep}/siteops-daily-20261006.md"
open(rp, "w", encoding="utf-8").write(f"""# SiteOps 日报 — 2026-10-06

## 核心页面
13 项线上探测 → 非 200：{len(bad)} （{', '.join(bad) if bad else '无'}）

## 修复（上游裸发布页 第5批）
7 篇：mili 4（20261006 六条清单 / 20261005 停供正当性 / 20261004 偏差结算 / bambu FTO）
+ najie 3（20261005 年费5信号 / 20261005 商标法2027 / 20261003 商标无效500万）
- 补 JSON-LD（Article + BreadcrumbList），json.loads 全通
- 补 og:image / og:site_name / og:locale / twitter:title+image（summary → summary_large_image）
- description 去标题复读，改用 md 源首段（274-300 字符，中文引号转 “”）
- 裸 markdown 表格 3 张转 <table>；** 强调 13 处转 <strong>；缺 h1 回填 2 篇
- 字节：7143→12724 / 6971→11984 / 6940→11540 / 6059→10836 / 5629→10483 / 8602→10893 / 6347→11464

## 索引
mili/blog/index +1 卡（108）；主索引 +3 卡（201）；div 深度 0；日期降序插位

## articles.json
守卫第 10 次隔离 224 → 174（50 条无页面条目），首页 slice(0,6) 全部有页面

## 未处理（下一轮）
- en/blog 与 fr/blog 的 20261005 商标法 2027 页：缺 JSON-LD / og:image / twitter 卡（i18n 房屋待确认）
- /najie/blog/cnptes-three-layer-architecture-diagram.html：架构图页，按 09-23 口径不入主索引
""")
print("日报:", rp)

# 提交收尾
subprocess.run("git add -A", shell=True)
r = subprocess.run('git commit -q -m "log(1006): 修正 deploy-log entry 91 描述 + 日报"', shell=True, capture_output=True, text=True)
print("commit:", r.returncode, (r.stdout + r.stderr)[:150])
r = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
print("push:", r.returncode, (r.stdout + r.stderr)[-200:])
r = subprocess.run("git log --oneline -1", shell=True, capture_output=True, text=True)
print("HEAD:", r.stdout.strip())
print("线上非200:", bad, "| raw 未达标:", raw_bad)
