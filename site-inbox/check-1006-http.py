#!/usr/bin/env python3
"""SiteOps 每日核心页面 HTTP 状态检查 — 瞬断重试3次取终态"""
import subprocess, time, json, sys

URLS = [
    "https://najieip.com",
    "https://najieip.com/mili/",
    "https://najieip.com/najie/",
    "https://najieip.com/blog/",
    "https://najieip.com/sitemap.xml",
    "https://najieip.com/llms.txt",
]

def head(url):
    try:
        r = subprocess.run(["curl", "-sI", "-L", "-o", "/dev/null",
                            "-w", "%{http_code}", "--max-time", "20", url],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return "000"

results = {}
for u in URLS:
    code = head(u)
    if code != "200":
        for _ in range(2):
            time.sleep(2.5)
            code = head(u)
            if code == "200":
                break
    results[u] = code
    print(f"{code}  {u}")

bad = {k: v for k, v in results.items() if v != "200"}
print("---")
print(json.dumps({"ok": len(bad) == 0, "bad": bad}, ensure_ascii=False))
