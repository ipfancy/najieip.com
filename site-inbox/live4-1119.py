#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, json, time

for i in range(4):
    r = subprocess.run(["curl", "-s", "--max-time", "60", "-A", "Mozilla/5.0",
                        f"https://najieip.com/articles.json?cb={int(time.time())}{i}"],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        a = d if isinstance(d, list) else d.get("articles", [])
        print(f"try{i+1}: OK live_articles={len(a)} top1={a[0].get('url')}")
        break
    except Exception:
        print(f"try{i+1}: fail bytes={len(r.stdout)}")
        time.sleep(4)
