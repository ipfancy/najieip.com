import os,json,subprocess
ROOT="/Users/ziganghe/wiki/najieip-verify"
p=os.path.join(ROOT,"site-inbox/deploy-log.json")
subprocess.run(["git","-C",ROOT,"checkout","--","site-inbox/deploy-log.json"],check=True)
raw=open(p,encoding="utf-8").read()
log=json.loads(raw)
print("indent=1?" , raw.startswith('{\n "deploys"'))
d=log["deploys"]
print("count",len(d))
print("first:",d[0]["date"],list(d[0].keys()))
print("last:",d[-1]["date"],list(d[-1].keys()))
for e in d[-4:]:
    print(" tail entry",e["date"],e.get("time"),list(e.keys()))
# newest by date
mx=max(e["date"] for e in d)
newest=[e for e in d if e["date"]==mx]
print("max date",mx,"count",len(newest),"keys",list(newest[-1].keys()))
print("is last entry max date?", d[-1]["date"]==mx)
