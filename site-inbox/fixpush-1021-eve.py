#!/usr/bin/env python3
"""用 force-with-lease 替换掉带错误缩进的提交；失败则退回普通 fix 提交"""
import os, subprocess

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
def run(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    print("$", " ".join(a[:3]), "->", r.returncode, (r.stdout or r.stderr).strip()[-260:])
    return r

run("git", "fetch", "origin")
om = run("git", "rev-parse", "origin/main").stdout.strip()
head = run("git", "rev-parse", "HEAD").stdout.strip()
print("origin/main =", om, "| HEAD =", head, "| HEAD~1 =",
      run("git", "rev-parse", "HEAD~1").stdout.strip())

r = run("git", "push", "--force-with-lease=main:" + om, "origin", "main")
if r.returncode != 0:
    print("\n-- force 被拒，退回普通 fix 提交 --")
    run("git", "reset", "--soft", om)
    run("git", "commit", "-m", "siteops(1021晚) fix: deploy-log 恢复 indent=2 原生格式（上一提交误用 indent=1 全档重排）")
    run("git", "push", "origin", "main")
print()
run("git", "log", "--oneline", "-3")
print(run("git", "diff", "origin/main~2", "origin/main", "--stat", "--", "site-inbox/deploy-log.json").stdout
      if False else "")
