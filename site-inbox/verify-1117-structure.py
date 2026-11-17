import re, os, subprocess
REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261117-mili-dove-ad-role"

def load(path, rev=None):
    if rev:
        return subprocess.check_output(["git", "-C", REPO, "show", "%s:%s" % (rev, path)], text=True)
    return open(os.path.join(REPO, path), encoding="utf-8").read()

for path in ["mili/blog/index.html", "blog/index.html"]:
    base = load(path, "HEAD")
    new = load(path)
    op0, cl0 = base.count("<div"), base.count("</div>")
    op, cl = new.count("<div"), new.count("</div>")
    print("==", path, "cards", base.count('<div class="article-card">'), "->", new.count('<div class="article-card">'))
    print("   div", op0, cl0, "->", op, cl, "delta", op - op0, cl - cl0)
    hits = re.findall(r'<h[23][^>]*><a href="([^"]*)"', new)
    mine = [h for h in hits if SLUG in h]
    print("   card_hrefs", mine)
    from collections import Counter
    dup = [k for k, v in Counter(hits).items() if v > 1]
    print("   dup_hrefs", dup)
    malformed = len(re.findall(r'<div class="article-card">\s*<div class="meta">', new))
    print("   malformed_order", malformed)
    # 卡片深度配平（相对偏差）
    print("   delta_symmetric", (op - op0) == (cl - cl0))
