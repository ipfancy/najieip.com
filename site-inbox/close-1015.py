#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理备份 + git add/commit/push（publickey 自动回退）"""
import os, glob, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

for f in glob.glob("mili/blog/*.bak-1015") + glob.glob("blog/*.bak-1015"):
    os.remove(f)
    print("rm", f)

def run(cmd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, env=e)
    print("$ " + " ".join(cmd), "->", p.returncode)
    if p.stdout.strip():
        print(p.stdout.strip()[:2000])
    if p.stderr.strip():
        print("[err]", p.stderr.strip()[:800])
    return p

run(["git", "add", "-A"])
run(["git", "status", "--porcelain"])
p = run(["git", "commit", "-m",
         "siteops(1015): 精修 mili 新页(补 JSON-LD Article+BreadcrumbList / og:image / og:site_name / twitter 卡 / keywords / 真摘要,描述去标题复读) 7,308->11,759B + 双索引补卡(mili 117->118, 主 214->215) + 封面图入库"])
if p.returncode != 0:
    print("commit rc != 0 (可能无变更)")
p = run(["git", "push", "origin", "main"])
if p.returncode != 0 or "publickey" in (p.stderr or ""):
    print(">>> 回退：显式 key 重试")
    run(["git", "push", "origin", "main"], env={
        "GIT_SSH_COMMAND": "ssh -i /Users/ziganghe/.ssh/id_ed25519 -o IdentitiesOnly=yes"})
run(["git", "log", "origin/main", "--oneline", "-3"])
run(["git", "status", "--porcelain"])
