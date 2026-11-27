#!/usr/bin/env python3
"""单条全量抓取：秘塔「食品委托生产合同 商标许可 要补哪些条款」——验证内容缺口"""
import importlib.util, json, sys

spec = importlib.util.spec_from_file_location(
    "ms", "/Users/ziganghe/wiki/najieip-verify/site-inbox/geo-run-1128-metaso.py")
ms = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(ms)

# 直接复用内部函数，但取全文
import time, urllib.parse, websocket

Q = "食品委托生产合同 商标许可 要补哪些条款"
tab = ms.get_page()
ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60)
mid = 1
ms.cdp(ws, mid, "Page.navigate", {"url": "https://metaso.cn/?q=" + urllib.parse.quote(Q)})
mid += 1
prev, stable, t = "", 0, ""
for _ in range(16):
    time.sleep(5)
    t = ms.ev(ws, mid, "document.body ? document.body.innerText : ''") or ""
    mid += 1
    if len(t) > 300 and t == prev:
        stable += 1
    else:
        stable = 0
    prev = t
    if stable >= 2:
        break
ws.close()
open("/Users/ziganghe/wiki/najieip-verify/site-inbox/geo-metaso-1128-full-0135q3.txt", "w").write(t)
print("LEN", len(t))
for p in ["55条", "五十五", "解除", "多重委托", "再委托", "情形8", "情形7", "去标", "模具", "30天", "10个工作日", "著作权", "Know-how", "秘方"]:
    print(p, p in t)
print("TAIL:", t[-700:].replace("\n", " | "))
