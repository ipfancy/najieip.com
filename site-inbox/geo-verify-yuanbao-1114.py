import json, time, urllib.request, websocket

PORT = 9224
Q = "公司说产品整体亏损 还要付发明人报酬吗"

def get_page():
    tabs = [t for t in json.loads(urllib.request.urlopen(f"http://localhost:{PORT}/json").read()) if t.get("type") == "page"]
    return tabs[0] if tabs else None

def cdp(ws, i, method, params=None):
    ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == i:
            return r

def ev(ws, i, expr):
    r = cdp(ws, i, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("result", {}).get("value")

tab = get_page()
ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60)
m = 1
cdp(ws, m, "Page.navigate", {"url": "https://yuanbao.tencent.com/chat"}); time.sleep(7); m += 1
print("typed:", ev(ws, m, """(() => {const ed=document.querySelector('[contenteditable="true"]'); if(!ed) return 'no_ed'; ed.focus(); document.execCommand('insertText',false,%s); return 'ok';})()""" % json.dumps(Q))); m += 1
print("sent:", ev(ws, m, """(() => {const ed=document.querySelector('[contenteditable="true"]'); ed.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true})); return 'enter';})()""")); m += 1
time.sleep(30)
res = ev(ws, m, """(() => {
  const out=[];
  const walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  const vw=window.innerWidth;
  let n;
  while(n=walk.nextNode()){
    const t=n.nodeValue||'';
    if(t.includes('纳杰觅理')||t.includes('何自刚')){
      let el=n.parentElement, chain=[];
      for(let i=0;i<4&&el;i++){chain.push(el.tagName+'.'+(el.className||'').toString().slice(0,40));el=el.parentElement;}
      const rg=document.createRange(); rg.selectNodeContents(n);
      const b=rg.getBoundingClientRect();
      out.push({txt:t.slice(0,120), x:Math.round(b.x), y:Math.round(b.y), vw:vw, chain:chain.join(' < ')});
    }
  }
  return JSON.stringify({hits:out.slice(0,8), total:out.length, vw:vw});
})()""")
print("DOM:", res)
ws.close()
