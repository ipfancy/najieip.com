import os, re, json, subprocess
ROOT="/Users/ziganghe/wiki/najieip-verify"; ART="/Users/ziganghe/wiki/digital-employees/articles"
fails=[]
def chk(cond,msg):
    print(("PASS " if cond else "FAIL ")+msg)
    if not cond: fails.append(msg)

def textify_html(b):
    m=re.search(r"<article>(.*?)</article>", b, re.S)
    a=m.group(1) if m else ""
    a=re.sub(r"<h1>.*?</h1>"," ",a,flags=re.S)
    a=re.sub(r"<h2>.*?</h2>"," ",a,flags=re.S)
    a=re.sub(r"<[^>]+>"," ",a)
    a=a.replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;",'"')
    a=re.sub(r"[\s*|]+","",a)
    return a

def textify_md(t):
    t=re.sub(r"<!--.*?-->","",t,flags=re.S)
    t=re.sub(r"^#\s.*$","",t,flags=re.M)
    t=re.sub(r"^##\s.*$","",t,flags=re.M)
    t=t.replace("|","")
    t=re.sub(r"^[-:\s]+$","",t,flags=re.M)
    t=re.sub(r"^>\s?","",t,flags=re.M)
    t=re.sub(r"[\s*]+","",t)
    return t

for stem in ["20261025-mili-ai-label-service","20261024-mili-yetan-will"]:
    p=os.path.join(ROOT,"mili/blog",stem+".html"); b=open(p,encoding="utf-8").read()
    md=open(os.path.join(ART,stem+".md"),encoding="utf-8").read()
    chk(len(re.findall(r"<h1[ >]",b))==1, f"{stem} h1==1")
    chk(len(re.findall(r'application/ld\+json',b))==2, f"{stem} ld==2")
    chk("og:image" in b and "twitter:image" in b, f"{stem} og/twitter image")
    chk(b.count("**")==0, f"{stem} no **")
    chk(not re.search(r"<p>\|",b), f"{stem} no raw md table")
    m=re.search(r'<meta name="description" content="([^"]*)"',b); d=m.group(1)
    h1=re.sub(r"<[^>]+>","",re.search(r"<h1>(.*?)</h1>",b,re.S).group(1))
    chk(len(d)>80 and d[:15]!=h1[:15], f"{stem} desc len={len(d)} not title-dup")
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>',b,re.S):
        json.loads(blk)
    chk(True, f"{stem} ld json parse")
    ta, tm = textify_html(b), textify_md(md)
    # md tail std lines are appended by generator; page has them too -> compare only md-side containment
    ok = tm == ta
    chk(ok, f"{stem} body fidelity (md head/tail present) page_len={len(ta)} md_len={len(tm)}")
    # div balance
    depth=0; bad=False
    for m2 in re.finditer(r"</?div\b", b[b.find("<body"):]):
        if m2.group(0).startswith("</"):
            depth-=1
            if depth<0: bad=True
        else: depth+=1
    chk(depth==0 and not bad, f"{stem} div balance (depth={depth})")

# defendant page
d=open(os.path.join(ROOT,"mili/blog/20261025-defendant-info-query-beijing.html"),encoding="utf-8").read()
chk(len(re.findall(r"<h1[ >]",d))==1,"defendant h1==1")
chk(len(re.findall(r'application/ld\+json',d))>=2,"defendant ld>=2")
chk('property="og:image"' in d and 'name="twitter:image"' in d,"defendant og+twitter image")
chk('property="og:image" content="https://najieip.com/img/20261025-defendant-info-query-beijing.png"' in d,"defendant og image url")
chk(os.path.exists(os.path.join(ROOT,"img/20261025-defendant-info-query-beijing.png")),"defendant img file exists")

# index card counts vs git HEAD
for idx in ["mili/blog/index.html","blog/index.html"]:
    cur=open(os.path.join(ROOT,idx),encoding="utf-8").read()
    old=subprocess.run(["git","-C",ROOT,"show","HEAD:"+idx],capture_output=True,text=True).stdout
    c1=cur.count('<div class="article-card">'); c0=old.count('<div class="article-card">')
    chk(c1==c0+ (2 if idx=="mili/blog/index.html" else 2), f"{idx} cards {c0}->{c1}")
    chk(cur.count("**")==0, f"{idx} no **")
    # depth distribution delta
    def dist(t):
        dd={}; dep=0
        for m in re.finditer(r"<(/?)div\b[^>]*>", t[t.find("<body"):]):
            if m.group(1)=="":
                if 'class="article-card"' in m.group(0): dd[dep]=dd.get(dep,0)+1
                dep+=1
            else: dep-=1
        return dd
    a,b2=dist(old),dist(cur)
    delta={k:b2.get(k,0)-a.get(k,0) for k in set(a)|set(b2)}
    chk(sum(delta.values())==2, f"{idx} depth-hist delta sum=2 {delta}")

aj=json.load(open(os.path.join(ROOT,"articles.json"),encoding="utf-8"))
urls=[a["url"] for a in aj]
chk(len(urls)==len(set(urls)),"articles.json no dup urls")
chk("/mili/blog/20261025-mili-ai-label-service.html" in urls and "/mili/blog/20261024-mili-yetan-will.html" in urls,"articles.json has 2 new entries")
print("TOTAL FAILS:",len(fails))
