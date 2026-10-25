import os,re,json
ROOT="/Users/ziganghe/wiki/najieip-verify"
p=os.path.join(ROOT,"articles.json")
aj=json.load(open(p,encoding="utf-8"))
u="/mili/blog/20261025-defendant-info-query-beijing.html"
if any(a["url"]==u for a in aj):
    print("already present")
else:
    pg=open(os.path.join(ROOT,u.lstrip("/")),encoding="utf-8").read()
    title=re.search(r'<meta property="og:title" content="([^"]+)"',pg).group(1)
    desc=re.search(r'<meta name="description" content="([^"]+)"',pg).group(1)
    if len(desc)>260: desc=desc[:260].rsplit("。",1)[0]+"。"
    entry={"url":u,"title":title,"date":"2026-10-25","site":"mili","description":desc,
           "tags":["立案实务","调查取证","刑事辩护"]}
    idx=0
    for k,a in enumerate(aj):
        if a.get("date","9999")<"2026-10-25": idx=k; break
    aj.insert(idx,entry)
    open(p,"w",encoding="utf-8").write(json.dumps(aj,ensure_ascii=False,indent=2)+"\n")
    print("inserted at",idx,"total",len(aj))
# cleanup one-off diag scripts from worktree
for f in ["site-inbox/diag-1025.py","site-inbox/diag2-1025.py","site-inbox/diag3-1025.py","site-inbox/diag4-1025.py","site-inbox/diag5-1025.py"]:
    fp=os.path.join(ROOT,f)
    if os.path.exists(fp): os.remove(fp); print("removed",f)
