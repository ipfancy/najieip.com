import os,re,subprocess,json
ROOT="/Users/ziganghe/wiki/najieip-verify"
for idx in ["blog/index.html","mili/blog/index.html"]:
    t=open(os.path.join(ROOT,idx),encoding="utf-8").read()
    body=t[t.find("<body"):]
    dep=0;bad=False
    for m in re.finditer(r"<(/?)div\b",body):
        dep += -1 if m.group(1)=="/" else 1
        if dep<0: bad=True
    print(idx,"cards",t.count('<div class="article-card">'),"divdepth",dep,"bad",bad,"stars",t.count("**"))
r=subprocess.run(["python3",os.path.join(ROOT,"site-inbox/guard-0918-articles-json.py"),"--check"],capture_output=True,text=True)
print("guard --check rc",r.returncode)
print((r.stdout or "")[-600:])
print((r.stderr or "")[-300:])
