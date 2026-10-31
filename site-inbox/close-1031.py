#!/usr/bin/env python3
"""articles.json guard apply + sitemap presence + aipunajie dead-card cleanup."""
import os, re, subprocess, sys, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
APPLY = "--apply" in sys.argv

def sh(cmd, cwd=REPO, timeout=180):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "").strip(), (r.stderr or "").strip(), r.returncode

print("=== GUARD ===")
out, err, rc = sh("python3 site-inbox/guard-0918-articles-json.py " + ("--apply" if APPLY else "--check"))
print("rc=", rc); print((out or err)[-1200:])

print("\n=== SITEMAP presence ===")
sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
for slug in ("20261031-najie-specialized-sme-patent-screen", "20261031-mili-ai-product-image-review-tool-neutrality",
             "20261031-mili-mofcom-trade-secret-sanctions"):
    hits = re.findall(r"<loc>([^<]*" + re.escape(slug) + r"[^<]*)</loc>", sm)
    print(slug, "->", hits)

print("\n=== aipunajie dead cards ===")
p = os.path.join(REPO, "aipunajie/blog/index.html")
t = open(p, encoding="utf-8").read()
missing = ['20260723-weituo-chuangzuo-banquan-xieyi-bi-keng.html', 'ai-ip-compliance-redline-20260726.html',
           'wipo-ai-ip-dialogue-20260725.html', 'wipo-free-databases-20260726.html', '觅理加盟-创始合伙人亲述-20260719.html']
dead = []
for mb in missing:
    live, _, _ = sh(f'curl -sI -o /dev/null -w "%{{http_code}}" -A "{UA}" -m 20 "https://najieip.com/aipunajie/blog/{mb}"', timeout=40)
    exists_local = os.path.exists(os.path.join(REPO, "aipunajie/blog", mb))
    print(f"{live}  local={exists_local}  {mb}")
    if live.strip() != "200" and not exists_local:
        dead.append(mb)

if dead:
    newt = t
    removed = 0
    retargeted = 0
    for mb in dead:
        # if the same file exists under another brand dir, retarget instead of removing
        alt = [b for b in ("mili", "najie", "blog") if os.path.exists(os.path.join(REPO, b, "blog", mb.replace(".html", ".html")))]
        if alt:
            newt = newt.replace('href="./' + mb + '"', f'href="/{alt[0]}/blog/{mb}"')
            retargeted += 1
            print(f"RETARGETED {mb} -> /{alt[0]}/blog/")
            continue
        # locate card containing this href via depth pairing
        idx = newt.find(mb)
        if idx == -1:
            continue
        start = newt.rfind('<div class="article-card">', 0, idx)
        if start == -1:
            start = newt.rfind("<div", 0, idx)
        # find end by depth scan from start
        i, depth, end = start, 0, None
        while i < len(newt):
            no = newt.find("<div", i + 1); nc = newt.find("</div>", i + 1)
            if nc == -1: break
            if no != -1 and no < nc:
                depth += 1; i = no + 4
            else:
                if depth == 0:
                    end = nc + len("</div>"); break
                depth -= 1; i = nc + 5
        if not end:
            print("could not bound card for", mb); continue
        blk = newt[start:end]
        # trim trailing separator
        newt = newt[:start] + newt[end:]
        removed += 1
        print(f"REMOVED dead card ({len(blk)}B): {mb}")
    print("removed:", removed, "cards; balance div:", newt.count("<div") - newt.count("</div>"), "vs old", t.count("<div") - t.count("</div>"))
    assert newt.count("<div") - newt.count("</div>") == t.count("<div") - t.count("</div>"), "div imbalance"
    if APPLY and removed:
        open(p, "w", encoding="utf-8").write(newt)
        print("WROTE aipunajie index")
else:
    print("no dead cards")
