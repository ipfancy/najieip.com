#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cf_apply_redirects.py — 用 CF API 把 /articles/ 旧路径 301 到三主体规范路径

读 `site-inbox/cf-redirects-articles-20260916.csv`（76 条 source→target），
幂等地建 Bulk Redirect List + items + 账户级 http_request_redirect 规则，最后逐条复测 301。

token 读取顺序（任一存在即可，绝不打印 token 内容）：
  1) 环境变量 CLOUDFLARE_API_TOKEN
  2) 文件 ~/.cloudflared/api_token
  3) ~/.hermes/.env 里的 CLOUDFLARE_API_TOKEN=...

用法：
  python3 site-inbox/cf_apply_redirects.py            # dry-run：只验证 token + 打印将提交的内容
  python3 site-inbox/cf_apply_redirects.py --apply    # 真正创建列表/条目/规则，并复测 301
  python3 site-inbox/cf_apply_redirects.py --verify    # 只复测线上 301 状态（不写 CF）
"""
import argparse, csv, json, os, re, ssl, subprocess, sys, urllib.error, urllib.parse, urllib.request

ROOT = "/mnt/c/Users/zigan/najieip-site"
os.chdir(ROOT)
SITE = "https://najieip.com"
ACCOUNT_ID = "d40df36c147f676b33595ccca1668ea4"          # 来自本机 cloudflared 凭据 AccountTag
LIST_NAME = "articles_legacy_301"
LIST_DESC = "najieip.com /articles/* 旧路径 → 三主体 blog 规范路径（2026-09-16 门丞）"
RULE_DESC = "najieip articles legacy 301"
CSV_PATH = "site-inbox/cf-redirects-articles-20260916.dashboard.csv"
API = "https://api.cloudflare.com/client/v4"

def read_token():
    t = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if t:
        return t, "env"
    p = os.path.expanduser("~/.cloudflared/api_token")
    if os.path.exists(p):
        return open(p).read().strip(), p
    p = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(p):
        for line in open(p):
            if line.startswith("CLOUDFLARE_API_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"'), p
    return None, ""

def api(method, path, token, body=None, ok=(200, 201)):
    req = urllib.request.Request(API + path, method=method,
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data, timeout=45, context=ssl.create_default_context()) as r:
            j = json.loads(r.read() or b"{}")
            return r.status, (j if isinstance(j, dict) else {"result": j})
    except urllib.error.HTTPError as e:
        raw = e.read()[:400].decode("utf-8", "replace")
        try:
            j = json.loads(raw)
        except Exception:
            j = {}
        j["success"] = False
        j["http_status"] = e.code
        j.setdefault("raw", raw)
        return e.code, j

def load_rows():
    """读控制台版无表头 CSV（SOURCE,TARGET,STATUS,PRESERVE_QUERY_STRING,INCLUDE_SUBDOMAINS,SUBPATH_MATCHING,PRESERVE_PATH_SUFFIX）"""
    rows = []
    for line in open(CSV_PATH, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        p = line.split(",")
        rows.append({"source": p[0], "target": p[1], "status": (p[2] or "301") if len(p) > 2 else "301",
                     "preserve_query_string": (p[3] if len(p) > 3 else "false").lower() == "true",
                     "include_subdomains": (p[4] if len(p) > 4 else "false").lower() == "true",
                     "subpath_matching": (p[5] if len(p) > 5 else "false").lower() == "true",
                     "preserve_path_suffix": (p[6] if len(p) > 6 else "false").lower() == "true"})
    items = [{"redirect": {"source_url": r["source"], "target_url": r["target"],
                           "status_code": int(r["status"]),
                           "preserve_query_string": r["preserve_query_string"],
                           "include_subdomains": r["include_subdomains"],
                           "subpath_matching": r["subpath_matching"],
                           "preserve_path_suffix": r["preserve_path_suffix"]}} for r in rows]
    return rows, items

def find_list(token):
    st, j = api("GET", f"/accounts/{ACCOUNT_ID}/rules/lists", token)
    if st != 200 or not j.get("success"):
        print("  ⚠️ 读列表失败:", st, j); return None
    for l in j.get("result", []):
        if l.get("name") == LIST_NAME:
            return l["id"]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows, items = load_rows()
    print(f"映射: {len(items)} 条（{CSV_PATH}）")

    token, src = read_token()
    if not token and not args.verify:
        sys.exit("✗ 未找到 CF token。请把 token 写入 ~/.cloudflared/api_token（chmod 600）后重试。")
    if token:
        st, j = api("GET", "/user/tokens/verify", token)
        status = (j.get("result") or {}).get("status") if isinstance(j, dict) else None
        print(f"token 来源: {src} | verify: HTTP {st} status={status} success={j.get('success') if isinstance(j,dict) else '?'}")
        if st != 200 or not (isinstance(j, dict) and j.get("success")):
            sys.exit(f"✗ token 无效或被拒（{j}）")

    if not args.verify:
        lid = find_list(token)
        print(f"列表 {LIST_NAME}: {'已存在 ' + lid if lid else '需创建'}")
        print("\n将提交的内容（前 3 条示例）:")
        for it in items[:3]:
            print("   ", json.dumps(it["redirect"], ensure_ascii=False))
        rule = {"action": "redirect", "enabled": True, "description": RULE_DESC,
                "expression": f"http.request.full_uri in ${LIST_NAME}",
                "action_parameters": {"from_list": {"name": LIST_NAME, "key": "http.request.full_uri"}}}
        print("将提交的规则:")
        print("   ", json.dumps(rule, ensure_ascii=False))

    if args.apply:
        lid = find_list(token)
        if not lid:
            st, j = api("POST", f"/accounts/{ACCOUNT_ID}/rules/lists", token,
                        {"name": LIST_NAME, "description": LIST_DESC, "kind": "redirect"})
            print(f"创建列表: HTTP {st} success={j.get('success')}")
            if st != 200 or not j.get("success"):
                sys.exit(f"✗ 创建列表失败：{j}（若为配额/权限错，回执里记下原文）")
            lid = j["result"]["id"]
        for i in range(0, len(items), 500):
            chunk = items[i:i + 500]
            st, j = api("PUT", f"/accounts/{ACCOUNT_ID}/rules/lists/{lid}/items", token, chunk)
            print(f"写入条目 {i}–{i+len(chunk)-1}: HTTP {st} success={j.get('success')}")
            if st != 200 or not j.get("success"):
                sys.exit(f"✗ 写入条目失败：{j}")
        rule = {"action": "redirect", "enabled": True, "description": RULE_DESC,
                "expression": f"http.request.full_uri in ${LIST_NAME}",
                "action_parameters": {"from_list": {"name": LIST_NAME, "key": "http.request.full_uri"}}}
        st, j = api("GET", f"/accounts/{ACCOUNT_ID}/rulesets/phases/http_request_redirect/entrypoint", token)
        if st == 200 and j.get("success"):
            rid = j["result"]["id"]
            existing = [r for r in j["result"].get("rules", []) if r.get("description") != RULE_DESC]
            st2, j2 = api("PUT", f"/accounts/{ACCOUNT_ID}/rulesets/{rid}", token,
                          {"rules": existing + [rule]})
            print(f"更新已有 ruleset {rid}: HTTP {st2} success={j2.get('success')}")
        else:
            st2, j2 = api("POST", f"/accounts/{ACCOUNT_ID}/rulesets", token,
                          {"name": "Bulk Redirects (najieip articles legacy)",
                           "kind": "root", "phase": "http_request_redirect", "rules": [rule]})
            print(f"创建 ruleset: HTTP {st2} success={j2.get('success')}")
        if st2 != 200 or not j2.get("success"):
            sys.exit(f"✗ 规则写入失败：{j2}")

    # 复测 301
    print("\n复测（期望 301 + Location 指规范路径）:")
    bad = []
    for r in rows:
        out = subprocess.run(["curl", "-s", "-o", "/dev/null", "-D", "-", "--max-time", "20",
                              "-H", "Cache-Control: no-cache", r["source"]],
                             capture_output=True, text=True).stdout
        m = re.search(r"^HTTP/\S+ (\d{3})", out, re.M)
        loc = re.search(r"^location:\s*(\S+)", out, re.M | re.I)
        code = m.group(1) if m else "???"
        good = code == "301" and loc and urllib.parse.unquote(loc.group(1)) == urllib.parse.unquote(r["target"])
        if not good:
            bad.append((r["source"], code, loc.group(1) if loc else "-"))
        print(f"  {'✅' if good else '⏳'} {code}  {urllib.parse.unquote(r['source'])}")
    print(f"\n301 已生效: {len(rows)-len(bad)}/{len(rows)}" + (f"；未生效 {len(bad)} 条（CF 规则未配时全为 200/无 Location）" if bad else " 🎉"))
    for b in bad[:5]:
        print("   ", b)
    return 0

if __name__ == "__main__":
    sys.exit(main())
