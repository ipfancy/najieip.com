#!/usr/bin/env python3
"""SiteOps 1007: core page HTTP status check (UA required, Cloudflare 403 otherwise)."""
import subprocess, sys, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
URLS = [
    "https://najieip.com",
    "https://najieip.com/mili/",
    "https://najieip.com/najie/",
    "https://najieip.com/blog/",
    "https://najieip.com/sitemap.xml",
    "https://najieip.com/llms.txt",
    "https://najieip.com/en/",
    "https://najieip.com/fr/",
    "https://najieip.com/mili/blog/",
    "https://najieip.com/najie/blog/",
]


def code(u):
    p = subprocess.run(
        ["curl", "-sI", "-A", UA, "-o", "/dev/null", "-w", "%{http_code}", "-L",
         "--max-time", "25", u],
        capture_output=True, text=True)
    return (p.stdout or "000").strip()


def main():
    bad = []
    for u in URLS:
        c = code(u)
        if c != "200":                     # single non-200 -> retry up to 2 more times
            for _ in range(2):
                time.sleep(2)
                c = code(u)
                if c == "200":
                    break
        print(f"{c}  {u}")
        if c != "200":
            bad.append((c, u))
    print("---")
    print("FAILURES: " + (str(bad) if bad else "none"))


if __name__ == "__main__":
    main()
