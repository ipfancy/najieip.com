#!/usr/bin/env python3
"""gather 1009: 打印缺陷页全文 + 模板页房屋部件 + 样本卡"""
import os, re
BASE = os.path.expanduser("~/wiki/najieip-verify")
def load(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

target = os.path.join(BASE, "mili/blog/20261009-mili-ai-short-drama-token-evidence.html")
tmpl = os.path.join(BASE, "mili/blog/20261008-mili-ai-math-solution-copyright.html")

t = load(target)
print("========== TARGET PAGE (%d bytes) ==========" % len(t))
print(t)
print("\n\n========== TEMPLATE HEAD (%s) ==========" % os.path.basename(tmpl))
tt = load(tmpl)
print(tt[:tt.find("<body")])
