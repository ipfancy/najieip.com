import re, os, json, subprocess
REPO = os.path.expanduser("~/wiki/najieip-verify")
PAGES = ["mili/blog/20261103-mili-unfair-competition-data-scraping.html",
         "mili/blog/20261103-mili-patrol-robot-four-questions.html"]
def zh_len(s): return len(re.findall(r"[\u4e00-\u9fff]", s))
for rel in PAGES:
    p = os.path.join(REPO, rel)
    t = open(p, encoding="utf-8").read()
    slug = os.path.basename(rel)[:-5]
    desc = re.search(r'<meta name="description" content="(.*?)">', t, re.S)
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    ldok = 0
    for b in ld:
        try: json.loads(b); ldok += 1
        except Exception as e: print("  LD-BAD:", e)
    body = t[t.find("<body"):]
    stars = len(re.findall(r"[0-9*]\*\*", body))
    bl = len(re.findall(r"<p>\s*\|", body))
    d = desc.group(1) if desc else ""
    ti = title.group(1) if title else ""
    print(f"== {rel}")
    print(f"  size={os.path.getsize(p)} h1={len(h1)} h2={t.count('<h2')} ld={len(ld)}(ok={ldok})")
    print(f"  og:image={'og:image' in t} twitter:title={'twitter:title' in t} kw={'name=\"keywords\"' in t} site_name={'og:site_name' in t}")
    print(f"  desc_len={len(d)} desc_eq_title={d.strip()==ti.strip()} stars={stars} baretable={bl}")
    print(f"  canonical={re.search(r'rel=.canonical. href=.([^\\\"]+)', t).group(1) if re.search(r'rel=.canonical. href=.([^\\\"]+)', t) else None}")
print("--- INDEX CARDS ---")
for idx in ["blog/index.html","mili/blog/index.html","najie/blog/index.html"]:
    t = open(os.path.join(REPO, idx), encoding="utf-8").read()
    for slug in ["20261103-mili-unfair-competition-data-scraping","20261103-mili-patrol-robot-four-questions"]:
        n = len(re.findall(r'<h[23][^>]*><a href="[^"]*'+slug, t))
        print(f"  {idx}: {slug} cards={n}")
print("--- ARTICLES.JSON top6 ---")
aj = json.load(open(os.path.join(REPO,"articles.json"), encoding="utf-8"))
for a in aj[:6]:
    u = a.get("url") or a.get("link") or ""
    f = os.path.join(REPO, u.lstrip("/"))
    print("  ", a.get("date"), u, "FILE" if os.path.exists(f) else "MISSING")
print("  total:", len(aj))
