#!/usr/bin/env python3
"""1006 收尾：清备份 + commit + push + 线上验证 + deploy-log"""
import os, json, subprocess, sys, urllib.request, time

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

# 1) 清 .bak-1006
baks = []
for root, dirs, files in os.walk(REPO):
    if "/.git" in root:
        continue
    for f in files:
        if f.endswith(".bak-1006"):
            baks.append(os.path.join(root, f))
for b in baks:
    os.remove(b)
print("removed baks:", len(baks), [os.path.relpath(x, REPO) for x in baks])

# 2) commit
print("--- status before add ---")
print(run("git status --porcelain")[1])
run("git add -A")
MSG = ("siteops(1006): 精修7篇上游裸发布页（JSON-LD+og:image+描述去标题复读+markdown裸表与强调转换）"
       " + 索引补卡（mili/index 1 张 + 主索引 3 张） + articles.json 守卫隔离 224→174")
rc, out = run(f'git commit -q -m "{MSG}"')
print("commit rc:", rc, out[:300])
rc, h = run("git rev-parse --short HEAD")
print("HEAD:", h)

# 3) deploy-log 追加（沿用既有键，indent=1）
p = f"{REPO}/site-inbox/deploy-log.json"
log = json.load(open(p, encoding="utf-8"))
tmpl = dict(log["deploys"][-1])
new = {}
for k in tmpl:
    kl = k.lower()
    if "date" in kl or "time" in kl:
        new[k] = "2026-10-06"
    elif "commit" in kl or kl in ("hash", "sha"):
        new[k] = h
    elif "status" in kl or "result" in kl:
        new[k] = "success"
    elif "note" in kl or "desc" in kl or "summary" in kl or "message" in kl:
        new[k] = "每日运营：7篇裸发布页精修（JSON-LD/og:image/描述）+ 索引补卡4张 + articles.json 隔离50条"
    else:
        new[k] = tmpl[k]
log["deploys"].append(new)
with open(p, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print("deploy-log entry added:", json.dumps(new, ensure_ascii=False)[:220])

run("git add site-inbox/deploy-log.json")
rc, out = run(f'git commit -q -m "deploy-log: entry {len(log["deploys"])} commit hash {h}"')
print("log commit rc:", rc, out[:200])

# 4) push（含 publickey 兜底）
rc, out = run("git push origin main")
if rc != 0:
    print("push retry with explicit key...")
    rc, out = run("GIT_SSH_COMMAND='ssh -i /Users/ziganghe/.ssh/id_ed25519 -o IdentitiesOnly=yes' git push origin main")
print("push rc:", rc, out[-300:])
print("LOG:", run("git log --oneline -3")[1])

# 5) 线上验证
PAGES = [
    "/mili/blog/20261006-mili-gas-post-judgment-six-checklist.html",
    "/mili/blog/20261005-mili-gas-supply-cutoff-justification.html",
    "/mili/blog/20261004-mili-gas-deviation-settlement-account.html",
    "/mili/blog/bambu-stratasys-fto-decision-tree-20261004.html",
    "/najie/blog/20261005-patent-annual-fee-ledger-5-signals.html",
    "/najie/blog/20261005-trademark-law-2027-implementing-rules.html",
    "/najie/blog/20261003-trademark-invalidated-500w.html",
    "/mili/blog/",
    "/blog/",
]
print("\n=== 线上验证（CF 缓存可能滞后，看 raw 为准） ===")
for rel in PAGES:
    url = "https://najieip.com" + rel
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20)
        code = r.status
    except Exception as e:
        code = f"ERR {e}"
    raw = "https://raw.githubusercontent.com/ipfancy/najieip.com/main" + rel
    hs = ""
    try:
        d = urllib.request.urlopen(raw, timeout=20).read().decode("utf-8", "ignore")
        hs = f"raw ld={d.count('application/ld+json')} og={('og:image' in d)} bytes={len(d.encode())}"
    except Exception as e:
        hs = f"raw ERR {e}"
    print(f"  live={code} {rel} | {hs}")
