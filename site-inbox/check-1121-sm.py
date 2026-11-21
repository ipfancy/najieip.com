import re, os
REPO = os.path.expanduser("~/wiki/najieip-verify")
sm = open(os.path.join(REPO, "sitemap.xml"), encoding="utf-8").read()
loc = re.findall(r"<loc>(.*?)</loc>", sm)
print("sitemap loc", len(loc))
for s in ("20261121-mili-divorce-game-account-88w", "20261121-mili-patent-agency-revoked-34",
          "20261121-najie-sep-administrative-ruling-37-articles"):
    hit = [u for u in loc if s in u]
    print("  sm", s[:46], hit or "MISSING")
feed = open(os.path.join(REPO, "feed.xml"), encoding="utf-8").read()
items = re.findall(r"<item>(.*?)</item>", feed, re.S)
print("feed items", len(items))
for s in ("20261121-mili-divorce-game-account-88w", "20261121-mili-patent-agency-revoked-34",
          "20261121-najie-sep-administrative-ruling-37-articles"):
    print("  feed", s[:46], any(s in i for i in items))
# 首页曝光结构提示
print("sitemap lastmod missing", len([b for b in re.findall(r"<url>(.*?)</url>", sm, re.S) if "<lastmod>" not in b]))
