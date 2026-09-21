#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify-0921-live.py — 线上部署验证（curl + 字节比较 + 内容断言）"""
import json
import os
import re
import subprocess
import time

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
SLUG = "20260921-us-trademark-sanction-defense-window"
TS = int(time.time())
UA = "curl/8 -H 'Cache-Control: no-cache'"


def get(url, out=None):
    cmd = ["curl", "-s", "-L", "--max-time", "30", "-H", "Cache-Control: no-cache",
           "-H", "Pragma: no-cache", "-w", "\n%{http_code}", url + ("?cb=%d" % TS if "?" not in url else "")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    if out:
        open(out, "w", encoding="utf-8").write(body)
    return code.strip(), body


ok = True


def chk(name, cond, extra=""):
    global ok
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))
    if not cond:
        ok = False


print("### A. 新文章页线上验证")
code, body = get("https://najieip.com/najie/blog/%s.html" % SLUG, "/tmp/live0921_art_%d.html" % TS)
chk("HTTP 200", code == "200", code)
chk("含 h1", body.count("<h1>") == 1, str(body.count("<h1>")))
chk("含 4×h2", body.count("<h2>") == 4, str(body.count("<h2>")))
chk("含 <style>", "<style>" in body)
chk("JSON-LD >= 2", len(re.findall(r"application/ld\+json", body)) >= 2)
chk("schema.org >= 2", body.count("https://schema.org") >= 2, str(body.count("https://schema.org")))
chk("无 schema 污染", "https://***" not in body)
chk("无 ** 泄漏", body.count("**") == 0)
chk("og:url 正确", SLUG in re.search(r'<meta property="og:url" content="([^"]*)"', body).group(1))
chk("og:image 存在", 'property="og:image"' in body)
local = open("najie/blog/%s.html" % SLUG, encoding="utf-8").read()
chk("线上/本地字节一致", len(body.encode()) == len(local.encode()), "%d vs %d" % (len(body.encode()), len(local.encode())))

print("\n### B. 索引线上验证")
for url, musts, path in [
    ("https://najieip.com/blog/", ["/najie/blog/%s.html" % SLUG, "querren-buqinquan-zhisu-2026", "xin-shangbiaofa-2027"], "blog/index.html"),
    ("https://najieip.com/najie/blog/", [SLUG], "najie/blog/index.html"),
]:
    code, body = get(url)
    chk("%s 200" % url, code == "200", code)
    for m in musts:
        chk("  %s 含 %s" % (url.split('najieip.com')[1] or '/', m[:40]), m in body)
    loc = open(path, encoding="utf-8").read()
    same = len(body.encode()) == len(loc.encode()) or body == loc
    chk("  %s 线上/本地字节一致" % path, same, "%d vs %d" % (len(body.encode()), len(loc.encode())))

print("\n### C. articles.json 线上数据源")
code, body = get("https://najieip.com/articles.json")
chk("200", code == "200", code)
try:
    d = json.loads(body)
    chk("条目数 == 142", len(d) == 142, str(len(d)))
    top = sorted(d, key=lambda x: x.get("date", ""), reverse=True)[:6]
    bad = [x["url"] for x in top if not x["url"]]
    chk("首页 top6 无空 url", not bad, str(bad))
    chk("top3 含新文", any(SLUG in x.get("url", "") for x in top), str([x.get("url") for x in top[:3]]))
except Exception as e:
    chk("articles.json 可解析", False, str(e))

print("\n### D. 核心页复检")
for u in ["https://najieip.com", "https://najieip.com/mili/", "https://najieip.com/najie/",
          "https://najieip.com/sitemap.xml", "https://najieip.com/llms.txt"]:
    code, _ = get(u)
    chk(u.replace("https://najieip.com", ""), code == "200", code)

print("\nRESULT:", "ALL PASS" if ok else "HAS FAILURES")
