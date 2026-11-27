#!/usr/bin/env python3
"""SiteOps GEO 第48周 秘塔批量检测 — 本地 CDP 9225，9 查询，结果落 JSON
可靠路径：https://metaso.cn/?q=<urlencoded> + 轮询 innerText（连续 2 次不变视为生成完成）
"""
import json, sys, time, urllib.request, urllib.parse, websocket

PORT = 9225
BRANDS = ["najieip.com", "纳杰觅理", "何自刚", "爱普纳杰", "觅理", "纳杰"]
WALL_WORDS = ("微信扫码", "登录后继续", "手机验证", "账号密码")

QUERIES = [
    ("ART-2026-0134", "离婚前把游戏账号卖给朋友 钱还要分吗"),
    ("ART-2026-0134", "游戏账号离婚能分割吗 民法典127条"),
    ("ART-2026-0134", "抖音号离婚怎么估值 一般分几成"),
    ("ART-2026-0135", "食品贴牌 只授权商标 算不算委托生产"),
    ("ART-2026-0135", "12月1日 食品委托生产 标签还能写监制吗"),
    ("ART-2026-0135", "食品委托生产合同 商标许可 要补哪些条款"),
    ("ART-2026-0136", "高企认定2026新规 是真的吗"),
    ("ART-2026-0136", "高新技术企业 发明专利权重 45% 有文件吗"),
    ("ART-2026-0136", "高企证书 每年5月报表 忘了报会怎样"),
]


def get_page():
    tabs = [t for t in json.loads(urllib.request.urlopen(f"http://localhost:{PORT}/json").read())
            if t.get("type") == "page"]
    return tabs[0] if tabs else None


def cdp(ws, msg, method, params=None):
    ws.send(json.dumps({"id": msg, "method": method, "params": params or {}}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg:
            return resp


def ev(ws, msg, expr):
    r = cdp(ws, msg, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("result", {}).get("value")


def check(query):
    tab = get_page()
    if not tab:
        return {"error": "CDP 9225 无页面"}
    ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60)
    mid = 1
    try:
        url = "https://metaso.cn/?q=" + urllib.parse.quote(query)
        cdp(ws, mid, "Page.navigate", {"url": url})
        mid += 1
        prev, stable, t = "", 0, ""
        for _ in range(16):
            time.sleep(5)
            t = ev(ws, mid, "document.body ? document.body.innerText : ''") or ""
            mid += 1
            if len(t) > 300 and t == prev:
                stable += 1
            else:
                stable = 0
            prev = t
            if stable >= 2:
                break
            if len(t) < 130 and any(w in t for w in WALL_WORDS):
                break
        wall = len(t) < 130 and any(w in t for w in WALL_WORDS)
        body_start = t.rfind(query)
        body = t[body_start + len(query):] if body_start != -1 else t
        hits = {}
        for b in BRANDS:
            c = body.count(b)
            if c:
                i = body.find(b)
                hits[b] = {"count": c, "ctx": body[max(0, i - 60):i + 60].replace("\n", " | ")}
        src = ""
        k = t.rfind("来源")
        if k != -1:
            src = t[k:k + 1200].replace("\n", " | ")
        return {"query": query, "answer_len": len(t), "body_len": len(body),
                "login_wall": wall, "body_hits": hits,
                "body_head": body[:400].replace("\n", " | "),
                "sources_tail": src}
    finally:
        ws.close()


if __name__ == "__main__":
    out = "/Users/ziganghe/wiki/najieip-verify/site-inbox/geo-metaso-1128.json"
    results = []
    for aid, q in QUERIES:
        rec = {"article_id": aid, "query": q, "platform": "metaso"}
        try:
            rec.update(check(q))
        except Exception as e:
            rec["error"] = f"EXC: {e}"
        results.append(rec)
        print(json.dumps({"i": len(results), "art": aid, "q": q,
                          "len": rec.get("answer_len"), "wall": rec.get("login_wall"),
                          "hits": list((rec.get("body_hits") or {}).keys()),
                          "head": (rec.get("body_head") or "")[:150],
                          "src": (rec.get("sources_tail") or "")[:200],
                          "err": rec.get("error")}, ensure_ascii=False), flush=True)
        with open(out, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        time.sleep(3)
    print("DONE", out, len(results))
