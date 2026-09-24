#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 线上/本地 diff 归因：确认 Δ367B 仅为 Cloudflare beacon 注入"""
import difflib, urllib.request, os

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20260924-malicious-litigation-supervision"
URL = "https://najieip.com/mili/blog/%s.html" % SLUG
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 siteops"})
live = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
loc = open(os.path.join(REPO, "mili/blog/%s.html" % SLUG), encoding="utf-8").read()
print("Δ bytes:", len(live.encode()) - len(loc.encode()))
d = list(difflib.unified_diff(loc.splitlines(), live.splitlines(), "local", "live", lineterm="", n=1))
print("diff 行数:", len(d))
for line in d[:40]:
    print(line[:200])
extra = [l for l in d if l.startswith("+") and not l.startswith("+++")]
print("\n新增行数:", len(extra))
print("新增行中非 beacon 相关:", [l[:120] for l in extra if "beacon" not in l and "cloudflareinsights" not in l and "cf-beacon" not in l])
