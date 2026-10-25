import os, sys, re, json, importlib.util
ROOT="/Users/ziganghe/wiki/najieip-verify"
spec=importlib.util.spec_from_file_location("gen1025", os.path.join(ROOT,"site-inbox/gen-1025-pages.py"))
g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

main_index=os.path.join(ROOT,"blog/index.html")
mili_index=os.path.join(ROOT,"mili/blog/index.html")
najie_index=os.path.join(ROOT,"najie/blog/index.html")

def meta_from_brand(index_path, needle):
    t=open(index_path,encoding="utf-8").read()
    m=re.search(r'<h2><a href="[^"]*%s"[^>]*>(.*?)</a></h2>\s*<div class="meta">((?:(?!</div>).)*)</div>\s*<p>(.*?)</p>' % re.escape(needle), t, re.S)
    if not m: return None
    title=m.group(1); meta=m.group(2); desc=m.group(3)
    tags=re.findall(r'<span class="tag">([^<]*)</span>', meta)
    dm=re.search(r'(\d{4}-\d{2}-\d{2}) · ([^<]*)', meta)
    return dict(title=title, tags=tags, date=dm.group(1) if dm else "", desc=desc, site=(dm.group(2) if dm else "").strip())

main_txt=open(main_index,encoding="utf-8").read()
tpl_main=g.card_tpl(main_index,"20261024-mili-personal-safety-protection-order.html")

targets=[("mili/blog/20261025-defendant-info-query-beijing.html", mili_index, "20261025-defendant-info-query-beijing.html"),
         ("najie/blog/20261025-najie-license-filing.html", najie_index, "20261025-najie-license-filing.html")]

added=[]
for url_path, bidx, needle in targets:
    if "/"+url_path in main_txt:
        print("already in main:", url_path); continue
    info=meta_from_brand(bidx, needle)
    if not info:
        print("META NOT FOUND", needle); continue
    card=g.make_card(tpl_main, "/"+url_path, info["title"], info["tags"], info["date"], info["desc"], site_label=info["site"] or "北京觅理律师事务所")
    # unwrap escaped title back (brand card title is already plain text w/ possible entities) - keep as is but unescape for make_card
    main_txt=g.insert_card(main_index, card, info["date"])
    open(main_index,"w",encoding="utf-8").write(main_txt)
    added.append((url_path, info["date"], info["title"]))
    print("added main card:", url_path, info["date"], info["title"][:30])

print("added", len(added))
# assertions
cur=open(main_index,encoding="utf-8").read()
print("cards:", cur.count('<div class="article-card">'), "** count:", cur.count("**"))
for u,_,_ in added:
    print("HIT", u, ("/"+u) in cur)
