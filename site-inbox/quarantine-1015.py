#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""articles.json 守卫 --apply + 提交推送 + 复核"""
import os, subprocess, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
G = "site-inbox/guard-0918-articles-json.py"

def run(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, capture_output=True, text=True, env=e)
    print("$ " + " ".join(cmd), "->", p.returncode)
    if p.stdout.strip(): print(p.stdout.strip()[:2500])
    if p.stderr.strip(): print("[err]", p.stderr.strip()[:600])
    return p

run(["python3", G, "--apply"])
run(["python3", G, "--check"])
run(["git", "status", "--porcelain"])
p = run(["git", "commit", "-am", "siteops(1015): articles.json 守卫第16次隔离(239->189，50条无页面条目移入 quarantine)"])
if p.returncode != 0:
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "siteops(1015): articles.json 守卫第16次隔离(239->189) + 巡检脚本"])
p = run(["git", "push", "origin", "main"])
if p.returncode != 0 or "publickey" in (p.stderr or ""):
    run(["git", "push", "origin", "main"],
        env={"GIT_SSH_COMMAND": "ssh -i /Users/ziganghe/.ssh/id_ed25519 -o IdentitiesOnly=yes"})
run(["git", "log", "origin/main", "--oneline", "-2"])
run(["git", "status", "--porcelain"])
