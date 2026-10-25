import os,re,subprocess,json,urllib.request,random
ROOT="/Users/ziganghe/wiki/najieip-verify"
sm=open(os.path.join(ROOT,"sitemap.xml"),encoding="utf-8").read()
urls=["/mili/blog/20261025-mili-ai-label-service.html",
      "/mili/blog/20261024-mili-yetan-will.html",
      "/mili/blog/20261025-defendant-info-query-beijing.html",
      "/najie/blog/20261025-najie-license-filing.html"]
for u in urls:
    print("sitemap", ("HIT " if ("https://najieip.com"+u) in sm else "MISS"), u)
print("--- git ---")
print(subprocess.run(["git","-C",ROOT,"log","origin/main","--oneline","-3"],capture_output=True,text=True).stdout)
print(subprocess.run(["git","-C",ROOT,"status","--porcelain"],capture_output=True,text=True).stdout[:400])
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def fetch(u):
    req=urllib.request.Request(u,headers=UA)
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status, r.read()
    except Exception as e:
        code=getattr(e,'code',0)
        return code, b''
print("--- live ---")
ok=0
for u in urls+["/img/20261025-mili-ai-label-service.png","/img/20261024-mili-yetan-will.png","/img/20261025-defendant-info-query-beijing.png"]:
    full="https://najieip.com"+u+"?cb=%d"%random.randint(1,999999)
    st,body=fetch(full)
    if u.endswith(".png"):
        print("LIVE",st,u,"bytes",len(body)); ok+= st==200; continue
    b=body.decode("utf-8","ignore")
    h1=len(re.findall(r"<h1[ >]",b)); ld=len(re.findall(r'application/ld\+json',b))
    print("LIVE",st,u,"h1",h1,"ld",ld,"og:image",'property="og:image"' in b,"stars",b.count("**"))
    ok+= (st==200 and h1==1 and ld>=2)
print("ok count",ok,"of",len(urls)+3)
# index live cards
for idx,needles in [("/blog/",["20261025-mili-ai-label-service","20261024-mili-yetan-will","20261025-defendant-info-query-beijing","20261025-najie-license-filing"]),
                    ("/mili/blog/",["20261025-mili-ai-label-service","20261024-mili-yetan-will"])]:
    st,body=fetch("https://najieip.com"+idx+"?cb=%d"%random.randint(1,999999))
    b=body.decode("utf-8","ignore")
    print("LIVE",st,idx,"cards",b.count('class="article-card"'),{n:(n in b) for n in needles})
