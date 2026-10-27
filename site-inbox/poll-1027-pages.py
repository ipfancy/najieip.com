#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Poll GitHub Pages build status for a given run id until completed (max ~6 min)."""
import json, subprocess, time, sys

SHA = sys.argv[1] if len(sys.argv) > 1 else "60c789b"
deadline = time.time() + 360
last = None
while time.time() < deadline:
    out = subprocess.run(["curl", "-s",
                          "https://api.github.com/repos/ipfancy/najieip.com/actions/runs?per_page=4"],
                         capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
    except Exception:
        time.sleep(10); continue
    for r in d.get("workflow_runs", []):
        if r["head_sha"].startswith(SHA):
            last = (r["id"], r["status"], r["conclusion"], r["updated_at"])
            print(r["id"], r["status"], r["conclusion"], r["updated_at"], flush=True)
            if r["status"] == "completed":
                print("FINAL:", r["status"], r["conclusion"])
                sys.exit(0)
            break
    else:
        print("run for", SHA, "not found yet", flush=True)
    time.sleep(20)
print("TIMEOUT, last seen:", last)
