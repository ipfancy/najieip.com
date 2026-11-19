#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, json, time

UA = "Mozilla/5.0"


def code(u):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "35", "-A", UA, u],
                       capture_output=True, text=True)
    return r.stdout.strip()


for u in ["https://najieip.com/", "https://najieip.com/mili/",
          "https://najieip.com/img/20261119-mili-tv-box-backdoor-four-layers.png"]:
    c = code(u) if "json" not in u else ""
    if c in ("000", ""):
        c = code(u)
    print(f"{c} {u}")

r = subprocess.run(["curl", "-s", "--max-time", "60", "-A", UA,
                    f"https://najieip.com/articles.json?cb={int(time.time())}"],
                   capture_output=True, text=True)
try:
    d = json.loads(r.stdout)
    a = d if isinstance(d, list) else d.get("articles", [])
    print("live_articles =", len(a))
    print("top1 =", a[0].get("url"))
except Exception as e:
    print("ERR", e, len(r.stdout))
