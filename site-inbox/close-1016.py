#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-16 收尾：清理 site-inbox 冗余副本（与 HEAD 已发布页字节相同，无待同步内容）"""
import os, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

SI = "site-inbox/customs-ip-filing-3-things-20261016.html"
PUB = "najie/blog/customs-ip-filing-3-things-20261016.html"

head_ver = subprocess.run(["git", "show", "HEAD:%s" % PUB], capture_output=True, text=True).stdout
with open(SI, encoding="utf-8") as f:
    si = f.read()

print("site-inbox 副本 == HEAD 已发布页 :", si == head_ver)
if si == head_ver:
    os.remove(SI)
    print("已删除冗余副本:", SI, "(内容已存在于 git HEAD 的已发布页，零信息损失)")
else:
    print("跳过删除（内容与已发布页不同，保留待人工判断）")
